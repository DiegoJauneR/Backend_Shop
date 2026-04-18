"""
Servicio de Cierre de Caja
"""
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from typing import Optional, List
from datetime import datetime, timezone
from decimal import Decimal
from app.models.cierre_caja import CierreCaja
from app.schemas.cierre_caja import CierreCajaCreate, CierreCajaUpdate, AbrirCajaSchema, CerrarCajaSchema
from app.core.exceptions import NotFoundException, BadRequestException


class CierreCajaService:

    @staticmethod
    async def get_all(db: AsyncSession, skip: int = 0, limit: int = 100) -> List[CierreCaja]:
        result = await db.execute(
            select(CierreCaja).order_by(CierreCaja.fecha_apertura.desc()).offset(skip).limit(limit)
        )
        return result.scalars().all()

    @staticmethod
    async def get_by_id(db: AsyncSession, cierre_id: int) -> CierreCaja:
        result = await db.execute(select(CierreCaja).where(CierreCaja.id == cierre_id))
        obj = result.scalar_one_or_none()
        if not obj:
            raise NotFoundException("Cierre de caja no encontrado")
        return obj

    @staticmethod
    async def create(db: AsyncSession, data: CierreCajaCreate) -> CierreCaja:
        obj = CierreCaja(**data.model_dump(exclude_unset=False))
        db.add(obj)
        await db.commit()
        await db.refresh(obj)
        return obj

    @staticmethod
    async def update(db: AsyncSession, cierre_id: int, data: CierreCajaUpdate) -> CierreCaja:
        obj = await CierreCajaService.get_by_id(db, cierre_id)
        for field, value in data.model_dump(exclude_unset=True).items():
            setattr(obj, field, value)
        await db.commit()
        await db.refresh(obj)
        return obj

    @staticmethod
    async def delete(db: AsyncSession, cierre_id: int) -> None:
        obj = await CierreCajaService.get_by_id(db, cierre_id)
        await db.delete(obj)
        await db.commit()

    @staticmethod
    async def abrir_caja(db: AsyncSession, data: AbrirCajaSchema) -> CierreCaja:
        obj = CierreCaja(
            id_usuario=data.id_usuario,
            monto_inicial_caja=data.monto_inicial_caja,
            monto_esperado_caja=data.monto_inicial_caja,
            total_ventas=Decimal("0.00"),
            cantidad_ventas=0,
            total_efectivo=Decimal("0.00"),
            total_debito=Decimal("0.00"),
            total_credito=Decimal("0.00"),
            total_transferencia=Decimal("0.00"),
            diferencia=Decimal("0.00"),
            estado="abierta",
        )
        db.add(obj)
        await db.commit()
        await db.refresh(obj)
        return obj

    @staticmethod
    async def cerrar_caja(db: AsyncSession, cierre_id: int, data: CerrarCajaSchema) -> CierreCaja:
        obj = await CierreCajaService.get_by_id(db, cierre_id)
        if obj.estado == "cerrada":
            raise BadRequestException("La caja ya está cerrada")

        monto_esperado = obj.monto_esperado_caja or Decimal("0.00")
        diferencia = data.monto_real_caja - monto_esperado

        obj.monto_real_caja = data.monto_real_caja
        obj.diferencia = diferencia
        obj.fecha_cierre = datetime.now(timezone.utc)
        obj.estado = "cerrada"

        await db.commit()
        await db.refresh(obj)
        return obj
