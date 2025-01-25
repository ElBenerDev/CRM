# app/middleware/rate_limit.py
from fastapi import Request, HTTPException
from fastapi.responses import JSONResponse
import time
from collections import defaultdict

class RateLimiter:
    def __init__(self, requests_per_minute: int = 60):
        self.requests_per_minute = requests_per_minute
        self.requests = defaultdict(list)

    async def __call__(self, request: Request, call_next):
        client_ip = request.client.host
        now = time.time()
        
        # Limpiar solicitudes antiguas
        self.requests[client_ip] = [
            req_time for req_time in self.requests[client_ip]
            if req_time > now - 60
        ]
        
        # Verificar límite
        if len(self.requests[client_ip]) >= self.requests_per_minute:
            return JSONResponse(
                status_code=429,
                content={
                    "detail": "Demasiadas solicitudes. Por favor, intente más tarde."
                }
            )
        
        # Agregar nueva solicitud
        self.requests[client_ip].append(now)
        
        return await call_next(request)