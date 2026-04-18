"""
Modelo de Producto
"""
from sqlalchemy import Column, BigInteger, String, Numeric
from app.config.database import Base


class Producto(Base):
    __tablename__ = "producto"

    id = Column(BigInteger, primary_key=True, index=True, autoincrement=True)
    codigo = Column(String(50), unique=True, nullable=True)
    cod_barra = Column(String(100), unique=True, nullable=True)
    categoria = Column(String(100), nullable=True)
    nombre = Column(String(150), nullable=False)
    descripcion = Column(String(255), nullable=True)
    costo = Column(Numeric(12, 2), nullable=True)
    precio = Column(Numeric(12, 2), nullable=False)

    def __repr__(self):
        return f"<Producto(id={self.id}, nombre={self.nombre})>"
