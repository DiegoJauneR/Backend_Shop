"""
Schemas de Cliente
"""
from pydantic import BaseModel, EmailStr
from typing import Optional


class ClienteBase(BaseModel):
    rut: Optional[str] = None
    nombre: Optional[str] = None
    direccion: Optional[str] = None
    ciudad: Optional[str] = None
    telefono: Optional[str] = None
    correo: Optional[str] = None
    giro: Optional[str] = None


class ClienteCreate(ClienteBase):
    pass


class ClienteUpdate(ClienteBase):
    pass


class ClienteResponse(ClienteBase):
    id: int

    class Config:
        from_attributes = True
