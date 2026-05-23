import os
import pandas as pd
import requests
import streamlit as st
from pathlib import Path
from datetime import date

# API_URL pode ser definida via variável de ambiente (Streamlit Cloud Secrets
# ou Render env vars). Fallback para localhost em desenvolvimento local.
API_BASE = os.getenv("API_URL", "http://localhost:8000").rstrip("/")

# Caminhos absolutos — funcionam tanto localmente quanto no Streamlit Cloud.
# carregador.py fica em dashboard/componentes/, então .parent.parent.parent = PRATO/
_ROOT = Path(__file__).resolve().parent.parent.parent
CAMINHO_PREVISOES = _ROOT / "outputs" / "previsoes" / "previsoes_melhor_modelo.csv"
CAMINHO_TREINO    = _ROOT / "data"    / "processed" / "vendas_treino.csv"
CAMINHO_TESTE     = _ROOT / "data"    / "processed" / "vendas_teste.csv"
CAMINHO_METRICAS  = _ROOT / "outputs" / "metricas"  / "comparacao_modelos.csv"
CAMINHO_AVALIACAO = _ROOT / "outputs" / "avaliacao" / "relatorio_avaliacao.json"


def api_disponivel() -> bool:
    try:
        r = requests.get(f"{API_BASE}/saude/", timeout=0.5)
        return r.status_code == 200
    except Exception:
        return False


@st.cache_data(ttl=60)
def carregar_produtos() -> pd.DataFrame:
    if api_disponivel():
        r = requests.get(f"{API_BASE}/produtos/")
        if r.ok:
            return pd.DataFrame(r.json())
    return pd.DataFrame(columns=["id", "nome", "categoria"])


@st.cache_data(ttl=60)
def carregar_historico_vendas(data_inicio=None, data_fim=None) -> pd.DataFrame:
    if api_disponivel():
        params = {"limite": 1000}
        if data_inicio:
            params["data_inicio"] = str(data_inicio)
        if data_fim:
            params["data_fim"] = str(data_fim)
        r = requests.get(f"{API_BASE}/vendas/", params=params)
        if r.ok and r.json():
            df = pd.DataFrame(r.json())
            df["data"] = pd.to_datetime(df["data"])
            return df

    for caminho in [CAMINHO_TREINO, CAMINHO_TESTE]:
        if caminho.exists():
            partes = [pd.read_csv(c, parse_dates=["data"]) for c in [CAMINHO_TREINO, CAMINHO_TESTE] if c.exists()]
            if partes:
                return pd.concat(partes, ignore_index=True)
    return pd.DataFrame()


@st.cache_data(ttl=300)
def carregar_metricas() -> dict:
    import json
    if CAMINHO_AVALIACAO.exists():
        with open(CAMINHO_AVALIACAO, encoding="utf-8") as f:
            return json.load(f)
    return {}


@st.cache_data(ttl=300)
def carregar_previsoes_arquivo() -> pd.DataFrame:
    if CAMINHO_PREVISOES.exists():
        return pd.read_csv(CAMINHO_PREVISOES, parse_dates=["data"])
    return pd.DataFrame()


def solicitar_previsao(data: date, produto_id: int, turno_id: int) -> dict | None:
    if not api_disponivel():
        return None
    try:
        r = requests.post(f"{API_BASE}/previsoes/", json={
            "data": str(data), "produto_id": produto_id, "turno_id": turno_id,
        }, timeout=10)
        return r.json() if r.ok else None
    except Exception:
        return None


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
