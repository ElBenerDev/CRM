# app/middleware/auth.py
from fastapi import Request
from fastapi.responses import RedirectResponse
from starlette.middleware.base import BaseHTTPMiddleware
from app.utils.logging_config import logger

class AuthMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        # Rutas que no requieren autenticación
        public_paths = ["/auth/login", "/auth/token", "/static"]
        
        # Si es una ruta pública, permitir acceso
        if any(request.url.path.startswith(path) for path in public_paths):
            return await call_next(request)

        # Verificar si hay sesión
        if not request.session.get("user_id"):
            print("No hay sesión activa")
            return RedirectResponse(url="/auth/login", status_code=302)

        return await call_next(request)