"""
Modelo de Cliente
"""
from sqlalchemy import Column, BigInteger, String
from app.config.database import Base


class Cliente(Base):
    __tablename__ = "cliente"

    id = Column(BigInteger, primary_key=True, index=True, autoincrement=True)
    rut = Column(String(12), nullable=True)
    nombre = Column(String(40), nullable=True)
    direccion = Column(String(50), nullable=True)
    ciudad = Column(String(40), nullable=True)
    telefono = Column(String(12), nullable=True)
    correo = Column(String(40), nullable=True)
    giro = Column(String(40), nullable=True)

    def __repr__(self):
        return f"<Cliente(id={self.id}, rut={self.rut}, nombre={self.nombre})>"
