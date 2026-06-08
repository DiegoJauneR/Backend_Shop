"""
Schemas de Producto
"""
from pydantic import BaseModel, Field, ConfigDict
from typing import Literal, Optional
from decimal import Decimal


TipoVenta = Literal["unidad", "peso"]


class ProductoBase(BaseModel):
    codigo: Optional[str] = Field(None, max_length=50)
    cod_barra: Optional[str] = Field(None, max_length=100)
    categoria: Optional[str] = Field(None, max_length=100)
    nombre: str = Field(..., max_length=150)
    costo: Optional[Decimal] = Field(None, ge=0)
    precio: Decimal = Field(..., ge=0)
    stock: Decimal = Field(default=Decimal("0"), ge=0)
    unidad: str = Field(default="unidad", max_length=30)
    tipo_venta: TipoVenta = "unidad"


class ProductoCreate(ProductoBase):
    pass


class ProductoUpdate(BaseModel):
    codigo: Optional[str] = Field(None, max_length=50)
    cod_barra: Optional[str] = Field(None, max_length=100)
    categoria: Optional[str] = Field(None, max_length=100)
    nombre: Optional[str] = Field(None, max_length=150)
    costo: Optional[Decimal] = Field(None, ge=0)
    precio: Optional[Decimal] = Field(None, ge=0)
    stock: Optional[Decimal] = Field(None, ge=0)
    unidad: Optional[str] = Field(None, max_length=30)
    tipo_venta: Optional[TipoVenta] = None


class ProductoPatch(ProductoUpdate):
    pass


class ProductoResponse(ProductoBase):
    id: int

    model_config = ConfigDict(from_attributes=True)
