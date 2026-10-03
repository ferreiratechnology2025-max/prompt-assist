from app.templates.pecas.base_template import (
    criar_documento, adicionar_titulo, adicionar_enderecamento,
    adicionar_secao, adicionar_lista, adicionar_paragrafo,
    adicionar_aviso_legal, adicionar_local_data, adicionar_advogado,
    adicionar_rodape, salvar_docx
)


def gerar_memoriais(analise: dict, processo: dict, output_path: str) -> str:
    doc = criar_documento("Memoriais")
    adicionar_rodape(doc)

    adicionar_enderecamento(doc)

    adicionar_titulo(doc, "MEMORIAIS")

    partes = analise.get("partes", {})
    adicionar_paragrafo(doc, f"Autor: {partes.get('autor', '[AUTOR]')}")
    adicionar_paragrafo(doc, f"Réu: {partes.get('reu', '[RÉU]')}")
    adicionar_paragrafo(doc, "Processo nº [NÚMERO DO PROCESSO]")

    adicionar_secao(doc, "I - SÍNTESE PROCESSUAL", "[Histórico do andamento processual]")

    adicionar_secao(doc, "II - DOS FATOS", analise.get("resumo_fatos", "[Resumo dos fatos]"))

    adicionar_secao(doc, "III - DO DIREITO", analise.get("fundamentacao_juridica", "[Argumentação jurídica]"))

    adicionar_lista(doc, "IV - DOS PEDIDOS", [
        "O julgamento de procedência dos pedidos iniciais;",
        "A condenação da parte contrária ao pagamento de custas e honorários."
    ])

    adicionar_local_data(doc)
    adicionar_advogado(doc)
    adicionar_aviso_legal(doc)

    return salvar_docx(doc, output_path)
