from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from typing import List
from app.database import get_async_session
from app.models.palabras import PalabraClave
from app.schemas.palabras import PalabraClaveCreate, PalabraClaveOut

router = APIRouter(prefix="/palabras-clave", tags=["Palabras clave"])

@router.post("/", response_model=PalabraClaveOut)
async def agregar_palabra(data: PalabraClaveCreate, session: AsyncSession = Depends(get_async_session)):
    nueva = PalabraClave(**data.dict())
    session.add(nueva)
    await session.commit()
    await session.refresh(nueva)
    return nueva

@router.get("/{cliente_id}", response_model=List[PalabraClaveOut])
async def listar_palabras(cliente_id: int, session: AsyncSession = Depends(get_async_session)):
    result = await session.execute(select(PalabraClave).where(PalabraClave.cliente_id == cliente_id))
    return result.scalars().all()

@router.delete("/{palabra_id}")
async def eliminar_palabra(palabra_id: int, session: AsyncSession = Depends(get_async_session)):
    palabra = await session.get(PalabraClave, palabra_id)
    if not palabra:
        raise HTTPException(status_code=404, detail="Palabra no encontrada")
    await session.delete(palabra)
    await session.commit()
    return {"mensaje": "Palabra eliminada"}
