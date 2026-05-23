"""Utilitários de calendário: popula tabela calendario no banco de dados."""

import sqlite3
from datetime import date, timedelta


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
    """Algoritmo de Meeus/Jones/Butcher para calcular a data da Páscoa."""
    a = ano % 19
    b = ano // 100
    c = ano % 100
    d = b // 4
    e = b % 4
    f = (b + 8) // 25
    g = (b - f + 1) // 3
    h = (19 * a + b - d - g + 15) % 30
    i = c // 4
    k = c % 4
    l = (32 + 2 * e + 2 * i - h - k) % 7
    m = (a + 11 * h + 22 * l) // 451
    mes = (h + l - 7 * m + 114) // 31
    dia = ((h + l - 7 * m + 114) % 31) + 1
    return date(ano, mes, dia)


def feriados_ano(ano: int) -> dict[date, str]:
    feriados = {}
    for (mes, dia), nome in FERIADOS_FIXOS.items():
        feriados[date(ano, mes, dia)] = nome

    pascoa = _pascoa(ano)
    feriados[pascoa - timedelta(days=48)] = "Segunda de Carnaval"
    feriados[pascoa - timedelta(days=47)] = "Terça de Carnaval"
    feriados[pascoa - timedelta(days=2)] = "Sexta-Feira Santa"
    feriados[pascoa] = "Páscoa"
    feriados[pascoa + timedelta(days=60)] = "Corpus Christi"
    return feriados


def popular_calendario(caminho_db: str, ano_inicio: int = 2022, ano_fim: int = 2026):
    conn = sqlite3.connect(caminho_db)
    cursor = conn.cursor()

    for ano in range(ano_inicio, ano_fim + 1):
        feriados = feriados_ano(ano)
        data_atual = date(ano, 1, 1)
        while data_atual.year == ano:
            dia_semana = data_atual.weekday()
            is_feriado = data_atual in feriados
            cursor.execute("""
                INSERT OR IGNORE INTO calendario
                    (data, dia_semana, nome_dia, mes, ano, semana_do_ano,
                     trimestre, is_fim_de_semana, is_feriado, descricao_feriado)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                str(data_atual),
                dia_semana,
                ["Segunda", "Terça", "Quarta", "Quinta",
                 "Sexta", "Sábado", "Domingo"][dia_semana],
                data_atual.month,
                data_atual.year,
                data_atual.isocalendar()[1],
                (data_atual.month - 1) // 3 + 1,
                int(dia_semana >= 5),
                int(is_feriado),
                feriados.get(data_atual),
            ))
            data_atual += timedelta(days=1)

    conn.commit()
    conn.close()
    print(f"Calendário populado: {ano_inicio}–{ano_fim}")
