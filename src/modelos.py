"""Modelos supervisionados: Regressão Linear, Random Forest e XGBoost."""

import json
import warnings
import numpy as np
import pandas as pd
import joblib
from pathlib import Path
from datetime import datetime
from sklearn.linear_model import LinearRegression
from sklearn.preprocessing import StandardScaler
from sklearn.pipeline import Pipeline
from sklearn.ensemble import RandomForestRegressor
from sklearn.model_selection import TimeSeriesSplit, cross_val_score
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score
from xgboost import XGBRegressor

warnings.filterwarnings("ignore")

FEATURES_BASE = [
    "produto_cod", "turno_cod", "dia_semana", "mes",
    "semana_do_ano", "trimestre", "is_fim_de_semana", "is_feriado", "ano",
]
FEATURES_OPCIONAIS = [
    "categoria_cod", "lag_1d", "lag_7d", "media_movel_7d", "media_movel_14d"
]
# Variáveis que NUNCA devem entrar como features (leakage direto ou pós-venda)
COLUNAS_PROIBIDAS = {
    "quantidade_vendida", "receita_total", "quantidade_cancelada",
    "data", "produto", "turno", "turno_original", "categoria", "nome_dia",
}

HP_RANDOM_FOREST = {
    "n_estimators": 200, "max_depth": 10, "min_samples_leaf": 5,
    "max_features": "sqrt", "n_jobs": -1, "random_state": 42,
}
HP_XGBOOST = {
    "n_estimators": 500, "max_depth": 5, "learning_rate": 0.05,
    "subsample": 0.8, "colsample_bytree": 0.8,
    "reg_alpha": 0.1, "reg_lambda": 1.0, "min_child_weight": 5,
    "early_stopping_rounds": 50, "eval_metric": "mae",
    "random_state": 42, "verbosity": 0,
}


def selecionar_features(df: pd.DataFrame) -> list[str]:
    disponiveis = set(df.columns) - COLUNAS_PROIBIDAS
    features = [f for f in FEATURES_BASE if f in disponiveis]
    features += [f for f in FEATURES_OPCIONAIS if f in disponiveis]
    return features


def preparar_xy(
    df: pd.DataFrame,
    features: list[str],
    col_alvo: str = "quantidade_vendida",
    remover_nulos: bool = True,
) -> tuple[pd.DataFrame, pd.Series]:
    X = df[features].copy().astype(float)
    y = df[col_alvo].copy().astype(float)
    if remover_nulos:
        mask = X.notna().all(axis=1) & y.notna()
        X, y = X[mask], y[mask]
    return X, y


def calcular_metricas(
    y_real: np.ndarray,
    y_previsto: np.ndarray,
    nome: str,
    conjunto: str,
) -> dict:
    y_prev = np.clip(y_previsto, 0, None)
    mask = y_real > 0
    mape = (np.abs((y_real[mask] - y_prev[mask]) / y_real[mask]).mean() * 100
            if mask.any() else np.nan)
    return {
        "nome": nome, "conjunto": conjunto,
        "mae": mean_absolute_error(y_real, y_prev),
        "rmse": np.sqrt(mean_squared_error(y_real, y_prev)),
        "r2": r2_score(y_real, y_prev),
        "mape": mape,
    }


def validar_cruzada(modelo, X: pd.DataFrame, y: pd.Series, n_splits: int = 5) -> dict:
    tscv = TimeSeriesSplit(n_splits=n_splits)
    scores = -cross_val_score(modelo, X, y, cv=tscv, scoring="neg_mean_absolute_error")
    return {"cv_mae_mean": scores.mean(), "cv_mae_std": scores.std()}


def treinar_regressao_linear(
    X_treino: pd.DataFrame, y_treino: pd.Series, n_splits_cv: int = 5
) -> tuple:
    modelo = Pipeline([("scaler", StandardScaler()), ("reg", LinearRegression())])
    cv = validar_cruzada(modelo, X_treino, y_treino, n_splits_cv)
    modelo.fit(X_treino, y_treino)
    return modelo, cv


def treinar_random_forest(
    X_treino: pd.DataFrame, y_treino: pd.Series,
    n_splits_cv: int = 5, hp: dict = HP_RANDOM_FOREST,
) -> tuple:
    modelo = RandomForestRegressor(**hp)
    cv = validar_cruzada(modelo, X_treino, y_treino, n_splits_cv)
    modelo.fit(X_treino, y_treino)
    return modelo, cv


