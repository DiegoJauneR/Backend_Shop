"""
Utilidades de respuesta
"""
from typing import Any, Optional
from fastapi.responses import JSONResponse
from fastapi import status


def success_response(
    data: Any = None,
    message: str = "Operación exitosa",
    status_code: int = status.HTTP_200_OK
) -> JSONResponse:
    """Crear respuesta exitosa"""
    return JSONResponse(
        status_code=status_code,
        content={
            "success": True,
            "message": message,
            "data": data
        }
    )


def error_response(
    message: str,
    detail: Optional[Any] = None,
    status_code: int = status.HTTP_400_BAD_REQUEST
) -> JSONResponse:
    """Crear respuesta de error"""
    content = {
        "success": False,
        "error": message
    }
    
    if detail is not None:
        content["detail"] = detail
    
    return JSONResponse(
        status_code=status_code,
        content=content
    )
