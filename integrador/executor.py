"""
executor.py
Orquestrador do pipeline de integração: conectar → ler → validar → transformar → entregar.
Ponto de entrada único para qualquer conector (CSV ou API).
"""

from __future__ import annotations

import logging
from pathlib import Path
from typing import Optional, Tuple

import pandas as pd

from integrador.config_integracao import DIR_PROCESSED, DIR_QUARANTINE_PDV, DIR_QUARANTINE_ESTOQUE
from integrador.connectors.base_connector import BaseConnector
from integrador.log_integracao import registrar_execucao
from integrador.transformador import transformar_vendas, transformar_estoque
from integrador.validador import ResultadoValidacao, validar_vendas, validar_estoque

logger = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# Execução de ingestão de vendas
# ---------------------------------------------------------------------------

def executar_ingestao_vendas(
    conector:    BaseConnector,
    data_inicio: Optional[str] = None,
    data_fim:    Optional[str] = None,
    destino:     Optional[Path] = None,
) -> Tuple[pd.DataFrame, ResultadoValidacao]:
    """
    Pipeline completo de ingestão de vendas.

    Fluxo
    -----
    1. Conecta à fonte de dados.
    2. Lê registros de vendas.
    3. Valida (rejeições vão para quarentena).
    4. Transforma para formato PRATO.
    5. Salva no destino (opcional) e registra log.

    Parameters
    ----------
    conector : BaseConnector
        Instância de CsvConnector, ApiConnector, etc.
    data_inicio, data_fim : str, optional
        Filtros de data ISO (YYYY-MM-DD).
    destino : Path, optional
        Se informado, salva o DataFrame válido transformado em CSV.

    Returns
    -------
    (df_transformado, resultado_validacao)
    """
    logger.info("Iniciando ingestão de vendas | conector=%s", type(conector).__name__)

    # 1. Conectar
    disponivel = conector.conectar()
    if not disponivel:
        logger.error("Conector indisponível. Abortando ingestão.")
        vazio = pd.DataFrame()
        return vazio, ResultadoValidacao(
            valido=False, total_linhas=0, linhas_ok=0,
            linhas_rejeitadas=0, taxa_rejeicao=0.0,
            erros=["Conector indisponível."],
        )

    try:
        # 2. Ler
        df_bruto = conector.ler_vendas(data_inicio=data_inicio, data_fim=data_fim)
        logger.info("Registros lidos: %d", len(df_bruto))

        if df_bruto.empty:
            logger.info("Nenhum dado de vendas disponível.")
            return df_bruto, ResultadoValidacao(
                valido=True, total_linhas=0, linhas_ok=0,
                linhas_rejeitadas=0, taxa_rejeicao=0.0,
            )

        # 3. Validar
        resultado = validar_vendas(df_bruto)

        # Enviar rejeitados para quarentena
        if not resultado.df_rejeitado.empty:
            _salvar_quarentena(resultado.df_rejeitado, DIR_QUARANTINE_PDV, "vendas")

        if not resultado.valido:
            logger.warning("Lote de vendas inválido — todo lote para quarentena.")
            _salvar_quarentena(df_bruto, DIR_QUARANTINE_PDV, "vendas_lote_completo")
            return pd.DataFrame(), resultado

        # 4. Transformar
        df_final = transformar_vendas(resultado.df_valido)

        # 5. Salvar
        if destino is not None:
            destino = Path(destino)
            destino.parent.mkdir(parents=True, exist_ok=True)
            df_final.to_csv(destino, index=False)
            logger.info("Dados transformados salvos em: %s", destino)

        registrar_execucao(
            tipo="vendas",
            conector=type(conector).__name__,
            total=resultado.total_linhas,
            ok=resultado.linhas_ok,
            rejeitados=resultado.linhas_rejeitadas,
            erros=resultado.erros,
        )

        return df_final, resultado

    finally:
        conector.desconectar()


# ---------------------------------------------------------------------------
# Execução de ingestão de estoque
# ---------------------------------------------------------------------------

def executar_ingestao_estoque(
    conector:        BaseConnector,
    data_referencia: Optional[str] = None,
    destino:         Optional[Path] = None,
) -> Tuple[pd.DataFrame, ResultadoValidacao]:
    """
    Pipeline completo de ingestão de estoque.
    Segue o mesmo fluxo de vendas: conectar → ler → validar → transformar → salvar.
    """
    logger.info("Iniciando ingestão de estoque | conector=%s", type(conector).__name__)

    disponivel = conector.conectar()
    if not disponivel:
        logger.error("Conector indisponível. Abortando ingestão de estoque.")
        return pd.DataFrame(), ResultadoValidacao(
            valido=False, total_linhas=0, linhas_ok=0,
            linhas_rejeitadas=0, taxa_rejeicao=0.0,
            erros=["Conector indisponível."],
        )

    try:
        df_bruto  = conector.ler_estoque(data_referencia=data_referencia)
        resultado = validar_estoque(df_bruto)

        if not resultado.df_rejeitado.empty:
            _salvar_quarentena(resultado.df_rejeitado, DIR_QUARANTINE_ESTOQUE, "estoque")

        if not resultado.valido:
            return pd.DataFrame(), resultado

        df_final = transformar_estoque(resultado.df_valido)

        if destino is not None:
            destino = Path(destino)
            destino.parent.mkdir(parents=True, exist_ok=True)
            df_final.to_csv(destino, index=False)

        registrar_execucao(
            tipo="estoque",
            conector=type(conector).__name__,
            total=resultado.total_linhas,
            ok=resultado.linhas_ok,
            rejeitados=resultado.linhas_rejeitadas,
            erros=resultado.erros,
        )

        return df_final, resultado

    finally:
        conector.desconectar()


# ---------------------------------------------------------------------------
# Helper
# ---------------------------------------------------------------------------

def _salvar_quarentena(df: pd.DataFrame, diretorio: Path, prefixo: str) -> None:
    from datetime import datetime
    ts   = datetime.now().strftime("%Y%m%d_%H%M%S")
    path = diretorio / f"{prefixo}_quarentena_{ts}.csv"
    diretorio.mkdir(parents=True, exist_ok=True)
    df.to_csv(path, index=False)
    logger.warning("Registros rejeitados salvos em quarentena: %s", path)
