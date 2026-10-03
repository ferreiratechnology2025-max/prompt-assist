import time
import logging
from app.services.ocr_service import extract_text
from app.services.llm_service import analyze_with_ollama
from app.services.alert_service import gerar_alertas
from app.services.validator import validar_analise

logger = logging.getLogger(__name__)


def process_document(file_path: str) -> dict:
    inicio = time.time()

    logger.info("Iniciando processamento de: %s", file_path)

    texto_extraido = extract_text(file_path)
    logger.info(
        "Texto extraído: %d caracteres", len(texto_extraido)
    )

    analise = analyze_with_ollama(texto_extraido)
    validacao = validar_analise(analise)
    alertas = gerar_alertas(texto_extraido, validacao.get("dados", analise))

    tempo_decorrido = round(time.time() - inicio, 2)
    logger.info(
        "Processamento concluído em %.2f segundos", tempo_decorrido
    )

    return {
        "texto_extraido": texto_extraido,
        "analise": analise,
        "alertas": alertas,
        "validacao": validacao,
        "tempo_segundos": tempo_decorrido,
    }
