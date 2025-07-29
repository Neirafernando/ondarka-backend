from pydantic import BaseModel
from typing import Optional
from datetime import datetime

# Para leer datos desde la base
class ClienteBase(BaseModel):
    nombre: Optional[str]
    rut: Optional[str]
    email: Optional[str]
    telefono: Optional[str]
    direccion: Optional[str]
    logo: Optional[str]
    plan_id: Optional[int]
    estado: Optional[str]
    fecha_alta: Optional[datetime]

# Para mostrar un cliente
class ClienteOut(ClienteBase):
    id: int

    class Config:
        orm_mode = True

# Para crear un nuevo cliente
class ClienteCreate(ClienteBase):
    nombre: str
    rut: str
    email: str
    telefono: str
    direccion: str
    plan_id: int
