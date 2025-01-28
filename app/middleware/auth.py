from fastapi import Request
from fastapi.responses import RedirectResponse
from sqlalchemy.orm import Session
from app.utils.db import get_db
from app.models.models import User
from starlette.middleware.base import BaseHTTPMiddleware
from typing import List

class AuthMiddleware(BaseHTTPMiddleware):
    def __init__(self, app):
        super().__init__(app)
        self.public_paths: List[str] = [
            "/auth/login",
            "/auth/token",
            "/static",
            "/favicon.ico"
        ]

    async def dispatch(self, request: Request, call_next):
        # Verificar si la ruta actual es pública
        if any(request.url.path.startswith(path) for path in self.public_paths):
            return await call_next(request)

        try:
            # Verificar si hay sesión activa
            if not hasattr(request, "session"):
                return RedirectResponse(url="/auth/login", status_code=302)

            user_id = request.session.get("user_id")
            if not user_id:
                return RedirectResponse(url="/auth/login", status_code=302)

            # Obtener usuario de la DB
            db = next(get_db())
            user = db.query(User).filter(User.id == user_id).first()
            
            if not user:
                # Si el usuario no existe, limpiar sesión y redireccionar
                if hasattr(request, "session"):
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