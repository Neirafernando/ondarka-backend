from sqlalchemy import Column, Integer, String, DECIMAL
from app.database import Base
from sqlalchemy.orm import relationship

class Plan(Base):
    __tablename__ = "planes"

    id = Column(Integer, primary_key=True, index=True)
    nombre = Column(String(50), unique=True)
    max_usuarios = Column(Integer)
    max_espacio_gb = Column(Integer)
    max_canales = Column(Integer)
    precio = Column(DECIMAL(10, 2))

    clientes = relationship("Cliente", back_populates="plan")
