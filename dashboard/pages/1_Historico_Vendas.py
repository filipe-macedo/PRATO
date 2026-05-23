import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

import streamlit as st
import pandas as pd
from componentes.carregador import carregar_historico_vendas
from componentes.graficos import serie_temporal_vendas, barras_por_produto, heatmap_dia_turno
from componentes.tabelas import tabela_vendas_resumo

st.set_page_config(page_title="Histórico de Vendas | PRATO", layout="wide")
st.title("📊 Histórico de Vendas")

df = st.session_state.get("df_vendas", carregar_historico_vendas())

if df.empty:
    st.warning("Nenhum dado disponível. Carregue um arquivo na página Início.")
    st.stop()

with st.expander("Filtros", expanded=True):
    col1, col2, col3 = st.columns(3)
    data_min = df["data"].min().date()
    data_max = df["data"].max().date()
    intervalo = col1.date_input("Período", value=(data_min, data_max),
                                min_value=data_min, max_value=data_max)
    produtos_sel = col2.multiselect("Produtos", sorted(df["produto"].unique()) if "produto" in df.columns else [])
    turnos_sel = col3.multiselect("Turnos", sorted(df["turno"].unique()) if "turno" in df.columns else [])

df_filt = df.copy()
if len(intervalo) == 2:
    df_filt = df_filt[(df_filt["data"].dt.date >= intervalo[0]) & (df_filt["data"].dt.date <= intervalo[1])]
if produtos_sel:
    df_filt = df_filt[df_filt["produto"].isin(produtos_sel)]
if turnos_sel:
    df_filt = df_filt[df_filt["turno"].isin(turnos_sel)]

st.caption(f"{len(df_filt):,} registros após filtros.")

tab1, tab2, tab3 = st.tabs(["Série Temporal", "Por Produto", "Dia × Turno"])
with tab1:
    st.plotly_chart(serie_temporal_vendas(df_filt), use_container_width=True)
with tab2:
    top_n = st.slider("Produtos exibidos", 5, 30, 15)
    st.plotly_chart(barras_por_produto(df_filt, top_n=top_n), use_container_width=True)
with tab3:
    if "turno" in df_filt.columns:
        st.plotly_chart(heatmap_dia_turno(df_filt), use_container_width=True)

with st.expander("Ver tabela de dados"):
    st.dataframe(tabela_vendas_resumo(df_filt).head(500), use_container_width=True, hide_index=True)
    st.download_button("⬇ Exportar CSV",
                       df_filt.to_csv(index=False).encode("utf-8"),
                       "historico_filtrado.csv", "text/csv")
