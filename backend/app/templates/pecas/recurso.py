from app.templates.pecas.base_template import (
    criar_documento, adicionar_titulo, adicionar_enderecamento,
    adicionar_qualificacao, adicionar_secao, adicionar_lista,
    adicionar_paragrafo, adicionar_aviso_legal, adicionar_local_data,
    adicionar_advogado, adicionar_rodape, salvar_docx
)


def gerar_recurso(analise: dict, processo: dict, output_path: str) -> str:
    doc = criar_documento("Recurso")
    adicionar_rodape(doc)

    adicionar_enderecamento(doc, "COLENDO TRIBUNAL DE JUSTIÇA DO ESTADO DE ___")
    adicionar_paragrafo(doc, "RAZÕES DE RECURSO", bold=True)
    adicionar_paragrafo(doc, "")

    partes = analise.get("partes", {})
    adicionar_qualificacao(doc, "Recorrente", partes.get("reu", "[NOME DO RECORRENTE]"))
    adicionar_qualificacao(doc, "Recorrido", partes.get("autor", "[NOME DO RECORRIDO]"))

    adicionar_paragrafo(doc, "Processo nº [NÚMERO DO PROCESSO]")
    adicionar_paragrafo(doc, "Origem: ___ Vara Cível da Comarca de ___")

    adicionar_secao(doc, "I - DO CABIMENTO E TEMPESTIVIDADE", "O presente recurso é cabível e tempestivo, tendo em vista que a decisão recorrida [DESCREVER DECISÃO]. A interposição ocorre dentro do prazo legal de [PRAZO] dias.")

    adicionar_secao(doc, "II - DOS FATOS", analise.get("resumo_fatos", "[Breve relato dos fatos]"))

    adicionar_secao(doc, "III - DO DIREITO", analise.get("fundamentacao_juridica", "[Fundamentação recursal]"))

    fracos = analise.get("pontos_fracos", [])
    if fracos:
        adicionar_lista(doc, "IV - DOS FUNDAMENTOS PARA REFORMA DA DECISÃO", fracos)

    adicionar_lista(doc, "V - DOS PEDIDOS", [
        "O conhecimento e provimento do presente recurso;",
        "A reforma integral da decisão recorrida;",
        "A condenação do Recorrido ao pagamento de custas e honorários."
    ])

    adicionar_local_data(doc)
    adicionar_advogado(doc)
    adicionar_aviso_legal(doc)

    return salvar_docx(doc, output_path)
