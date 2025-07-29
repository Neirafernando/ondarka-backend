from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import func, select, and_
from app.database import get_async_session
from app.models.grabaciones import Grabacion

router = APIRouter(prefix="/api/stats", tags=["Estadísticas"])

# --- Total de grabaciones
@router.get("/total")
async def total_grabaciones(
    cliente_id: int = Query(None),
    usuario_id: int = Query(None),
    session: AsyncSession = Depends(get_async_session)
):
    stmt = select(func.count()).select_from(Grabacion)
    if cliente_id:
        stmt = stmt.where(Grabacion.cliente_id == cliente_id)
    if usuario_id:
        stmt = stmt.where(Grabacion.usuario_id == usuario_id)
    total = await session.execute(stmt)
    return {"total_audios": total.scalar()}

# --- Duración total (string hh:mm:ss)
@router.get("/duration")
async def duracion_total(session: AsyncSession = Depends(get_async_session)):
    result = await session.execute(select(Grabacion.duracion))
    total_segundos = 0
    for fila in result.scalars():
        if fila:
            # Si es string tipo 'HH:MM:SS'
            if isinstance(fila, str) and ':' in fila:
                h, m, s = [int(part) for part in fila.split(":")]
            # Si es datetime.time
            elif hasattr(fila, "hour"):
                h, m, s = fila.hour, fila.minute, fila.second
            else:
                continue
            total_segundos += h * 3600 + m * 60 + s

    horas = total_segundos // 3600
    minutos = (total_segundos % 3600) // 60
    segundos = total_segundos % 60
    return {"total_duration": f"{horas:02}:{minutos:02}:{segundos:02}"}


# --- Última grabación
@router.get("/last")
async def ultima_grabacion(
    cliente_id: int = Query(None),
    usuario_id: int = Query(None),
    session: AsyncSession = Depends(get_async_session)
):
    stmt = select(Grabacion).order_by(Grabacion.fecha.desc()).limit(1)
    if cliente_id:
        stmt = stmt.where(Grabacion.cliente_id == cliente_id)
    if usuario_id:
        stmt = stmt.where(Grabacion.usuario_id == usuario_id)
    result = await session.execute(stmt)
    grabacion = result.scalar_one_or_none()
    if grabacion:
        return {
            "timestamp": grabacion.fecha,
            "filename": grabacion.archivo,
            "canal": grabacion.canal,
            "duration": grabacion.duracion
        }
    return {}

# --- Canales activos
@router.get("/canales")
async def canales(
    cliente_id: int = Query(None),
    usuario_id: int = Query(None),
    session: AsyncSession = Depends(get_async_session)
):
    stmt = select(Grabacion.canal).distinct()
    if cliente_id:
        stmt = stmt.where(Grabacion.cliente_id == cliente_id)
    if usuario_id:
        stmt = stmt.where(Grabacion.usuario_id == usuario_id)
    result = await session.execute(stmt)
    canales = [row[0] for row in result if row[0]]
    return {"canales_activos": canales, "cantidad": len(canales)}

# --- Grabaciones por día
@router.get("/dias")
async def actividad_diaria(
    cliente_id: int = Query(None),
    usuario_id: int = Query(None),
    session: AsyncSession = Depends(get_async_session)
):
    stmt = select(
        func.date(Grabacion.fecha), func.count()
    )
    if cliente_id:
        stmt = stmt.where(Grabacion.cliente_id == cliente_id)
    if usuario_id:
        stmt = stmt.where(Grabacion.usuario_id == usuario_id)
    stmt = stmt.group_by(func.date(Grabacion.fecha)).order_by(func.date(Grabacion.fecha))
    result = await session.execute(stmt)
    return [{"fecha": str(row[0]), "grabaciones": row[1]} for row in result]
