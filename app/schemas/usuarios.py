from pydantic import BaseModel
from typing import Optional

class UsuarioBase(BaseModel):
    nombre: Optional[str]
    usuario: Optional[str]
    email: Optional[str]
    rol: Optional[str]
    activo: Optional[int]
    cliente_id: Optional[int]

class UsuarioCreate(UsuarioBase):
    nombre: str
    usuario: str
    password: str
    rol: str
    email: str
    cliente_id: int

class UsuarioOut(UsuarioBase):
    id: int

    class Config:
        from_attributes = True  # para que funcione con SQLAlchemy
