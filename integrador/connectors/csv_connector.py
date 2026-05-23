"""
csv_connector.py
Conector de Estágio 1 — lê vendas e estoque de arquivos CSV depositados
em diretórios monitorados (data/incoming/pdv/ e data/incoming/estoque/).

Fluxo:
    1. `conectar()` verifica se o diretório de entrada existe.
    2. `ler_vendas()` carrega todos os .csv encontrados no diretório PDV,
       concatena, filtra por data e remove os arquivos processados para
       data/processed/ (ou data/quarantine/ se inválidos).
    3. `ler_estoque()` segue o mesmo padrão para o diretório de estoque.
"""

import hashlib
import logging
import shutil
from datetime import datetime
from pathlib import Path
from typing import Optional

import pandas as pd

from integrador.config_integracao import (
    CAMPOS_ANONIMIZAR,
    COLUNAS_ESTOQUE_OBRIGATORIAS,
    COLUNAS_PDV_OBRIGATORIAS,
    DIR_INCOMING_ESTOQUE,
    DIR_INCOMING_PDV,
    DIR_PROCESSED,
    DIR_QUARANTINE_ESTOQUE,
    DIR_QUARANTINE_PDV,
    ENCODINGS_CSV,
)
from integrador.connectors.base_connector import BaseConnector

logger = logging.getLogger(__name__)


def _sha256(valor: str) -> str:
    """Anonimiza campo sensível via SHA-256 (LGPD)."""
    return hashlib.sha256(str(valor).encode()).hexdigest()


def _ler_csv_com_fallback(caminho: Path) -> pd.DataFrame:
    """Tenta encodings em sequência; levanta ValueError se nenhum funcionar."""
    for enc in ENCODINGS_CSV:
        try:
            return pd.read_csv(caminho, encoding=enc)
        except (UnicodeDecodeError, Exception):
            continue
    raise ValueError(f"Não foi possível ler {caminho} com nenhum encoding tentado.")


class CsvConnector(BaseConnector):
    """
    Conector CSV para integração de Estágio 1 (MVP).

    Parameters
    ----------
    dir_pdv : Path, optional
        Diretório de arquivos CSV de vendas. Padrão: data/incoming/pdv/
    dir_estoque : Path, optional
        Diretório de arquivos CSV de estoque. Padrão: data/incoming/estoque/
    mover_processados : bool
        Se True, move arquivos lidos para data/processed/. Padrão: True.
    """

    def __init__(
        self,
        dir_pdv:           Path = DIR_INCOMING_PDV,
        dir_estoque:       Path = DIR_INCOMING_ESTOQUE,
        mover_processados: bool = True,
    ):
        self.dir_pdv           = Path(dir_pdv)
        self.dir_estoque       = Path(dir_estoque)
        self.mover_processados = mover_processados
        self._disponivel       = False
        self._ultima_leitura:  Optional[str] = None
        self._registros_lidos: int = 0

    # ------------------------------------------------------------------
    # Ciclo de vida
    # ------------------------------------------------------------------

    def conectar(self) -> bool:
        self._disponivel = self.dir_pdv.exists() and self.dir_estoque.exists()
        if not self._disponivel:
            logger.warning(
                "CsvConnector: diretórios de entrada não encontrados. "
                "Crie data/incoming/pdv/ e data/incoming/estoque/."
            )
        return self._disponivel

    def desconectar(self) -> None:
        pass  # sem recursos para liberar

    # ------------------------------------------------------------------
    # Leitura de vendas
    # ------------------------------------------------------------------

    def ler_vendas(
        self,
        data_inicio: Optional[str] = None,
        data_fim:    Optional[str] = None,
    ) -> pd.DataFrame:
        arquivos = sorted(self.dir_pdv.glob("*.csv"))
        if not arquivos:
            logger.info("CsvConnector: nenhum arquivo CSV de vendas encontrado.")
            return pd.DataFrame(columns=COLUNAS_PDV_OBRIGATORIAS)

        frames = []
        for arq in arquivos:
            try:
                df = _ler_csv_com_fallback(arq)
                df = self._anonimizar(df)
                frames.append(df)
                if self.mover_processados:
                    destino = DIR_PROCESSED / arq.name
                    shutil.move(str(arq), str(destino))
                    logger.info("Movido para processados: %s", arq.name)
            except Exception as exc:
                logger.error("Erro ao ler %s: %s — movendo para quarentena.", arq.name, exc)
                shutil.move(str(arq), str(DIR_QUARANTINE_PDV / arq.name))

        if not frames:
            return pd.DataFrame(columns=COLUNAS_PDV_OBRIGATORIAS)

        resultado = pd.concat(frames, ignore_index=True)
        resultado = self._filtrar_datas(resultado, data_inicio, data_fim)

        self._ultima_leitura  = datetime.now().isoformat(timespec="seconds")
        self._registros_lidos = len(resultado)
        return resultado

    # ------------------------------------------------------------------
    # Leitura de estoque
    # ------------------------------------------------------------------

    def ler_estoque(
        self,
        data_referencia: Optional[str] = None,
    ) -> pd.DataFrame:
        arquivos = sorted(self.dir_estoque.glob("*.csv"))
        if not arquivos:
            logger.info("CsvConnector: nenhum arquivo CSV de estoque encontrado.")
            return pd.DataFrame(columns=COLUNAS_ESTOQUE_OBRIGATORIAS)

        frames = []
        for arq in arquivos:
            try:
                df = _ler_csv_com_fallback(arq)
                frames.append(df)
                if self.mover_processados:
                    shutil.move(str(arq), str(DIR_PROCESSED / arq.name))
            except Exception as exc:
                logger.error("Erro ao ler estoque %s: %s", arq.name, exc)
                shutil.move(str(arq), str(DIR_QUARANTINE_ESTOQUE / arq.name))

        if not frames:
            return pd.DataFrame(columns=COLUNAS_ESTOQUE_OBRIGATORIAS)

        resultado = pd.concat(frames, ignore_index=True)
        if data_referencia and "data" in resultado.columns:
            resultado["data"] = pd.to_datetime(resultado["data"], errors="coerce")
            resultado = resultado[resultado["data"] == pd.Timestamp(data_referencia)]

        return resultado

    # ------------------------------------------------------------------
    # Status
    # ------------------------------------------------------------------

    def status(self) -> dict:
        return {
            "tipo":                      "csv",
            "disponivel":                self._disponivel,
            "ultima_leitura":            self._ultima_leitura,
            "registros_ultima_leitura":  self._registros_lidos,
            "dir_pdv":                   str(self.dir_pdv),
            "dir_estoque":               str(self.dir_estoque),
        }

    # ------------------------------------------------------------------
    # Helpers privados
    # ------------------------------------------------------------------

    @staticmethod
    def _anonimizar(df: pd.DataFrame) -> pd.DataFrame:
        """Aplica SHA-256 nos campos sensíveis presentes no DataFrame."""
        for campo in CAMPOS_ANONIMIZAR:
            if campo in df.columns:
                df[campo] = df[campo].astype(str).apply(_sha256)
        return df

    @staticmethod
    def _filtrar_datas(
        df: pd.DataFrame,
        inicio: Optional[str],
        fim:    Optional[str],
    ) -> pd.DataFrame:
        if "data" not in df.columns:
            return df
        df["data"] = pd.to_datetime(df["data"], errors="coerce")
        if inicio:
            df = df[df["data"] >= pd.Timestamp(inicio)]
        if fim:
            df = df[df["data"] <= pd.Timestamp(fim)]
        return df
