from sqlalchemy import Column, Integer, String, Enum, ForeignKey
from sqlalchemy.orm import relationship
from app.database import Base

class Usuario(Base):
    __tablename__ = "usuarios"

    id = Column(Integer, primary_key=True, index=True)
    cliente_id = Column(Integer, ForeignKey("clientes.id"))
    nombre = Column(String(100))
    usuario = Column(String(50))
    password = Column(String(255))
    rol = Column(Enum("admin", "operador", "lectura", name="rol_usuario"))
    email = Column(String(100))
    activo = Column(Integer, default=1)

    cliente = relationship("Cliente", back_populates="usuarios")
    grabaciones = relationship("Grabacion", back_populates="usuario")
