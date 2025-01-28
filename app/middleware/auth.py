from fastapi import Request
from fastapi.responses import RedirectResponse
from sqlalchemy.orm import Session
from app.utils.db import get_db
from app.models.models import User
from starlette.middleware.base import BaseHTTPMiddleware

async def verify_auth(request: Request, call_next):
    if request.url.path.startswith("/auth/"):
        return await call_next(request)
        
    if request.url.path.startswith("/static/"):
        return await call_next(request)

    user_id = request.session.get("user_id")
    if not user_id:
        return RedirectResponse(url="/auth/login", status_code=302)

    # Obtener usuario de la DB
    db = next(get_db())
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        return RedirectResponse(url="/auth/login", status_code=302)

    # Añadir usuario a request state
    request.state.user = user
    response = await call_next(request)
    return response

class AuthMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        # Rutas públicas que no requieren autenticación
        public_paths = ["/auth/login", "/auth/token", "/static"]
        
        # Verificar si la ruta actual es pública
        if any(request.url.path.startswith(path) for path in public_paths):
            return await call_next(request)

        # Verificar si hay sesión activa
        user_id = request.session.get("user_id")
        if not user_id:
            return RedirectResponse(url="/auth/login", status_code=302)

        # Obtener usuario de la DB
        try:
            db = next(get_db())
            user = db.query(User).filter(User.id == user_id).first()
            if not user:
                # Si el usuario no existe, limpiar sesión y redireccionar
                request.session.clear()
                return RedirectResponse(url="/auth/login", status_code=302)

            # Añadir usuario a request state para uso en las rutas
            request.state.user = user
            
            # Continuar con la solicitud
            response = await call_next(request)
            return response
            
        except Exception as e:
            # En caso de error, redireccionar al login
            return RedirectResponse(url="/auth/login", status_code=302)