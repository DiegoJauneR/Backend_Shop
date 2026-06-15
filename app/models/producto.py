"""
Modelo de Producto
"""
from sqlalchemy import CheckConstraint, Column, BigInteger, Integer, String, Numeric
from sqlalchemy.orm import relationship
from app.config.database import Base

BigIntPrimaryKey = BigInteger().with_variant(Integer, "sqlite")


class Producto(Base):
    __tablename__ = "producto"
    __table_args__ = (
        CheckConstraint("tipo_venta in ('unidad', 'peso')", name="ck_producto_tipo_venta"),
    )

    id = Column(BigIntPrimaryKey, primary_key=True, index=True, autoincrement=True)
    cod_barra = Column(String(100), unique=True, nullable=True)
    categoria = Column(String(100), nullable=True)
    nombre = Column(String(150), nullable=False)
    costo = Column(Numeric(12, 2), nullable=True)
    precio = Column(Numeric(12, 2), nullable=False)
    unidad = Column(String(30), nullable=False, default="unidad", server_default="unidad")
    tipo_venta = Column(String(20), nullable=False, default="unidad", server_default="unidad")

    detalles = relationship("DetalleVenta", back_populates="producto")

    def __repr__(self):
        return f"<Producto(id={self.id}, nombre={self.nombre})>"
