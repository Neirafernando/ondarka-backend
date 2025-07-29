from sqlalchemy import Column, Integer, String, DateTime, Enum, ForeignKey
from sqlalchemy.orm import relationship
from app.database import Base

class Cliente(Base):
    __tablename__ = "clientes"

    id = Column(Integer, primary_key=True, index=True)
    nombre = Column(String(100))
    rut = Column(String(20), unique=True)
    email = Column(String(100))
    telefono = Column(String(30))
    direccion = Column(String(150))
    logo = Column(String(255))
    plan_id = Column(Integer, ForeignKey("planes.id"))
    estado = Column(Enum("activo", "suspendido", "eliminado", name="estado_cliente"))
    fecha_alta = Column(DateTime)

    plan = relationship("Plan", back_populates="clientes")
    usuarios = relationship("Usuario", back_populates="cliente")
    grabaciones = relationship("Grabacion", back_populates="cliente")
    alertas = relationship("Alerta", back_populates="cliente")
