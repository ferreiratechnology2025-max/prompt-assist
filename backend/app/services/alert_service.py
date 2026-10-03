import re
import logging
from datetime import datetime, date

logger = logging.getLogger(__name__)


def gerar_alertas(texto: str, analise: dict) -> list:
    alertas = []
    hoje = date.today()

    alertas.extend(_detectar_prazos_vencidos(texto, hoje))
    alertas.extend(_detectar_inconsistencias(texto, analise))
    alertas.extend(_detectar_valores_desproporcionais(texto, analise))

    return alertas


def _detectar_prazos_vencidos(texto: str, hoje: date) -> list:
    alertas = []
    padroes_data = [
        r"(\d{1,2})[/](\d{1,2})[/](\d{4})",
        r"(\d{1,2}) de (janeiro|fevereiro|março|abril|maio|junho|julho|agosto|setembro|outubro|novembro|dezembro) de (\d{4})",
    ]

    meses = {
        "janeiro": 1, "fevereiro": 2, "março": 3, "abril": 4,
        "maio": 5, "junho": 6, "julho": 7, "agosto": 8,
        "setembro": 9, "outubro": 10, "novembro": 11, "dezembro": 12,
    }

    for padrao in padroes_data:
        for match in re.finditer(padrao, texto, re.IGNORECASE):
            try:
                if "/" in match.group(0):
                    d, m, a = int(match.group(1)), int(match.group(2)), int(match.group(3))
                else:
                    d = int(match.group(1))
                    m = meses.get(match.group(2).lower(), 1)
                    a = int(match.group(3))

                data = date(a, m, d)
                if data < hoje:
                    dias_atrasado = (hoje - data).days
                    if "prazo" in texto[max(0, match.start() - 100):match.end() + 100].lower():
                        alertas.append({
                            "tipo": "prazo_vencido",
                            "severidade": "alta",
                            "mensagem": f"Prazo vencido em {data.strftime('%d/%m/%Y')} (há {dias_atrasado} dias)",
                            "trecho": texto[max(0, match.start() - 30):match.end() + 30],
                        })
            except (ValueError, KeyError):
                continue

    return alertas


def _detectar_inconsistencias(texto: str, analise: dict) -> list:
    alertas = []
    pedidos = analise.get("pedidos_autor", [])
    resumo = analise.get("resumo_fatos", "")

    if pedidos and resumo:
        palavras_pedido = set()
        for p in pedidos:
            palavras_pedido.update(p.lower().split()[:5])

        palavras_fatos = set(resumo.lower().split())
        overlap = palavras_pedido & palavras_fatos

        if len(overlap) < 2 and len(pedidos) > 0:
            alertas.append({
                "tipo": "inconsistencia",
                "severidade": "media",
                "mensagem": "Possível inconsistência entre fatos narrados e pedidos formulados",
                "trecho": "",
            })

    return alertas


def _detectar_valores_desproporcionais(texto: str, analise: dict) -> list:
    alertas = []
    valores = re.findall(r"R?\$?\s?[\d.,]+", texto)
    valores_numericos = []
    for v in valores:
        v_clean = v.replace("R$", "").replace("$", "").replace(".", "").replace(",", ".").strip()
        try:
            valores_numericos.append(float(v_clean))
        except ValueError:
            continue

    if valores_numericos:
        maior = max(valores_numericos)
        for v in valores_numericos:
            if v > 0 and maior > 0 and v > maior * 0.3 and v != maior:
                alertas.append({
                    "tipo": "valor_desproporcional",
                    "severidade": "baixa",
                    "mensagem": f"Valor R$ {v:,.2f} pode ser desproporcional em relação ao valor da causa",
                    "trecho": "",
                })

    return alertas
