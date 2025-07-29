from fastapi import FastAPI
from app.database import engine, Base
from app.routers import clientes
from app.routers import clientes, auth
from app.routers import usuarios
from app.routers import grabaciones
from app.routers import alertas
from app.routers import stats
from app.routers import palabras

app = FastAPI()

@app.on_event("startup")
async def startup():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

# Registrar los routers fuera de cualquier función
app.include_router(clientes.router)
app.include_router(clientes.router)
app.include_router(auth.router)
app.include_router(usuarios.router)
app.include_router(grabaciones.router)
app.include_router(alertas.router)
app.include_router(stats.router)
app.include_router(palabras.router)

@app.get("/")
def home():
    return {"message": "API conectada a MySQL con éxito"}
