"""
Endpoints CRUD de Detalle de Venta
"""
from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List
from app.config.database import get_db
from app.schemas.detalle_venta import (
    DetalleVentaCreate,
    DetalleVentaUpdate,
    DetalleVentaPatch,
    DetalleVentaResponse,
)
from app.schemas.common import MessageResponse
from app.services.detalle_venta_service import DetalleVentaService

router = APIRouter(prefix="/detalles-venta", tags=["Detalles de Venta"])


@router.get("", response_model=List[DetalleVentaResponse])
async def list_detalles(
    skip: int = 0,
    limit: int = 100,
    db: AsyncSession = Depends(get_db),
):
    return await DetalleVentaService.get_all(db, skip=skip, limit=limit)


@router.get("/venta/{venta_id}", response_model=List[DetalleVentaResponse])
async def get_detalles_por_venta(
    venta_id: int,
    db: AsyncSession = Depends(get_db),
):
    """Obtener todos los detalles de una venta específica."""
    return await DetalleVentaService.get_by_venta(db, venta_id)


@router.get("/{detalle_id}", response_model=DetalleVentaResponse)
async def get_detalle(
    detalle_id: int,
    db: AsyncSession = Depends(get_db),
):
    return await DetalleVentaService.get_by_id(db, detalle_id)


@router.post("", response_model=DetalleVentaResponse, status_code=status.HTTP_201_CREATED)
async def create_detalle(
    data: DetalleVentaCreate,
    db: AsyncSession = Depends(get_db),
):
    return await DetalleVentaService.create(db, data)


@router.put("/{detalle_id}", response_model=DetalleVentaResponse)
async def update_detalle(
    detalle_id: int,
    data: DetalleVentaUpdate,
    db: AsyncSession = Depends(get_db),
):
    return await DetalleVentaService.update(db, detalle_id, data)


@router.patch("/{detalle_id}", response_model=DetalleVentaResponse)
async def patch_detalle(
    detalle_id: int,
    data: DetalleVentaPatch,
    db: AsyncSession = Depends(get_db),
):
    return await DetalleVentaService.update(db, detalle_id, data)


@router.delete("/{detalle_id}", response_model=MessageResponse)
async def delete_detalle(
    detalle_id: int,
    db: AsyncSession = Depends(get_db),
):
    await DetalleVentaService.delete(db, detalle_id)
    return MessageResponse(message="Detalle de venta eliminado exitosamente")
