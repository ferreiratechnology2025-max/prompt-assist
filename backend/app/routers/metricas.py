import json
import logging
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import func
from app.database import get_db
from app.models import Analise, PecaGerada, Processo

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/metricas", tags=["metricas"])


@router.get("/dashboard")
def dashboard(db: Session = Depends(get_db)):
    total_pecas = db.query(PecaGerada).count()
    total_analises = db.query(Analise).count()
    total_processos = db.query(Processo).count()

    tempo_medio = db.query(func.avg(Analise.tempo_processamento)).scalar() or 0
    tempo_medio = round(tempo_medio, 1)

    total_cache = db.query(Analise).filter(
        Analise.tempo_processamento < 1.0
    ).count()
    cache_hit_rate = round(total_cache / max(total_analises, 1), 2)

    pecas_por_tipo_raw = (
        db.query(PecaGerada.tipo, func.count(PecaGerada.id))
        .group_by(PecaGerada.tipo)
        .all()
    )
    pecas_por_tipo = {t: c for t, c in pecas_por_tipo_raw}

    economia_horas = round(
        (total_analises * 0.75) + (total_pecas * 0.5), 1
    )

    return {
        "total_pecas_geradas": total_pecas,
        "total_analises": total_analises,
        "total_processos": total_processos,
        "tempo_medio_analise_segundos": tempo_medio,
        "cache_hit_rate": cache_hit_rate,
        "pecas_por_tipo": pecas_por_tipo,
        "total_arquivos_processados": total_analises,
        "economia_tempo_estimada_horas": economia_horas,
    }
