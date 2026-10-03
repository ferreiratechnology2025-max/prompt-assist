import logging

from fastapi import APIRouter

from app.api.dependencies import get_memory

logger = logging.getLogger(__name__)
router = APIRouter()


@router.get("/health")
async def health():
    status = "ok"
    llm_ok = False
    mem_ok = False
    db_ok = False

    try:
        from app.api.dependencies import _prompt_engine
        if _prompt_engine and _prompt_engine.llm:
            llm_ok = await _prompt_engine.llm.health_check()
    except Exception:
        pass

    try:
        from app.api.dependencies import _memory
        if _memory:
            _memory.get_stats()
            mem_ok = True
    except Exception:
        pass

    try:
        from app.api.dependencies import _template_service
        if _template_service:
            _template_service.list_names()
            db_ok = True
    except Exception:
        pass

    if not llm_ok:
        status = "degraded"

    return {
        "status": status,
        "services": {
            "llm": {"connected": llm_ok},
            "memory": {"available": mem_ok},
            "database": {"available": db_ok},
        },
    }


@router.get("/health/llm")
async def health_llm():
    try:
        from app.api.dependencies import _prompt_engine
        if _prompt_engine and _prompt_engine.llm:
            ok = await _prompt_engine.llm.health_check()
            return {
                "connected": ok,
                "model": _prompt_engine.llm.model,
                "base_url": _prompt_engine.llm.base_url,
            }
    except Exception:
        pass

    return {"connected": False, "model": None, "base_url": None}
