from pydantic import BaseModel

class PalabraClaveCreate(BaseModel):
    cliente_id: int
    canal: str
    palabra: str

class PalabraClaveOut(PalabraClaveCreate):
    id: int

    class Config:
        from_attributes = True  # si usas Pydantic V2
