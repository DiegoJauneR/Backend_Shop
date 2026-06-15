"""
Schemas de Boleta
"""
from pydantic import BaseModel, Field, ConfigDict
from typing import List, Optional, Literal
from decimal import Decimal
from datetime import datetime


TipoPago = Literal["efectivo", "debito", "credito", "transferencia"]


class BoletaDetalleResponse(BaseModel):
    id_detalle: int
    id_boleta: int
    id_producto: Optional[int] = None
    codigo_producto: Optional[str] = None
    nombre_producto: str
    cantidad: Decimal
    precio_unitario: Decimal
    subtotal_linea: Decimal

    model_config = ConfigDict(from_attributes=True)


class BoletaBase(BaseModel):
    id_venta: int
    subtotal: Decimal = Field(..., ge=0)
    total_pagar: Decimal = Field(..., ge=0)
    tipo_pago: TipoPago


class BoletaCreate(BoletaBase):
    fecha_emision: Optional[datetime] = None


class BoletaUpdate(BaseModel):
    id_venta: Optional[int] = None
    subtotal: Optional[Decimal] = Field(None, ge=0)
    total_pagar: Optional[Decimal] = Field(None, ge=0)
    tipo_pago: Optional[TipoPago] = None


class BoletaPatch(BoletaUpdate):
    pass


class BoletaResponse(BoletaBase):
    id_boleta: int
    fecha_emision: Optional[datetime]
    detalles: List[BoletaDetalleResponse] = Field(default_factory=list)

    model_config = ConfigDict(from_attributes=True)
