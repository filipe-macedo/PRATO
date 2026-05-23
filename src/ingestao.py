"""Módulo M1 — Carregamento e validação inicial dos dados brutos."""

import re
import unicodedata
import pandas as pd
from pathlib import Path
from src.config import COLUNAS_OBRIGATORIAS


def carregar_dados(
    caminho: str,
    separador: str = ";",
    encoding: str = "utf-8",
    aba_excel: str | None = None,
) -> pd.DataFrame:
    """
    Carrega CSV ou Excel e normaliza nomes de colunas para snake_case sem acentos.

    Args:
        caminho: Caminho para o arquivo.
        separador: Delimitador do CSV. Ignorado para Excel.
        encoding: Codificação do CSV.
        aba_excel: Nome ou índice da aba para arquivos .xlsx/.xls.

    Returns:
        DataFrame com colunas normalizadas.

    Raises:
        FileNotFoundError: Arquivo não encontrado.
        ValueError: Extensão não suportada.
    """
    caminho = Path(caminho)
    if not caminho.exists():
        raise FileNotFoundError(f"Arquivo não encontrado: {caminho}")

    ext = caminho.suffix.lower()
    if ext == ".csv":
        try:
            df = pd.read_csv(caminho, sep=separador, encoding=encoding, dtype=str)
        except UnicodeDecodeError:
            df = pd.read_csv(caminho, sep=separador, encoding="latin-1", dtype=str)
    elif ext in (".xlsx", ".xls"):
        df = pd.read_excel(caminho, sheet_name=aba_excel or 0, dtype=str)
    else:
        raise ValueError(f"Extensão '{ext}' não suportada. Use .csv, .xlsx ou .xls.")

    df.columns = _normalizar_nomes_colunas(df.columns)
    return df


def _normalizar_nomes_colunas(colunas) -> list[str]:
    resultado = []
    for col in colunas:
        col = str(col).strip().lower()
        col = unicodedata.normalize("NFKD", col)
        col = col.encode("ascii", "ignore").decode("ascii")
        col = re.sub(r"[^a-z0-9_]", "_", col)
        col = re.sub(r"_+", "_", col).strip("_")
        resultado.append(col)
    return resultado


def validar_colunas(
    df: pd.DataFrame,
    colunas_obrigatorias: list[str] = COLUNAS_OBRIGATORIAS,
) -> tuple[bool, list[str]]:
    ausentes = [c for c in colunas_obrigatorias if c not in df.columns]
    return len(ausentes) == 0, ausentes


def inspecionar_dados(df: pd.DataFrame) -> dict:
    """Retorna resumo estatístico: shape, nulos, duplicatas e período."""
    info = {
        "shape": df.shape,
        "nulos": df.isnull().sum().to_dict(),
        "duplicatas": int(df.duplicated().sum()),
    }
    if "data" in df.columns:
        try:
            datas = pd.to_datetime(df["data"], errors="coerce")
            info["periodo"] = {
                "inicio": str(datas.min().date()),
                "fim": str(datas.max().date()),
                "dias": (datas.max() - datas.min()).days,
            }
        except Exception:
            info["periodo"] = "indisponível"
    return info
