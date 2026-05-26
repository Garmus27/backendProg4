from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.core.database import create_db_and_tables
from app.db.seed import run_seed
from app.modules.health.router import router as health_router
from app.modules.usuarios.router import router as auth_router
from app.modules.direcciones.router import router as direcciones_router
from app.modules.unidad_medida.router import router as unidades_router
from app.modules.categorias.router import router as categorias_router
from app.modules.ingredientes.router import router as ingredientes_router
from app.modules.productos.router import router as productos_router
from app.modules.pedidos.router import router as pedidos_router


@asynccontextmanager
async def lifespan(app: FastAPI):
    create_db_and_tables()
    run_seed()
    yield


app = FastAPI(title="Parcial Programación IV", version="1.0.0", lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(health_router)
app.include_router(auth_router,         prefix="/auth",            tags=["auth"])
app.include_router(direcciones_router,  prefix="/direcciones",     tags=["direcciones"])
app.include_router(unidades_router,     prefix="/unidades-medida", tags=["unidades-medida"])
app.include_router(categorias_router,   prefix="/categorias",      tags=["categorias"])
app.include_router(ingredientes_router, prefix="/ingredientes",    tags=["ingredientes"])
app.include_router(productos_router,    prefix="/productos",       tags=["productos"])
app.include_router(pedidos_router,      prefix="/pedidos",         tags=["pedidos"])
