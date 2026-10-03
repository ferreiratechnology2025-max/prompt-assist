import logging
from typing import List

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from fastapi import Depends

from app.api.dependencies import get_memory, verify_admin_token

logger = logging.getLogger(__name__)
router = APIRouter()


class MemoryEntryModel(BaseModel):
    id: int
    template_name: str
    domain: str
    has_constraints: bool
    has_examples: bool
    goal_length_category: str
    best_score: float
    usage_count: int
    last_used: str
    created_at: str
    updated_at: str


class MemoryStatsModel(BaseModel):
    total_entries: int
    average_score: float
    improvements_logged: int
    epsilon: float


@router.get("/stats", response_model=MemoryStatsModel)
async def memory_stats():
    memory = get_memory()
    stats = memory.get_stats()
    return MemoryStatsModel(**stats)


@router.get("/entries", response_model=List[MemoryEntryModel])
async def memory_entries(admin: bool = Depends(verify_admin_token)):
    memory = get_memory()
    import sqlite3

    conn = sqlite3.connect(str(memory.db_path))
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    cursor.execute(
        """
        SELECT id, template_name, domain, has_constraints, has_examples,
               goal_length_category, best_score, usage_count,
               last_used, created_at, updated_at
        FROM memory_associations
        ORDER BY best_score DESC
    """
    )
    rows = cursor.fetchall()
    conn.close()

    entries = []
    for row in rows:
        entries.append(
            MemoryEntryModel(
                id=row["id"],
                template_name=row["template_name"],
                domain=row["domain"] or "",
                has_constraints=bool(row["has_constraints"]),
                has_examples=bool(row["has_examples"]),
                goal_length_category=row["goal_length_category"],
                best_score=row["best_score"],
                usage_count=row["usage_count"],
                last_used=row["last_used"] or "",
                created_at=row["created_at"] or "",
                updated_at=row["updated_at"] or "",
            )
        )
    return entries


@router.delete("/entries/{entry_id}")
async def delete_memory_entry(entry_id: int, admin: bool = Depends(verify_admin_token)):
    memory = get_memory()
    import sqlite3

    conn = sqlite3.connect(str(memory.db_path))
    cursor = conn.cursor()
    cursor.execute(
        "DELETE FROM memory_associations WHERE id = ?", (entry_id,)
    )
    deleted = cursor.rowcount
    conn.commit()
    conn.close()

    if deleted == 0:
        raise HTTPException(
            status_code=404,
            detail=f"Entrada de memoria {entry_id} nao encontrada",
        )

    return {"status": "deleted", "id": entry_id}


@router.put("/epsilon/{value}")
async def set_epsilon(value: float, admin: bool = Depends(verify_admin_token)):
    if not 0.0 <= value <= 1.0:
        raise HTTPException(
            status_code=400,
            detail="Epsilon deve estar entre 0.0 e 1.0",
        )
    memory = get_memory()
    memory.epsilon = value
    return {"status": "ok", "epsilon": value}
