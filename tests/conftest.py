import pytest
import pandas as pd
from datetime import date


@pytest.fixture
def df_vendas_valido():
    return pd.DataFrame({
        "data": pd.to_datetime(["2024-01-15", "2024-01-15", "2024-01-16",
                                "2024-01-16", "2024-01-17"]),
        "produto": ["prato_executivo", "salada_caesar", "prato_executivo",
                    "salada_caesar", "prato_executivo"],
        "turno": ["almoco", "almoco", "jantar", "jantar", "almoco"],
        "quantidade_vendida": [45.0, 12.0, 28.0, 8.0, 50.0],
        "categoria": ["prato_principal", "entrada", "prato_principal", "entrada", "prato_principal"],
        "preco_unitario": [35.90, 18.50, 35.90, 18.50, 35.90],
    })


@pytest.fixture
def df_vendas_com_problemas(df_vendas_valido):
    df = df_vendas_valido.copy()
    problema = pd.DataFrame({
        "data": [pd.NaT],
        "produto": [None],
        "turno": ["almoco"],
        "quantidade_vendida": [-5.0],
        "categoria": [None],
        "preco_unitario": [None],
    })
    return pd.concat([df, problema], ignore_index=True)
