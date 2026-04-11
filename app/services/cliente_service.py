"""
Servicio CRUD para Cliente
"""
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import List, Optional
from app.models.cliente import Cliente
from app.schemas.cliente import ClienteCreate, ClienteUpdate
from app.core.exceptions import NotFoundException


class ClienteService:

    @staticmethod
    async def get_all(db: AsyncSession, skip: int = 0, limit: int = 100) -> List[Cliente]:
        result = await db.execute(select(Cliente).offset(skip).limit(limit))
        return result.scalars().all()

    @staticmethod
    async def get_by_id(db: AsyncSession, cliente_id: int) -> Cliente:
        result = await db.execute(select(Cliente).where(Cliente.id == cliente_id))
        cliente = result.scalar_one_or_none()
        if not cliente:
            raise NotFoundException(f"Cliente con id {cliente_id} no encontrado")
        return cliente

    @staticmethod
    async def create(db: AsyncSession, data: ClienteCreate) -> Cliente:
        cliente = Cliente(**data.model_dump())
        db.add(cliente)
        await db.flush()
        await db.refresh(cliente)
        return cliente

    @staticmethod
    async def update(db: AsyncSession, cliente_id: int, data: ClienteUpdate) -> Cliente:
        cliente = await ClienteService.get_by_id(db, cliente_id)
        for field, value in data.model_dump(exclude_unset=True).items():
            setattr(cliente, field, value)
        await db.flush()
        await db.refresh(cliente)
        return cliente

    @staticmethod
    async def delete(db: AsyncSession, cliente_id: int) -> None:
        cliente = await ClienteService.get_by_id(db, cliente_id)
        await db.delete(cliente)
        await db.flush()
