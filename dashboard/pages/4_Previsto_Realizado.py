import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

import numpy as np
import streamlit as st
import pandas as pd
from componentes.carregador import carregar_historico_vendas, carregar_previsoes_arquivo
from componentes.graficos import previsto_vs_realizado, dispersao_previsto_realizado, distribuicao_erros

st.set_page_config(page_title="Previsto × Realizado | PRATO", layout="wide")
st.title("⚖ Previsto × Realizado")

df_hist = carregar_historico_vendas()
df_prev = carregar_previsoes_arquivo()

if df_hist.empty or df_prev.empty:
    st.warning("Necessário histórico de vendas e arquivo de previsões. Execute `make pipeline`.")
    st.stop()

chaves = [c for c in ["data", "produto", "turno"] if c in df_hist.columns and c in df_prev.columns]
df_merged = df_hist.merge(df_prev[chaves + ["quantidade_prevista"]], on=chaves, how="inner")

if df_merged.empty:
    st.warning("Nenhum período em comum entre histórico e previsões.")
    st.stop()

col1, col2 = st.columns(2)
if "produto" in df_merged.columns:
    prod_sel = col1.selectbox("Produto", ["Todos"] + sorted(df_merged["produto"].unique()))
    if prod_sel != "Todos":
        df_merged = df_merged[df_merged["produto"] == prod_sel]
if "turno" in df_merged.columns:
    turno_sel = col2.selectbox("Turno", ["Todos"] + sorted(df_merged["turno"].unique()))
    if turno_sel != "Todos":
        df_merged = df_merged[df_merged["turno"] == turno_sel]

df_agg = (df_merged.groupby("data")[["quantidade_vendida", "quantidade_prevista"]]
          .sum().reset_index().sort_values("data"))

erro = df_agg["quantidade_prevista"] - df_agg["quantidade_vendida"]
mae = np.abs(erro).mean()
rmse = np.sqrt((erro**2).mean())
bias = erro.mean()
within_20 = (np.abs(erro) / df_agg["quantidade_vendida"].replace(0, np.nan) <= 0.20).mean() * 100

m1, m2, m3, m4 = st.columns(4)
m1.metric("MAE", f"{mae:.1f}")
m2.metric("RMSE", f"{rmse:.1f}")
m3.metric("Bias médio", f"{bias:+.1f}")
m4.metric("Dentro de ±20%", f"{within_20:.0f}%")

tab1, tab2, tab3 = st.tabs(["Série Temporal", "Dispersão", "Distribuição de Erros"])
with tab1:
    st.plotly_chart(previsto_vs_realizado(df_agg), use_container_width=True)
with tab2:
    st.plotly_chart(dispersao_previsto_realizado(df_agg), use_container_width=True)
with tab3:
    st.plotly_chart(distribuicao_erros(df_agg), use_container_width=True)
