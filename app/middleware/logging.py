# app/middleware/logging.py
from fastapi import Request
import time
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def log_request_middleware(request: Request, call_next):
    start_time = time.time()
    
    # Log request
    logger.info(f"🔄 Request: {request.method} {request.url}")
    
    try:
        response = await call_next(request)
        
        # Log response
        process_time = time.time() - start_time
        status_code = response.status_code
        logger.info(f"✅ Response: {status_code} in {process_time:.2f}s")
        
        return response
    except Exception as e:
        logger.error(f"❌ Error: {str(e)}")
        raise