"""
Gera vendas_exemplo.csv com dados FICTÍCIOS para demonstração.
Nenhum dado real é utilizado.

Execução: python data/samples/gerar_dados_exemplo.py
"""

import pandas as pd
import numpy as np
from pathlib import Path

np.random.seed(42)

PRODUTOS = {
    "prato_executivo":   {"cat": "prato_principal", "preco": 35.90, "media": 45},
    "salada_caesar":     {"cat": "entrada",          "preco": 18.50, "media": 12},
    "frango_grelhado":   {"cat": "prato_principal",  "preco": 32.00, "media": 30},
    "suco_laranja":      {"cat": "bebida",            "preco":  8.00, "media": 60},
    "sobremesa_dia":     {"cat": "sobremesa",         "preco": 12.00, "media": 20},
    "prato_vegetariano": {"cat": "prato_principal",   "preco": 28.00, "media": 18},
}

TURNOS = {
    "almoco":     [1.0, 1.2, 1.1, 1.2, 1.4, 0.7, 0.5],
    "jantar":     [0.8, 0.9, 0.9, 1.0, 1.5, 1.4, 0.6],
    "cafe_manha": [0.9, 1.0, 1.0, 1.0, 1.1, 0.8, 0.7],
}

datas = pd.date_range("2023-01-01", "2024-06-30", freq="D")
registros = []

for data in datas:
    dia_semana = data.dayofweek
    is_feriado = (data.month == 1 and data.day == 1)
    for produto, info in PRODUTOS.items():
        for turno, pesos_dia in TURNOS.items():
            peso = pesos_dia[dia_semana]
            fator = 0.4 if is_feriado else 1.0
            sazonalidade = 1.0 + 0.15 * np.sin(2 * np.pi * data.dayofyear / 365)
            media = info["media"] * peso * fator * sazonalidade
            quantidade = max(0, np.random.poisson(max(1, media)))
            if np.random.random() < 0.03:  # ~3% de registros faltando (ruído realista)
                continue
            registros.append({
                "data": data.strftime("%Y-%m-%d"),
                "produto": produto,
                "turno": turno,
                "quantidade_vendida": quantidade,
                "categoria": info["cat"],
                "preco_unitario": info["preco"],
            })

df = pd.DataFrame(registros)
caminho = Path(__file__).parent / "vendas_exemplo.csv"
df.to_csv(caminho, index=False, sep=";")

print(f"Arquivo gerado: {caminho}")
print(f"Registros: {len(df):,}")
print(f"Período: {df['data'].min()} a {df['data'].max()}")
print(f"Produtos: {df['produto'].nunique()} | Turnos: {df['turno'].nunique()}")
