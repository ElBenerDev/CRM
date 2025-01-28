from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware
import os
from app.core.config import settings

class DebugMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        print(f"\n🔍 DEBUG - Request path: {request.url.path}")
        print(f"🔍 DEBUG - Templates dir: {settings.TEMPLATES_DIR}")
        print(f"🔍 DEBUG - Template files: {os.listdir(settings.TEMPLATES_DIR)}")
        
        try:
            response = await call_next(request)
            print(f"🔍 DEBUG - Response status: {response.status_code}")
            return response
        except Exception as e:
            print(f"❌ DEBUG - Error: {str(e)}")
            raise e