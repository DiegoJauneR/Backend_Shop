"""
Servicio de Venta
"""
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import func, or_, select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import selectinload
from typing import List, Optional
from datetime import date, datetime, time, timedelta
from decimal import Decimal

from app.core.exceptions import BadRequestException, ConflictException, NotFoundException
from app.models.boleta import Boleta
from app.models.boleta_detalle import BoletaDetalle
from app.models.detalle_venta import DetalleVenta
from app.models.producto import Producto
from app.models.ticket_balanza import TicketBalanza
from app.models.venta import Venta
from app.schemas.venta import (
    ResumenDiario,
    ResumenDiarioPorTrabajador,
    VentaCreate,
    VentaItemCreate,
    VentaUpdate,
)


class VentaService:
    MONEY_PRECISION = Decimal("0.01")
    SCALE_TICKET_PREFIX = "29"
    SCALE_ORIGIN = "BALANZA"

    @staticmethod
    def _money(value: Decimal) -> Decimal:
        return value.quantize(VentaService.MONEY_PRECISION)

    @staticmethod
    def _ean13_check_digit(payload: str) -> int:
        total = 0
        for index, digit in enumerate(payload):
            multiplier = 1 if index % 2 == 0 else 3
            total += int(digit) * multiplier
        return (10 - (total % 10)) % 10

    @staticmethod
    def parse_ticket_balanza(cod_barra: str) -> dict:
        code = (cod_barra or "").strip()

        if not code.startswith(VentaService.SCALE_TICKET_PREFIX):
            raise BadRequestException("El codigo no corresponde a una boleta de balanza")
        if len(code) != 13 or not code.isdigit():
            raise BadRequestException("Codigo de balanza invalido")
        if VentaService._ean13_check_digit(code[:12]) != int(code[-1]):
            raise BadRequestException("Codigo de balanza con digito verificador invalido")

        numero_ticket = code[2:7].lstrip("0") or "0"
        total = VentaService._money(Decimal(code[7:12]))

        if total <= Decimal("0.00"):
            raise BadRequestException("El total de la boleta de balanza debe ser mayor a cero")

        return {
            "codigo_barra": code,
            "numero_ticket": numero_ticket,
            "total": total,
            "origen": VentaService.SCALE_ORIGIN,
            "nombre_producto": f"Productos pesados - Ticket {numero_ticket}",
        }

    @staticmethod
    async def _ensure_ticket_balanza_unused(db: AsyncSession, ticket_data: dict) -> None:
        result = await db.execute(
            select(TicketBalanza).where(
                or_(
                    TicketBalanza.numero_ticket == ticket_data["numero_ticket"],
                    TicketBalanza.codigo_barra == ticket_data["codigo_barra"],
                )
            )
        )
        if result.scalar_one_or_none():
            raise ConflictException("El ticket de balanza ya fue utilizado")

    @staticmethod
    async def validate_ticket_balanza(db: AsyncSession, cod_barra: str) -> dict:
        ticket_data = VentaService.parse_ticket_balanza(cod_barra)
        await VentaService._ensure_ticket_balanza_unused(db, ticket_data)
        return ticket_data

    @staticmethod
    def _load_options():
        return (
            selectinload(Venta.detalles),
            selectinload(Venta.usuario),
            selectinload(Venta.boleta).selectinload(Boleta.detalles),
        )

    @staticmethod
    def _validate_payment_method(payment_method: Optional[str]) -> None:
        if payment_method and payment_method not in {
            "efectivo",
            "debito",
            "credito",
            "transferencia",
        }:
            raise BadRequestException("paymentMethod inválido")

    @staticmethod
    def _period_range(period: Optional[str]) -> Optional[tuple[date, date]]:
        if not period:
            return None

        value = period.strip().lower()
        today = date.today()

        if value == "today":
            return today, today + timedelta(days=1)
        if value == "week":
            start = today - timedelta(days=today.weekday())
            return start, start + timedelta(days=7)
        if value == "month":
            start = date(today.year, today.month, 1)
            end = date(today.year + 1, 1, 1) if today.month == 12 else date(today.year, today.month + 1, 1)
            return start, end
        if value == "year":
            start = date(today.year, 1, 1)
            return start, date(today.year + 1, 1, 1)

        try:
            day = date.fromisoformat(value)
            return day, day + timedelta(days=1)
        except ValueError as exc:
            raise BadRequestException("period inválido. Usa today, week, month, year o YYYY-MM-DD") from exc

    @staticmethod
    def _apply_filters(
        stmt,
        period: Optional[str] = None,
        employee: Optional[int] = None,
        payment_method: Optional[str] = None,
    ):
        VentaService._validate_payment_method(payment_method)

        date_range = VentaService._period_range(period)
        if date_range:
            start, end = date_range
            stmt = stmt.where(
                Venta.fecha >= datetime.combine(start, time.min),
                Venta.fecha < datetime.combine(end, time.min),
            )

        if employee is not None:
            stmt = stmt.where(Venta.id_usuario == employee)

        if payment_method:
            stmt = stmt.where(Venta.tipo_pago == payment_method)

        return stmt

    @staticmethod
    async def get_all(
        db: AsyncSession,
        skip: int = 0,
        limit: int = 100,
        period: Optional[str] = None,
        employee: Optional[int] = None,
        payment_method: Optional[str] = None,
    ) -> List[Venta]:
        stmt = select(Venta).options(*VentaService._load_options())
        stmt = VentaService._apply_filters(stmt, period, employee, payment_method)
        result = await db.execute(
            stmt.order_by(Venta.fecha.desc()).offset(skip).limit(limit)
        )
        return result.scalars().all()

    @staticmethod
    async def get_by_id(db: AsyncSession, venta_id: int) -> Venta:
        result = await db.execute(
            select(Venta)
            .options(*VentaService._load_options())
            .where(Venta.id == venta_id)
        )
        obj = result.scalar_one_or_none()
        if not obj:
            raise NotFoundException("Venta no encontrada")
        return obj

    @staticmethod
    async def _get_producto_for_item(db: AsyncSession, item: VentaItemCreate) -> Producto:
        stmt = select(Producto).with_for_update()

        if item.id_producto:
            stmt = stmt.where(Producto.id == item.id_producto)
        else:
            stmt = stmt.where(Producto.cod_barra == item.cod_barra)

        result = await db.execute(stmt)
        producto = result.scalar_one_or_none()
        if not producto:
            raise NotFoundException("Producto no encontrado")
        return producto

    @staticmethod
    async def create(
        db: AsyncSession,
        data: VentaCreate,
        current_user_id: Optional[int] = None,
    ) -> Venta:
        if data.estado == "anulada":
            raise BadRequestException("Para anular una venta usa el endpoint de anulación")

        subtotal = Decimal("0.00")
        detalles_data = []
        tickets_balanza_data = []
        tickets_balanza_en_venta = set()

        for item in data.items:
            cod_barra = (item.cod_barra or "").strip()

            if item.origen == VentaService.SCALE_ORIGIN or cod_barra.startswith(VentaService.SCALE_TICKET_PREFIX):
                ticket_data = await VentaService.validate_ticket_balanza(db, cod_barra)

                if ticket_data["numero_ticket"] in tickets_balanza_en_venta:
                    raise BadRequestException("El ticket de balanza ya esta en esta venta")

                if item.ticket_balanza and item.ticket_balanza.lstrip("0") != ticket_data["numero_ticket"]:
                    raise BadRequestException("El numero de ticket no coincide con el codigo de balanza")

                if item.total_balanza is not None and VentaService._money(item.total_balanza) != ticket_data["total"]:
                    raise BadRequestException("El total informado no coincide con el codigo de balanza")

                tickets_balanza_en_venta.add(ticket_data["numero_ticket"])
                tickets_balanza_data.append(ticket_data)

                subtotal += ticket_data["total"]
                detalles_data.append(
                    {
                        "id_producto": None,
                        "codigo_producto": ticket_data["codigo_barra"],
                        "nombre_producto": ticket_data["nombre_producto"],
                        "cantidad": Decimal("1"),
                        "precio_unitario": ticket_data["total"],
                        "subtotal_linea": ticket_data["total"],
                    }
                )
                continue

            producto = await VentaService._get_producto_for_item(db, item)
            cantidad = Decimal(item.cantidad)

            precio_unitario = VentaService._money(Decimal(producto.precio))
            subtotal_linea = VentaService._money(precio_unitario * cantidad)
            subtotal += subtotal_linea

            detalles_data.append(
                {
                    "id_producto": producto.id,
                    "codigo_producto": producto.cod_barra,
                    "nombre_producto": producto.nombre,
                    "cantidad": cantidad,
                    "precio_unitario": precio_unitario,
                    "subtotal_linea": subtotal_linea,
                }
            )

        subtotal = VentaService._money(subtotal)
        descuento = VentaService._money(data.descuento)
        recargo = VentaService._money(data.recargo)
        total = VentaService._money(subtotal - descuento + recargo)

        if total < Decimal("0.00"):
            raise BadRequestException("El total no puede ser negativo")

        vuelto = Decimal("0.00")
        if data.tipo_pago == "efectivo" and data.efectivo_recibido is not None:
            efectivo_recibido = VentaService._money(data.efectivo_recibido)
            if efectivo_recibido < total:
                raise BadRequestException("Efectivo recibido insuficiente")
            vuelto = VentaService._money(efectivo_recibido - total)
        else:
            efectivo_recibido = data.efectivo_recibido

        venta_data = {
            "id_usuario": current_user_id if current_user_id is not None else data.id_usuario,
            "id_cierre_caja": data.id_cierre_caja,
            "subtotal": subtotal,
            "descuento": descuento,
            "recargo": recargo,
            "total": total,
            "tipo_pago": data.tipo_pago,
            "efectivo_recibido": efectivo_recibido,
            "vuelto": vuelto,
            "comprobante": data.comprobante,
            "estado": data.estado,
            "fecha": data.fecha or datetime.now(),
        }

        venta = Venta(**venta_data)
        db.add(venta)
        await db.flush()

        for detalle_data in detalles_data:
            db.add(DetalleVenta(id_venta=venta.id, **detalle_data))

        for ticket_data in tickets_balanza_data:
            db.add(
                TicketBalanza(
                    id_venta=venta.id,
                    numero_ticket=ticket_data["numero_ticket"],
                    codigo_barra=ticket_data["codigo_barra"],
                    total=ticket_data["total"],
                    origen=ticket_data["origen"],
                )
            )

        if data.comprobante == "boleta":
            boleta = Boleta(
                id_venta=venta.id,
                subtotal=subtotal,
                total_pagar=total,
                tipo_pago=data.tipo_pago,
            )
            db.add(boleta)
            await db.flush()

            for detalle_data in detalles_data:
                db.add(BoletaDetalle(id_boleta=boleta.id_boleta, **detalle_data))

        try:
            await db.commit()
        except IntegrityError as exc:
            await db.rollback()
            raise ConflictException("El ticket de balanza ya fue utilizado") from exc
        return await VentaService.get_by_id(db, venta.id)

    @staticmethod
    async def update(db: AsyncSession, venta_id: int, data: VentaUpdate) -> Venta:
        obj = await VentaService.get_by_id(db, venta_id)
        for field, value in data.model_dump(exclude_unset=True).items():
            setattr(obj, field, value)
        await db.commit()
        return await VentaService.get_by_id(db, venta_id)

    @staticmethod
    async def delete(db: AsyncSession, venta_id: int) -> None:
        obj = await VentaService.get_by_id(db, venta_id)
        await db.delete(obj)
        await db.commit()

    @staticmethod
    async def anular(db: AsyncSession, venta_id: int) -> Venta:
        venta = await VentaService.get_by_id(db, venta_id)

        if venta.estado == "anulada":
            raise BadRequestException("La venta ya está anulada")

        venta.estado = "anulada"
        await db.commit()
        return await VentaService.get_by_id(db, venta_id)

    @staticmethod
    async def get_ventas_hoy(db: AsyncSession) -> List[Venta]:
        hoy = date.today()
        manana = hoy + timedelta(days=1)
        result = await db.execute(
            select(Venta)
            .options(*VentaService._load_options())
            .where(
                Venta.fecha >= datetime.combine(hoy, time.min),
                Venta.fecha < datetime.combine(manana, time.min),
            )
            .order_by(Venta.fecha.desc())
        )
        return result.scalars().all()

    @staticmethod
    async def get_ventas_por_usuario(db: AsyncSession, usuario_id: int) -> List[Venta]:
        result = await db.execute(
            select(Venta)
            .options(*VentaService._load_options())
            .where(Venta.id_usuario == usuario_id)
            .order_by(Venta.fecha.desc())
        )
        return result.scalars().all()

    @staticmethod
    async def get_resumen_diario(
        db: AsyncSession,
        fecha: Optional[date] = None,
        usuario_id: Optional[int] = None,
    ) -> ResumenDiario:
        target = fecha or date.today()
        end = target + timedelta(days=1)

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
            Venta.fecha >= datetime.combine(target, time.min),
            Venta.fecha < datetime.combine(end, time.min),
            Venta.estado != "anulada",
        )

        if usuario_id is not None:
            stmt = stmt.where(Venta.id_usuario == usuario_id)

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
        end = target + timedelta(days=1)

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
            Venta.fecha >= datetime.combine(target, time.min),
            Venta.fecha < datetime.combine(end, time.min),
            Venta.id_usuario == usuario_id,
            Venta.estado != "anulada",
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
