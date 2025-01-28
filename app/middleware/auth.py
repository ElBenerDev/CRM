from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import RedirectResponse
from jose import JWTError, jwt
from app.core.config import settings

class AuthMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        excluded_paths = [
            "/auth/login",
            "/auth/token", 
            "/auth/register",
            "/auth/logout",
            "/static"
        ]
        
        if any(request.url.path.startswith(path) for path in excluded_paths):
            return await call_next(request)

        try:
            token = request.cookies.get("access_token")
            if not token:
                return RedirectResponse(url="/auth/login", status_code=302)

            if token.startswith("Bearer "):
                token = token.split(" ")[1]

            try:
                payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
                if not payload.get("sub"):
                    raise JWTError
            except JWTError:
                return RedirectResponse(url="/auth/login", status_code=302)

            response = await call_next(request)
            return response
            
        except Exception as e:
            print(f"Error en AuthMiddleware: {str(e)}")
            return RedirectResponse(url="/auth/login", status_code=302)