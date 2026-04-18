"""
Modelo de Cierre de Caja
"""
from sqlalchemy import Column, BigInteger, Integer, String, Numeric, Date, DateTime, ForeignKey
from sqlalchemy.sql import func
from app.config.database import Base


class CierreCaja(Base):
    __tablename__ = "cierre_caja"

    id = Column(BigInteger, primary_key=True, index=True, autoincrement=True)
    id_usuario = Column(Integer, ForeignKey("users.id"), nullable=True)
    fecha = Column(Date, server_default=func.current_date())
    fecha_apertura = Column(DateTime(timezone=True), server_default=func.now())
    fecha_cierre = Column(DateTime(timezone=True), nullable=True)
    monto_inicial_caja = Column(Numeric(12, 2), nullable=False)
    total_ventas = Column(Numeric(12, 2), default=0)
    cantidad_ventas = Column(Integer, default=0)
    total_efectivo = Column(Numeric(12, 2), default=0)
    total_debito = Column(Numeric(12, 2), default=0)
    total_credito = Column(Numeric(12, 2), default=0)
    total_transferencia = Column(Numeric(12, 2), default=0)
    monto_esperado_caja = Column(Numeric(12, 2), default=0)
    monto_real_caja = Column(Numeric(12, 2), nullable=True)
    diferencia = Column(Numeric(12, 2), default=0)
    estado = Column(String(20), default="abierta", nullable=False)

    def __repr__(self):
        return f"<CierreCaja(id={self.id}, estado={self.estado})>"
