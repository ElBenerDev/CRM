import logging
from fastapi import Request
from fastapi.responses import RedirectResponse
from sqlalchemy.orm import Session
from app.utils.db import get_db
from app.models.models import User
from starlette.middleware.base import BaseHTTPMiddleware
from typing import List

logger = logging.getLogger(__name__)

class AuthMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        # Lista de rutas públicas
        public_paths = ["/auth/login", "/auth/token", "/static", "/favicon.ico"]
        
        # Permitir rutas públicas
        if any(request.url.path.startswith(path) for path in public_paths):
            return await call_next(request)

        # Verificar sesión
        user_id = request.session.get("user_id")
        if not user_id:
            return RedirectResponse(url="/auth/login")

        # Continuar con la solicitud
        return await call_next(request)