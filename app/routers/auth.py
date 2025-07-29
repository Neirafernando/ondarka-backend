from fastapi import APIRouter, Depends, HTTPException, status, Form
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from app.database import get_async_session
from app.models.admin_usuarios import AdminUsuario
from app.auth import verify_password, create_access_token
from datetime import timedelta

router = APIRouter(prefix="/auth", tags=["Auth"])

@router.post("/login")
async def login(
    username: str = Form(...),
    password: str = Form(...),
    session: AsyncSession = Depends(get_async_session)
):
    result = await session.execute(select(AdminUsuario).where(AdminUsuario.usuario == username))
    user = result.scalar_one_or_none()

    if not user or not verify_password(password, user.password):
        raise HTTPException(status_code=401, detail="Credenciales inválidas")

    token = create_access_token(
        data={"sub": user.usuario, "rol": user.rol},
        expires_delta=timedelta(minutes=60)
    )

    return {"access_token": token, "token_type": "bearer"}
