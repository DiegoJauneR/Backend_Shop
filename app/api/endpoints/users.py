"""
Endpoints de usuarios
"""
from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List
from app.config.database import get_db
from app.schemas.user import UserAdminCreate, UserResponse, UserSelfUpdate, UserUpdate
from app.schemas.common import MessageResponse
from app.services.user_service import UserService
from app.core.security import get_current_user_id
from app.core.exceptions import BadRequestException, ForbiddenException, NotFoundException
from app.middleware.rate_limit import limiter
from fastapi import Request

router = APIRouter(prefix="/users", tags=["Users"])


async def require_admin_user(
    user_id: int = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db),
):
    user = await UserService.get_by_id(db, user_id)
    if not user:
        raise NotFoundException("Usuario no encontrado")

    if user.role != "admin" and not user.is_superuser:
        raise ForbiddenException("Solo un administrador puede gestionar trabajadores")

    return user


@router.get("/me", response_model=UserResponse)
async def get_current_user(
    user_id: int = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db)
):
    user = await UserService.get_by_id(db, user_id)
    return user


@router.put("/me", response_model=UserResponse)
async def update_current_user(
    user_data: UserSelfUpdate,
    user_id: int = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db)
):
    user = await UserService.update(db, user_id, user_data)
    return user


@router.delete("/me", response_model=MessageResponse)
async def delete_current_user(
    user_id: int = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db)
):
    await UserService.delete(db, user_id)
    return MessageResponse(message="Usuario eliminado exitosamente")


@router.get("", response_model=List[UserResponse])
@limiter.limit("30/minute")
async def get_users(
    request: Request,
    skip: int = 0,
    limit: int = 100,
    admin_user=Depends(require_admin_user),
    db: AsyncSession = Depends(get_db)
):
    users = await UserService.get_all(db, skip=skip, limit=limit)
    return users


@router.post("", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
@limiter.limit("20/minute")
async def create_user(
    request: Request,
    user_data: UserAdminCreate,
    admin_user=Depends(require_admin_user),
    db: AsyncSession = Depends(get_db),
):
    user = await UserService.create(db, user_data)
    return user


@router.get("/{user_id_param}", response_model=UserResponse)
async def get_user(
    user_id_param: int,
    admin_user=Depends(require_admin_user),
    db: AsyncSession = Depends(get_db)
):
    user = await UserService.get_by_id(db, user_id_param)
    if not user:
        raise NotFoundException("Usuario no encontrado")
    return user


@router.put("/{user_id_param}", response_model=UserResponse)
async def update_user(
    user_id_param: int,
    user_data: UserUpdate,
    admin_user=Depends(require_admin_user),
    db: AsyncSession = Depends(get_db),
):
    user = await UserService.update(db, user_id_param, user_data)
    return user


@router.delete("/{user_id_param}", response_model=MessageResponse)
async def delete_user(
    user_id_param: int,
    admin_user=Depends(require_admin_user),
    db: AsyncSession = Depends(get_db),
):
    if user_id_param == admin_user.id:
        raise BadRequestException("No puedes desactivar tu propio usuario administrador")

    await UserService.update(db, user_id_param, UserUpdate(is_active=False))
    return MessageResponse(message="Trabajador desactivado exitosamente")
