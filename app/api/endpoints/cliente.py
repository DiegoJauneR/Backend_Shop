"""
Endpoints CRUD de Cliente
"""
from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List
from app.config.database import get_db
from app.schemas.cliente import ClienteCreate, ClienteUpdate, ClienteResponse
from app.schemas.common import MessageResponse
from app.services.cliente_service import ClienteService

router = APIRouter(prefix="/cliente", tags=["Cliente"])


@router.get("", response_model=List[ClienteResponse])
async def list_clientes(
    skip: int = 0,
    limit: int = 100,
    db: AsyncSession = Depends(get_db)
):
    return await ClienteService.get_all(db, skip=skip, limit=limit)


@router.post("", response_model=ClienteResponse, status_code=status.HTTP_201_CREATED)
async def create_cliente(
    data: ClienteCreate,
    db: AsyncSession = Depends(get_db)
):
    return await ClienteService.create(db, data)


@router.get("/{cliente_id}", response_model=ClienteResponse)
async def get_cliente(
    cliente_id: int,
    db: AsyncSession = Depends(get_db)
):
    return await ClienteService.get_by_id(db, cliente_id)


@router.put("/{cliente_id}", response_model=ClienteResponse)
async def update_cliente(
    cliente_id: int,
    data: ClienteUpdate,
    db: AsyncSession = Depends(get_db)
):
    return await ClienteService.update(db, cliente_id, data)


@router.delete("/{cliente_id}", response_model=MessageResponse)
async def delete_cliente(
    cliente_id: int,
    db: AsyncSession = Depends(get_db)
):
    await ClienteService.delete(db, cliente_id)
    return MessageResponse(message=f"Cliente {cliente_id} eliminado exitosamente")
