"""
validador.py
Valida DataFrames vindos de qualquer conector antes de ingestão no pipeline.
Retorna relatório estruturado em vez de lançar exceção diretamente,
permitindo quarentena parcial (linhas válidas seguem; inválidas vão para log).
"""

from __future__ import annotations

import logging
from dataclasses import dataclass, field
from typing import List, Tuple

import pandas as pd

from integrador.config_integracao import (
    COLUNAS_ESTOQUE_OBRIGATORIAS,
    COLUNAS_PDV_OBRIGATORIAS,
    TAXA_REJEICAO_MAX,
)

logger = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# Estrutura de resultado
# ---------------------------------------------------------------------------

@dataclass
class ResultadoValidacao:
    valido:         bool
    total_linhas:   int
    linhas_ok:      int
    linhas_rejeitadas: int
    taxa_rejeicao:  float
    erros:          List[str] = field(default_factory=list)
    df_valido:      pd.DataFrame = field(default_factory=pd.DataFrame)
    df_rejeitado:   pd.DataFrame = field(default_factory=pd.DataFrame)


# ---------------------------------------------------------------------------
# Validação de vendas (PDV)
# ---------------------------------------------------------------------------

def validar_vendas(df: pd.DataFrame) -> ResultadoValidacao:
    """
    Valida DataFrame de vendas do PDV.

    Regras aplicadas
    ----------------
    1. Colunas obrigatórias presentes.
    2. Coluna ``data`` parsável como datetime.
    3. ``quantidade_vendida`` >= 0.
    4. Nenhum NaN nas colunas obrigatórias (linhas com NaN vão para rejeitados).
    5. Taxa de rejeição <= TAXA_REJEICAO_MAX.
    """
    erros: List[str] = []
    total = len(df)

    # 1. Colunas obrigatórias
    ausentes = [c for c in COLUNAS_PDV_OBRIGATORIAS if c not in df.columns]
    if ausentes:
        return ResultadoValidacao(
            valido=False,
            total_linhas=total,
            linhas_ok=0,
            linhas_rejeitadas=total,
            taxa_rejeicao=1.0,
            erros=[f"Colunas obrigatórias ausentes: {ausentes}"],
            df_valido=pd.DataFrame(),
            df_rejeitado=df,
        )

    df = df.copy()

    # 2. Parse de datas
    df["data"] = pd.to_datetime(df["data"], errors="coerce")
    mask_data_invalida = df["data"].isna()
    if mask_data_invalida.any():
        erros.append(f"{mask_data_invalida.sum()} linhas com data inválida.")

    # 3. Quantidade negativa
    df["quantidade_vendida"] = pd.to_numeric(df["quantidade_vendida"], errors="coerce")
    mask_qtd_negativa = df["quantidade_vendida"] < 0
    if mask_qtd_negativa.any():
        erros.append(f"{mask_qtd_negativa.sum()} linhas com quantidade_vendida negativa.")

    # 4. NaN nas colunas obrigatórias
    mask_nan = df[COLUNAS_PDV_OBRIGATORIAS].isna().any(axis=1)

    # Combinação de rejeições
    mask_rejeitar = mask_data_invalida | mask_qtd_negativa | mask_nan
    df_valido    = df[~mask_rejeitar].reset_index(drop=True)
    df_rejeitado = df[mask_rejeitar].reset_index(drop=True)

    linhas_ok         = len(df_valido)
    linhas_rejeitadas = len(df_rejeitado)
    taxa_rejeicao     = linhas_rejeitadas / total if total > 0 else 0.0

    # 5. Taxa de rejeição
    lote_valido = taxa_rejeicao <= TAXA_REJEICAO_MAX
    if not lote_valido:
        erros.append(
            f"Taxa de rejeição {taxa_rejeicao:.1%} excede limite de {TAXA_REJEICAO_MAX:.0%}. "
            "Lote movido para quarentena."
        )

    resultado = ResultadoValidacao(
        valido=lote_valido and len(erros) == 0,
        total_linhas=total,
        linhas_ok=linhas_ok,
        linhas_rejeitadas=linhas_rejeitadas,
        taxa_rejeicao=taxa_rejeicao,
        erros=erros,
        df_valido=df_valido,
        df_rejeitado=df_rejeitado,
    )

    _logar_resultado(resultado, "vendas")
    return resultado


# ---------------------------------------------------------------------------
# Validação de estoque
# ---------------------------------------------------------------------------

def validar_estoque(df: pd.DataFrame) -> ResultadoValidacao:
    """
    Valida DataFrame de estoque.

    Regras: colunas obrigatórias presentes, data parsável,
    quantidade_disponivel >= 0.
    """
    erros: List[str] = []
    total = len(df)

    ausentes = [c for c in COLUNAS_ESTOQUE_OBRIGATORIAS if c not in df.columns]
    if ausentes:
        return ResultadoValidacao(
            valido=False,
            total_linhas=total,
            linhas_ok=0,
            linhas_rejeitadas=total,
            taxa_rejeicao=1.0,
            erros=[f"Colunas obrigatórias ausentes: {ausentes}"],
            df_valido=pd.DataFrame(),
            df_rejeitado=df,
        )

    df = df.copy()
    df["data"] = pd.to_datetime(df["data"], errors="coerce")
    df["quantidade_disponivel"] = pd.to_numeric(df["quantidade_disponivel"], errors="coerce")

    mask_rejeitar = (
        df["data"].isna()
        | (df["quantidade_disponivel"] < 0)
        | df[COLUNAS_ESTOQUE_OBRIGATORIAS].isna().any(axis=1)
    )

    df_valido    = df[~mask_rejeitar].reset_index(drop=True)
    df_rejeitado = df[mask_rejeitar].reset_index(drop=True)

    linhas_ok         = len(df_valido)
    linhas_rejeitadas = len(df_rejeitado)
    taxa_rejeicao     = linhas_rejeitadas / total if total > 0 else 0.0

    resultado = ResultadoValidacao(
        valido=taxa_rejeicao <= TAXA_REJEICAO_MAX,
        total_linhas=total,
        linhas_ok=linhas_ok,
        linhas_rejeitadas=linhas_rejeitadas,
        taxa_rejeicao=taxa_rejeicao,
        erros=erros,
        df_valido=df_valido,
        df_rejeitado=df_rejeitado,
    )

    _logar_resultado(resultado, "estoque")
    return resultado


# ---------------------------------------------------------------------------
# Helper
# ---------------------------------------------------------------------------

def _logar_resultado(r: ResultadoValidacao, tipo: str) -> None:
    nivel = logging.INFO if r.valido else logging.WARNING
    logger.log(
        nivel,
        "Validação %s: %d/%d linhas OK (%.1f%% rejeitadas). Válido=%s",
        tipo, r.linhas_ok, r.total_linhas, r.taxa_rejeicao * 100, r.valido,
    )
    for erro in r.erros:
        logger.warning("  • %s", erro)
