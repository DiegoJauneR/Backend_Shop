"""
Endpoints CRUD de Boleta
"""
from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List
from app.config.database import get_db
from app.schemas.boleta import BoletaCreate, BoletaUpdate, BoletaPatch, BoletaResponse
from app.schemas.common import MessageResponse
from app.services.boleta_service import BoletaService

router = APIRouter(prefix="/boletas", tags=["Boletas"])


@router.get("", response_model=List[BoletaResponse])
async def list_boletas(
    skip: int = 0,
    limit: int = 100,
    db: AsyncSession = Depends(get_db),
):
    return await BoletaService.get_all(db, skip=skip, limit=limit)


@router.get("/venta/{venta_id}", response_model=BoletaResponse)
async def get_boleta_por_venta(
    venta_id: int,
    db: AsyncSession = Depends(get_db),
):
    """Obtener la boleta asociada a una venta específica."""
    return await BoletaService.get_by_venta(db, venta_id)


@router.get("/{boleta_id}", response_model=BoletaResponse)
async def get_boleta(
    boleta_id: int,
    db: AsyncSession = Depends(get_db),
):
    return await BoletaService.get_by_id(db, boleta_id)


@router.post("", response_model=BoletaResponse, status_code=status.HTTP_201_CREATED)
async def create_boleta(
    data: BoletaCreate,
    db: AsyncSession = Depends(get_db),
):
    return await BoletaService.create(db, data)


@router.put("/{boleta_id}", response_model=BoletaResponse)
async def update_boleta(
    boleta_id: int,
    data: BoletaUpdate,
    db: AsyncSession = Depends(get_db),
):
    return await BoletaService.update(db, boleta_id, data)


@router.patch("/{boleta_id}", response_model=BoletaResponse)
async def patch_boleta(
    boleta_id: int,
    data: BoletaPatch,
    db: AsyncSession = Depends(get_db),
):
    return await BoletaService.update(db, boleta_id, data)


@router.delete("/{boleta_id}", response_model=MessageResponse)
async def delete_boleta(
    boleta_id: int,
    db: AsyncSession = Depends(get_db),
):
    await BoletaService.delete(db, boleta_id)
    return MessageResponse(message="Boleta eliminada exitosamente")
