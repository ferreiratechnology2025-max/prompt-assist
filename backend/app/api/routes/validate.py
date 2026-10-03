import logging
from typing import Dict, List, Optional

from fastapi import APIRouter
from pydantic import BaseModel

from app.api.dependencies import get_validator

logger = logging.getLogger(__name__)
router = APIRouter()


class ValidateRequest(BaseModel):
    prompt: str
    original_goal: str


class CheckResultModel(BaseModel):
    name: str
    passed: bool
    weight: float
    score: float
    details: str
    severity: str


class ValidateResponse(BaseModel):
    score: float
    passed: bool
    checks: Dict[str, CheckResultModel]
    feedback: str
    suggested_fixes: List[str]
    iteration_needed: bool


@router.post("", response_model=ValidateResponse)
async def validate_prompt(req: ValidateRequest):
    validator = get_validator()
    result = await validator.validate(prompt=req.prompt, original_goal=req.original_goal)

    return ValidateResponse(
        score=result.score,
        passed=result.passed,
        checks={
            name: CheckResultModel(
                name=c.name,
                passed=c.passed,
                weight=c.weight,
                score=c.score,
                details=c.details,
                severity=c.severity.value,
            )
            for name, c in result.checks.items()
        },
        feedback=result.feedback,
        suggested_fixes=result.suggested_fixes,
        iteration_needed=result.iteration_needed,
    )
