"""
Middleware logging
"""
import time
import logging
from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware

logger = logging.getLogger(__name__)


class LoggingMiddleware(BaseHTTPMiddleware):
    """
    Middleware para logging de requests
    """
    
    async def dispatch(self, request: Request, call_next):
        start_time = time.time()
        
        # Log de request
        has_auth = "Authorization" in request.headers
        auth_preview = ""
        if has_auth:
            auth_val = request.headers["Authorization"]
            auth_preview = f" | Auth: {auth_val[:20]}..."
        else:
            auth_preview = " | Auth: MISSING"
        logger.info(f"Request: {request.method} {request.url.path}{auth_preview}")
        
        # Procesar request
        response = await call_next(request)
        
        # Calcular tiempo de procesamiento
        process_time = time.time() - start_time
        
        # Log de response
        logger.info(
            f"Response: {request.method} {request.url.path} "
            f"Status: {response.status_code} Time: {process_time:.3f}s"
        )
        
        # Agregar header de tiempo de procesamiento
        response.headers["X-Process-Time"] = str(process_time)
        
        return response
