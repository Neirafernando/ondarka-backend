from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Time, Text
from sqlalchemy.orm import relationship
from app.database import Base

class Grabacion(Base):
    __tablename__ = "grabaciones"

    id = Column(Integer, primary_key=True, index=True)
    cliente_id = Column(Integer, ForeignKey("clientes.id"))
    usuario_id = Column(Integer, ForeignKey("usuarios.id"))
    canal = Column(String(50))
    fecha = Column(DateTime)
    duracion = Column(Time)
    archivo = Column(String(255))
    transcripcion = Column(Text)

    cliente = relationship("Cliente", back_populates="grabaciones")
    usuario = relationship("Usuario", back_populates="grabaciones")
