# En app/middleware/auth.py
from fastapi import Request
from fastapi.responses import RedirectResponse
from starlette.middleware.base import BaseHTTPMiddleware

class AuthMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        # Lista de rutas públicas que no requieren autenticación
        public_routes = [
            "/auth/login",
            "/static",
            "/favicon.ico",
            "/"
        ]
        
        # Si la ruta es pública, no verificar sesión
        if request.url.path in public_routes:
            return await call_next(request)
        
        # Verificar si hay una sesión activa
        if not request.session.get("user_id"):
            return RedirectResponse(url="/auth/login", status_code=303)
        
        return await call_next(request)