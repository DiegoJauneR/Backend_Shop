"""
Endpoints CRUD de Cierre de Caja + abrir/cerrar caja
"""
from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List
from app.config.database import get_db
from app.schemas.cierre_caja import (
    CierreCajaCreate,
    CierreCajaUpdate,
    CierreCajaPatch,
    CierreCajaResponse,
    AbrirCajaSchema,
    CerrarCajaSchema,
)
from app.schemas.common import MessageResponse
from app.services.cierre_caja_service import CierreCajaService

router = APIRouter(prefix="/cierre-caja", tags=["Cierre de Caja"])


@router.get("", response_model=List[CierreCajaResponse])
async def list_cierres(
    skip: int = 0,
    limit: int = 100,
    db: AsyncSession = Depends(get_db),
):
    return await CierreCajaService.get_all(db, skip=skip, limit=limit)


@router.get("/{cierre_id}", response_model=CierreCajaResponse)
async def get_cierre(
    cierre_id: int,
    db: AsyncSession = Depends(get_db),
):
    return await CierreCajaService.get_by_id(db, cierre_id)


@router.post("", response_model=CierreCajaResponse, status_code=status.HTTP_201_CREATED)
async def create_cierre(
    data: CierreCajaCreate,
    db: AsyncSession = Depends(get_db),
):
    return await CierreCajaService.create(db, data)


@router.put("/{cierre_id}", response_model=CierreCajaResponse)
async def update_cierre(
    cierre_id: int,
    data: CierreCajaUpdate,
    db: AsyncSession = Depends(get_db),
):
    return await CierreCajaService.update(db, cierre_id, data)


@router.patch("/{cierre_id}", response_model=CierreCajaResponse)
async def patch_cierre(
    cierre_id: int,
    data: CierreCajaPatch,
    db: AsyncSession = Depends(get_db),
):
    return await CierreCajaService.update(db, cierre_id, data)


@router.delete("/{cierre_id}", response_model=MessageResponse)
async def delete_cierre(
    cierre_id: int,
    db: AsyncSession = Depends(get_db),
):
    await CierreCajaService.delete(db, cierre_id)
    return MessageResponse(message="Cierre de caja eliminado exitosamente")


# ── Operaciones especiales ──────────────────────────────────────────────────

@router.post("/abrir", response_model=CierreCajaResponse, status_code=status.HTTP_201_CREATED)
async def abrir_caja(
    data: AbrirCajaSchema,
    db: AsyncSession = Depends(get_db),
):
    """Abrir una nueva caja con monto inicial."""
    return await CierreCajaService.abrir_caja(db, data)


@router.patch("/{cierre_id}/cerrar", response_model=CierreCajaResponse)
async def cerrar_caja(
    cierre_id: int,
    data: CerrarCajaSchema,
    db: AsyncSession = Depends(get_db),
):
    """Cerrar una caja abierta registrando el monto real y calculando diferencia."""
    return await CierreCajaService.cerrar_caja(db, cierre_id, data)
