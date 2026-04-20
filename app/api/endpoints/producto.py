"""
Endpoints CRUD de Producto
"""
from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List
from app.config.database import get_db
from app.schemas.producto import ProductoCreate, ProductoUpdate, ProductoPatch, ProductoResponse
from app.schemas.common import MessageResponse
from app.services.producto_service import ProductoService

router = APIRouter(prefix="/productos", tags=["Productos"])


@router.get("", response_model=List[ProductoResponse])
async def list_productos(
    skip: int = 0,
    limit: int = 100,
    db: AsyncSession = Depends(get_db),
):
    return await ProductoService.get_all(db, skip=skip, limit=limit)


@router.get("/{producto_id}", response_model=ProductoResponse)
async def get_producto(
    producto_id: int,
    db: AsyncSession = Depends(get_db),
):
    return await ProductoService.get_by_id(db, producto_id)


@router.post("", response_model=ProductoResponse, status_code=status.HTTP_201_CREATED)
async def create_producto(
    data: ProductoCreate,
    db: AsyncSession = Depends(get_db),
):
    return await ProductoService.create(db, data)


@router.put("/{producto_id}", response_model=ProductoResponse)
async def update_producto(
    producto_id: int,
    data: ProductoUpdate,
    db: AsyncSession = Depends(get_db),
):
    return await ProductoService.update(db, producto_id, data)


@router.patch("/{producto_id}", response_model=ProductoResponse)
async def patch_producto(
    producto_id: int,
    data: ProductoPatch,
    db: AsyncSession = Depends(get_db),
):
    return await ProductoService.update(db, producto_id, data)


@router.delete("/{producto_id}", response_model=MessageResponse)
async def delete_producto(
    producto_id: int,
    db: AsyncSession = Depends(get_db),
):
    await ProductoService.delete(db, producto_id)
    return MessageResponse(message="Producto eliminado exitosamente")
