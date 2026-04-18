"""
Schemas de Boleta
"""
from pydantic import BaseModel, Field, ConfigDict
from typing import Optional, Literal
from decimal import Decimal
from datetime import datetime


TipoPago = Literal["efectivo", "debito", "credito", "transferencia"]


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

    model_config = ConfigDict(from_attributes=True)
