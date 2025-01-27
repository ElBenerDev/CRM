# app/middleware/auth.py
from fastapi import Request
from fastapi.responses import RedirectResponse
from starlette.middleware.base import BaseHTTPMiddleware
from app.auth.utils import get_current_user, oauth2_scheme

class AuthMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        # Rutas que no requieren autenticación
        public_paths = [
            "/auth/login",
            "/auth/register",
            "/auth/token",
            "/static/",
        ]

        # Verificar si la ruta actual es pública
        if any(request.url.path.startswith(path) for path in public_paths):
            return await call_next(request)

        # Verificar token en cookies
        token = request.cookies.get("access_token")
        if not token:
            return RedirectResponse(url="/auth/login", status_code=302)

        try:
            # Limpiar el prefijo "Bearer " si existe
            if token.startswith("Bearer "):
                token = token.split(" ")[1]

            # Verificar el token y continuar si es válido
            return await call_next(request)
        except Exception:
            return RedirectResponse(url="/auth/login", status_code=302)