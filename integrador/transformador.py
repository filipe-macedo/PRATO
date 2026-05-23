"""
transformador.py
Transforma DataFrames brutos do PDV para o formato padronizado do pipeline PRATO.
Responsabilidade única: mapeamento de nomes de colunas, tipos e valores.
Nenhuma lógica de validação aqui — use validador.py antes.
"""

from __future__ import annotations

import logging
from typing import Dict, Optional

import pandas as pd

from src.config import MAPA_TURNOS

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Mapeamento de colunas — adapte conforme o PDV real
# ---------------------------------------------------------------------------
# Chave   = nome da coluna no sistema externo (PDV)
# Valor   = nome da coluna interna do PRATO
MAPA_COLUNAS_PADRAO: Dict[str, str] = {
    # Nomes alternativos comuns em sistemas PDV brasileiros
    "dt_venda":         "data",
    "date":             "data",
    "item":             "produto",
    "product":          "produto",
    "product_name":     "produto",
    "nome_produto":     "produto",
    "shift":            "turno",
    "periodo":          "turno",
    "qty":              "quantidade_vendida",
    "quantity":         "quantidade_vendida",
    "qtd":              "quantidade_vendida",
    "qtd_vendida":      "quantidade_vendida",
    "price":            "preco_unitario",
    "valor_unitario":   "preco_unitario",
    "unit_price":       "preco_unitario",
    "category":         "categoria",
}


# ---------------------------------------------------------------------------
# Transformação principal
# ---------------------------------------------------------------------------

def transformar_vendas(
    df: pd.DataFrame,
    mapa_colunas: Optional[Dict[str, str]] = None,
) -> pd.DataFrame:
    """
    Transforma DataFrame de vendas do PDV para o formato PRATO.

    Etapas
    ------
    1. Renomeia colunas conforme mapa (case-insensitive).
    2. Converte coluna ``data`` para datetime.
    3. Normaliza coluna ``turno`` (lowercase, sem acento) via MAPA_TURNOS.
    4. Converte ``quantidade_vendida`` para float.
    5. Remove colunas desnecessárias fora do esquema PRATO.

    Parameters
    ----------
    df : pd.DataFrame
        DataFrame bruto do conector.
    mapa_colunas : dict, optional
        Mapa adicional de renomeação (sobrescreve o padrão).

    Returns
    -------
    pd.DataFrame
        DataFrame no formato interno do PRATO.
    """
    df = df.copy()

    # 1. Renomeação de colunas (case-insensitive)
    mapa = {**MAPA_COLUNAS_PADRAO, **(mapa_colunas or {})}
    df.columns = [c.strip().lower() for c in df.columns]
    df = df.rename(columns={k.lower(): v for k, v in mapa.items()})

    # 2. Conversão de datas
    if "data" in df.columns:
        df["data"] = pd.to_datetime(df["data"], errors="coerce")

    # 3. Normalização de turnos
    if "turno" in df.columns:
        df["turno"] = df["turno"].astype(str).str.strip().str.lower()
        df["turno"] = df["turno"].str.normalize("NFKD").str.encode("ascii", errors="ignore").str.decode("ascii")
        df["turno"] = df["turno"].map(lambda t: MAPA_TURNOS.get(t, t))

    # 4. Tipo numérico
    if "quantidade_vendida" in df.columns:
        df["quantidade_vendida"] = pd.to_numeric(df["quantidade_vendida"], errors="coerce")

    if "preco_unitario" in df.columns:
        df["preco_unitario"] = pd.to_numeric(df["preco_unitario"], errors="coerce")

    # 5. Normalização do nome do produto (lowercase)
    if "produto" in df.columns:
        df["produto"] = df["produto"].astype(str).str.strip().str.lower()

    n_antes = len(df)
    logger.info("Transformação concluída: %d linhas processadas.", n_antes)
    return df


def transformar_estoque(
    df: pd.DataFrame,
    mapa_colunas: Optional[Dict[str, str]] = None,
) -> pd.DataFrame:
    """
    Transforma DataFrame de estoque do PDV para o formato PRATO.

    Parameters
    ----------
    df : pd.DataFrame
        DataFrame bruto do conector.
    mapa_colunas : dict, optional
        Mapa adicional de renomeação.

    Returns
    -------
    pd.DataFrame
    """
    df = df.copy()

    mapa_est = {
        "dt_estoque":           "data",
        "date":                 "data",
        "item":                 "produto",
        "product":              "produto",
        "nome_produto":         "produto",
        "qty_available":        "quantidade_disponivel",
        "qtd_disponivel":       "quantidade_disponivel",
        "stock":                "quantidade_disponivel",
        **(mapa_colunas or {}),
    }

    df.columns = [c.strip().lower() for c in df.columns]
    df = df.rename(columns={k.lower(): v for k, v in mapa_est.items()})

    if "data" in df.columns:
        df["data"] = pd.to_datetime(df["data"], errors="coerce")

    if "quantidade_disponivel" in df.columns:
        df["quantidade_disponivel"] = pd.to_numeric(df["quantidade_disponivel"], errors="coerce")

    if "produto" in df.columns:
        df["produto"] = df["produto"].astype(str).str.strip().str.lower()

    return df
