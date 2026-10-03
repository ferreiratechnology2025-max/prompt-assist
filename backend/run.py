from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
import logging

from app.core.config import settings
from app.services.llm_service import LLMService
from app.core.validator import ValidatorEngine
from app.services.template_service import TemplateService
from app.core.generator import PromptEngine
from app.core.memory import AdaptiveMemory
from app.api.dependencies import set_services
from app.api.routes.templates import router as templates_router
from app.api.routes.validate import router as validate_router
from app.api.routes.memory import router as memory_router
from app.api.routes.health import router as health_router

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

llm_service = None
validator = None
template_service = None
prompt_engine = None
memory = None


@asynccontextmanager
async def lifespan(app: FastAPI):
    global llm_service, validator, template_service, prompt_engine, memory
    logger.info("Iniciando QualiPrompt API...")

    llm_service = LLMService(
        base_url=settings.OLLAMA_BASE_URL,
        model=settings.LLM_MODEL,
    )

    if await llm_service.health_check():
        logger.info("Ollama conectado com sucesso")
    else:
        logger.warning("Ollama nao esta respondendo. Execute 'ollama serve'")

    validator = ValidatorEngine(llm_service)
    template_service = TemplateService()
    memory = AdaptiveMemory(
        epsilon=settings.MEMORY_EXPLORE_RATIO,
        model_version=settings.MODEL_VERSION,
    )
    prompt_engine = PromptEngine(llm_service, validator, memory=memory)

    set_services(template_service, prompt_engine, validator, memory)

    templates = template_service.list_names()
    logger.info(f"Templates carregados: {templates}")

    mem_stats = memory.get_stats()
    logger.info(f"Memoria: {mem_stats['total_entries']} entradas")

    yield

    logger.info("Desligando QualiPrompt API...")


app = FastAPI(
    title="QualiPrompt API",
    description="Sistema de engenharia de prompts com validacao rigorosa",
    version="0.3.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(templates_router, prefix="/api/templates", tags=["templates"])
app.include_router(validate_router, prefix="/api/validate", tags=["validation"])
app.include_router(memory_router, prefix="/api/memory", tags=["memory"])
app.include_router(health_router, prefix="/api", tags=["health"])


@app.get("/")
async def root():
    return {"status": "ok", "service": "QualiPrompt", "version": "0.3.0"}


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000, reload=True)
