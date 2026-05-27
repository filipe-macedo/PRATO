"""Modelos de referência (baseline) com fallback hierárquico B4→B3→B2→B1."""

import numpy as np
import pandas as pd
from pathlib import Path
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score


class BaselinePrevisao:
    ESTRATEGIAS = {
        "B1": "Média Global",
        "B2": "Média por Produto",
        "B3": "Média por Produto e Turno",
        "B4": "Média por Produto, Turno e Dia da Semana",
    }

    def __init__(self):
        self._medias: dict = {}
        self._col_alvo: str = "quantidade_vendida"

    def fit(self, df_treino: pd.DataFrame, col_alvo: str = "quantidade_vendida"):
        self._col_alvo = col_alvo
        v = col_alvo

        self._medias["B1"] = df_treino[v].mean()
        self._medias["B2"] = df_treino.groupby("produto")[v].mean().to_dict()
        self._medias["B3"] = (
            df_treino.groupby(["produto", "turno"])[v].mean().to_dict()
        )
        self._medias["B4"] = (
            df_treino.groupby(["produto", "turno", "dia_semana"])[v].mean().to_dict()
        )
        return self

    def _prever_linha(self, row, estrategia: str) -> float:
        if estrategia == "B4":
            val = self._medias["B4"].get((row["produto"], row["turno"], row["dia_semana"]))
            if val is not None:
                return val
            estrategia = "B3"

        if estrategia == "B3":
            val = self._medias["B3"].get((row["produto"], row["turno"]))
            if val is not None:
                return val
            estrategia = "B2"

        if estrategia == "B2":
            val = self._medias["B2"].get(row["produto"])
            if val is not None:
                return val

        return self._medias["B1"]

    def predict(self, df: pd.DataFrame, estrategia: str = "B4") -> np.ndarray:
        return df.apply(lambda row: self._prever_linha(row, estrategia), axis=1).values

    def predict_all(self, df: pd.DataFrame) -> pd.DataFrame:
        df = df.copy()
        for est in self.ESTRATEGIAS:
            df[f"prev_{est}"] = self.predict(df, est)
        return df


def calcular_metricas(
    y_real: np.ndarray,
    y_previsto: np.ndarray,
    nome: str,
    conjunto: str,
) -> dict:
    y_prev_clip = np.clip(y_previsto, 0, None)
    mask = y_real > 0
    mape = np.mean(np.abs((y_real[mask] - y_prev_clip[mask]) / y_real[mask])) * 100 if mask.any() else np.nan

    return {
        "modelo": nome,
        "conjunto": conjunto,
        "mae": mean_absolute_error(y_real, y_prev_clip),
        "rmse": np.sqrt(mean_squared_error(y_real, y_prev_clip)),
        "r2": r2_score(y_real, y_prev_clip),
        "mape": mape,
    }


def calcular_metricas_por_produto(
    df: pd.DataFrame,
    col_real: str,
    col_prev: str,
) -> pd.DataFrame:
    rows = []
    for produto, grupo in df.groupby("produto"):
        m = calcular_metricas(
            grupo[col_real].values,
            grupo[col_prev].values,
            produto,
            "teste",
        )
        rows.append(m)
    return pd.DataFrame(rows).sort_values("mae", ascending=False)


def avaliar_baseline(
    caminho_treino: str = "data/processed/vendas_treino.csv",
    caminho_teste: str = "data/processed/vendas_teste.csv",
) -> tuple[pd.DataFrame, pd.DataFrame]:
    df_treino = pd.read_csv(caminho_treino, parse_dates=["data"])
    df_teste = pd.read_csv(caminho_teste, parse_dates=["data"])

    modelo = BaselinePrevisao()
    modelo.fit(df_treino)
    df_prev = modelo.predict_all(df_teste)

    metricas = []
    for est in BaselinePrevisao.ESTRATEGIAS:
        metricas.append(calcular_metricas(
            df_prev["quantidade_vendida"].values,
            df_prev[f"prev_{est}"].values,
            f"Baseline {est}",
            "teste",
        ))

    df_metricas = pd.DataFrame(metricas)
    Path("outputs/metricas").mkdir(parents=True, exist_ok=True)
    df_metricas.to_csv("outputs/metricas/baseline_metricas.csv", index=False)

    df_por_produto = calcular_metricas_por_produto(
        df_prev, "quantidade_vendida", "prev_B4"
    )
    df_por_produto.to_csv("outputs/metricas/baseline_por_produto.csv", index=False)

    print("\n=== Métricas Baseline ===")
    print(df_metricas[["modelo", "mae", "rmse", "r2", "mape"]].to_string(index=False))
    return df_metricas, df_prev


if __name__ == "__main__":
    avaliar_baseline()
