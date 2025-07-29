from pydantic import BaseModel
from typing import Optional
from datetime import datetime

class AlertaBase(BaseModel):
    cliente_id: Optional[int]
    fecha: Optional[datetime]
    tipo: Optional[str]
    mensaje: Optional[str]
    estado: Optional[str]  # nuevo o visto

class AlertaCreate(AlertaBase):
    cliente_id: int
    tipo: str
    mensaje: str

class AlertaUpdate(BaseModel):
    estado: str

class AlertaOut(AlertaBase):
    id: int

    class Config:
        from_attributes = True
