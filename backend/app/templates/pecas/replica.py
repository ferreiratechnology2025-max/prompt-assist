from app.templates.pecas.base_template import (
    criar_documento, adicionar_titulo, adicionar_enderecamento,
    adicionar_qualificacao, adicionar_secao, adicionar_lista,
    adicionar_paragrafo, adicionar_aviso_legal, adicionar_local_data,
    adicionar_advogado, adicionar_rodape, salvar_docx
)


def gerar_replica(analise: dict, processo: dict, output_path: str) -> str:
    doc = criar_documento("Réplica")
    adicionar_rodape(doc)

    adicionar_enderecamento(doc)

    partes = analise.get("partes", {})
    adicionar_qualificacao(doc, "Autor", partes.get("autor", "[AUTOR]"))
    adicionar_qualificacao(doc, "Réu", partes.get("reu", "[RÉU]"))

    adicionar_titulo(doc, "RÉPLICA")

    adicionar_paragrafo(doc, f"{partes.get('autor', '[AUTOR]')}, já qualificado(a) nos autos, vem respeitosamente à presença de Vossa Excelência apresentar sua RÉPLICA à contestação apresentada pelo Réu.")

    adicionar_secao(doc, "I - DA CONTESTAÇÃO APRESENTADA", "[Breve resumo dos argumentos da contestação]")

    adicionar_secao(doc, "II - DA REJEIÇÃO DAS PRELIMINARES", "[Argumentos para rejeição das preliminares suscitadas. REVISAR]")

    adicionar_secao(doc, "III - DA RATIFICAÇÃO DA INICIAL", "O Autor ratifica integralmente os termos de sua petição inicial, reiterando todos os fatos, fundamentos jurídicos e pedidos ali formulados.")

    fracos = analise.get("pontos_fracos", [])
    if fracos:
        adicionar_lista(doc, "IV - DAS CONTRARRAZÕES À DEFESA", [
            "Os argumentos do Réu não merecem acolhimento;",
            "A prova dos autos demonstra a procedência do pedido;",
            "A jurisprudência consolidada é favorável ao Autor."
        ])

    adicionar_lista(doc, "V - DOS PEDIDOS", [
        "A rejeição integral da contestação apresentada pelo Réu;",
        "O julgamento de total procedência dos pedidos iniciais;",
        "A condenação do Réu nos ônus da sucumbência."
    ])

    adicionar_local_data(doc)
    adicionar_advogado(doc)
    adicionar_aviso_legal(doc)

    return salvar_docx(doc, output_path)
