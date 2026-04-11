"""
Script para crear un usuario administrador
"""
import asyncio
import logging
from app.config.database import AsyncSessionLocal
from app.schemas.user import UserCreate
from app.services.user_service import UserService

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


async def create_superuser():
    """Crear usuario administrador"""
    async with AsyncSessionLocal() as db:
        try:
            # Datos del superusuario
            user_data = UserCreate(
                email="admin@example.com",
                username="admin",
                password="Admin123!",
                full_name="Administrador"
            )
            
            # Verificar si ya existe
            existing = await UserService.get_by_email(db, user_data.email)
            if existing:
                logger.warning(f"⚠️  El usuario {user_data.email} ya existe")
                return
            
            # Crear usuario
            user = await UserService.create(db, user_data)
            
            # Actualizar para hacer superuser
            from app.models.user import User
            from sqlalchemy import select
            
            result = await db.execute(select(User).where(User.id == user.id))
            db_user = result.scalar_one()
            db_user.is_superuser = True
            
            await db.commit()
            
            logger.info(f"✅ Superusuario creado exitosamente")
            logger.info(f"   Email: {user_data.email}")
            logger.info(f"   Username: {user_data.username}")
            logger.info(f"   Password: {user_data.password}")
            
        except Exception as e:
            logger.error(f"❌ Error al crear superusuario: {e}")
            raise


if __name__ == "__main__":
    asyncio.run(create_superuser())
