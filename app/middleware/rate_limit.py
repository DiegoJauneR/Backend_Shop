"""
Middleware de rate limiting
"""
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded
from fastapi import FastAPI, Request
from app.config.settings import settings


# Crear limiter
limiter = Limiter(key_func=get_remote_address, default_limits=[])


def setup_rate_limiting(app: FastAPI) -> None:
    """
    Configurar rate limiting
    """
    if settings.RATE_LIMIT_ENABLED:
        app.state.limiter = limiter
        app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)
