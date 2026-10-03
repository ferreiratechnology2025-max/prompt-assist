from pydantic import BaseModel
from datetime import datetime
from typing import Optional


class ProcessoBase(BaseModel):
    nome: str
    cliente: str


class ProcessoCreate(ProcessoBase):
    pass


class ProcessoResponse(ProcessoBase):
    id: int
    data_criacao: datetime
    status: str

    model_config = {"from_attributes": True}


class AnaliseResponse(BaseModel):
    id: int
    processo_id: Optional[int] = None
    nome_arquivo: Optional[str] = None
    analise_json: str
    data_analise: datetime
    tempo_processamento: Optional[float] = None

    model_config = {"from_attributes": True}


class DocumentoUploadResponse(BaseModel):
    analise: dict
    processo_id: Optional[int] = None
    analise_id: int
    tempo_segundos: float


class PecaGerarRequest(BaseModel):
    analise_id: int
    tipo: str


class PecaGerarResponse(BaseModel):
    download_url: str
    mensagem: str
    tamanho_bytes: int
    tipo: str


class TipoPecaResponse(BaseModel):
    id: str
    nome: str
