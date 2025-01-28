from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware
import time

class LoggingMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        start_time = time.time()
        
        print(f"\n{'='*50}")
        print(f"🔄 Request: {request.method} {request.url}")
        
        print("\nHeaders:")
        for name, value in request.headers.items():
            print(f"{name}: {value}")
        
        if request.method in ["POST", "PUT"]:
            try:
                body = await request.body()
                body_str = body.decode()
                print(f"\nRequest Body: {body_str}")
                request._body = body
            except Exception as e:
                print(f"❌ Error reading request body: {str(e)}")

        try:
            response = await call_next(request)
            process_time = time.time() - start_time
            
            print(f"\nResponse Status: {response.status_code}")
            print(f"Process Time: {process_time:.2f}s")
            print(f"{'='*50}\n")
            
            return response
        except Exception as e:
            print(f"❌ Error in request processing: {str(e)}")
            raise