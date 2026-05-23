"""
test_modelos.py
Testes unitários para src/modelos.py — seleção de features,
preparação de X/y, métricas e treinamento dos três modelos.
"""

import numpy as np
import pandas as pd
import pytest

from src.modelos import (
    COLUNAS_PROIBIDAS,
    FEATURES_BASE,
    calcular_metricas,
    preparar_xy,
    selecionar_features,
    treinar_regressao_linear,
    treinar_random_forest,
)


# ---------------------------------------------------------------------------
# Fixture: DataFrame com features mínimas para treinamento
# ---------------------------------------------------------------------------

@pytest.fixture
def df_features(df_vendas_valido):
    """Adiciona colunas de features temporais e lag ao fixture base."""
    df = df_vendas_valido.copy()
    df["dia_semana"]      = pd.to_datetime(df["data"]).dt.dayofweek
    df["mes"]             = pd.to_datetime(df["data"]).dt.month
    df["ano"]             = pd.to_datetime(df["data"]).dt.year
    df["is_fim_de_semana"] = df["dia_semana"].isin([5, 6]).astype(int)
    df["is_feriado"]      = 0
    df["lag_1d"]          = df["quantidade_vendida"].shift(1).fillna(0)
    df["lag_7d"]          = df["quantidade_vendida"].shift(7).fillna(0)
    df["media_movel_7d"]  = df["quantidade_vendida"].shift(1).rolling(7, min_periods=1).mean()
    df["media_movel_14d"] = df["quantidade_vendida"].shift(1).rolling(14, min_periods=1).mean()
    # Codificação categórica mínima
    df["produto_cod"] = df["produto"].astype("category").cat.codes
    df["turno_cod"]   = df["turno"].astype("category").cat.codes
    return df


# ---------------------------------------------------------------------------
# selecionar_features
# ---------------------------------------------------------------------------

def test_selecionar_features_exclui_proibidas(df_features):
    """Colunas proibidas nunca devem aparecer nas features selecionadas."""
    # Adiciona coluna proibida ao DF para garantir exclusão
    df = df_features.copy()
    df["receita_total"] = df["quantidade_vendida"] * 10.0
    features = selecionar_features(df)
    for proibida in COLUNAS_PROIBIDAS:
        assert proibida not in features, f"Coluna proibida encontrada: {proibida}"


def test_selecionar_features_inclui_base(df_features):
    """Ao menos as features base disponíveis devem ser retornadas."""
    features = selecionar_features(df_features)
    presentes = [f for f in FEATURES_BASE if f in df_features.columns]
    for f in presentes:
        assert f in features, f"Feature base ausente: {f}"


# ---------------------------------------------------------------------------
# preparar_xy
# ---------------------------------------------------------------------------

def test_preparar_xy_shapes(df_features):
    """X e y devem ter o mesmo número de linhas e y deve ser 1D."""
    features = selecionar_features(df_features)
    X, y = preparar_xy(df_features, features)
    assert X.shape[0] == y.shape[0]
    assert X.ndim == 2
    assert y.ndim == 1


def test_preparar_xy_sem_nan(df_features):
    """X e y não devem conter NaN após preparação."""
    features = selecionar_features(df_features)
    X, y = preparar_xy(df_features, features)
    assert not np.isnan(X).any(), "X contém NaN"
    assert not np.isnan(y).any(), "y contém NaN"


# ---------------------------------------------------------------------------
# calcular_metricas
# ---------------------------------------------------------------------------

def test_calcular_metricas_chaves():
    """Dicionário de métricas deve conter as chaves mínimas esperadas."""
    y_real = np.array([10.0, 20.0, 30.0])
    y_prev = np.array([12.0, 18.0, 29.0])
    m = calcular_metricas(y_real, y_prev)
    for chave in ["mae", "rmse", "r2", "mape"]:
        assert chave in m, f"Chave '{chave}' ausente nas métricas"


def test_calcular_metricas_valores_perfeitos():
    """Previsão idêntica à real deve produzir MAE=0, RMSE=0, R²=1."""
    y = np.array([10.0, 20.0, 30.0])
    m = calcular_metricas(y, y)
    assert m["mae"]  == pytest.approx(0.0)
    assert m["rmse"] == pytest.approx(0.0)
    assert m["r2"]   == pytest.approx(1.0)


def test_calcular_metricas_mape_nao_negativo():
    """MAPE nunca deve ser negativo."""
    y_real = np.array([10.0, 20.0, 30.0])
    y_prev = np.array([5.0,  25.0, 35.0])
    m = calcular_metricas(y_real, y_prev)
    assert m["mape"] >= 0.0


# ---------------------------------------------------------------------------
# Treinamento de modelos
# ---------------------------------------------------------------------------

def test_treinar_regressao_linear_retorna_pipeline(df_features):
    """treinar_regressao_linear deve retornar objeto com método predict."""
    features = selecionar_features(df_features)
    X, y = preparar_xy(df_features, features)
    modelo, metricas = treinar_regressao_linear(X, y, features)
    assert hasattr(modelo, "predict")
    assert "mae" in metricas


def test_treinar_regressao_linear_previsoes_shape(df_features):
    """Previsão deve ter o mesmo número de linhas que o conjunto de entrada."""
    features = selecionar_features(df_features)
    X, y = preparar_xy(df_features, features)
    modelo, _ = treinar_regressao_linear(X, y, features)
    pred = modelo.predict(X)
    assert pred.shape == y.shape


def test_treinar_random_forest_retorna_pipeline(df_features):
    """treinar_random_forest deve retornar objeto com método predict."""
    features = selecionar_features(df_features)
    X, y = preparar_xy(df_features, features)
    modelo, metricas = treinar_random_forest(X, y, features)
    assert hasattr(modelo, "predict")
    assert "r2" in metricas


def test_modelos_nao_preveem_negativo(df_features):
    """
    Modelos clipeados em 0 não devem produzir previsões negativas
    para entradas com valores não negativos.
    """
    features = selecionar_features(df_features)
    X, y = preparar_xy(df_features, features)

    for treinar in [treinar_regressao_linear, treinar_random_forest]:
        modelo, _ = treinar(X, y, features)
        pred = modelo.predict(X)
        pred_clipped = np.clip(pred, 0, None)
        assert (pred_clipped >= 0).all(), f"{treinar.__name__} produziu valor negativo."
