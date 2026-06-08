"""
Schemas de Venta
"""
from pydantic import AliasChoices, BaseModel, ConfigDict, Field, model_validator
from typing import List, Literal, Optional
from decimal import Decimal
from datetime import datetime, date

from app.schemas.detalle_venta import DetalleVentaResponse


TipoPago = Literal["efectivo", "debito", "credito", "transferencia"]
TipoComprobante = Literal["boleta", "factura", "cotizacion"]
EstadoVenta = Literal["pagado", "anulada", "pendiente"]


class VentaItemCreate(BaseModel):
    id_producto: Optional[int] = Field(
        None,
        gt=0,
        validation_alias=AliasChoices("id_producto", "producto_id", "productId"),
    )
    codigo: Optional[str] = Field(None, max_length=50)
    cod_barra: Optional[str] = Field(
        None,
        max_length=100,
        validation_alias=AliasChoices("cod_barra", "barcode", "barCode"),
    )
    cantidad: Decimal = Field(..., gt=0)

    model_config = ConfigDict(populate_by_name=True, extra="ignore")

    @model_validator(mode="after")
    def validate_producto_identifier(self):
        if not self.id_producto and not self.codigo and not self.cod_barra:
            raise ValueError("Debes indicar id_producto, codigo o cod_barra")
        return self


class VentaCreate(BaseModel):
    id_usuario: Optional[int] = Field(
        None,
        validation_alias=AliasChoices("id_usuario", "employee", "employeeId"),
    )
    id_cierre_caja: Optional[int] = None
    items: List[VentaItemCreate] = Field(
        ...,
        min_length=1,
        validation_alias=AliasChoices("items", "detalles", "productos"),
    )
    descuento: Decimal = Field(default=Decimal("0.00"), ge=0)
    recargo: Decimal = Field(default=Decimal("0.00"), ge=0)
    tipo_pago: TipoPago = Field(
        ...,
        validation_alias=AliasChoices("tipo_pago", "paymentMethod", "payment_method"),
    )
    efectivo_recibido: Optional[Decimal] = Field(None, ge=0)
    comprobante: TipoComprobante = "boleta"
    estado: EstadoVenta = "pagado"
    fecha: Optional[datetime] = None

    model_config = ConfigDict(populate_by_name=True, extra="ignore")


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


class VentaResponse(BaseModel):
    id: int
    fecha: Optional[datetime]
    id_usuario: Optional[int] = None
    id_cierre_caja: Optional[int] = None
    subtotal: Decimal
    descuento: Decimal
    recargo: Decimal
    total: Decimal
    tipo_pago: TipoPago
    efectivo_recibido: Optional[Decimal] = None
    vuelto: Decimal
    comprobante: TipoComprobante
    estado: EstadoVenta
    detalles: List[DetalleVentaResponse] = Field(default_factory=list)

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
