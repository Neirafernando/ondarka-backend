from pydantic import BaseModel
from typing import Optional
from datetime import datetime

class GrabacionOut(BaseModel):
    id: int
    canal: Optional[str]
    fecha: Optional[datetime]
    duracion: Optional[str]
    archivo: Optional[str]
    transcripcion: Optional[str]
    cliente_id: Optional[int]
    usuario_id: Optional[int]

    class Config:
        from_attributes = True

class GrabacionUpdate(BaseModel):
    canal: Optional[str]
    fecha: Optional[datetime]
    transcripcion: Optional[str]
 
