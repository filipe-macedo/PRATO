from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.config import configuracoes
from app.database import engine, Base
from app.dependencies import _carregar_modelo
from app.routers import saude, produtos, vendas, previsoes

Base.metadata.create_all(bind=engine)


@asynccontextmanager
async def lifespan(app: FastAPI):
    try:
        _carregar_modelo()
        print("[PRATO] Modelo ML carregado com sucesso.")
    except FileNotFoundError as exc:
        print(f"[PRATO] AVISO: {exc}")
    yield


app = FastAPI(
    title="PRATO — API de Previsão de Demanda",
    description=(
        "Backend do sistema de previsão de demanda para restaurantes. "
        "Permite registro de vendas, consulta de produtos e geração de "
        "previsões via modelos de machine learning."
    ),
    version="1.0.0",
    lifespan=lifespan,
    docs_url="/docs",
    redoc_url="/redoc",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=configuracoes.origens_permitidas,
    allow_credentials=False,
    allow_methods=["GET", "POST", "PUT"],
    allow_headers=["Content-Type", "Accept"],
)

app.include_router(saude.router)
app.include_router(produtos.router)
app.include_router(vendas.router)
app.include_router(previsoes.router)
