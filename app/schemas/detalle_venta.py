"""
Schemas de Detalle de Venta
"""
from pydantic import BaseModel, Field, ConfigDict
from typing import Optional
from decimal import Decimal


class DetalleVentaBase(BaseModel):
    id_venta: int
    id_producto: Optional[int] = None
    codigo_producto: Optional[str] = Field(None, max_length=50)
    nombre_producto: str = Field(..., max_length=150)
    cantidad: Decimal = Field(..., gt=0)
    precio_unitario: Decimal = Field(..., ge=0)
    subtotal_linea: Decimal = Field(..., ge=0)


class DetalleVentaCreate(DetalleVentaBase):
    pass


class DetalleVentaUpdate(BaseModel):
    id_venta: Optional[int] = None
    id_producto: Optional[int] = None
    codigo_producto: Optional[str] = Field(None, max_length=50)
    nombre_producto: Optional[str] = Field(None, max_length=150)
    cantidad: Optional[Decimal] = Field(None, gt=0)
    precio_unitario: Optional[Decimal] = Field(None, ge=0)
    subtotal_linea: Optional[Decimal] = Field(None, ge=0)


class DetalleVentaPatch(DetalleVentaUpdate):
    pass


class DetalleVentaResponse(DetalleVentaBase):
    id: int

    model_config = ConfigDict(from_attributes=True)
