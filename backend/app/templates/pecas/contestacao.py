from app.templates.pecas.base_template import (
    criar_documento, adicionar_titulo, adicionar_enderecamento,
    adicionar_qualificacao, adicionar_secao, adicionar_lista,
    adicionar_paragrafo, adicionar_aviso_legal, adicionar_local_data,
    adicionar_advogado, adicionar_rodape, salvar_docx
)


def gerar_contestacao(analise: dict, processo: dict, output_path: str) -> str:
    doc = criar_documento("Contestação")
    adicionar_rodape(doc)

    adicionar_enderecamento(doc)

    partes = analise.get("partes", {})
    adicionar_qualificacao(doc, "Réu", partes.get("reu", "[NOME DO RÉU]"))
    adicionar_qualificacao(doc, "Autor", partes.get("autor", "[NOME DO AUTOR]"))

    adicionar_paragrafo(doc, f"{partes.get('reu', '[RÉU]')}, já qualificado(a), por seu advogado que esta subscreve, vem respeitosamente à presença de Vossa Excelência apresentar")

    adicionar_titulo(doc, "CONTESTAÇÃO")
    adicionar_paragrafo(doc, f"nos autos da Ação proposta por {partes.get('autor', '[AUTOR]')}, pelos fatos e fundamentos que passa a expor.")

    adicionar_secao(doc, "I - SÍNTESE DA INICIAL", analise.get("resumo_fatos", "[Resumo da inicial]"))

    adicionar_secao(doc, "II - PRELIMINARES", "[Arguição de preliminares, se houver. REVISAR]")

    adicionar_secao(doc, "III - DO MÉRITO", analise.get("fundamentacao_juridica", "[Fundamentação de mérito]"))

    fracos = analise.get("pontos_fracos", [])
    if fracos:
        adicionar_lista(doc, "IV - DOS PONTOS CONTESTADOS", fracos)

    adicionar_lista(doc, "V - DOS PEDIDOS", [
        "Seja julgada IMPROCEDENTE a ação proposta pelo Autor;",
        "A condenação do Autor ao pagamento de custas processuais e honorários advocatícios;",
        "A produção de provas documental, testemunhal e demais provas admitidas em direito."
    ])

    adicionar_paragrafo(doc, "Dá-se à causa o valor de R$ [VALOR DA CAUSA].")

    adicionar_local_data(doc)
    adicionar_advogado(doc)
    adicionar_aviso_legal(doc)

    return salvar_docx(doc, output_path)
