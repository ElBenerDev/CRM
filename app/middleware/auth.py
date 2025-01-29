from fastapi import Request
from fastapi.responses import RedirectResponse
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.types import ASGIApp

class AuthMiddleware(BaseHTTPMiddleware):
    def __init__(self, app: ASGIApp):
        # Lista de rutas públicas
        self.public_routes = {
            "/auth/login",
            "/static",
            "/favicon.ico",
            "/"
        }
        super().__init__(app)

    async def dispatch(self, request: Request, call_next):
        # Si es una ruta pública, omitir verificación
        if any(request.url.path.startswith(route) for route in self.public_routes):
            return await call_next(request)
        
        # Verificar sesión solo para rutas privadas
        if not request.session.get("user_id"):
            return RedirectResponse(url="/auth/login", status_code=303)
        
        return await call_next(request)