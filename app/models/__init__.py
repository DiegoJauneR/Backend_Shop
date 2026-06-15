"""
Models init - Importar todos los modelos aquí para que sean descubiertos por Alembic
"""
from app.models.user import User
from app.models.producto import Producto
from app.models.cierre_caja import CierreCaja
from app.models.venta import Venta
from app.models.detalle_venta import DetalleVenta
from app.models.boleta import Boleta
from app.models.boleta_detalle import BoletaDetalle

__all__ = ["User", "Producto", "CierreCaja", "Venta", "DetalleVenta", "Boleta", "BoletaDetalle"]
