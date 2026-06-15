"""
Servicio de Boleta
"""
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.orm import selectinload
from typing import List
from app.models.boleta import Boleta
from app.schemas.boleta import BoletaCreate, BoletaUpdate
from app.core.exceptions import NotFoundException, ConflictException


class BoletaService:

    @staticmethod
    async def get_all(db: AsyncSession, skip: int = 0, limit: int = 100) -> List[Boleta]:
        result = await db.execute(
            select(Boleta).options(selectinload(Boleta.detalles)).offset(skip).limit(limit)
        )
        return result.scalars().all()

    @staticmethod
    async def get_by_id(db: AsyncSession, boleta_id: int) -> Boleta:
        result = await db.execute(
            select(Boleta)
            .options(selectinload(Boleta.detalles))
            .where(Boleta.id_boleta == boleta_id)
        )
        obj = result.scalar_one_or_none()
        if not obj:
            raise NotFoundException("Boleta no encontrada")
        return obj

    @staticmethod
    async def get_by_venta(db: AsyncSession, venta_id: int) -> Boleta:
        result = await db.execute(
            select(Boleta)
            .options(selectinload(Boleta.detalles))
            .where(Boleta.id_venta == venta_id)
        )
        obj = result.scalar_one_or_none()
        if not obj:
            raise NotFoundException("Boleta para la venta indicada no encontrada")
        return obj

    @staticmethod
    async def create(db: AsyncSession, data: BoletaCreate) -> Boleta:
        existing = await db.execute(select(Boleta).where(Boleta.id_venta == data.id_venta))
        if existing.scalar_one_or_none():
            raise ConflictException("Ya existe una boleta para esta venta")

        obj = Boleta(**data.model_dump(exclude_unset=False))
        db.add(obj)
        await db.commit()
        await db.refresh(obj)
        return obj

    @staticmethod
    async def update(db: AsyncSession, boleta_id: int, data: BoletaUpdate) -> Boleta:
        obj = await BoletaService.get_by_id(db, boleta_id)
        update_data = data.model_dump(exclude_unset=True)

        if "id_venta" in update_data and update_data["id_venta"] != obj.id_venta:
            existing = await db.execute(
                select(Boleta).where(
                    Boleta.id_venta == update_data["id_venta"],
                    Boleta.id_boleta != boleta_id,
                )
            )
            if existing.scalar_one_or_none():
                raise ConflictException("Ya existe una boleta para esa venta")

        for field, value in update_data.items():
            setattr(obj, field, value)
        await db.commit()
        await db.refresh(obj)
        return obj

    @staticmethod
    async def delete(db: AsyncSession, boleta_id: int) -> None:
        obj = await BoletaService.get_by_id(db, boleta_id)
        await db.delete(obj)
        await db.commit()
