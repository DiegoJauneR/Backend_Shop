"""
Script para inicializar la base de datos
Crear tablas y datos iniciales
"""
import asyncio
import logging
from app.config.database import init_db
from app.config.settings import settings

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


async def init():
    """Inicializar base de datos"""
    logger.info("Inicializando base de datos...")
    logger.info(f"Database URL: {settings.DATABASE_URL}")
    
    try:
        await init_db()
        logger.info("✅ Base de datos inicializada correctamente")
    except Exception as e:
        logger.error(f"❌ Error al inicializar base de datos: {e}")
        raise


if __name__ == "__main__":
    asyncio.run(init())
