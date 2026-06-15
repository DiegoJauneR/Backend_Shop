"""
Modelo de Detalle de Boleta
"""
from sqlalchemy import Column, BigInteger, Integer, String, Numeric, ForeignKey
from sqlalchemy.orm import relationship
from app.config.database import Base

BigIntPrimaryKey = BigInteger().with_variant(Integer, "sqlite")


class BoletaDetalle(Base):
    __tablename__ = "boleta_detalle"

    id_detalle = Column(BigIntPrimaryKey, primary_key=True, index=True, autoincrement=True)
    id_boleta = Column(BigInteger, ForeignKey("boleta.id_boleta"), nullable=False)
    id_producto = Column(BigInteger, ForeignKey("producto.id"), nullable=True)
    codigo_producto = Column(String(50), nullable=True)
    nombre_producto = Column(String(150), nullable=False)
    cantidad = Column(Numeric(12, 3), nullable=False)
    precio_unitario = Column(Numeric(12, 2), nullable=False)
    subtotal_linea = Column(Numeric(12, 2), nullable=False)

    boleta = relationship("Boleta", back_populates="detalles")
    producto = relationship("Producto")

    def __repr__(self):
        return f"<BoletaDetalle(id_detalle={self.id_detalle}, id_boleta={self.id_boleta})>"
