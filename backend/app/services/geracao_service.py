import os
import json
import uuid
import logging
from datetime import datetime

from app.templates.pecas import (
    gerar_contestacao,
    gerar_peticao_inicial,
    gerar_recurso,
    gerar_parecer,
    gerar_memoriais,
    gerar_alegacoes_finais,
    gerar_notificacao,
    gerar_contrato,
    gerar_defesa,
    gerar_replica,
    gerar_analise_estrategica,
)

logger = logging.getLogger(__name__)

PECAS_DIR = os.path.abspath(
    os.path.join(os.path.dirname(__file__), "..", "..", "..", "storage", "pecas")
)
os.makedirs(PECAS_DIR, exist_ok=True)

TIPOS_PECA = {
    "contestacao": {"nome": "Contestação", "funcao": gerar_contestacao},
    "peticao_inicial": {"nome": "Petição Inicial", "funcao": gerar_peticao_inicial},
    "recurso": {"nome": "Recurso", "funcao": gerar_recurso},
    "parecer": {"nome": "Parecer Jurídico", "funcao": gerar_parecer},
    "memoriais": {"nome": "Memoriais", "funcao": gerar_memoriais},
    "alegacoes_finais": {"nome": "Alegações Finais", "funcao": gerar_alegacoes_finais},
    "notificacao": {"nome": "Notificação Extrajudicial", "funcao": gerar_notificacao},
    "contrato": {"nome": "Minuta de Contrato", "funcao": gerar_contrato},
    "defesa": {"nome": "Defesa", "funcao": gerar_defesa},
    "replica": {"nome": "Réplica", "funcao": gerar_replica},
    "analise_estrategica": {"nome": "Análise Estratégica", "funcao": gerar_analise_estrategica},
}


def listar_tipos() -> list:
    return [
        {"id": k, "nome": v["nome"]}
        for k, v in TIPOS_PECA.items()
    ]


def gerar_peca(tipo: str, analise: dict, processo: dict) -> dict:
    if tipo not in TIPOS_PECA:
        raise ValueError(f"Tipo de peça inválido: {tipo}")

    info = TIPOS_PECA[tipo]
    analise_parsed = analise
    if isinstance(analise_parsed, str):
        analise_parsed = json.loads(analise_parsed)

    filename = f"{uuid.uuid4().hex}_{tipo}.docx"
    output_path = os.path.join(PECAS_DIR, filename)

    logger.info("Gerando peça '%s'", tipo)
    caminho_arquivo = info["funcao"](analise_parsed, processo, output_path)

    tamanho = os.path.getsize(caminho_arquivo)
    logger.info("Peça gerada: %s (%d bytes)", caminho_arquivo, tamanho)

    return {
        "arquivo_path": caminho_arquivo,
        "filename": filename,
        "tamanho_bytes": tamanho,
        "tipo": tipo,
    }
