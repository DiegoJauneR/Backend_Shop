"""
Servicio de Detalle de Venta
"""
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import List
from app.models.detalle_venta import DetalleVenta
from app.schemas.detalle_venta import DetalleVentaCreate, DetalleVentaUpdate
from app.core.exceptions import NotFoundException


class DetalleVentaService:

    @staticmethod
    async def get_all(db: AsyncSession, skip: int = 0, limit: int = 100) -> List[DetalleVenta]:
        result = await db.execute(select(DetalleVenta).offset(skip).limit(limit))
        return result.scalars().all()

    @staticmethod
    async def get_by_id(db: AsyncSession, detalle_id: int) -> DetalleVenta:
        result = await db.execute(select(DetalleVenta).where(DetalleVenta.id == detalle_id))
        obj = result.scalar_one_or_none()
        if not obj:
            raise NotFoundException("Detalle de venta no encontrado")
        return obj

    @staticmethod
    async def get_by_venta(db: AsyncSession, venta_id: int) -> List[DetalleVenta]:
        result = await db.execute(
            select(DetalleVenta).where(DetalleVenta.id_venta == venta_id)
        )
        return result.scalars().all()

    @staticmethod
    async def create(db: AsyncSession, data: DetalleVentaCreate) -> DetalleVenta:
        obj = DetalleVenta(**data.model_dump())
        db.add(obj)
        await db.commit()
        await db.refresh(obj)
        return obj

    @staticmethod
    async def update(db: AsyncSession, detalle_id: int, data: DetalleVentaUpdate) -> DetalleVenta:
        obj = await DetalleVentaService.get_by_id(db, detalle_id)
        for field, value in data.model_dump(exclude_unset=True).items():
            setattr(obj, field, value)
        await db.commit()
        await db.refresh(obj)
        return obj

    @staticmethod
    async def delete(db: AsyncSession, detalle_id: int) -> None:
        obj = await DetalleVentaService.get_by_id(db, detalle_id)
        await db.delete(obj)
        await db.commit()
