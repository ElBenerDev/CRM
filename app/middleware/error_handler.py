# app/middleware/error_handler.py
from fastapi import Request, HTTPException
from fastapi.responses import JSONResponse
import traceback
import logging

logger = logging.getLogger(__name__)

async def error_handler_middleware(request: Request, call_next):
    try:
        return await call_next(request)
    except HTTPException as http_ex:
        return JSONResponse(
            status_code=http_ex.status_code,
            content={"detail": http_ex.detail}
        )
    except Exception as e:
        logger.error(f"Error no manejado: {str(e)}\n{traceback.format_exc()}")
        return JSONResponse(
            status_code=500,
            content={
                "detail": "Error interno del servidor",
                "type": type(e).__name__
            }
        )