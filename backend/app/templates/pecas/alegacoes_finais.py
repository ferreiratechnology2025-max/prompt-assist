from app.templates.pecas.base_template import (
    criar_documento, adicionar_titulo, adicionar_enderecamento,
    adicionar_secao, adicionar_lista, adicionar_paragrafo,
    adicionar_aviso_legal, adicionar_local_data, adicionar_advogado,
    adicionar_rodape, salvar_docx
)


def gerar_alegacoes_finais(analise: dict, processo: dict, output_path: str) -> str:
    doc = criar_documento("Alegações Finais")
    adicionar_rodape(doc)

    adicionar_enderecamento(doc)

    adicionar_titulo(doc, "ALEGAÇÕES FINAIS")

    partes = analise.get("partes", {})
    adicionar_paragrafo(doc, f"Autor: {partes.get('autor', '[AUTOR]')}")
    adicionar_paragrafo(doc, f"Réu: {partes.get('reu', '[RÉU]')}")
    adicionar_paragrafo(doc, "Processo nº [NÚMERO DO PROCESSO]")

    adicionar_paragrafo(doc, "MM. Juiz, conforme despacho de fls. [FOLHAS], a parte requerente/apresenta suas alegações finais nos seguintes termos:")

    adicionar_secao(doc, "I - SÍNTESE DA INSTRUÇÃO", "[Breve resumo das provas produzidas em audiência / nos autos]")

    adicionar_secao(doc, "II - DOS FATOS E DO DIREITO", analise.get("fundamentacao_juridica", "[Argumentação final]"))

    fracos = analise.get("pontos_fracos", [])
    if fracos:
        adicionar_lista(doc, "III - DOS PONTOS RELEVANTES", fracos)

    adicionar_lista(doc, "IV - DOS PEDIDOS", [
        "O julgamento de total procedência dos pedidos;",
        "A condenação da parte adversa nos ônus da sucumbência."
    ])

    adicionar_local_data(doc)
    adicionar_advogado(doc)
    adicionar_aviso_legal(doc)

    return salvar_docx(doc, output_path)
