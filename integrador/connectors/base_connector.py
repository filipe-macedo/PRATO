"""
base_connector.py
Interface abstrata (Adapter) que todo conector de PDV/estoque deve implementar.
Nenhuma lógica de negócio vive aqui — apenas o contrato.
"""

from abc import ABC, abstractmethod
from typing import Optional
import pandas as pd


class BaseConnector(ABC):
    """
    Contrato mínimo para conectores de origem de dados.

    Subclasses concretas:
        - CsvConnector  — lê arquivos CSV depositados em diretório monitorado
        - ApiConnector  — consome endpoint REST externo (implementação futura)
    """

    # ------------------------------------------------------------------
    # Ciclo de vida
    # ------------------------------------------------------------------

    @abstractmethod
    def conectar(self) -> bool:
        """
        Estabelece conexão / verifica disponibilidade da fonte.

        Returns
        -------
        bool
            True se a fonte está acessível; False caso contrário.
        """

    @abstractmethod
    def desconectar(self) -> None:
        """Libera recursos de conexão (fechar arquivo, encerrar sessão HTTP, etc.)."""

    # ------------------------------------------------------------------
    # Leitura de dados
    # ------------------------------------------------------------------

    @abstractmethod
    def ler_vendas(
        self,
        data_inicio: Optional[str] = None,
        data_fim:    Optional[str] = None,
    ) -> pd.DataFrame:
        """
        Lê registros de vendas da fonte de dados.

        Parameters
        ----------
        data_inicio : str, optional
            Filtro de data inicial no formato ISO (YYYY-MM-DD).
        data_fim : str, optional
            Filtro de data final no formato ISO (YYYY-MM-DD).

        Returns
        -------
        pd.DataFrame
            DataFrame com ao menos as colunas definidas em
            ``config_integracao.COLUNAS_PDV_OBRIGATORIAS``.
        """

    @abstractmethod
    def ler_estoque(
        self,
        data_referencia: Optional[str] = None,
    ) -> pd.DataFrame:
        """
        Lê snapshot de estoque da fonte de dados.

        Parameters
        ----------
        data_referencia : str, optional
            Data de referência no formato ISO (YYYY-MM-DD).

        Returns
        -------
        pd.DataFrame
            DataFrame com ao menos as colunas definidas em
            ``config_integracao.COLUNAS_ESTOQUE_OBRIGATORIAS``.
        """

    # ------------------------------------------------------------------
    # Metadados
    # ------------------------------------------------------------------

    @abstractmethod
    def status(self) -> dict:
        """
        Retorna dicionário com informações de saúde do conector.

        Exemplo de retorno::

            {
                "tipo": "csv",
                "disponivel": True,
                "ultima_leitura": "2024-03-15T10:22:00",
                "registros_ultima_leitura": 142,
            }
        """

    # ------------------------------------------------------------------
    # Context manager (opcional — implementação padrão)
    # ------------------------------------------------------------------

    def __enter__(self):
        self.conectar()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.desconectar()
        return False  # não suprime exceções
