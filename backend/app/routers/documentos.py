import os
import json
import uuid
import logging
from fastapi import APIRouter, UploadFile, File, Form, HTTPException, Depends
from sqlalchemy.orm import Session
from app.database import get_db
from app.models import Processo, Analise
from app.services.analyzer import process_document
from app.services.cache_service import calcular_hash, buscar_cache

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/documentos", tags=["documentos"])

UPLOAD_DIR = os.path.abspath(
    os.path.join(os.path.dirname(__file__), "..", "..", "..", "storage", "uploads")
)
os.makedirs(UPLOAD_DIR, exist_ok=True)

ALLOWED_EXTENSIONS = {".pdf", ".docx", ".png", ".jpg", ".jpeg"}


@router.post("/upload")
async def upload_documento(
    arquivo: UploadFile = File(...),
    processo_id: int = Form(None),
    db: Session = Depends(get_db),
):
    ext = os.path.splitext(arquivo.filename or "")[1].lower()
    if ext not in ALLOWED_EXTENSIONS:
        raise HTTPException(
            status_code=400,
            detail=f"Formato não permitido: {ext}. Use: {', '.join(ALLOWED_EXTENSIONS)}",
        )

    conteudo = await arquivo.read()
    hash_arquivo = calcular_hash(conteudo)

    cache = buscar_cache(hash_arquivo, db)
    if cache:
        return cache

    nome_arquivo = f"{uuid.uuid4().hex}{ext}"
    caminho = os.path.join(UPLOAD_DIR, nome_arquivo)

    with open(caminho, "wb") as f:
        f.write(conteudo)

    logger.info("Arquivo salvo: %s (%d bytes)", caminho, len(conteudo))

    try:
        resultado = process_document(caminho)
    except Exception as e:
        logger.exception("Erro ao processar documento")
        raise HTTPException(status_code=500, detail=f"Erro no processamento: {str(e)}")

    if not processo_id:
        nome_processo = os.path.splitext(arquivo.filename or "documento")[0]
        processo = Processo(
            nome=nome_processo,
            cliente="Análise Automática",
            status="analisado",
        )
        db.add(processo)
        db.commit()
        db.refresh(processo)
        processo_id = processo.id

    analise = Analise(
        processo_id=processo_id,
        nome_arquivo=arquivo.filename,
        hash_arquivo=hash_arquivo,
        texto_extraido=resultado["texto_extraido"],
        analise_json=json.dumps(resultado["analise"], ensure_ascii=False),
        alertas_json=json.dumps(resultado.get("alertas", []), ensure_ascii=False),
        tempo_processamento=resultado["tempo_segundos"],
    )
    db.add(analise)
    db.commit()
    db.refresh(analise)

    if processo_id:
        db.query(Processo).filter(Processo.id == processo_id).update(
            {"status": "analisado"}
        )
        db.commit()

    return {
        "analise": resultado["analise"],
        "alertas": resultado.get("alertas", []),
        "processo_id": processo_id,
        "analise_id": analise.id,
        "tempo_segundos": resultado["tempo_segundos"],
    }
