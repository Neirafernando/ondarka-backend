from sqlalchemy import Column, Integer, String, Enum
from app.database import Base

class AdminUsuario(Base):
    __tablename__ = "admin_usuarios"

    id = Column(Integer, primary_key=True, index=True)
    nombre = Column(String(100))
    usuario = Column(String(50), unique=True)
    password = Column(String(255))
    rol = Column(Enum("superadmin", "soporte", name="rol_admin"))
