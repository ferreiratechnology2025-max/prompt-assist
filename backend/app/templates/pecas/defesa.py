from app.templates.pecas.base_template import (
    criar_documento, adicionar_titulo, adicionar_enderecamento,
    adicionar_qualificacao, adicionar_secao, adicionar_lista,
    adicionar_paragrafo, adicionar_aviso_legal, adicionar_local_data,
    adicionar_advogado, adicionar_rodape, salvar_docx
)


def gerar_defesa(analise: dict, processo: dict, output_path: str) -> str:
    doc = criar_documento("Defesa")
    adicionar_rodape(doc)

    adicionar_enderecamento(doc)

    partes = analise.get("partes", {})
    adicionar_qualificacao(doc, "Defendente", partes.get("reu", "[DEFENDENTE]"))
    adicionar_qualificacao(doc, "Defendido por", "[NOME DO ADVOGADO]")

    adicionar_titulo(doc, "DEFESA")

    adicionar_paragrafo(doc, f"{partes.get('reu', '[DEFENDENTE]')}, já qualificado(a) nos autos, por seu advogado, vem respeitosamente à presença de Vossa Excelência apresentar sua DEFESA nos autos da ação proposta por {partes.get('autor', 'PARTE AUTORA')}.")

    adicionar_secao(doc, "I - DOS FATOS", analise.get("resumo_fatos", "[Narrativa dos fatos sob a ótica do defendente]"))

    adicionar_secao(doc, "II - DAS PRELIMINARES", "[Preliminares de defesa processual, se houver. REVISAR]")

    adicionar_secao(doc, "III - DO MÉRITO", analise.get("fundamentacao_juridica", "[Argumentação de mérito da defesa]"))

    fracos = analise.get("pontos_fracos", [])
    if fracos:
        adicionar_lista(doc, "IV - DAS CONTRARRAZÕES", fracos)

    prazos = analise.get("prazos_importantes", [])
    if prazos:
        adicionar_lista(doc, "V - DOS PRAZOS PROCESSUAIS", prazos)

    adicionar_lista(doc, "VI - DOS PEDIDOS", [
        "O acolhimento das preliminares arguidas;",
        "No mérito, a total improcedência da ação;",
        "A condenação do Autor ao pagamento de custas processuais e honorários advocatícios;",
        "A produção de provas documental, testemunhal e pericial."
    ])

    adicionar_local_data(doc)
    adicionar_advogado(doc)
    adicionar_aviso_legal(doc)

    return salvar_docx(doc, output_path)
