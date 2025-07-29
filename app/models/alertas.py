from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Enum
from sqlalchemy.orm import relationship
from app.database import Base

class Alerta(Base):
    __tablename__ = "alertas"

    id = Column(Integer, primary_key=True, index=True)
    cliente_id = Column(Integer, ForeignKey("clientes.id"))
    fecha = Column(DateTime)
    tipo = Column(String(40))
    mensaje = Column(String(255))
    estado = Column(Enum("nuevo", "visto", name="estado_alerta"))

    cliente = relationship("Cliente", back_populates="alertas")
