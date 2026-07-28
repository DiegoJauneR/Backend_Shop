"""
Modelo de Venta
"""
from sqlalchemy import Column, BigInteger, Integer, String, Numeric, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.config.database import Base

BigIntPrimaryKey = BigInteger().with_variant(Integer, "sqlite")


class Venta(Base):
    __tablename__ = "venta"

    id = Column(BigIntPrimaryKey, primary_key=True, index=True, autoincrement=True)
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

    detalles = relationship(
        "DetalleVenta",
        back_populates="venta",
        cascade="all, delete-orphan",
        lazy="selectin",
    )
    boleta = relationship(
        "Boleta",
        back_populates="venta",
        cascade="all, delete-orphan",
        uselist=False,
        lazy="selectin",
    )
    tickets_balanza = relationship(
        "TicketBalanza",
        back_populates="venta",
        cascade="all, delete-orphan",
        lazy="selectin",
    )
    usuario = relationship("User", lazy="selectin")

    @property
    def employee_name(self):
        if not self.usuario:
            return None
        return self.usuario.full_name or self.usuario.username or self.usuario.email

    def __repr__(self):
        return f"<Venta(id={self.id}, total={self.total}, estado={self.estado})>"
