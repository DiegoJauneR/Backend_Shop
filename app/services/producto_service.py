"""
Servicio de Producto
"""
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import Optional, List
from app.models.producto import Producto
from app.schemas.producto import ProductoCreate, ProductoUpdate
from app.core.exceptions import NotFoundException, ConflictException


class ProductoService:

    @staticmethod
    async def get_all(db: AsyncSession, skip: int = 0, limit: int = 100) -> List[Producto]:
        result = await db.execute(select(Producto).offset(skip).limit(limit))
        return result.scalars().all()

    @staticmethod
    async def get_by_id(db: AsyncSession, producto_id: int) -> Producto:
        result = await db.execute(select(Producto).where(Producto.id == producto_id))
        obj = result.scalar_one_or_none()
        if not obj:
            raise NotFoundException("Producto no encontrado")
        return obj

    @staticmethod
    async def _check_unique(db: AsyncSession, field: str, value: str, exclude_id: Optional[int] = None):
        col = getattr(Producto, field)
        stmt = select(Producto).where(col == value)
        if exclude_id is not None:
            stmt = stmt.where(Producto.id != exclude_id)
        result = await db.execute(stmt)
        if result.scalar_one_or_none():
            raise ConflictException(f"El {field} '{value}' ya está en uso")

    @staticmethod
    async def create(db: AsyncSession, data: ProductoCreate) -> Producto:
        if data.codigo:
            await ProductoService._check_unique(db, "codigo", data.codigo)
        if data.cod_barra:
            await ProductoService._check_unique(db, "cod_barra", data.cod_barra)

        obj = Producto(**data.model_dump())
        db.add(obj)
        await db.commit()
        await db.refresh(obj)
        return obj

    @staticmethod
    async def update(db: AsyncSession, producto_id: int, data: ProductoUpdate) -> Producto:
        obj = await ProductoService.get_by_id(db, producto_id)
        update_data = data.model_dump(exclude_unset=True)

        if "codigo" in update_data and update_data["codigo"] and update_data["codigo"] != obj.codigo:
            await ProductoService._check_unique(db, "codigo", update_data["codigo"], exclude_id=producto_id)
        if "cod_barra" in update_data and update_data["cod_barra"] and update_data["cod_barra"] != obj.cod_barra:
            await ProductoService._check_unique(db, "cod_barra", update_data["cod_barra"], exclude_id=producto_id)

        for field, value in update_data.items():
            setattr(obj, field, value)

        await db.commit()
        await db.refresh(obj)
        return obj

    @staticmethod
    async def delete(db: AsyncSession, producto_id: int) -> None:
        obj = await ProductoService.get_by_id(db, producto_id)
        await db.delete(obj)
        await db.commit()
