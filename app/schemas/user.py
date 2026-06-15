"""
Schemas de Usuario
"""
from pydantic import BaseModel, EmailStr, Field, ConfigDict
from typing import Literal, Optional
from datetime import datetime


UserRole = Literal["admin", "vendedor"]


class UserBase(BaseModel):
    """Schema base de usuario"""
    email: EmailStr
    username: str = Field(..., min_length=3, max_length=100)
    full_name: Optional[str] = Field(None, max_length=255)


class UserCreate(UserBase):
    """Schema para crear usuario"""
    password: str = Field(..., min_length=8, max_length=100)


class UserAdminCreate(UserCreate):
    """Schema para crear trabajadores desde administración"""
    role: UserRole = "vendedor"
    is_active: bool = True


class UserUpdate(BaseModel):
    """Schema para actualizar usuario"""
    email: Optional[EmailStr] = None
    username: Optional[str] = Field(None, min_length=3, max_length=100)
    full_name: Optional[str] = Field(None, max_length=255)
    password: Optional[str] = Field(None, min_length=8, max_length=100)
    role: Optional[UserRole] = None
    is_active: Optional[bool] = None


class UserSelfUpdate(BaseModel):
    """Schema para actualizar el perfil propio"""
    email: Optional[EmailStr] = None
    username: Optional[str] = Field(None, min_length=3, max_length=100)
    full_name: Optional[str] = Field(None, max_length=255)
    password: Optional[str] = Field(None, min_length=8, max_length=100)


class UserResponse(UserBase):
    """Schema de respuesta de usuario"""
    id: int
    is_active: bool
    is_superuser: bool
    role: UserRole = "vendedor"
    created_at: datetime
    updated_at: Optional[datetime] = None
    
    model_config = ConfigDict(from_attributes=True)


class UserLogin(BaseModel):
    """Schema para login"""
    username: str
    password: str


class Token(BaseModel):
    """Schema de token"""
    access_token: str
    refresh_token: str
    token_type: str = "bearer"


class TokenRefresh(BaseModel):
    """Schema para refrescar token"""
    refresh_token: str


class TokenResponse(BaseModel):
    """Schema de respuesta de token"""
    access_token: str
    token_type: str = "bearer"
