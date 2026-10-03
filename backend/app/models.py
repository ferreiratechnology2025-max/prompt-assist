from sqlalchemy import Column, Integer, String, Text, DateTime, Float, ForeignKey, func
from app.database import Base


class Processo(Base):
    __tablename__ = "processos"

    id = Column(Integer, primary_key=True, index=True)
    nome = Column(String, nullable=False)
    cliente = Column(String, nullable=False)
    data_criacao = Column(DateTime, server_default=func.now())
    status = Column(String, default="pendente")


class Analise(Base):
    __tablename__ = "analises"

    id = Column(Integer, primary_key=True, index=True)
    processo_id = Column(Integer, ForeignKey("processos.id"), nullable=True)
    nome_arquivo = Column(String)
    hash_arquivo = Column(String, index=True, nullable=True)
    texto_extraido = Column(Text)
    analise_json = Column(Text)
    alertas_json = Column(Text, nullable=True)
    data_analise = Column(DateTime, server_default=func.now())
    tempo_processamento = Column(Float)


class PecaGerada(Base):
    __tablename__ = "pecas_geradas"

    id = Column(Integer, primary_key=True, index=True)
    analise_id = Column(Integer, ForeignKey("analises.id"))
    tipo = Column(String(50))
    arquivo_path = Column(String(500))
    data_geracao = Column(DateTime, server_default=func.now())
    tamanho_bytes = Column(Integer)
