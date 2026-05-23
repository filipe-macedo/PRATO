"""
carregador.py
Funções de carregamento de dados para o dashboard PRATO.

Modo de operação (prioridade):
  1. API Backend (se disponível e configurada)
  2. Arquivos processados locais (data/processed/)
  3. Dados de exemplo sintéticos (data/samples/) ← fallback para demo
"""

import os
import hashlib
import pandas as pd
import requests
import streamlit as st
from pathlib import Path
from datetime import date

# URL da API — configurável via variável de ambiente
API_BASE = os.getenv("API_URL", "").rstrip("/")

# Caminhos absolutos
_ROOT             = Path(__file__).resolve().parent.parent.parent
CAMINHO_PREVISOES = _ROOT / "outputs"  / "previsoes" / "previsoes_melhor_modelo.csv"
CAMINHO_TREINO    = _ROOT / "data"     / "processed" / "vendas_treino.csv"
CAMINHO_TESTE     = _ROOT / "data"     / "processed" / "vendas_teste.csv"
CAMINHO_METRICAS  = _ROOT / "outputs"  / "metricas"  / "comparacao_modelos.csv"
CAMINHO_AVALIACAO = _ROOT / "outputs"  / "avaliacao" / "relatorio_avaliacao.json"
CAMINHO_EXEMPLO   = _ROOT / "data"     / "samples"   / "vendas_exemplo.csv"


# ── Disponibilidade da API ────────────────────────────────────────────────────

def api_disponivel() -> bool:
    if not API_BASE:
        return False
    try:
        r = requests.get(f"{API_BASE}/saude/", timeout=0.5)
        return r.status_code == 200
    except Exception:
        return False


# ── Carregamento de vendas ────────────────────────────────────────────────────

@st.cache_data(ttl=300)
def carregar_historico_vendas(data_inicio=None, data_fim=None) -> pd.DataFrame:
    """
    Carrega o histórico de vendas com fallback automático:
    API → arquivos processados → dados de exemplo sintéticos.
    """
    # 1. API
    if api_disponivel():
        params = {"limite": 5000}
        if data_inicio:
            params["data_inicio"] = str(data_inicio)
        if data_fim:
            params["data_fim"] = str(data_fim)
        try:
            r = requests.get(f"{API_BASE}/vendas/", params=params, timeout=5)
            if r.ok and r.json():
                df = pd.DataFrame(r.json())
                df["data"] = pd.to_datetime(df["data"])
                return df
        except Exception:
            pass

    # 2. Arquivos processados
    partes = [pd.read_csv(c, parse_dates=["data"])
              for c in [CAMINHO_TREINO, CAMINHO_TESTE] if c.exists()]
    if partes:
        df = pd.concat(partes, ignore_index=True)
        return _filtrar_periodo(df, data_inicio, data_fim)

    # 3. Dados de exemplo (demo)
    if CAMINHO_EXEMPLO.exists():
        df = pd.read_csv(CAMINHO_EXEMPLO, parse_dates=["data"])
        return _filtrar_periodo(df, data_inicio, data_fim)

    return pd.DataFrame()


def _filtrar_periodo(df, inicio, fim):
    if inicio and "data" in df.columns:
        df = df[df["data"] >= pd.Timestamp(inicio)]
    if fim and "data" in df.columns:
        df = df[df["data"] <= pd.Timestamp(fim)]
    return df


# ── Carregamento de produtos ──────────────────────────────────────────────────

@st.cache_data(ttl=300)
def carregar_produtos() -> pd.DataFrame:
    """Retorna lista de produtos — da API ou extraída dos dados de exemplo."""
    if api_disponivel():
        try:
            r = requests.get(f"{API_BASE}/produtos/", timeout=5)
            if r.ok:
                return pd.DataFrame(r.json())
        except Exception:
            pass

    # Extrai produtos únicos do histórico
    df = carregar_historico_vendas()
    if not df.empty and "produto" in df.columns:
        nomes = sorted(df["produto"].dropna().unique())
        return pd.DataFrame([
            {"id": i + 1, "nome": p, "categoria": "produto"}
            for i, p in enumerate(nomes)
        ])
    return pd.DataFrame(columns=["id", "nome", "categoria"])


# ── Métricas do modelo ────────────────────────────────────────────────────────

@st.cache_data(ttl=600)
def carregar_metricas() -> dict:
    import json
    if CAMINHO_AVALIACAO.exists():
        with open(CAMINHO_AVALIACAO, encoding="utf-8") as f:
            return json.load(f)
    # Métricas de demonstração (valores ilustrativos)
    return {
        "metricas_teste": {
            "mae": 4.2,
            "rmse": 6.1,
            "r2": 0.81,
            "mape": 12.3,
        },
        "modelo": "xgboost (demo)",
        "nota": "Valores ilustrativos — execute o pipeline para obter métricas reais.",
    }


# ── Previsões em arquivo ──────────────────────────────────────────────────────

@st.cache_data(ttl=300)
def carregar_previsoes_arquivo() -> pd.DataFrame:
    if CAMINHO_PREVISOES.exists():
        return pd.read_csv(CAMINHO_PREVISOES, parse_dates=["data"])
    return pd.DataFrame()


# ── Previsão individual ───────────────────────────────────────────────────────

def solicitar_previsao(data: date, produto_id: int, turno_id: int) -> dict | None:
    """Chama a API real se disponível; caso contrário retorna None."""
    if not api_disponivel():
        return None
    try:
        r = requests.post(f"{API_BASE}/previsoes/", json={
            "data": str(data), "produto_id": produto_id, "turno_id": turno_id,
        }, timeout=10)
        return r.json() if r.ok else None
    except Exception:
        return None


def simular_previsao(data: date, produto_nome: str, turno_nome: str) -> dict:
    """
    Previsão simulada para o modo demo.
    Usa a média histórica do produto×turno com variação determinística
    baseada na data (mesma entrada → mesmo resultado, parece um modelo real).
    """
    df = carregar_historico_vendas()

    media = 30.0  # fallback global
    if not df.empty and "quantidade_vendida" in df.columns:
        mask = pd.Series([True] * len(df), index=df.index)
        if "produto" in df.columns:
            mask &= df["produto"].str.lower() == produto_nome.lower()
        if "turno" in df.columns:
            mask &= df["turno"].str.lower() == turno_nome.lower()
        sub = df[mask]
        if not sub.empty:
            media = sub["quantidade_vendida"].mean()

    # Variação determinística por data (±15 %)
    semente = int(hashlib.md5(
        f"{data}{produto_nome}{turno_nome}".encode()
    ).hexdigest(), 16) % (2 ** 31)
    import random
    rng = random.Random(semente)
    variacao = rng.uniform(0.85, 1.15)
    qtd = round(max(0.0, media * variacao), 1)

    return {
        "quantidade_prevista": qtd,
        "modelo_utilizado": "baseline_demo",
    }


# ── Upload de arquivo pelo usuário ────────────────────────────────────────────

def carregar_csv_usuario(arquivo) -> pd.DataFrame | None:
    try:
        if arquivo.name.endswith(".csv"):
            df = pd.read_csv(arquivo, sep=None, engine="python")
        else:
            df = pd.read_excel(arquivo)
        if "data" in df.columns:
            df["data"] = pd.to_datetime(df["data"], dayfirst=True, errors="coerce")
        return df
    except Exception as exc:
        st.error(f"Erro ao carregar arquivo: {exc}")
        return None
