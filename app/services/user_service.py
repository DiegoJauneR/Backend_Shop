"""
Servicio de Usuario
"""
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import Optional, List
import logging
from app.models.user import User
from app.schemas.user import UserCreate, UserUpdate
from app.core.security import get_password_hash, verify_password
from app.core.exceptions import NotFoundException, ConflictException

logger = logging.getLogger(__name__)


class UserService:
    """Servicio para operaciones de usuario"""
    
    @staticmethod
    async def get_by_id(db: AsyncSession, user_id: int) -> Optional[User]:
        """Obtener usuario por ID"""
        result = await db.execute(select(User).where(User.id == user_id))
        return result.scalar_one_or_none()
    
    @staticmethod
    async def get_by_email(db: AsyncSession, email: str) -> Optional[User]:
        """Obtener usuario por email"""
        result = await db.execute(select(User).where(User.email == email))
        return result.scalar_one_or_none()
    
    @staticmethod
    async def get_by_username(db: AsyncSession, username: str) -> Optional[User]:
        """Obtener usuario por username"""
        result = await db.execute(select(User).where(User.username == username))
        return result.scalar_one_or_none()
    
    @staticmethod
    async def get_all(db: AsyncSession, skip: int = 0, limit: int = 100) -> List[User]:
        """Obtener todos los usuarios"""
        result = await db.execute(select(User).offset(skip).limit(limit))
        return result.scalars().all()
    
    @staticmethod
    async def create(db: AsyncSession, user_data: UserCreate) -> User:
        """Crear nuevo usuario"""
        # Verificar si el email ya existe
        existing_user = await UserService.get_by_email(db, user_data.email)
        if existing_user:
            raise ConflictException("El email ya está registrado")
        
        # Verificar si el username ya existe
        existing_username = await UserService.get_by_username(db, user_data.username)
        if existing_username:
            raise ConflictException("El username ya está en uso")
        
        # Crear usuario
        hashed_password = get_password_hash(user_data.password)
        
        db_user = User(
            email=user_data.email,
            username=user_data.username,
            full_name=user_data.full_name,
            hashed_password=hashed_password,
        )
        
        db.add(db_user)
        await db.commit()
        await db.refresh(db_user)
        
        return db_user
    
    @staticmethod
    async def update(db: AsyncSession, user_id: int, user_data: UserUpdate) -> User:
        """Actualizar usuario"""
        db_user = await UserService.get_by_id(db, user_id)
        if not db_user:
            raise NotFoundException("Usuario no encontrado")
        
        # Actualizar campos si se proporcionan
        update_data = user_data.model_dump(exclude_unset=True)
        
        # Si se actualiza el password, hashearlo
        if "password" in update_data:
            update_data["hashed_password"] = get_password_hash(update_data.pop("password"))
        
        # Verificar email único
        if "email" in update_data and update_data["email"] != db_user.email:
            existing = await UserService.get_by_email(db, update_data["email"])
            if existing:
                raise ConflictException("El email ya está registrado")
        
        # Verificar username único
        if "username" in update_data and update_data["username"] != db_user.username:
            existing = await UserService.get_by_username(db, update_data["username"])
            if existing:
                raise ConflictException("El username ya está en uso")
        
        for field, value in update_data.items():
            setattr(db_user, field, value)
        
        await db.commit()
        await db.refresh(db_user)
        
        return db_user
    
    @staticmethod
    async def delete(db: AsyncSession, user_id: int) -> bool:
        """Eliminar usuario"""
        db_user = await UserService.get_by_id(db, user_id)
        if not db_user:
            raise NotFoundException("Usuario no encontrado")
        
        await db.delete(db_user)
        await db.commit()
        
        return True
    
    @staticmethod
    async def authenticate(db: AsyncSession, username: str, password: str) -> Optional[User]:
        """Autenticar usuario"""
        user = await UserService.get_by_username(db, username)
        if not user:
            user = await UserService.get_by_email(db, username)

        if not user:
            logger.warning(f"authenticate: usuario '{username}' no encontrado")
            return None

        if not verify_password(password, user.hashed_password):
            logger.warning(f"authenticate: contraseña incorrecta para '{username}'")
            return None

        if not user.is_active:
            logger.warning(f"authenticate: usuario '{username}' inactivo")
            return None

        return user
