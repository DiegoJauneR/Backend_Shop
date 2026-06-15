"""
Servicio de Venta
"""
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import func, select
from sqlalchemy.orm import selectinload
from typing import List, Optional
from datetime import date, datetime, time, timedelta
from decimal import Decimal

from app.core.exceptions import BadRequestException, NotFoundException
from app.models.boleta import Boleta
from app.models.boleta_detalle import BoletaDetalle
from app.models.detalle_venta import DetalleVenta
from app.models.producto import Producto
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

    @staticmethod
    def _money(value: Decimal) -> Decimal:
        return value.quantize(VentaService.MONEY_PRECISION)

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

        for item in data.items:
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

        await db.commit()
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
