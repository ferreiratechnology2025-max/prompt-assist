import json
import logging

logger = logging.getLogger(__name__)

CAMPOS_OBRIGATORIOS = ["partes", "resumo_fatos", "pedidos_autor", "fundamentacao_juridica"]


def validar_analise(analise_json: str | dict) -> dict:
    if isinstance(analise_json, str):
        try:
            dados = json.loads(analise_json)
        except json.JSONDecodeError:
            return {"valido": False, "erro": "JSON inválido", "dados": {}}
    else:
        dados = analise_json

    erros = []
    avisos = []

    for campo in CAMPOS_OBRIGATORIOS:
        if campo not in dados or not dados[campo]:
            erros.append(f"Campo obrigatório ausente: {campo}")
            dados[campo] = _valor_padrao(campo)

    if "partes" in dados and isinstance(dados["partes"], dict):
        if not dados["partes"].get("autor") or dados["partes"]["autor"] == "Não informado":
            avisos.append("Autor não identificado na análise")
        if not dados["partes"].get("reu") or dados["partes"]["reu"] == "Não informado":
            avisos.append("Réu não identificado na análise")

    if "pedidos_autor" in dados and isinstance(dados["pedidos_autor"], list):
        if len(dados["pedidos_autor"]) == 0:
            erros.append("Nenhum pedido extraído")

    resultado = {"valido": len(erros) == 0, "dados": dados}
    if erros:
        resultado["erros"] = erros
    if avisos:
        resultado["avisos"] = avisos

    return resultado


def _valor_padrao(campo: str):
    padroes = {
        "partes": {"autor": "Não identificado", "reu": "Não identificado"},
        "resumo_fatos": "Resumo dos fatos não disponível. REVISAR.",
        "pedidos_autor": ["Pedido não extraído automaticamente. REVISAR."],
        "fundamentacao_juridica": "Fundamentação jurídica não extraída. REVISAR.",
    }
    return padroes.get(campo, "")
