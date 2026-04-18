"""
Schemas de Venta
"""
from pydantic import BaseModel, Field, ConfigDict
from typing import Optional, Literal
from decimal import Decimal
from datetime import datetime, date


TipoPago = Literal["efectivo", "debito", "credito", "transferencia"]
TipoComprobante = Literal["boleta", "factura", "cotizacion"]
EstadoVenta = Literal["pagado", "anulada", "pendiente"]


class VentaBase(BaseModel):
    id_usuario: Optional[int] = None
    id_cierre_caja: Optional[int] = None
    subtotal: Decimal = Field(..., ge=0)
    descuento: Decimal = Field(default=Decimal("0.00"), ge=0)
    recargo: Decimal = Field(default=Decimal("0.00"), ge=0)
    total: Decimal = Field(..., ge=0)
    tipo_pago: TipoPago
    efectivo_recibido: Optional[Decimal] = Field(None, ge=0)
    vuelto: Decimal = Field(default=Decimal("0.00"), ge=0)
    comprobante: TipoComprobante
    estado: EstadoVenta


class VentaCreate(VentaBase):
    fecha: Optional[datetime] = None


class VentaUpdate(BaseModel):
    id_usuario: Optional[int] = None
    id_cierre_caja: Optional[int] = None
    fecha: Optional[datetime] = None
    subtotal: Optional[Decimal] = Field(None, ge=0)
    descuento: Optional[Decimal] = Field(None, ge=0)
    recargo: Optional[Decimal] = Field(None, ge=0)
    total: Optional[Decimal] = Field(None, ge=0)
    tipo_pago: Optional[TipoPago] = None
    efectivo_recibido: Optional[Decimal] = Field(None, ge=0)
    vuelto: Optional[Decimal] = Field(None, ge=0)
    comprobante: Optional[TipoComprobante] = None
    estado: Optional[EstadoVenta] = None


class VentaPatch(VentaUpdate):
    pass


class VentaResponse(VentaBase):
    id: int
    fecha: Optional[datetime]

    model_config = ConfigDict(from_attributes=True)


class ResumenDiario(BaseModel):
    fecha: date
    cantidad_ventas: int
    monto_total: Decimal
    total_efectivo: Decimal
    total_debito: Decimal
    total_credito: Decimal
    total_transferencia: Decimal


class ResumenDiarioPorTrabajador(ResumenDiario):
    id_usuario: Optional[int]
