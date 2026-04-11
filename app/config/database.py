"""
Configuración de la base de datos
"""
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy.orm import declarative_base
from app.config.settings import settings

# Crear engine asíncrono (solo si DATABASE_URL está configurada)
engine = None
if settings.DATABASE_URL:
    engine = create_async_engine(
        settings.DATABASE_URL,
        echo=settings.DB_ECHO,
        future=True,
        pool_pre_ping=True,
        pool_size=10,
        max_overflow=20
    )

# Session maker
AsyncSessionLocal = None
if engine:
    AsyncSessionLocal = async_sessionmaker(
        engine,
        class_=AsyncSession,
        expire_on_commit=False,
        autocommit=False,
        autoflush=False
    )

# Base para los modelos
Base = declarative_base()


async def get_db():
    """
    Dependency para obtener la sesión de base de datos
    """
    if not AsyncSessionLocal:
        raise RuntimeError("Database no configurada. Define DATABASE_URL en .env")
    
    async with AsyncSessionLocal() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()


async def init_db():
    """
    Inicializar la base de datos (crear tablas)
    """
    if not settings.DATABASE_URL:
        return
    
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)


async def close_db():
    """
    Cerrar conexión a la base de datos
    """
    if engine:
        await engine.dispose()
