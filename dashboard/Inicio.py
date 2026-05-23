import sys
import os

# ── Diagnóstico de startup — visível em "App logs" no Streamlit Cloud ──────
print("=== PRATO startup ===", flush=True)
print(f"Python: {sys.version}", flush=True)
print(f"CWD: {os.getcwd()}", flush=True)

import streamlit as st
import pandas as pd
from pathlib import Path

# Garante que dashboard/ e a raiz do projeto estão no sys.path
_ROOT = Path(__file__).resolve().parent.parent   # PRATO/
_DASH = Path(__file__).resolve().parent           # PRATO/dashboard/
for _p in [str(_ROOT), str(_DASH)]:
    if _p not in sys.path:
        sys.path.insert(0, _p)

print(f"ROOT: {_ROOT}", flush=True)
print(f"DASH: {_DASH}", flush=True)
print(f"sys.path[:4]: {sys.path[:4]}", flush=True)

# Importações com captura de erro explícita
try:
    from componentes.carregador import (
        carregar_historico_vendas, carregar_metricas,
        carregar_csv_usuario, api_disponivel,
    )
    print("✅ carregador importado", flush=True)
except Exception as _e:
    print(f"❌ Erro ao importar carregador: {_e}", flush=True)
    st.error(f"Erro de importação (carregador): {_e}")
    st.stop()

try:
    from componentes.graficos import serie_temporal_vendas
    print("✅ graficos importado", flush=True)
except Exception as _e:
    print(f"❌ Erro ao importar graficos: {_e}", flush=True)
    st.error(f"Erro de importação (graficos): {_e}")
    st.stop()

print("✅ Todos os imports OK — iniciando interface", flush=True)

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
    st.markdown("**Fonte de dados**")

    _api_ok = api_disponivel()
    fonte = st.radio(
        "Origem:",
        ["Arquivo CSV/Excel", "API Backend"],
        index=1 if _api_ok else 0,
    )

    if fonte == "Arquivo CSV/Excel":
        arquivo = st.file_uploader(
            "Carregue o arquivo de vendas",
            type=["csv", "xlsx", "xls"],
        )
        if arquivo:
            df_usuario = carregar_csv_usuario(arquivo)
            if df_usuario is not None:
                st.session_state["df_vendas"] = df_usuario
                st.success(f"{len(df_usuario):,} registros carregados.")
    else:
        status = "🟢 Online" if _api_ok else "🔴 Offline"
        st.markdown(f"**Status API:** {status}")
        if st.button("Atualizar dados"):
            st.cache_data.clear()

    st.markdown("---")
    st.caption("PRATO v1.0 · github.com/filipe-macedo")

# ── Corpo principal ─────────────────────────────────────────────────────────
st.title("🍽 PRATO — Sistema de Previsão de Demanda")
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
