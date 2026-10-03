from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.database import get_db
from app.models import Processo
from app.schemas import ProcessoCreate, ProcessoResponse

router = APIRouter(prefix="/api/processos", tags=["processos"])


@router.post("/upload", response_model=ProcessoResponse)
def upload_processo(payload: ProcessoCreate, db: Session = Depends(get_db)):
    processo = Processo(nome=payload.nome, cliente=payload.cliente)
    db.add(processo)
    db.commit()
    db.refresh(processo)
    return processo


@router.get("", response_model=list[ProcessoResponse])
def listar_processos(db: Session = Depends(get_db)):
    return db.query(Processo).all()
