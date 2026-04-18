"""
Modelo de Boleta
"""
from sqlalchemy import Column, BigInteger, String, Numeric, DateTime, ForeignKey
from sqlalchemy.sql import func
from app.config.database import Base


class Boleta(Base):
    __tablename__ = "boleta"

    id_boleta = Column(BigInteger, primary_key=True, index=True, autoincrement=True)
    id_venta = Column(BigInteger, ForeignKey("venta.id"), unique=True, nullable=False)
    fecha_emision = Column(DateTime(timezone=True), server_default=func.now())
    subtotal = Column(Numeric(12, 2), nullable=False)
    total_pagar = Column(Numeric(12, 2), nullable=False)
    tipo_pago = Column(String(30), nullable=False)

    def __repr__(self):
        return f"<Boleta(id_boleta={self.id_boleta}, id_venta={self.id_venta})>"
