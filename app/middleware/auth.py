import logging
from fastapi import Request
from fastapi.responses import RedirectResponse
from starlette.middleware.base import BaseHTTPMiddleware

logger = logging.getLogger(__name__)
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

class AuthMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        # Lista de rutas públicas
        public_paths = ["/auth/login", "/auth/token", "/static", "/favicon.ico"]
        
        # Permitir rutas públicas
        if any(request.url.path.startswith(path) for path in public_paths):
            return await call_next(request)

        try:
            # Verificar sesión
            if not hasattr(request, "session"):
                return RedirectResponse(url="/auth/login")
                
            user_id = request.session.get("user_id")
            if not user_id:
                return RedirectResponse(url="/auth/login")

            # Continuar con la solicitud
            return await call_next(request)
            
        except Exception as e:
            logger.error(f"Error en AuthMiddleware: {str(e)}")
            return RedirectResponse(url="/auth/login")