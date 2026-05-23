import numpy as np
import pandas as pd
import pytest
from src.baseline import BaselinePrevisao, calcular_metricas


@pytest.fixture
def modelo_treinado(df_vendas_valido):
    df = df_vendas_valido.copy()
    if "dia_semana" not in df.columns:
        df["dia_semana"] = pd.to_datetime(df["data"]).dt.dayofweek
    modelo = BaselinePrevisao()
    modelo.fit(df)
    return modelo, df


def test_baseline_retorna_array(modelo_treinado):
    modelo, df = modelo_treinado
    pred = modelo.predict(df, "B4")
    assert isinstance(pred, np.ndarray)
    assert len(pred) == len(df)


def test_fallback_zero_safe():
    """Zero é valor válido — não deve ser tratado como ausente."""
    df_treino = pd.DataFrame({
        "data": pd.to_datetime(["2024-01-01"]),
        "produto": ["x"], "turno": ["almoco"],
        "quantidade_vendida": [0.0], "dia_semana": [0],
    })
    modelo = BaselinePrevisao()
    modelo.fit(df_treino)
    pred = modelo.predict(df_treino, "B4")
    assert pred[0] == 0.0  # 0 é válido, não deve cair no fallback


def test_calcular_metricas_retorna_chaves():
    y_real = np.array([10.0, 20.0, 30.0])
    y_prev = np.array([12.0, 18.0, 28.0])
    m = calcular_metricas(y_real, y_prev, "teste", "teste")
    assert all(k in m for k in ["mae", "rmse", "r2", "mape"])
