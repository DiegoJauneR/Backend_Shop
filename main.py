"""
FastAPI Backend Template
Aplicación principal con FastAPI
"""
from fastapi import FastAPI
from contextlib import asynccontextmanager
import logging

from app.config.settings import settings
from app.config.database import init_db, close_db
from app.api.v1.router import api_router
from app.middleware.cors import setup_cors
from app.middleware.rate_limit import setup_rate_limiting
from app.middleware.error_handler import setup_exception_handlers
from app.middleware.logging import LoggingMiddleware
from app.utils.logger import setup_logging

# Configurar logging
setup_logging("INFO" if not settings.DEBUG else "DEBUG")
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Gestión del ciclo de vida de la aplicación
    """
    # Startup
    logger.info("🚀 Iniciando aplicación...")
    logger.info(f"📝 Entorno: {settings.ENVIRONMENT}")
    logger.info(f"🔐 DEBUG: {settings.DEBUG}")
    
    # Inicializar base de datos (si está configurada)
    if settings.DATABASE_URL:
        try:
            await init_db()
            logger.info("✅ Base de datos inicializada")
        except Exception as e:
            logger.error(f"❌ Error al inicializar base de datos: {e}")
    else:
        logger.warning("⚠️  Base de datos no configurada - Define DATABASE_URL en .env")
    
    yield
    
    # Shutdown
    logger.info("👋 Cerrando aplicación...")
    await close_db()
    logger.info("✅ Conexiones cerradas")


# Crear instancia de FastAPI
app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    description="Backend API Template con FastAPI, JWT, PostgreSQL y más",
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json",
    lifespan=lifespan
)

# Configurar middleware
setup_cors(app)
setup_rate_limiting(app)
setup_exception_handlers(app)
app.add_middleware(LoggingMiddleware)

# Incluir routers
app.include_router(api_router, prefix=settings.API_PREFIX)


@app.get("/")
async def root():
    """Endpoint raíz"""
    return {
        "message": f"Bienvenido a {settings.APP_NAME}",
        "version": settings.APP_VERSION,
        "docs": "/docs",
        "status": "running"
    }


@app.get("/health")
async def health_check():
    """Endpoint de health check"""
    return {
        "status": "healthy",
        "environment": settings.ENVIRONMENT,
        "version": settings.APP_VERSION
    }


if __name__ == "__main__":
    import uvicorn
    
    uvicorn.run(
        "main:app",
        host=settings.HOST,
        port=settings.PORT,
        reload=settings.DEBUG,
        log_level="info"
    )