def treinar_xgboost(
    X_treino: pd.DataFrame, y_treino: pd.Series,
    n_splits_cv: int = 5, hp: dict = HP_XGBOOST,
    proporcao_val_es: float = 0.15,
) -> tuple:
    # CV sem early stopping (n_estimators fixo em 200)
    hp_cv = {k: v for k, v in hp.items() if k != "early_stopping_rounds"}
    hp_cv["n_estimators"] = 200
    modelo_cv = XGBRegressor(**hp_cv)
    cv = validar_cruzada(modelo_cv, X_treino, y_treino, n_splits_cv)

    # Treino final com early stopping no último bloco temporal
    n_val = int(len(X_treino) * proporcao_val_es)
    X_tr, X_val = X_treino.iloc[:-n_val], X_treino.iloc[-n_val:]
    y_tr, y_val = y_treino.iloc[:-n_val], y_treino.iloc[-n_val:]

    modelo = XGBRegressor(**hp)
    modelo.fit(X_tr, y_tr, eval_set=[(X_val, y_val)], verbose=False)
    return modelo, cv


def salvar_modelo(modelo, metadados: dict, nome_arquivo: str) -> None:
    Path("models").mkdir(exist_ok=True)
    joblib.dump(modelo, f"models/{nome_arquivo}.pkl", compress=3)
    with open(f"models/{nome_arquivo}_metadados.json", "w", encoding="utf-8") as f:
        json.dump(metadados, f, ensure_ascii=False, indent=2)
    print(f"  Modelo salvo: models/{nome_arquivo}.pkl")


def carregar_modelo(nome_arquivo: str) -> tuple:
    modelo = joblib.load(f"models/{nome_arquivo}.pkl")
    with open(f"models/{nome_arquivo}_metadados.json", encoding="utf-8") as f:
        metadados = json.load(f)
    return modelo, metadados


def treinar_todos_modelos(
    caminho_treino: str = "data/processed/vendas_treino.csv",
    caminho_teste: str = "data/processed/vendas_teste.csv",
) -> pd.DataFrame:
    print("\n========== PRATO — Treinamento de Modelos ==========")

    df_treino = pd.read_csv(caminho_treino, parse_dates=["data"])
    df_teste = pd.read_csv(caminho_teste, parse_dates=["data"])

    features = selecionar_features(df_treino)
    print(f"  Features selecionadas ({len(features)}): {features}")

    X_treino, y_treino = preparar_xy(df_treino, features)
    X_teste, y_teste = preparar_xy(df_teste, features)

    resultados = []
    melhor_mae = float("inf")
    melhor_nome = None

    configs = [
        ("regressao_linear", treinar_regressao_linear, {}),
        ("random_forest", treinar_random_forest, {}),
        ("xgboost", treinar_xgboost, {}),
    ]

    for nome, fn_treino, kwargs in configs:
        print(f"\n  [{nome}] Treinando...")
        modelo, cv = fn_treino(X_treino, y_treino, **kwargs)

        m_treino = calcular_metricas(y_treino.values, modelo.predict(X_treino), nome, "treino")
        m_teste = calcular_metricas(y_teste.values, modelo.predict(X_teste), nome, "teste")

        gap = (m_teste["mae"] - m_treino["mae"]) / (m_treino["mae"] + 1e-9)
        if gap > 0.20:
            print(f"  ⚠  Gap treino/teste = {gap:.1%} — possível overfitting.")

        metadados = {
            "nome": nome,
            "features": features,
            "data_treino": datetime.now().isoformat(),
            "metricas_treino": m_treino,
            "metricas_teste": m_teste,
            "cv_mae_mean": cv["cv_mae_mean"],
            "cv_mae_std": cv["cv_mae_std"],
        }
        salvar_modelo(modelo, metadados, nome)

        linha = {**m_teste, "cv_mae_mean": cv["cv_mae_mean"], "cv_mae_std": cv["cv_mae_std"]}
        resultados.append(linha)

        if m_teste["mae"] < melhor_mae:
            melhor_mae = m_teste["mae"]
            melhor_nome = nome

    # Salva o melhor modelo como modelo_final
    melhor_modelo, meta = carregar_modelo(melhor_nome)
    salvar_modelo(melhor_modelo, meta, "modelo_final")

    df_comp = pd.DataFrame(resultados)
    Path("outputs/metricas").mkdir(parents=True, exist_ok=True)
    df_comp.to_csv("outputs/metricas/comparacao_modelos.csv", index=False)

    # Gera previsões do melhor modelo no conjunto de teste
    df_prev = df_teste.copy()
    df_prev["quantidade_prevista"] = np.clip(melhor_modelo.predict(X_teste), 0, None)
    Path("outputs/previsoes").mkdir(parents=True, exist_ok=True)
    df_prev.to_csv("outputs/previsoes/previsoes_melhor_modelo.csv", index=False)

    print(f"\n  Melhor modelo: {melhor_nome} (MAE={melhor_mae:.2f})")
    print("========== Treinamento concluído ==========")
    return df_comp


if __name__ == "__main__":
    treinar_todos_modelos()
