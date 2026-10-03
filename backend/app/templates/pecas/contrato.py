from app.templates.pecas.base_template import (
    criar_documento, adicionar_titulo, adicionar_qualificacao,
    adicionar_paragrafo, adicionar_aviso_legal, adicionar_local_data,
    adicionar_advogado, adicionar_rodape, salvar_docx
)


def gerar_contrato(analise: dict, processo: dict, output_path: str) -> str:
    doc = criar_documento("Minuta de Contrato")
    adicionar_rodape(doc)

    adicionar_titulo(doc, "CONTRATO DE PRESTAÇÃO DE SERVIÇOS / [NATUREZA DO CONTRATO]")

    partes = analise.get("partes", {})
    adicionar_qualificacao(doc, "CONTRATANTE", partes.get("autor", "[CONTRATANTE]"))
    adicionar_qualificacao(doc, "CONTRATADA", partes.get("reu", "[CONTRATADA]"))

    adicionar_paragrafo(doc, "As partes acima identificadas celebram o presente contrato mediante as cláusulas seguintes:")

    adicionar_paragrafo(doc, "CLÁUSULA PRIMEIRA - DO OBJETO", bold=True)
    adicionar_paragrafo(doc, f"O objeto do presente contrato é {analise.get('resumo_fatos', '[DESCREVER O OBJETO]')}. [REVISAR]")

    adicionar_paragrafo(doc, "CLÁUSULA SEGUNDA - DAS OBRIGAÇÕES DAS PARTES", bold=True)
    adicionar_paragrafo(doc, "São obrigações das partes: \n[LISTAR OBRIGAÇÕES. REVISAR]")

    adicionar_paragrafo(doc, "CLÁUSULA TERCEIRA - DO VALOR E FORMA DE PAGAMENTO", bold=True)
    adicionar_paragrafo(doc, "O valor do presente contrato é de R$ [VALOR] a ser pago conforme [CONDIÇÕES DE PAGAMENTO]. [REVISAR]")

    adicionar_paragrafo(doc, "CLÁUSULA QUARTA - DO PRAZO E VIGÊNCIA", bold=True)
    adicionar_paragrafo(doc, "O presente contrato vigorará por [PRAZO] meses/anos, a contar da data de assinatura. [REVISAR]")

    adicionar_paragrafo(doc, "CLÁUSULA QUINTA - DA RESCISÃO", bold=True)
    adicionar_paragrafo(doc, "Qualquer das partes poderá rescindir o presente contrato mediante comunicação prévia de [PRAZO] dias, nas hipóteses previstas em lei. [REVISAR]")

    adicionar_paragrafo(doc, "CLÁUSULA SEXTA - DAS PENALIDADES", bold=True)
    adicionar_paragrafo(doc, "O descumprimento de qualquer cláusula contratual sujeitará a parte infratora ao pagamento de multa de [PERCENTUAL]% sobre o valor do contrato. [REVISAR]")

    adicionar_paragrafo(doc, "CLÁUSULA SÉTIMA - DO FORO", bold=True)
    adicionar_paragrafo(doc, "Fica eleito o foro da Comarca de [CIDADE] para dirimir quaisquer controvérsias oriundas do presente contrato.")

    adicionar_local_data(doc)
    adicionar_paragrafo(doc, "")
    adicionar_paragrafo(doc, "_________________________", alinhar_direita=False)
    adicionar_paragrafo(doc, "CONTRATANTE", bold=True)

    adicionar_paragrafo(doc, "")
    adicionar_paragrafo(doc, "_________________________", alinhar_direita=False)
    adicionar_paragrafo(doc, "CONTRATADA", bold=True)

    adicionar_paragrafo(doc, "")
    adicionar_paragrafo(doc, "_________________________", alinhar_direita=False)
    adicionar_paragrafo(doc, "TESTEMUNHAS:\n1. _________________________\n2. _________________________")

    adicionar_aviso_legal(doc)

    return salvar_docx(doc, output_path)
