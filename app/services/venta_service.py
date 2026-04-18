"""
Servicio de Venta
"""
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, cast, Date
from typing import Optional, List
from datetime import date, datetime, timezone
from decimal import Decimal
from app.models.venta import Venta
from app.schemas.venta import VentaCreate, VentaUpdate, ResumenDiario, ResumenDiarioPorTrabajador
from app.core.exceptions import NotFoundException


class VentaService:

    @staticmethod
    async def get_all(db: AsyncSession, skip: int = 0, limit: int = 100) -> List[Venta]:
        result = await db.execute(
            select(Venta).order_by(Venta.fecha.desc()).offset(skip).limit(limit)
        )
        return result.scalars().all()

    @staticmethod
    async def get_by_id(db: AsyncSession, venta_id: int) -> Venta:
        result = await db.execute(select(Venta).where(Venta.id == venta_id))
        obj = result.scalar_one_or_none()
        if not obj:
            raise NotFoundException("Venta no encontrada")
        return obj

    @staticmethod
    async def create(db: AsyncSession, data: VentaCreate) -> Venta:
        obj = Venta(**data.model_dump(exclude_unset=False))
        db.add(obj)
        await db.commit()
        await db.refresh(obj)
        return obj

    @staticmethod
    async def update(db: AsyncSession, venta_id: int, data: VentaUpdate) -> Venta:
        obj = await VentaService.get_by_id(db, venta_id)
        for field, value in data.model_dump(exclude_unset=True).items():
            setattr(obj, field, value)
        await db.commit()
        await db.refresh(obj)
        return obj

    @staticmethod
    async def delete(db: AsyncSession, venta_id: int) -> None:
        obj = await VentaService.get_by_id(db, venta_id)
        await db.delete(obj)
        await db.commit()

    @staticmethod
    async def get_ventas_hoy(db: AsyncSession) -> List[Venta]:
        hoy = date.today()
        result = await db.execute(
            select(Venta)
            .where(cast(Venta.fecha, Date) == hoy)
            .order_by(Venta.fecha.desc())
        )
        return result.scalars().all()

    @staticmethod
    async def get_ventas_por_usuario(db: AsyncSession, usuario_id: int) -> List[Venta]:
        result = await db.execute(
            select(Venta)
            .where(Venta.id_usuario == usuario_id)
            .order_by(Venta.fecha.desc())
        )
        return result.scalars().all()

    @staticmethod
    async def get_resumen_diario(db: AsyncSession, fecha: Optional[date] = None) -> ResumenDiario:
        target = fecha or date.today()

        stmt = select(
            func.count(Venta.id).label("cantidad_ventas"),
            func.coalesce(func.sum(Venta.total), Decimal("0")).label("monto_total"),
            func.coalesce(
                func.sum(Venta.total).filter(Venta.tipo_pago == "efectivo"), Decimal("0")
            ).label("total_efectivo"),
            func.coalesce(
                func.sum(Venta.total).filter(Venta.tipo_pago == "debito"), Decimal("0")
            ).label("total_debito"),
            func.coalesce(
                func.sum(Venta.total).filter(Venta.tipo_pago == "credito"), Decimal("0")
            ).label("total_credito"),
            func.coalesce(
                func.sum(Venta.total).filter(Venta.tipo_pago == "transferencia"), Decimal("0")
            ).label("total_transferencia"),
        ).where(cast(Venta.fecha, Date) == target)

        result = await db.execute(stmt)
        row = result.one()

        return ResumenDiario(
            fecha=target,
            cantidad_ventas=row.cantidad_ventas or 0,
            monto_total=row.monto_total or Decimal("0"),
            total_efectivo=row.total_efectivo or Decimal("0"),
            total_debito=row.total_debito or Decimal("0"),
            total_credito=row.total_credito or Decimal("0"),
            total_transferencia=row.total_transferencia or Decimal("0"),
        )

    @staticmethod
    async def get_resumen_diario_por_trabajador(
        db: AsyncSession, usuario_id: int, fecha: Optional[date] = None
    ) -> ResumenDiarioPorTrabajador:
        target = fecha or date.today()

        stmt = select(
            func.count(Venta.id).label("cantidad_ventas"),
            func.coalesce(func.sum(Venta.total), Decimal("0")).label("monto_total"),
            func.coalesce(
                func.sum(Venta.total).filter(Venta.tipo_pago == "efectivo"), Decimal("0")
            ).label("total_efectivo"),
            func.coalesce(
                func.sum(Venta.total).filter(Venta.tipo_pago == "debito"), Decimal("0")
            ).label("total_debito"),
            func.coalesce(
                func.sum(Venta.total).filter(Venta.tipo_pago == "credito"), Decimal("0")
            ).label("total_credito"),
            func.coalesce(
                func.sum(Venta.total).filter(Venta.tipo_pago == "transferencia"), Decimal("0")
            ).label("total_transferencia"),
        ).where(
            cast(Venta.fecha, Date) == target,
            Venta.id_usuario == usuario_id,
        )

        result = await db.execute(stmt)
        row = result.one()

        return ResumenDiarioPorTrabajador(
            fecha=target,
            id_usuario=usuario_id,
            cantidad_ventas=row.cantidad_ventas or 0,
            monto_total=row.monto_total or Decimal("0"),
            total_efectivo=row.total_efectivo or Decimal("0"),
            total_debito=row.total_debito or Decimal("0"),
            total_credito=row.total_credito or Decimal("0"),
            total_transferencia=row.total_transferencia or Decimal("0"),
        )
