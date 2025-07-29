from sqlalchemy import Column, Integer, String, ForeignKey
from app.database import Base

class PalabraClave(Base):
    __tablename__ = "palabras_clave"

    id = Column(Integer, primary_key=True, index=True)
    cliente_id = Column(Integer, ForeignKey("clientes.id"))
    canal = Column(String(50))
    palabra = Column(String(100))
