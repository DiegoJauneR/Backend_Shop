"""
Middleware de manejo de errores
"""
from fastapi import FastAPI, Request, status
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from sqlalchemy.exc import SQLAlchemyError
import traceback
import logging

logger = logging.getLogger(__name__)


def setup_exception_handlers(app: FastAPI) -> None:
    """
    Configurar manejadores de excepciones
    """
    
    @app.exception_handler(RequestValidationError)
    async def validation_exception_handler(request: Request, exc: RequestValidationError):
        """Manejar errores de validación de Pydantic"""
        logger.error(f"Error de validación: {exc.errors()}")

        def make_serializable(obj):
            if isinstance(obj, bytes):
                return obj.decode("utf-8", errors="replace")
            if isinstance(obj, dict):
                return {k: make_serializable(v) for k, v in obj.items()}
            if isinstance(obj, list):
                return [make_serializable(i) for i in obj]
            return obj

        body = exc.body
        if isinstance(body, bytes):
            body = body.decode("utf-8", errors="replace")

        return JSONResponse(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            content={
                "detail": make_serializable(exc.errors()),
                "body": body,
                "message": "Error de validación en los datos enviados"
            }
        )
    
    @app.exception_handler(SQLAlchemyError)
    async def sqlalchemy_exception_handler(request: Request, exc: SQLAlchemyError):
        """Manejar errores de SQLAlchemy"""
        logger.error(f"Error de base de datos: {str(exc)}")
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={
                "detail": "Error en la base de datos",
                "message": "Ocurrió un error al procesar la solicitud"
            }
        )
    
    @app.exception_handler(Exception)
    async def general_exception_handler(request: Request, exc: Exception):
        """Manejar errores generales"""
        logger.error(f"Error no manejado: {str(exc)}\n{traceback.format_exc()}")
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={
                "detail": str(exc) if app.debug else "Error interno del servidor",
                "message": "Ocurrió un error inesperado"
            }
        )
