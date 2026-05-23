import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

import streamlit as st
from datetime import date, timedelta
from componentes.carregador import carregar_produtos, solicitar_previsao, carregar_previsoes_arquivo, carregar_historico_vendas
from componentes.graficos import gauge_risco
from componentes.alertas import classificar_risco, exibir_alerta

st.set_page_config(page_title="Previsão de Demanda | PRATO", layout="wide")
st.title("🔮 Previsão de Demanda")

TURNOS = {"1 — Café da Manhã": 1, "2 — Almoço": 2, "3 — Lanche": 3, "4 — Jantar": 4}

st.markdown("### Consulta por Data, Produto e Turno")
produtos_df = carregar_produtos()
opcoes_produto = {row["nome"]: row["id"] for _, row in produtos_df.iterrows()} if not produtos_df.empty else {}

col1, col2, col3 = st.columns(3)
data_sel = col1.date_input("Data da previsão", value=date.today() + timedelta(days=1))
produto_nome = col2.selectbox("Produto", list(opcoes_produto.keys()) if opcoes_produto else ["(sem produtos)"])
turno_nome = col3.selectbox("Turno", list(TURNOS.keys()))
capacidade_ref = st.number_input("Capacidade de produção (referência):", min_value=1, value=100, step=5)

if st.button("Gerar Previsão", type="primary", use_container_width=True):
    produto_id = opcoes_produto.get(produto_nome)
    turno_id = TURNOS[turno_nome]
    if produto_id:
        with st.spinner("Consultando modelo..."):
            resultado = solicitar_previsao(data_sel, produto_id, turno_id)
        if resultado:
            qtd = resultado["quantidade_prevista"]
            r1, r2, r3 = st.columns(3)
            r1.metric("Quantidade Prevista", f"{qtd:.1f} unidades")
            r2.metric("Modelo", resultado.get("modelo_utilizado", "—"))
            r3.metric("Ocupação", f"{qtd/capacidade_ref*100:.0f}%")
            st.plotly_chart(gauge_risco(qtd, capacidade_ref), use_container_width=False)
            df_hist = carregar_historico_vendas()
            media_hist = 0
            if not df_hist.empty and "produto" in df_hist.columns:
                h = df_hist[df_hist["produto"] == produto_nome]
                media_hist = h["quantidade_vendida"].mean() if not h.empty else 0
            exibir_alerta(classificar_risco(qtd, media_hist))
        else:
            st.error("Não foi possível obter a previsão. Verifique se a API está ativa.")

st.markdown("---")
st.markdown("### Previsões em Lote (arquivo do modelo)")
df_prev = carregar_previsoes_arquivo()
if not df_prev.empty:
    st.dataframe(df_prev.head(300), use_container_width=True, hide_index=True)
else:
    st.info("Execute `make pipeline` para gerar previsões.")
