import sys
import os

import streamlit as st
import pandas as pd
from pathlib import Path

_ROOT = Path(__file__).resolve().parent.parent
_DASH = Path(__file__).resolve().parent
for _p in [str(_ROOT), str(_DASH)]:
    if _p not in sys.path:
        sys.path.insert(0, _p)

from componentes.carregador import (
    carregar_historico_vendas, carregar_metricas, api_disponivel,
)
from componentes.graficos import serie_temporal_vendas
from componentes.estilos import aplicar_estilos
from componentes.sidebar import renderizar_sidebar

st.set_page_config(
    page_title="PRATO — Previsão de Demanda",
    page_icon="favicon.png" if Path(_DASH / "favicon.png").exists() else None,
    layout="wide",
    initial_sidebar_state="expanded",
)

aplicar_estilos()
renderizar_sidebar(mostrar_upload=True)

# ── Corpo principal ─────────────────────────────────────────────────────────
st.title("Dashboard de Previsão de Demanda")

if not _api_ok:
    st.info(
        "Modo Demo — os dados abaixo são sintéticos. "
        "Conecte a API ou carregue um arquivo CSV para usar dados reais."
    )

df       = st.session_state.get("df_vendas", carregar_historico_vendas())
metricas = carregar_metricas()

st.markdown("### Visão Geral")
c1, c2, c3, c4 = st.columns(4)

if not df.empty and "quantidade_vendida" in df.columns:
    total_registros = len(df)
    total_vendas    = df["quantidade_vendida"].sum()
    n_produtos      = df["produto"].nunique() if "produto" in df.columns else "—"
    periodo = (
        f"{df['data'].min().strftime('%d/%m/%Y')} — {df['data'].max().strftime('%d/%m/%Y')}"
        if "data" in df.columns else "—"
    )
else:
    total_registros = total_vendas = n_produtos = 0
    periodo = "Sem dados"

c1.metric("Registros",       f"{total_registros:,}")
c2.metric("Unidades Vendidas", f"{total_vendas:,.0f}")
c3.metric("Produtos",        str(n_produtos))
c4.metric("Período",         periodo)

if not df.empty and "data" in df.columns:
    st.markdown("### Tendência de Vendas — últimos 60 dias")
    df_recente = df[df["data"] >= df["data"].max() - pd.Timedelta(days=60)]
    st.plotly_chart(serie_temporal_vendas(df_recente), use_container_width=True)
else:
    st.info("Carregue um arquivo CSV ou conecte-se à API para visualizar os dados.")

if metricas:
    st.markdown("### Desempenho do Modelo")
    m = metricas.get("metricas_teste", {})
    cm1, cm2, cm3 = st.columns(3)
    cm1.metric("MAE",  f"{m.get('mae',  '—'):.2f}" if isinstance(m.get("mae"),  float) else "—")
    cm2.metric("RMSE", f"{m.get('rmse', '—'):.2f}" if isinstance(m.get("rmse"), float) else "—")
    cm3.metric("R²",   f"{m.get('r2',   '—'):.3f}" if isinstance(m.get("r2"),   float) else "—")
    if metricas.get("nota"):
        st.caption(metricas["nota"])
