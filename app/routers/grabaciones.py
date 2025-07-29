import os
from fastapi import APIRouter, UploadFile, File, Form, HTTPException, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy import func
from app.database import get_async_session
from app.models.grabaciones import Grabacion
from mutagen import File as MutagenFile
from datetime import datetime, time
from typing import List, Optional
from app.schemas.grabaciones import GrabacionOut, GrabacionUpdate

router = APIRouter(prefix="/grabaciones", tags=["Grabaciones"])

UPLOAD_DIR = "recordings"
os.makedirs(UPLOAD_DIR, exist_ok=True)

def duracion_a_str(valor):
    """Convierte un campo duración a string hh:mm:ss (acepta str, time, o None)."""
    if valor is None:
        return ""
    if isinstance(valor, str):
        return valor
    if isinstance(valor, time):
        return f"{valor.hour:02}:{valor.minute:02}:{valor.second:02}"
    return str(valor)

@router.post("/")
async def subir_grabacion(
    file: UploadFile = File(...),
    canal: str = Form(...),
    cliente_id: int = Form(...),
    usuario_id: int = Form(...),
    fecha: str = Form(None),  # formato ISO
    transcripcion: str = Form(None),
    session: AsyncSession = Depends(get_async_session)
):
    filename = file.filename
    timestamp = fecha or datetime.now().isoformat()
    filepath = os.path.join(UPLOAD_DIR, filename)

    try:
        # Guardar archivo en disco
        with open(filepath, "wb") as buffer:
            buffer.write(await file.read())

        # Obtener duración
        mutagen_audio = MutagenFile(filepath)
        if mutagen_audio is None or not mutagen_audio.info:
            raise HTTPException(status_code=400, detail="No se pudo leer duración del audio")
        total_seconds = int(mutagen_audio.info.length)
        minutos = total_seconds // 60
        segundos = total_seconds % 60
        duracion = f"{minutos:02d}:{segundos:02d}:00"

        nueva = Grabacion(
            canal=canal,
            cliente_id=cliente_id,
            usuario_id=usuario_id,
            fecha=timestamp,
            archivo=filename,
            duracion=duracion,
            transcripcion=transcripcion
        )

        session.add(nueva)
        await session.commit()
        await session.refresh(nueva)
        return {"mensaje": "Grabación guardada", "id": nueva.id}

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# Obtener todas las grabaciones con filtros y paginado
@router.get("/", response_model=List[GrabacionOut])
async def listar_grabaciones(
    usuario_id: Optional[int] = Query(None),
    cliente_id: Optional[int] = Query(None),
    canal: Optional[str] = Query(None),
    fecha: Optional[str] = Query(None),
    limit: int = Query(50),
    session: AsyncSession = Depends(get_async_session)
):
    stmt = select(Grabacion)

    if usuario_id:
        stmt = stmt.where(Grabacion.usuario_id == usuario_id)
    if cliente_id:
        stmt = stmt.where(Grabacion.cliente_id == cliente_id)
    if canal:
        stmt = stmt.where(Grabacion.canal.ilike(f"%{canal}%"))
    if fecha:
        try:
            fecha_dt = datetime.strptime(fecha, "%Y-%m-%d").date()
            stmt = stmt.where(func.date(Grabacion.fecha) == fecha_dt)
        except Exception:
            raise HTTPException(status_code=400, detail="Fecha debe ser YYYY-MM-DD")

    stmt = stmt.order_by(Grabacion.fecha.desc()).limit(limit)

    result = await session.execute(stmt)
    lista = []
    for g in result.scalars().all():
        item = g.__dict__.copy()
        item['duracion'] = duracion_a_str(g.duracion)
        lista.append(GrabacionOut(**item))
    return lista


# Obtener grabación por ID
@router.get("/{grabacion_id}", response_model=GrabacionOut)
async def obtener_grabacion(grabacion_id: int, session: AsyncSession = Depends(get_async_session)):
    grabacion = await session.get(Grabacion, grabacion_id)
    if not grabacion:
        raise HTTPException(status_code=404, detail="No encontrada")
    item = grabacion.__dict__.copy()
    item['duracion'] = duracion_a_str(grabacion.duracion)
    return GrabacionOut(**item)

# Eliminar grabación
@router.delete("/{grabacion_id}")
async def eliminar_grabacion(grabacion_id: int, session: AsyncSession = Depends(get_async_session)):
    grabacion = await session.get(Grabacion, grabacion_id)
    if not grabacion:
        raise HTTPException(status_code=404, detail="No encontrada")

    # Eliminar archivo del disco
    filepath = os.path.join(UPLOAD_DIR, grabacion.archivo or "")
    if os.path.exists(filepath):
        os.remove(filepath)

    await session.delete(grabacion)
    await session.commit()
    return {"mensaje": "Grabación eliminada"}

# Actualizar metadata
@router.put("/{grabacion_id}", response_model=GrabacionOut)
async def actualizar_grabacion(grabacion_id: int, data: GrabacionUpdate, session: AsyncSession = Depends(get_async_session)):
    grabacion = await session.get(Grabacion, grabacion_id)
    if not grabacion:
        raise HTTPException(status_code=404, detail="No encontrada")

    for key, value in data.dict(exclude_unset=True).items():
        setattr(grabacion, key, value)

    await session.commit()
    await session.refresh(grabacion)
    item = grabacion.__dict__.copy()
    item['duracion'] = duracion_a_str(grabacion.duracion)
    return GrabacionOut(**item)
