"""
Endpoints CRUD de Venta + endpoints especiales
"""
from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List, Optional
from datetime import date
from app.config.database import get_db
from app.schemas.venta import (
    VentaCreate,
    VentaUpdate,
    VentaPatch,
    VentaResponse,
    ResumenDiario,
    ResumenDiarioPorTrabajador,
)
from app.schemas.common import MessageResponse
from app.services.venta_service import VentaService

router = APIRouter(prefix="/ventas", tags=["Ventas"])


@router.get("", response_model=List[VentaResponse])
async def list_ventas(
    skip: int = 0,
    limit: int = 100,
    db: AsyncSession = Depends(get_db),
):
    return await VentaService.get_all(db, skip=skip, limit=limit)


@router.get("/hoy", response_model=List[VentaResponse])
async def ventas_hoy(
    db: AsyncSession = Depends(get_db),
):
    """Listar todas las ventas del día actual."""
    return await VentaService.get_ventas_hoy(db)


@router.get("/resumen/diario", response_model=ResumenDiario)
async def resumen_diario(
    fecha: Optional[date] = Query(None, description="Fecha (YYYY-MM-DD). Por defecto hoy."),
    db: AsyncSession = Depends(get_db),
):
    """Resumen de ventas total del día."""
    return await VentaService.get_resumen_diario(db, fecha)


@router.get("/resumen/diario/trabajador/{usuario_id}", response_model=ResumenDiarioPorTrabajador)
async def resumen_diario_trabajador(
    usuario_id: int,
    fecha: Optional[date] = Query(None, description="Fecha (YYYY-MM-DD). Por defecto hoy."),
    db: AsyncSession = Depends(get_db),
):
    """Resumen de ventas del día filtrado por trabajador."""
    return await VentaService.get_resumen_diario_por_trabajador(db, usuario_id, fecha)


@router.get("/usuario/{usuario_id}", response_model=List[VentaResponse])
async def ventas_por_usuario(
    usuario_id: int,
    db: AsyncSession = Depends(get_db),
):
    """Listar todas las ventas de un usuario específico."""
    return await VentaService.get_ventas_por_usuario(db, usuario_id)


@router.get("/{venta_id}", response_model=VentaResponse)
async def get_venta(
    venta_id: int,
    db: AsyncSession = Depends(get_db),
):
    return await VentaService.get_by_id(db, venta_id)


@router.post("", response_model=VentaResponse, status_code=status.HTTP_201_CREATED)
async def create_venta(
    data: VentaCreate,
    db: AsyncSession = Depends(get_db),
):
    return await VentaService.create(db, data)


@router.put("/{venta_id}", response_model=VentaResponse)
async def update_venta(
    venta_id: int,
    data: VentaUpdate,
    db: AsyncSession = Depends(get_db),
):
    return await VentaService.update(db, venta_id, data)


@router.patch("/{venta_id}", response_model=VentaResponse)
async def patch_venta(
    venta_id: int,
    data: VentaPatch,
    db: AsyncSession = Depends(get_db),
):
    return await VentaService.update(db, venta_id, data)


@router.delete("/{venta_id}", response_model=MessageResponse)
async def delete_venta(
    venta_id: int,
    db: AsyncSession = Depends(get_db),
):
    await VentaService.delete(db, venta_id)
    return MessageResponse(message="Venta eliminada exitosamente")
