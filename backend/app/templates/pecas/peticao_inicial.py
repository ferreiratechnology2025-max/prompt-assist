from app.templates.pecas.base_template import (
    criar_documento, adicionar_titulo, adicionar_enderecamento,
    adicionar_qualificacao, adicionar_secao, adicionar_lista,
    adicionar_paragrafo, adicionar_aviso_legal, adicionar_local_data,
    adicionar_advogado, adicionar_rodape, salvar_docx
)


def gerar_peticao_inicial(analise: dict, processo: dict, output_path: str) -> str:
    doc = criar_documento("Petição Inicial")
    adicionar_rodape(doc)

    adicionar_enderecamento(doc)

    partes = analise.get("partes", {})
    adicionar_qualificacao(doc, "Autor", partes.get("autor", "[NOME DO AUTOR]"))
    adicionar_qualificacao(doc, "Réu", partes.get("reu", "[NOME DO RÉU]"))

    adicionar_paragrafo(doc, f"{partes.get('autor', '[AUTOR]')}, já qualificado(a), vem respeitosamente à presença de Vossa Excelência propor a presente")

    adicionar_titulo(doc, "AÇÃO DE INDENIZAÇÃO POR DANOS MORAIS")
    adicionar_paragrafo(doc, "em face de " + f"{partes.get('reu', '[RÉU]')}", bold=False)

    adicionar_paragrafo(doc, "pelos fatos e fundamentos que passa a expor.")

    adicionar_secao(doc, "I - DOS FATOS", analise.get("resumo_fatos", "[Descrever os fatos]"))

    adicionar_secao(doc, "II - DO DIREITO", analise.get("fundamentacao_juridica", "[Fundamentação jurídica]"))

    adicionar_lista(doc, "III - DOS PEDIDOS", analise.get("pedidos_autor", ["[Pedido 1]", "[Pedido 2]"]))

    adicionar_secao(doc, "IV - DAS PROVAS", "Requer a produção de provas documental, testemunhal e demais provas admitidas em direito.")

    adicionar_paragrafo(doc, "Dá-se à causa o valor de R$ [VALOR DA CAUSA].")

    adicionar_local_data(doc)
    adicionar_advogado(doc)
    adicionar_aviso_legal(doc)

    return salvar_docx(doc, output_path)
