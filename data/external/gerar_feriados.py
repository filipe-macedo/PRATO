"""Gera feriados nacionais brasileiros de 2020 a 2027 em CSV."""

import csv
from datetime import date, timedelta
from pathlib import Path

FERIADOS_FIXOS = {
    (1, 1): "Ano Novo",
    (4, 21): "Tiradentes",
    (5, 1): "Dia do Trabalho",
    (9, 7): "Independência do Brasil",
    (10, 12): "Nossa Senhora Aparecida",
    (11, 2): "Finados",
    (11, 15): "Proclamação da República",
    (12, 25): "Natal",
}


def _pascoa(ano: int) -> date:
    """Algoritmo de Meeus/Jones/Butcher."""
    a = ano % 19
    b, c = divmod(ano, 100)
    d, e = divmod(b, 4)
    f = (b + 8) // 25
    g = (b - f + 1) // 3
    h = (19 * a + b - d - g + 15) % 30
    i, k = divmod(c, 4)
    l = (32 + 2 * e + 2 * i - h - k) % 7
    m = (a + 11 * h + 22 * l) // 451
    mes = (h + l - 7 * m + 114) // 31
    dia = (h + l - 7 * m + 114) % 31 + 1
    return date(ano, mes, dia)


def gerar_feriados(ano_inicio=2020, ano_fim=2027) -> list[dict]:
    registros = []
    for ano in range(ano_inicio, ano_fim + 1):
        for (mes, dia), nome in FERIADOS_FIXOS.items():
            registros.append({"data": date(ano, mes, dia).isoformat(), "descricao": nome, "tipo": "fixo"})

        pascoa = _pascoa(ano)
        moveis = [
            (pascoa - timedelta(days=48), "Segunda de Carnaval"),
            (pascoa - timedelta(days=47), "Terça de Carnaval"),
            (pascoa - timedelta(days=2),  "Sexta-Feira Santa"),
            (pascoa,                       "Páscoa"),
            (pascoa + timedelta(days=60),  "Corpus Christi"),
        ]
        for d, nome in moveis:
            registros.append({"data": d.isoformat(), "descricao": nome, "tipo": "movel"})

    return sorted(registros, key=lambda x: x["data"])


if __name__ == "__main__":
    caminho = Path(__file__).parent / "feriados_nacionais.csv"
    feriados = gerar_feriados()
    with open(caminho, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=["data", "descricao", "tipo"])
        writer.writeheader()
        writer.writerows(feriados)
    print(f"Feriados gerados: {len(feriados)} registros → {caminho}")
