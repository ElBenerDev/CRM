# app/middleware/auth.py
from fastapi import Request
from fastapi.responses import RedirectResponse
from starlette.middleware.base import BaseHTTPMiddleware
from app.utils.logging_config import logger

class AuthMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        public_paths = [
            "/auth/login",
            "/auth/token",
            "/static",
        ]
        
        path = request.url.path
        is_public = any(path.startswith(p) for p in public_paths)
        
        if is_public or request.session.get("user_id"):
            return await call_next(request)
            
        return RedirectResponse(url="/auth/login", status_code=302)