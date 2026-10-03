import hashlib
import json
import logging
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from app.models import Analise

logger = logging.getLogger(__name__)

CACHE_DIAS = 30


def calcular_hash(conteudo: bytes) -> str:
    return hashlib.sha256(conteudo).hexdigest()


def buscar_cache(hash_arquivo: str, db: Session) -> dict | None:
    analise = (
        db.query(Analise)
        .filter(Analise.hash_arquivo == hash_arquivo)
        .order_by(Analise.data_analise.desc())
        .first()
    )
    if not analise:
        return None

    limite = datetime.utcnow() - timedelta(days=CACHE_DIAS)
    if analise.data_analise.replace(tzinfo=None) < limite:
        logger.info("Cache expirado para hash %s", hash_arquivo)
        return None

    logger.info("Cache HIT para hash %s (análise %d)", hash_arquivo, analise.id)
    return {
        "analise": json.loads(analise.analise_json),
        "analise_id": analise.id,
        "processo_id": analise.processo_id,
        "tempo_segundos": 0.01,
        "cache_hit": True,
    }
