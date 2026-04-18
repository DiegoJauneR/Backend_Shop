"""
Modelo de Detalle de Venta
"""
from sqlalchemy import Column, BigInteger, String, Numeric, ForeignKey
from app.config.database import Base


class DetalleVenta(Base):
    __tablename__ = "detalle_venta"

    id = Column(BigInteger, primary_key=True, index=True, autoincrement=True)
    id_venta = Column(BigInteger, ForeignKey("venta.id"), nullable=False)
    id_producto = Column(BigInteger, ForeignKey("producto.id"), nullable=True)
    codigo_producto = Column(String(50), nullable=True)
    nombre_producto = Column(String(150), nullable=False)
    cantidad = Column(Numeric(10, 2), nullable=False)
    precio_unitario = Column(Numeric(12, 2), nullable=False)
    subtotal_linea = Column(Numeric(12, 2), nullable=False)

    def __repr__(self):
        return f"<DetalleVenta(id={self.id}, id_venta={self.id_venta}, nombre_producto={self.nombre_producto})>"
