"""
Models init - Importar todos los modelos aquí para que sean descubiertos por Alembic
"""
from app.models.user import User
from app.models.cliente import Cliente

__all__ = ["User", "Cliente"]
