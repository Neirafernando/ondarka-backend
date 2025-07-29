from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from app.database import get_async_session
from app.models.alertas import Alerta
from app.schemas.alertas import AlertaCreate, AlertaOut, AlertaUpdate
from app.models.grabaciones import Grabacion as AudioFile
from app.models.palabras import PalabraClave
from typing import List
from datetime import datetime
import os
import whisper

router = APIRouter(prefix="/alertas", tags=["Alertas"])

# Carga el modelo Whisper una vez
model = whisper.load_model("base")

# ----------------------
# Endpoint: Procesar audio y detectar palabras clave dinámicas
# ----------------------
@router.post("/procesar-audio/{audio_id}")
async def procesar_audio_para_alerta(audio_id: int, session: AsyncSession = Depends(get_async_session)):
    result = await session.execute(select(AudioFile).where(AudioFile.id == audio_id))
    audio = result.scalar_one_or_none()

    if not audio:
        raise HTTPException(status_code=404, detail="Audio no encontrado")

    filepath = os.path.join("recordings", audio.archivo)  # archivo = filename
    if not os.path.exists(filepath):
        raise HTTPException(status_code=404, detail="Archivo de audio no existe")

    try:
        result = model.transcribe(filepath, language="es")
        texto = result["text"].strip().lower()
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error al transcribir: {str(e)}")

    # Guardar transcripción en la grabación
    audio.transcripcion = texto
    await session.commit()

    # Buscar palabras clave activas para este cliente y canal
    query = select(PalabraClave).where(
        PalabraClave.cliente_id == audio.cliente_id,
        PalabraClave.canal == audio.canal
    )
    palabras_resultado = await session.execute(query)
    palabras = palabras_resultado.scalars().all()

    for palabra in palabras:
        if palabra.palabra.lower() in texto:
            nueva = Alerta(
                cliente_id=audio.cliente_id,
                tipo="automatica",
                mensaje=f"Palabra detectada: '{palabra.palabra}' en canal {audio.canal}",
                estado="nuevo",
                fecha=datetime.now()
            )
            session.add(nueva)
            await session.commit()
            await session.refresh(nueva)
            return {
                "mensaje": "Alerta generada",
                "palabra_detectada": palabra.palabra,
                "transcripcion": texto,
                "alerta_id": nueva.id
            }

    return {
        "mensaje": "Sin coincidencias",
        "transcripcion": texto
    }

# ----------------------
# CRUD existente
# ----------------------

@router.post("/", response_model=AlertaOut)
async def crear_alerta(data: AlertaCreate, session: AsyncSession = Depends(get_async_session)):
    nueva = Alerta(
        cliente_id=data.cliente_id,
        tipo=data.tipo,
        mensaje=data.mensaje,
        estado="nuevo",
        fecha=datetime.now()
    )
    session.add(nueva)
    await session.commit()
    await session.refresh(nueva)
    return nueva

@router.get("/", response_model=List[AlertaOut])
async def listar_alertas(session: AsyncSession = Depends(get_async_session)):
    result = await session.execute(select(Alerta))
    return result.scalars().all()

@router.get("/{alerta_id}", response_model=AlertaOut)
async def obtener_alerta(alerta_id: int, session: AsyncSession = Depends(get_async_session)):
    alerta = await session.get(Alerta, alerta_id)
    if not alerta:
        raise HTTPException(status_code=404, detail="No encontrada")
    return alerta

@router.put("/{alerta_id}", response_model=AlertaOut)
async def actualizar_alerta(alerta_id: int, data: AlertaUpdate, session: AsyncSession = Depends(get_async_session)):
    alerta = await session.get(Alerta, alerta_id)
    if not alerta:
        raise HTTPException(status_code=404, detail="No encontrada")
    alerta.estado = data.estado
    await session.commit()
    await session.refresh(alerta)
    return alerta

@router.delete("/{alerta_id}")
async def eliminar_alerta(alerta_id: int, session: AsyncSession = Depends(get_async_session)):
    alerta = await session.get(Alerta, alerta_id)
    if not alerta:
        raise HTTPException(status_code=404, detail="No encontrada")
    await session.delete(alerta)
    await session.commit()
    return {"mensaje": "Alerta eliminada"}
