# app/middleware/auth.py
from fastapi import Request
from fastapi.responses import RedirectResponse
from starlette.middleware.base import BaseHTTPMiddleware
from app.utils.logging_config import logger

from fastapi import Request

from typing import Callable
import functools

def require_auth(func: Callable):
    @functools.wraps(func)
    async def wrapper(request: Request, *args, **kwargs):
        user_id = request.session.get("user_id")
        if not user_id:
            return RedirectResponse(url="/auth/login", status_code=302)
        return await func(request, *args, **kwargs)
    return wrapper

class AuthMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        public_paths = [
            "/auth/login",
            "/static",
        ]

        is_public = any(request.url.path.startswith(path) for path in public_paths)
        if is_public or request.session.get("user_id"):
            return await call_next(request)
        return RedirectResponse(url="/auth/login", status_code=302)