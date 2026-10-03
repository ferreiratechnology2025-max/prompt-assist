from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.gzip import GZipMiddleware
from app.utils.logger import setup_logging
from app.database import engine, Base
from app.routers import processos, documentos, pecas, metricas

setup_logging()

Base.metadata.create_all(bind=engine)

app = FastAPI(title="Nex-Júris API", version="1.0.0")

app.add_middleware(GZipMiddleware, minimum_size=1000)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(processos.router)
app.include_router(documentos.router)
app.include_router(pecas.router)
app.include_router(metricas.router)


@app.get("/health")
def health():
    return {"status": "ok"}
