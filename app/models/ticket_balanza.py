"""
Modelo de tickets de balanza utilizados
"""
from sqlalchemy import Column, BigInteger, DateTime, ForeignKey, Integer, Numeric, String
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from app.config.database import Base

BigIntPrimaryKey = BigInteger().with_variant(Integer, "sqlite")


class TicketBalanza(Base):
    __tablename__ = "ticket_balanza"

    id = Column(BigIntPrimaryKey, primary_key=True, index=True, autoincrement=True)
    numero_ticket = Column(String(20), nullable=False, unique=True, index=True)
    codigo_barra = Column(String(13), nullable=False, unique=True, index=True)
    total = Column(Numeric(12, 2), nullable=False)
    origen = Column(String(30), nullable=False, default="BALANZA", server_default="BALANZA")
    id_venta = Column(BigInteger, ForeignKey("venta.id"), nullable=False)
    usado_en = Column(DateTime(timezone=True), server_default=func.now())

    venta = relationship("Venta", back_populates="tickets_balanza")

    def __repr__(self):
        return f"<TicketBalanza(numero_ticket={self.numero_ticket}, total={self.total})>"
