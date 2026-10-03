from app.templates.pecas.base_template import (
    criar_documento, adicionar_titulo, adicionar_paragrafo,
    adicionar_secao, adicionar_aviso_legal, adicionar_local_data,
    adicionar_advogado, adicionar_rodape, salvar_docx
)


def gerar_notificacao(analise: dict, processo: dict, output_path: str) -> str:
    doc = criar_documento("Notificação Extrajudicial")
    adicionar_rodape(doc)

    adicionar_titulo(doc, "NOTIFICAÇÃO EXTRAJUDICIAL")

    partes = analise.get("partes", {})
    adicionar_paragrafo(doc, f"Notificante: {partes.get('autor', '[NOTIFICANTE]')}")
    adicionar_paragrafo(doc, f"Notificado: {partes.get('reu', '[NOTIFICADO]')}")
    adicionar_paragrafo(doc, f"Endereço: [ENDEREÇO DO NOTIFICADO]")
    adicionar_paragrafo(doc, "")

    adicionar_paragrafo(doc, "Prezado(a) Senhor(a),")

    adicionar_secao(doc, "REF: [ASSUNTO DA NOTIFICAÇÃO]", analise.get("resumo_fatos", "[Descrição do objeto da notificação]"))

    adicionar_paragrafo(doc, "Sirvo-me da presente para, na forma do artigo [ARTIGO] do Código Civil, NOTIFICAR Vossa Senhoria acerca do seguinte:")

    fracos = analise.get("pontos_fracos", [])
    if fracos:
        adicionar_secao(doc, "DAS IRREGULARIDADES", "\n".join([f"{i+1}. {p}" for i, p in enumerate(fracos)]))

    adicionar_secao(doc, "DO PRAZO", "Concede-se o prazo de [PRAZO] dias úteis para regularização da situação, sob pena de adoção das medidas judiciais cabíveis.")

    adicionar_paragrafo(doc, "A presente notificação extrajudicial tem caráter interruptivo de prazo prescricional, nos termos do art. 202, VI, do Código Civil.")

    adicionar_local_data(doc)
    adicionar_advogado(doc)
    adicionar_aviso_legal(doc)

    return salvar_docx(doc, output_path)
