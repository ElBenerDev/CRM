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
            # Verificar sesión de manera segura
            session = request.session
            user_id = session.get("user_id") if hasattr(request, "session") else None

            if not user_id:
                return RedirectResponse(url="/auth/login", status_code=302)

            # Continuar con la solicitud
            response = await call_next(request)
            return response
            
        except Exception as e:
            logger.error(f"Error en AuthMiddleware: {str(e)}")
            return RedirectResponse(url="/auth/login", status_code=302)