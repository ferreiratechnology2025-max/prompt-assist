from app.templates.pecas.base_template import (
    criar_documento, adicionar_titulo, adicionar_secao, adicionar_lista,
    adicionar_paragrafo, adicionar_aviso_legal, adicionar_local_data,
    adicionar_advogado, adicionar_rodape, salvar_docx
)


def gerar_analise_estrategica(analise: dict, processo: dict, output_path: str) -> str:
    doc = criar_documento("Análise Estratégica")
    adicionar_rodape(doc)

    adicionar_titulo(doc, "ANÁLISE ESTRATÉGICA DO CASO")

    partes = analise.get("partes", {})
    adicionar_paragrafo(doc, f"Cliente: {partes.get('autor', '[CLIENTE]')}")
    adicionar_paragrafo(doc, f"Parte Contrária: {partes.get('reu', '[PARTE CONTRÁRIA]')}")
    adicionar_paragrafo(doc, f"Data da análise: [DATA]")

    adicionar_secao(doc, "1. RESUMO DO CASO", analise.get("resumo_fatos", "[Resumo executivo do caso]"))

    fundamentacao = analise.get("fundamentacao_juridica", "")
    if fundamentacao:
        adicionar_secao(doc, "2. FUNDAMENTAÇÃO JURÍDICA", fundamentacao)

    fracos = analise.get("pontos_fracos", [])
    if fracos:
        adicionar_lista(doc, "3. PONTOS FRACOS / RISCOS", fracos)

    prazos = analise.get("prazos_importantes", [])
    if prazos:
        adicionar_lista(doc, "4. PRAZOS CRÍTICOS", prazos)

    pedidos = analise.get("pedidos_autor", [])
    if pedidos:
        adicionar_lista(doc, "5. PEDIDOS / PRETENSÕES", pedidos)

    adicionar_secao(doc, "6. ANÁLISE DE PROGNOSE", "[Análise de probabilidade de êxito com base nos elementos disponíveis. REVISAR]")

    adicionar_secao(doc, "7. RECOMENDAÇÕES ESTRATÉGICAS", "[Recomendações sobre a melhor estratégia processual. REVISAR]")

    adicionar_paragrafo(doc, "8. PRÓXIMOS PASSOS", bold=True)
    adicionar_paragrafo(doc, "[Listar os próximos passos recomendados:\n1. [Ação 1]\n2. [Ação 2]\n3. [Ação 3]\n]")

    adicionar_local_data(doc)
    adicionar_advogado(doc, "[NOME DO ADVOGADO RESPONSÁVEL]")
    adicionar_aviso_legal(doc)

    return salvar_docx(doc, output_path)
