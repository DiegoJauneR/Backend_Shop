"""
Schema de respuestas genéricas
"""
from pydantic import BaseModel
from typing import Any, Optional


class MessageResponse(BaseModel):
    """Respuesta con mensaje"""
    message: str
    detail: Optional[str] = None


class ErrorResponse(BaseModel):
    """Respuesta de error"""
    error: str
    detail: Optional[Any] = None
    status_code: int


class SuccessResponse(BaseModel):
    """Respuesta exitosa genérica"""
    success: bool = True
    message: str
    data: Optional[Any] = None
