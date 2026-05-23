"""Módulo M2 — Limpeza, padronização e engenharia de atributos."""

import unicodedata
import numpy as np
import pandas as pd
from pathlib import Path
from scipy import stats
from src.config import (
    MAPA_TURNOS, FORMATOS_DATA, ZSCORE_LIMITE,
    LAGS_DIAS, JANELAS_MEDIA_MOVEL, ARQUIVO_FERIADOS,
)


def padronizar_datas(df: pd.DataFrame, col_data: str = "data") -> pd.DataFrame:
    df = df.copy()
    df[col_data] = pd.to_datetime(df[col_data], infer_datetime_format=True, errors="coerce")

    if df[col_data].isna().any():
        for fmt in FORMATOS_DATA:
            mask = df[col_data].isna()
            if not mask.any():
                break
            df.loc[mask, col_data] = pd.to_datetime(
                df.loc[mask, col_data].astype(str), format=fmt, errors="coerce"
            )

    n_invalidas = df[col_data].isna().sum()
    if n_invalidas > 0:
        print(f"  [AVISO] {n_invalidas} linhas removidas por data inválida.")
    return df.dropna(subset=[col_data]).reset_index(drop=True)


def _remover_acentos(texto: str) -> str:
    nfkd = unicodedata.normalize("NFKD", texto)
    return nfkd.encode("ascii", "ignore").decode("ascii")


def padronizar_texto(df: pd.DataFrame, colunas: list[str]) -> pd.DataFrame:
    df = df.copy()
    for col in colunas:
        if col in df.columns:
            df[col] = (
                df[col].astype(str).str.strip().str.lower()
                .apply(_remover_acentos)
            )
    return df


def padronizar_turnos(df: pd.DataFrame, mapa: dict = MAPA_TURNOS) -> pd.DataFrame:
    df = df.copy()
    if "turno" not in df.columns:
        return df
    df["turno_original"] = df["turno"]
    df["turno"] = df["turno"].str.strip().str.lower().apply(_remover_acentos)
    df["turno"] = df["turno"].map(mapa).fillna("desconhecido")
    return df


def tratar_valores_ausentes(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    obrigatorias = ["data", "produto", "quantidade_vendida", "turno"]
    df = df.dropna(subset=[c for c in obrigatorias if c in df.columns])

    if "categoria" in df.columns:
        df["categoria"] = df["categoria"].fillna("nao_informada")
    if "quantidade_cancelada" in df.columns:
        df["quantidade_cancelada"] = df["quantidade_cancelada"].fillna(0)
    return df.reset_index(drop=True)


def sinalizar_inconsistencias(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()

    df["flag_quantidade_negativa"] = (
        pd.to_numeric(df["quantidade_vendida"], errors="coerce").fillna(0) < 0
    ).astype(int)

    if "turno" in df.columns:
        df["flag_turno_desconhecido"] = (df["turno"] == "desconhecido").astype(int)

    df["flag_duplicata"] = df.duplicated(
        subset=["data", "produto", "turno"], keep="first"
    ).astype(int)

    # Z-score por grupo (produto + turno) para detectar outliers
    df["_qtd_num"] = pd.to_numeric(df["quantidade_vendida"], errors="coerce")
    grupos = df.groupby(["produto", "turno"])["_qtd_num"]
    df["_zscore"] = grupos.transform(
        lambda s: stats.zscore(s, nan_policy="omit") if len(s) > 2 else 0
    )
    df["flag_outlier_zscore"] = (df["_zscore"].abs() > ZSCORE_LIMITE).astype(int)
    df = df.drop(columns=["_qtd_num", "_zscore"])
    return df


def agregar_por_granularidade(df: pd.DataFrame) -> pd.DataFrame:
    """Soma quantidade_vendida para mesma (data, produto, turno)."""
    colunas_agg = {"quantidade_vendida": "sum"}
    if "preco_unitario" in df.columns:
        colunas_agg["preco_unitario"] = "first"
    if "receita_total" in df.columns:
        colunas_agg["receita_total"] = "sum"

    return (
        df.groupby(["data", "produto", "turno"], as_index=False)
        .agg(colunas_agg)
        .sort_values("data")
        .reset_index(drop=True)
    )


def carregar_feriados(caminho: str = ARQUIVO_FERIADOS) -> set:
    try:
        df = pd.read_csv(caminho, parse_dates=["data"])
        return set(df["data"].dt.date)
    except Exception:
        print(f"  [AVISO] Feriados não carregados de '{caminho}'. Usando conjunto vazio.")
        return set()


def criar_features_temporais(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    feriados = carregar_feriados()
    datas = pd.to_datetime(df["data"])

    df["dia_semana"] = datas.dt.dayofweek
    df["nome_dia"] = datas.dt.day_name()
    df["mes"] = datas.dt.month
    df["ano"] = datas.dt.year
    df["semana_do_ano"] = datas.dt.isocalendar().week.astype(int)
    df["trimestre"] = datas.dt.quarter
    df["is_fim_de_semana"] = (df["dia_semana"] >= 5).astype(int)
    df["is_feriado"] = datas.dt.date.isin(feriados).astype(int)
    return df


def criar_features_lag(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy().sort_values(["produto", "turno", "data"])

    for lag in LAGS_DIAS:
        # shift por grupo garante que não há vazamento entre produtos/turnos
        df[f"lag_{lag}d"] = df.groupby(["produto", "turno"])["quantidade_vendida"].transform(
            lambda s: s.shift(lag)
        )

    for janela in JANELAS_MEDIA_MOVEL:
        # shift(1) antes do rolling exclui o dia alvo da janela (anti-leakage)
        df[f"media_movel_{janela}d"] = df.groupby(["produto", "turno"])["quantidade_vendida"].transform(
            lambda s: s.shift(1).rolling(janela).mean()
        )

    return df


def codificar_variaveis_categoricas(df: pd.DataFrame) -> tuple[pd.DataFrame, dict]:
    df = df.copy()
    mapeamentos = {}

    for col, novo_col in [
        ("produto", "produto_cod"),
        ("turno", "turno_cod"),
        ("categoria", "categoria_cod"),
        ("nome_dia", "nome_dia_cod"),
    ]:
        if col in df.columns:
            categorias = sorted(df[col].dropna().unique())
            mapa = {v: i for i, v in enumerate(categorias)}
            df[novo_col] = df[col].map(mapa)
            mapeamentos[col] = mapa

    return df, mapeamentos


def separar_treino_teste(
    df: pd.DataFrame,
    proporcao_treino: float = 0.8,
) -> tuple[pd.DataFrame, pd.DataFrame]:
    """Separação CRONOLÓGICA — nunca aleatória para séries temporais."""
    df = df.sort_values("data").reset_index(drop=True)
    n_treino = int(len(df) * proporcao_treino)
    return df.iloc[:n_treino].copy(), df.iloc[n_treino:].copy()


def exportar_dados(
    df_treino: pd.DataFrame,
    df_teste: pd.DataFrame,
    df_completo: pd.DataFrame,
    caminho_saida: str = "data/processed/",
) -> None:
    Path(caminho_saida).mkdir(parents=True, exist_ok=True)
    df_treino.to_csv(f"{caminho_saida}vendas_treino.csv", index=False)
    df_teste.to_csv(f"{caminho_saida}vendas_teste.csv", index=False)
    df_completo.to_csv(f"{caminho_saida}vendas_tratado.csv", index=False)
    print(f"  Dados exportados para '{caminho_saida}'")
