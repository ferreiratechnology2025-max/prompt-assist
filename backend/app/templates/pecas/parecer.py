from app.templates.pecas.base_template import (
    criar_documento, adicionar_titulo, adicionar_secao, adicionar_paragrafo,
    adicionar_aviso_legal, adicionar_local_data, adicionar_advogado,
    adicionar_rodape, salvar_docx
)


def gerar_parecer(analise: dict, processo: dict, output_path: str) -> str:
    doc = criar_documento("Parecer Jurídico")
    adicionar_rodape(doc)

    adicionar_titulo(doc, "PARECER JURÍDICO")

    adicionar_paragrafo(doc, "Parecer nº [NÚMERO/ANO]")
    adicionar_paragrafo(doc, "Interessado: " + str(analise.get("partes", {}).get("autor", "[INTERESSADO]")))
    adicionar_paragrafo(doc, "Assunto: [ASSUNTO DO PARECER]")

    adicionar_secao(doc, "I - RELATÓRIO", analise.get("resumo_fatos", "[Relatório dos fatos e documentos analisados]"))

    adicionar_secao(doc, "II - FUNDAMENTAÇÃO", analise.get("fundamentacao_juridica", "[Análise jurídica do caso]"))

    fracos = analise.get("pontos_fracos", [])
    if fracos:
        adicionar_secao(doc, "III - RISCOS IDENTIFICADOS", "\n".join([f"- {p}" for p in fracos]))

    adicionar_secao(doc, "IV - CONCLUSÃO", "[Parecer conclusivo sobre a viabilidade jurídica. REVISAR]")

    adicionar_local_data(doc)
    adicionar_advogado(doc, "[NOME DO PARECERISTA]")
    adicionar_aviso_legal(doc)

    return salvar_docx(doc, output_path)
