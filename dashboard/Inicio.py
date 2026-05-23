import sys
import os

import streamlit as st
import pandas as pd
from pathlib import Path

# Garante que dashboard/ e a raiz do projeto estão no sys.path
_ROOT = Path(__file__).resolve().parent.parent   # PRATO/
_DASH = Path(__file__).resolve().parent           # PRATO/dashboard/
for _p in [str(_ROOT), str(_DASH)]:
    if _p not in sys.path:
        sys.path.insert(0, _p)

from componentes.carregador import (
    carregar_historico_vendas, carregar_metricas,
    carregar_csv_usuario, api_disponivel,
)
from componentes.graficos import serie_temporal_vendas

# ── Configuração da página ──────────────────────────────────────────────────
st.set_page_config(
    page_title="PRATO — Previsão de Demanda",
    page_icon="🍽",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ── Sidebar ─────────────────────────────────────────────────────────────────
with st.sidebar:
    st.title("🍽 PRATO")
    st.caption("Sistema de Previsão de Demanda")
    st.markdown("---")

    _api_ok = api_disponivel()

    if _api_ok:
        st.markdown("**Fonte de dados**")
        st.success("🟢 API Backend online")
        if st.button("Atualizar dados"):
            st.cache_data.clear()
    else:
        st.info("✅ Dados de demonstração carregados automaticamente")
        st.caption(
            "Este é o modo demo — os dados são sintéticos e as previsões "
            "são estimadas com base no histórico de exemplo."
        )
        st.markdown("---")
        st.markdown("**Carregar seus próprios dados**")
        arquivo = st.file_uploader(
            "CSV ou Excel de vendas (opcional)",
            type=["csv", "xlsx", "xls"],
        )
        if arquivo:
            df_usuario = carregar_csv_usuario(arquivo)
            if df_usuario is not None:
                st.session_state["df_vendas"] = df_usuario
                st.success(f"{len(df_usuario):,} registros carregados.")

    st.markdown("---")
    st.caption("PRATO v1.0 · github.com/filipe-macedo/PRATO")

# ── Corpo principal ─────────────────────────────────────────────────────────
st.title("🍽 PRATO — Sistema de Previsão de Demanda")

if not api_disponivel():
    st.info(
        "⚠️ **Modo Demo** — exibindo dados sintéticos. "
        "Conecte a API ou carregue um CSV na barra lateral para usar dados reais."
    )

st.markdown(
    "Bem-vindo ao painel. Navegue pelas páginas no menu lateral para explorar "
    "o histórico de vendas, consultar previsões e acompanhar o desempenho do modelo."
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
        f"{df['data'].min().strftime('%d/%m/%Y')} a {df['data'].max().strftime('%d/%m/%Y')}"
        if "data" in df.columns else "—"
    )
else:
    total_registros = total_vendas = n_produtos = 0
    periodo = "Sem dados"

c1.metric("Total de Registros", f"{total_registros:,}")
c2.metric("Unidades Vendidas",  f"{total_vendas:,.0f}")
c3.metric("Produtos Únicos",    str(n_produtos))
c4.metric("Período dos Dados",  periodo)

if not df.empty and "data" in df.columns:
    st.markdown("### Tendência de Vendas (últimos 60 dias)")
    df_recente = df[df["data"] >= df["data"].max() - pd.Timedelta(days=60)]
    st.plotly_chart(serie_temporal_vendas(df_recente), use_container_width=True)
else:
    st.info("Carregue um arquivo CSV ou conecte-se à API para visualizar os dados.")

if metricas:
    st.markdown("### Desempenho do Modelo Atual")
    m = metricas.get("metricas_teste", {})
    cm1, cm2, cm3 = st.columns(3)
    cm1.metric("MAE",  f"{m.get('mae',  '—'):.2f}" if isinstance(m.get("mae"),  float) else "—")
    cm2.metric("RMSE", f"{m.get('rmse', '—'):.2f}" if isinstance(m.get("rmse"), float) else "—")
    cm3.metric("R²",   f"{m.get('r2',   '—'):.3f}" if isinstance(m.get("r2"),   float) else "—")
    if metricas.get("nota"):
        st.caption(f"ℹ️ {metricas['nota']}")
