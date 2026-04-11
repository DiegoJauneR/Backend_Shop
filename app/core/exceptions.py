"""
Excepciones personalizadas
"""
from fastapi import HTTPException, status


class NotFoundException(HTTPException):
    """Excepción para recursos no encontrados"""
    def __init__(self, detail: str = "Recurso no encontrado"):
        super().__init__(status_code=status.HTTP_404_NOT_FOUND, detail=detail)


class BadRequestException(HTTPException):
    """Excepción para solicitudes incorrectas"""
    def __init__(self, detail: str = "Solicitud incorrecta"):
        super().__init__(status_code=status.HTTP_400_BAD_REQUEST, detail=detail)


class UnauthorizedException(HTTPException):
    """Excepción para acceso no autorizado"""
    def __init__(self, detail: str = "No autorizado"):
        super().__init__(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=detail,
            headers={"WWW-Authenticate": "Bearer"}
        )


class ForbiddenException(HTTPException):
    """Excepción para acceso prohibido"""
    def __init__(self, detail: str = "Acceso prohibido"):
        super().__init__(status_code=status.HTTP_403_FORBIDDEN, detail=detail)


class ConflictException(HTTPException):
    """Excepción para conflictos"""
    def __init__(self, detail: str = "Conflicto con el estado actual"):
        super().__init__(status_code=status.HTTP_409_CONFLICT, detail=detail)


class InternalServerException(HTTPException):
    """Excepción para errores internos del servidor"""
    def __init__(self, detail: str = "Error interno del servidor"):
        super().__init__(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=detail)
