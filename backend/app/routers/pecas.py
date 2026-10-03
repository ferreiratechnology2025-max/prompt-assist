import os
import json
import logging
from fastapi import APIRouter, HTTPException, Depends
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session
from app.database import get_db
from app.models import Analise, Processo, PecaGerada
from app.schemas import PecaGerarRequest
from app.services.geracao_service import listar_tipos, gerar_peca as service_gerar_peca

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/pecas", tags=["pecas"])


@router.get("/tipos")
def listar_tipos_pecas():
    return listar_tipos()


@router.post("/gerar")
def gerar_peca_endpoint(payload: PecaGerarRequest, db: Session = Depends(get_db)):
    analise = db.query(Analise).filter(Analise.id == payload.analise_id).first()
    if not analise:
        raise HTTPException(status_code=404, detail="Análise não encontrada")

    processo = None
    if analise.processo_id:
        processo = db.query(Processo).filter(Processo.id == analise.processo_id).first()

    try:
        resultado = service_gerar_peca(
            tipo=payload.tipo,
            analise=analise.analise_json,
            processo=processo.__dict__ if processo else {},
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

    peca_db = PecaGerada(
        analise_id=analise.id,
        tipo=payload.tipo,
        arquivo_path=resultado["arquivo_path"],
        tamanho_bytes=resultado["tamanho_bytes"],
    )
    db.add(peca_db)
    db.commit()
    db.refresh(peca_db)

    filename = resultado["filename"]

    return {
        "download_url": f"/api/pecas/download/{filename}",
        "mensagem": f"Peça '{payload.tipo}' gerada com sucesso",
        "tamanho_bytes": resultado["tamanho_bytes"],
        "tipo": payload.tipo,
    }


@router.get("/download/{filename}")
def download_peca(filename: str):
    from app.services.geracao_service import PECAS_DIR

    caminho = os.path.join(PECAS_DIR, filename)
    if not os.path.exists(caminho):
        raise HTTPException(status_code=404, detail="Arquivo não encontrado")

    return FileResponse(
        path=caminho,
        filename=filename,
        media_type="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
    )


@router.get("/historico/{analise_id}")
def historico_pecas(analise_id: int, db: Session = Depends(get_db)):
    pecas = (
        db.query(PecaGerada)
        .filter(PecaGerada.analise_id == analise_id)
        .order_by(PecaGerada.data_geracao.desc())
        .all()
    )
    return [
        {
            "id": p.id,
            "tipo": p.tipo,
            "data_geracao": p.data_geracao.isoformat(),
            "tamanho_bytes": p.tamanho_bytes,
            "download_url": f"/api/pecas/download/{os.path.basename(p.arquivo_path)}",
        }
        for p in pecas
    ]
