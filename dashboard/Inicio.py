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
    carregar_historico_vendas, carregar_metricas,
    carregar_csv_usuario, api_disponivel,
)
from componentes.graficos import serie_temporal_vendas
from componentes.estilos import aplicar_estilos

st.set_page_config(
    page_title="PRATO — Previsão de Demanda",
    page_icon="favicon.png" if Path(_DASH / "favicon.png").exists() else None,
    layout="wide",
    initial_sidebar_state="expanded",
)

aplicar_estilos()

# ── Sidebar ─────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("""
        <div style="padding:0.25rem 0 1.5rem 0">
            <span style="font-size:1.45rem;font-weight:800;color:#f1f5f9;
                         letter-spacing:-0.02em;font-family:sans-serif">PRATO</span>
            <span style="color:#22c55e;font-size:1.1rem;margin-left:3px">&#9679;</span>
            <div style="font-size:0.7rem;color:#475569;margin-top:4px;
                        font-weight:500;letter-spacing:0.05em;text-transform:uppercase">
                Previsão de Demanda
            </div>
        </div>
    """, unsafe_allow_html=True)

    _api_ok = api_disponivel()

    if _api_ok:
        st.success("API Backend online")
        if st.button("Atualizar dados"):
            st.cache_data.clear()
    else:
        st.info("Modo demo — dados sintéticos carregados automaticamente.")
        st.caption(
            "Previsões estimadas com base no histórico de exemplo."
        )
        st.markdown("---")
        st.markdown("**Usar seus próprios dados**")
        arquivo = st.file_uploader(
            "Arquivo CSV ou Excel (opcional)",
            type=["csv", "xlsx", "xls"],
        )
        if arquivo:
            df_usuario = carregar_csv_usuario(arquivo)
            if df_usuario is not None:
                st.session_state["df_vendas"] = df_usuario
                st.success(f"{len(df_usuario):,} registros carregados.")

    st.markdown("---")
    st.caption("v1.0.0 · github.com/filipe-macedo/PRATO")

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
