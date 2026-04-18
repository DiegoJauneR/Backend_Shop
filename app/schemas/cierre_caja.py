"""
Schemas de Cierre de Caja
"""
from pydantic import BaseModel, Field, ConfigDict
from typing import Optional, Literal
from decimal import Decimal
from datetime import date, datetime


EstadoCaja = Literal["abierta", "cerrada"]


class CierreCajaBase(BaseModel):
    id_usuario: Optional[int] = None
    monto_inicial_caja: Decimal = Field(..., ge=0)


class AbrirCajaSchema(BaseModel):
    id_usuario: Optional[int] = None
    monto_inicial_caja: Decimal = Field(..., ge=0)


class CerrarCajaSchema(BaseModel):
    monto_real_caja: Decimal = Field(..., ge=0)


class CierreCajaCreate(CierreCajaBase):
    fecha: Optional[date] = None
    total_ventas: Optional[Decimal] = Field(default=Decimal("0.00"), ge=0)
    cantidad_ventas: Optional[int] = Field(default=0, ge=0)
    total_efectivo: Optional[Decimal] = Field(default=Decimal("0.00"), ge=0)
    total_debito: Optional[Decimal] = Field(default=Decimal("0.00"), ge=0)
    total_credito: Optional[Decimal] = Field(default=Decimal("0.00"), ge=0)
    total_transferencia: Optional[Decimal] = Field(default=Decimal("0.00"), ge=0)
    monto_esperado_caja: Optional[Decimal] = Field(default=Decimal("0.00"), ge=0)
    monto_real_caja: Optional[Decimal] = Field(None, ge=0)
    diferencia: Optional[Decimal] = Field(default=Decimal("0.00"))
    estado: EstadoCaja = "abierta"


class CierreCajaUpdate(BaseModel):
    id_usuario: Optional[int] = None
    monto_inicial_caja: Optional[Decimal] = Field(None, ge=0)
    total_ventas: Optional[Decimal] = Field(None, ge=0)
    cantidad_ventas: Optional[int] = Field(None, ge=0)
    total_efectivo: Optional[Decimal] = Field(None, ge=0)
    total_debito: Optional[Decimal] = Field(None, ge=0)
    total_credito: Optional[Decimal] = Field(None, ge=0)
    total_transferencia: Optional[Decimal] = Field(None, ge=0)
    monto_esperado_caja: Optional[Decimal] = Field(None, ge=0)
    monto_real_caja: Optional[Decimal] = Field(None, ge=0)
    diferencia: Optional[Decimal] = None
    estado: Optional[EstadoCaja] = None


class CierreCajaPatch(CierreCajaUpdate):
    pass


class CierreCajaResponse(BaseModel):
    id: int
    id_usuario: Optional[int]
    fecha: Optional[date]
    fecha_apertura: Optional[datetime]
    fecha_cierre: Optional[datetime]
    monto_inicial_caja: Decimal
    total_ventas: Optional[Decimal]
    cantidad_ventas: Optional[int]
    total_efectivo: Optional[Decimal]
    total_debito: Optional[Decimal]
    total_credito: Optional[Decimal]
    total_transferencia: Optional[Decimal]
    monto_esperado_caja: Optional[Decimal]
    monto_real_caja: Optional[Decimal]
    diferencia: Optional[Decimal]
    estado: str

    model_config = ConfigDict(from_attributes=True)
