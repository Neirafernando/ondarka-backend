from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from app.database import get_async_session
from app.models.usuarios import Usuario
from app.schemas.usuarios import UsuarioCreate, UsuarioOut
from passlib.context import CryptContext
from typing import List

router = APIRouter(prefix="/usuarios", tags=["Usuarios"])

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# Obtener todos los usuarios
@router.get("/", response_model=List[UsuarioOut])
async def get_usuarios(session: AsyncSession = Depends(get_async_session)):
    result = await session.execute(select(Usuario))
    return result.scalars().all()

# Obtener usuario por ID
@router.get("/{usuario_id}", response_model=UsuarioOut)
async def get_usuario(usuario_id: int, session: AsyncSession = Depends(get_async_session)):
    usuario = await session.get(Usuario, usuario_id)
    if not usuario:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")
    return usuario

# Crear usuario
@router.post("/", response_model=UsuarioOut)
async def create_usuario(data: UsuarioCreate, session: AsyncSession = Depends(get_async_session)):
    hashed_password = pwd_context.hash(data.password)
    nuevo = Usuario(**data.dict(exclude={"password"}), password=hashed_password)
    session.add(nuevo)
    await session.commit()
    await session.refresh(nuevo)
    return nuevo

# Eliminar usuario
@router.delete("/{usuario_id}")
async def delete_usuario(usuario_id: int, session: AsyncSession = Depends(get_async_session)):
    usuario = await session.get(Usuario, usuario_id)
    if not usuario:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")
    await session.delete(usuario)
    await session.commit()
    return {"mensaje": "Usuario eliminado"}

# Actualizar usuario
@router.put("/{usuario_id}", response_model=UsuarioOut)
async def update_usuario(usuario_id: int, data: UsuarioCreate, session: AsyncSession = Depends(get_async_session)):
    usuario = await session.get(Usuario, usuario_id)
    if not usuario:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")

    for key, value in data.dict(exclude={"password"}).items():
        setattr(usuario, key, value)

    if data.password:
        usuario.password = pwd_context.hash(data.password)

    session.add(usuario)
    await session.commit()
    await session.refresh(usuario)
    return usuario
