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
from app.services.user_service import UserService
from app.core.security import get_current_user_id
from app.core.exceptions import ForbiddenException, NotFoundException

router = APIRouter(prefix="/ventas", tags=["Ventas"])


def _is_admin(user) -> bool:
    return bool(user and (user.role == "admin" or user.is_superuser))


async def get_current_sales_user(
    user_id: int = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db),
):
    user = await UserService.get_by_id(db, user_id)
    if not user:
        raise NotFoundException("Usuario no encontrado")
    return user


def _scoped_employee_filter(current_user, employee: Optional[int] = None) -> Optional[int]:
    if _is_admin(current_user):
        return employee
    return current_user.id


def _ensure_sale_access(current_user, venta: VentaResponse) -> None:
    if not _is_admin(current_user) and venta.id_usuario != current_user.id:
        raise ForbiddenException("Solo puedes ver tus propias ventas")


@router.get("", response_model=List[VentaResponse])
async def list_ventas(
    skip: int = 0,
    limit: int = 100,
    period: Optional[str] = Query(None, description="today, week, month, year o YYYY-MM-DD"),
    employee: Optional[int] = Query(None, description="ID del trabajador"),
    payment_method: Optional[str] = Query(None, alias="paymentMethod"),
    current_user=Depends(get_current_sales_user),
    db: AsyncSession = Depends(get_db),
):
    return await VentaService.get_all(
        db,
        skip=skip,
        limit=limit,
        period=period,
        employee=_scoped_employee_filter(current_user, employee),
        payment_method=payment_method,
    )


@router.get("/hoy", response_model=List[VentaResponse])
async def ventas_hoy(
    current_user=Depends(get_current_sales_user),
    db: AsyncSession = Depends(get_db),
):
    """Listar todas las ventas del día actual."""
    return await VentaService.get_all(
        db,
        period="today",
        employee=_scoped_employee_filter(current_user),
    )


@router.get("/resumen/diario", response_model=ResumenDiario)
async def resumen_diario(
    fecha: Optional[date] = Query(None, description="Fecha (YYYY-MM-DD). Por defecto hoy."),
    current_user=Depends(get_current_sales_user),
    db: AsyncSession = Depends(get_db),
):
    """Resumen de ventas total del día."""
    return await VentaService.get_resumen_diario(
        db,
        fecha,
        usuario_id=None if _is_admin(current_user) else current_user.id,
    )


@router.get("/resumen/diario/trabajador/{usuario_id}", response_model=ResumenDiarioPorTrabajador)
async def resumen_diario_trabajador(
    usuario_id: int,
    fecha: Optional[date] = Query(None, description="Fecha (YYYY-MM-DD). Por defecto hoy."),
    current_user=Depends(get_current_sales_user),
    db: AsyncSession = Depends(get_db),
):
    """Resumen de ventas del día filtrado por trabajador."""
    if not _is_admin(current_user) and usuario_id != current_user.id:
        raise ForbiddenException("Solo puedes ver tus propias ventas")
    return await VentaService.get_resumen_diario_por_trabajador(db, usuario_id, fecha)


@router.get("/usuario/{usuario_id}", response_model=List[VentaResponse])
async def ventas_por_usuario(
    usuario_id: int,
    current_user=Depends(get_current_sales_user),
    db: AsyncSession = Depends(get_db),
):
    """Listar todas las ventas de un usuario específico."""
    if not _is_admin(current_user) and usuario_id != current_user.id:
        raise ForbiddenException("Solo puedes ver tus propias ventas")
    return await VentaService.get_ventas_por_usuario(db, usuario_id)


@router.get("/tickets-balanza/{codigo_barra}/validar")
async def validar_ticket_balanza(
    codigo_barra: str,
    current_user=Depends(get_current_sales_user),
    db: AsyncSession = Depends(get_db),
):
    """Validar y decodificar una boleta emitida por la balanza."""
    return await VentaService.validate_ticket_balanza(db, codigo_barra)


@router.get("/{venta_id}", response_model=VentaResponse)
async def get_venta(
    venta_id: int,
    current_user=Depends(get_current_sales_user),
    db: AsyncSession = Depends(get_db),
):
    venta = await VentaService.get_by_id(db, venta_id)
    _ensure_sale_access(current_user, venta)
    return venta


@router.post("", response_model=VentaResponse, status_code=status.HTTP_201_CREATED)
async def create_venta(
    data: VentaCreate,
    user_id: int = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db),
):
    return await VentaService.create(db, data, current_user_id=user_id)


@router.put("/{venta_id}", response_model=VentaResponse)
async def update_venta(
    venta_id: int,
    data: VentaUpdate,
    current_user=Depends(get_current_sales_user),
    db: AsyncSession = Depends(get_db),
):
    if not _is_admin(current_user):
        raise ForbiddenException("Solo un administrador puede modificar ventas")
    return await VentaService.update(db, venta_id, data)


@router.patch("/{venta_id}", response_model=VentaResponse)
async def patch_venta(
    venta_id: int,
    data: VentaPatch,
    current_user=Depends(get_current_sales_user),
    db: AsyncSession = Depends(get_db),
):
    if not _is_admin(current_user):
        raise ForbiddenException("Solo un administrador puede modificar ventas")
    return await VentaService.update(db, venta_id, data)


@router.patch("/{venta_id}/anular", response_model=VentaResponse)
async def anular_venta(
    venta_id: int,
    current_user=Depends(get_current_sales_user),
    db: AsyncSession = Depends(get_db),
):
    if not _is_admin(current_user):
        raise ForbiddenException("Solo un administrador puede anular ventas")
    return await VentaService.anular(db, venta_id)


@router.delete("/{venta_id}", response_model=MessageResponse)
async def delete_venta(
    venta_id: int,
    current_user=Depends(get_current_sales_user),
    db: AsyncSession = Depends(get_db),
):
    if not _is_admin(current_user):
        raise ForbiddenException("Solo un administrador puede eliminar ventas")
    await VentaService.delete(db, venta_id)
    return MessageResponse(message="Venta eliminada exitosamente")
