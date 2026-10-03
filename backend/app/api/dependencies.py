from fastapi import Depends, HTTPException, Header

from app.core.config import settings
from app.services.template_service import TemplateService
from app.core.generator import PromptEngine
from app.core.validator import ValidatorEngine
from app.core.memory import AdaptiveMemory

_template_service = None
_prompt_engine = None
_validator = None
_memory = None


def set_services(
    template_service: TemplateService,
    prompt_engine: PromptEngine,
    validator: ValidatorEngine,
    memory: AdaptiveMemory,
):
    global _template_service, _prompt_engine, _validator, _memory
    _template_service = template_service
    _prompt_engine = prompt_engine
    _validator = validator
    _memory = memory


def get_template_service() -> TemplateService:
    if _template_service is None:
        raise HTTPException(status_code=503, detail="Template service not initialized")
    return _template_service


def get_prompt_engine() -> PromptEngine:
    if _prompt_engine is None:
        raise HTTPException(status_code=503, detail="Prompt engine not initialized")
    return _prompt_engine


def get_validator() -> ValidatorEngine:
    if _validator is None:
        raise HTTPException(status_code=503, detail="Validator not initialized")
    return _validator


def get_memory() -> AdaptiveMemory:
    if _memory is None:
        raise HTTPException(status_code=503, detail="Memory not initialized")
    return _memory


async def verify_admin_token(x_admin_token: str = Header(..., alias="X-Admin-Token")):
    if x_admin_token != settings.ADMIN_TOKEN:
        raise HTTPException(
            status_code=403, detail="Acesso negado. Token admin invalido."
        )
    return True
