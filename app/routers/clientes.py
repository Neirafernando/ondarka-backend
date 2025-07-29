from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from app.database import get_async_session
from app.models.clientes import Cliente
from app.schemas.clientes import ClienteCreate, ClienteOut
from typing import List

router = APIRouter(prefix="/clientes", tags=["Clientes"])

# Obtener todos los clientes
@router.get("/", response_model=List[ClienteOut])
async def get_clientes(session: AsyncSession = Depends(get_async_session)):
    result = await session.execute(select(Cliente))
    return result.scalars().all()

# Obtener un cliente por ID
@router.get("/{cliente_id}", response_model=ClienteOut)
async def get_cliente(cliente_id: int, session: AsyncSession = Depends(get_async_session)):
    result = await session.get(Cliente, cliente_id)
    if not result:
        raise HTTPException(status_code=404, detail="Cliente no encontrado")
    return result

# Crear un nuevo cliente
@router.post("/", response_model=ClienteOut)
async def create_cliente(data: ClienteCreate, session: AsyncSession = Depends(get_async_session)):
    nuevo_cliente = Cliente(**data.dict())
    session.add(nuevo_cliente)
    await session.commit()
    await session.refresh(nuevo_cliente)
    return nuevo_cliente

# Eliminar cliente
@router.delete("/{cliente_id}")
async def delete_cliente(cliente_id: int, session: AsyncSession = Depends(get_async_session)):
    cliente = await session.get(Cliente, cliente_id)
    if not cliente:
        raise HTTPException(status_code=404, detail="Cliente no encontrado")
    await session.delete(cliente)
    await session.commit()
    return {"mensaje": "Cliente eliminado"}

# Actualizar cliente
@router.put("/{cliente_id}", response_model=ClienteOut)
async def update_cliente(cliente_id: int, data: ClienteCreate, session: AsyncSession = Depends(get_async_session)):
    cliente = await session.get(Cliente, cliente_id)
    if not cliente:
        raise HTTPException(status_code=404, detail="Cliente no encontrado")

    for key, value in data.dict().items():
        setattr(cliente, key, value)

    session.add(cliente)
    await session.commit()
    await session.refresh(cliente)
    return cliente
