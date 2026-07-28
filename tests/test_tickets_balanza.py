"""
Tests de tickets de balanza
"""
import asyncio
from decimal import Decimal

import pytest
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from app.config.database import Base
from app.core.exceptions import BadRequestException, ConflictException
from app.models.ticket_balanza import TicketBalanza
from app.schemas.venta import VentaCreate
from app.services.venta_service import VentaService


async def run_with_test_db(operation):
    engine = create_async_engine("sqlite+aiosqlite:///:memory:", echo=False)
    SessionLocal = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    try:
        async with SessionLocal() as session:
            await operation(session)
    finally:
        async with engine.begin() as conn:
            await conn.run_sync(Base.metadata.drop_all)
        await engine.dispose()


def test_parse_ticket_balanza():
    ticket = VentaService.parse_ticket_balanza("2910000304085")

    assert ticket["codigo_barra"] == "2910000304085"
    assert ticket["numero_ticket"] == "10000"
    assert ticket["total"] == Decimal("30408.00")
    assert ticket["origen"] == "BALANZA"
    assert ticket["nombre_producto"] == "Productos pesados - Ticket 10000"


def test_parse_ticket_balanza_rejects_invalid_checksum():
    with pytest.raises(BadRequestException):
        VentaService.parse_ticket_balanza("2910000304084")


def test_create_sale_registers_scale_ticket():
    async def run(db_session: AsyncSession):
        sale = await VentaService.create(
            db_session,
            VentaCreate.model_validate(
                {
                    "tipo_pago": "efectivo",
                    "detalles": [
                        {
                            "origen": "BALANZA",
                            "cod_barra": "2910000304085",
                            "ticket_balanza": "10000",
                            "total_balanza": "30408.00",
                            "cantidad": 1,
                        }
                    ],
                    "comprobante": "boleta",
                    "estado": "pagado",
                }
            ),
        )

        assert sale.total == Decimal("30408.00")
        assert len(sale.detalles) == 1
        assert sale.detalles[0].id_producto is None
        assert sale.detalles[0].codigo_producto == "2910000304085"
        assert sale.detalles[0].nombre_producto == "Productos pesados - Ticket 10000"

        result = await db_session.execute(select(TicketBalanza))
        ticket = result.scalar_one()
        assert ticket.numero_ticket == "10000"
        assert ticket.codigo_barra == "2910000304085"
        assert ticket.id_venta == sale.id

    asyncio.run(run_with_test_db(run))


def test_create_sale_rejects_used_scale_ticket():
    async def run(db_session: AsyncSession):
        data = VentaCreate.model_validate(
            {
                "tipo_pago": "efectivo",
                "detalles": [
                    {
                        "origen": "BALANZA",
                        "cod_barra": "2910000304085",
                        "cantidad": 1,
                    }
                ],
                "comprobante": "boleta",
                "estado": "pagado",
            }
        )

        await VentaService.create(db_session, data)

        with pytest.raises(ConflictException):
            await VentaService.create(db_session, data)

    asyncio.run(run_with_test_db(run))
