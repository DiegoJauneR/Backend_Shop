"""
Modelo de Venta
"""
from sqlalchemy import Column, BigInteger, Integer, String, Numeric, DateTime, ForeignKey
from sqlalchemy.sql import func
from app.config.database import Base


class Venta(Base):
    __tablename__ = "venta"

    id = Column(BigInteger, primary_key=True, index=True, autoincrement=True)
    fecha = Column(DateTime(timezone=True), server_default=func.now())
    id_usuario = Column(Integer, ForeignKey("users.id"), nullable=True)
    id_cierre_caja = Column(BigInteger, ForeignKey("cierre_caja.id"), nullable=True)
    subtotal = Column(Numeric(12, 2), nullable=False)
    descuento = Column(Numeric(12, 2), default=0)
    recargo = Column(Numeric(12, 2), default=0)
    total = Column(Numeric(12, 2), nullable=False)
    tipo_pago = Column(String(30), nullable=False)
    efectivo_recibido = Column(Numeric(12, 2), nullable=True)
    vuelto = Column(Numeric(12, 2), default=0)
    comprobante = Column(String(30), nullable=False)
    estado = Column(String(30), nullable=False)

    def __repr__(self):
        return f"<Venta(id={self.id}, total={self.total}, estado={self.estado})>"
