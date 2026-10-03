import logging
from typing import Dict, List, Optional

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from app.api.dependencies import get_template_service, get_prompt_engine
from app.core.generator import PromptGenerationRequest

logger = logging.getLogger(__name__)
router = APIRouter()


class GenerateRequest(BaseModel):
    template_name: str
    field_values: Dict[str, str]
    user_goal: str
    skip_memory: bool = False


class GenerateResponse(BaseModel):
    success: bool
    generated_prompt: str
    validation_score: float
    passed_validation: bool
    iterations_used: int
    template_name: str
    memory_used: bool
    exploration_mode: bool
    error: Optional[str] = None


@router.get("")
async def list_templates():
    ts = get_template_service()
    templates = ts.load_all()
    return {
        "templates": [
            {"name": t["name"], "version": t.get("version", "1.0")}
            for t in templates
        ]
    }


@router.get("/{name}")
async def get_template(name: str):
    ts = get_template_service()
    tpl = ts.get(name)
    if not tpl:
        raise HTTPException(status_code=404, detail=f"Template '{name}' nao encontrado")
    return tpl


@router.get("/{name}/schema")
async def get_template_schema(name: str):
    ts = get_template_service()
    tpl = ts.get(name)
    if not tpl:
        raise HTTPException(status_code=404, detail=f"Template '{name}' nao encontrado")
    return {
        "name": tpl["name"],
        "required_fields": tpl["required_fields"],
        "assistant_role": tpl["assistant_role"],
    }


@router.post("/generate", response_model=GenerateResponse)
async def generate_prompt(req: GenerateRequest):
    ts = get_template_service()
    engine = get_prompt_engine()

    tpl = ts.get(req.template_name)
    if not tpl:
        raise HTTPException(
            status_code=404, detail=f"Template '{req.template_name}' nao encontrado"
        )

    request = PromptGenerationRequest(
        template_name=req.template_name,
        template=tpl,
        field_values=req.field_values,
        user_goal=req.user_goal,
    )

    try:
        result = await engine.generate_and_validate(request)

        memory_used = not req.skip_memory and engine.memory is not None
        exploration_mode = memory_used and result.get("iterations_used", 0) > 0

        return GenerateResponse(
            success=True,
            generated_prompt=result.get("generated_prompt", ""),
            validation_score=result.get("validation_score", 0),
            passed_validation=result.get("passed", False),
            iterations_used=result.get("iterations_used", 0),
            template_name=req.template_name,
            memory_used=memory_used,
            exploration_mode=exploration_mode,
        )

    except Exception as e:
        logger.error(f"Erro na geracao de prompt: {e}", exc_info=True)
        return GenerateResponse(
            success=False,
            generated_prompt="",
            validation_score=0,
            passed_validation=False,
            iterations_used=0,
            template_name=req.template_name,
            memory_used=False,
            exploration_mode=False,
            error=str(e),
        )
