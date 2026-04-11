"""
Endpoints de usuarios
"""
from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List
from app.config.database import get_db
from app.schemas.user import UserResponse, UserUpdate
from app.schemas.common import MessageResponse
from app.services.user_service import UserService
from app.core.security import get_current_user_id
from app.middleware.rate_limit import limiter
from fastapi import Request

router = APIRouter(prefix="/users", tags=["Users"])


@router.get("/me", response_model=UserResponse)
async def get_current_user(
    user_id: int = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db)
):
    """
    Obtener información del usuario actual
    """
    user = await UserService.get_by_id(db, user_id)
    return user


@router.put("/me", response_model=UserResponse)
async def update_current_user(
    user_data: UserUpdate,
    user_id: int = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db)
):
    """
    Actualizar información del usuario actual
    """
    user = await UserService.update(db, user_id, user_data)
    return user


@router.delete("/me", response_model=MessageResponse)
async def delete_current_user(
    user_id: int = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db)
):
    """
    Eliminar cuenta del usuario actual
    """
    await UserService.delete(db, user_id)
    return MessageResponse(message="Usuario eliminado exitosamente")


@router.get("", response_model=List[UserResponse])
@limiter.limit("30/minute")
async def get_users(
    request: Request,
    skip: int = 0,
    limit: int = 100,
    user_id: int = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db)
):
    """
    Obtener lista de usuarios (requiere autenticación)
    """
    users = await UserService.get_all(db, skip=skip, limit=limit)
    return users


@router.get("/{user_id_param}", response_model=UserResponse)
async def get_user(
    user_id_param: int,
    user_id: int = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db)
):
    """
    Obtener usuario por ID
    """
    user = await UserService.get_by_id(db, user_id_param)
    return user
