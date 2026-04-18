"""
Schemas de Producto
"""
from pydantic import BaseModel, Field, ConfigDict
from typing import Optional
from decimal import Decimal


class ProductoBase(BaseModel):
    codigo: Optional[str] = Field(None, max_length=50)
    cod_barra: Optional[str] = Field(None, max_length=100)
    categoria: Optional[str] = Field(None, max_length=100)
    nombre: str = Field(..., max_length=150)
    descripcion: Optional[str] = Field(None, max_length=255)
    costo: Optional[Decimal] = Field(None, ge=0)
    precio: Decimal = Field(..., ge=0)


class ProductoCreate(ProductoBase):
    pass


class ProductoUpdate(BaseModel):
    codigo: Optional[str] = Field(None, max_length=50)
    cod_barra: Optional[str] = Field(None, max_length=100)
    categoria: Optional[str] = Field(None, max_length=100)
    nombre: Optional[str] = Field(None, max_length=150)
    descripcion: Optional[str] = Field(None, max_length=255)
    costo: Optional[Decimal] = Field(None, ge=0)
    precio: Optional[Decimal] = Field(None, ge=0)


class ProductoPatch(ProductoUpdate):
    pass


class ProductoResponse(ProductoBase):
    id: int

    model_config = ConfigDict(from_attributes=True)
