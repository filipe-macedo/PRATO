import sys
from pathlib import Path

_ROOT = Path(__file__).resolve().parent.parent.parent
_DASH = Path(__file__).resolve().parent.parent
for _p in [str(_ROOT), str(_DASH)]:
    if _p not in sys.path:
        sys.path.insert(0, _p)

import streamlit as st
from datetime import date, timedelta
from componentes.carregador import (
    carregar_produtos, api_disponivel,
    solicitar_previsao, simular_previsao,
    carregar_previsoes_arquivo, carregar_historico_vendas,
)
from componentes.graficos import gauge_risco
from componentes.alertas import classificar_risco, exibir_alerta
from componentes.estilos import aplicar_estilos

st.set_page_config(page_title="Previsão de Demanda | PRATO", layout="wide")
aplicar_estilos()

st.title("Previsão de Demanda")

_api_ok = api_disponivel()
if not _api_ok:
    st.info(
        "Modo Demo — previsão estimada com base na média histórica "
        "do produto e turno selecionados."
    )

TURNOS    = ["Café da Manhã", "Almoço", "Lanche", "Jantar"]
TURNOS_ID = {"Café da Manhã": 1, "Almoço": 2, "Lanche": 3, "Jantar": 4}

st.markdown("### Consulta Individual")
produtos_df   = carregar_produtos()
opcoes_produto = (
    {row["nome"]: row["id"] for _, row in produtos_df.iterrows()}
    if not produtos_df.empty else {}
)

col1, col2, col3 = st.columns(3)
data_sel     = col1.date_input("Data", value=date.today() + timedelta(days=1))
produto_nome = col2.selectbox("Produto", list(opcoes_produto.keys()) if opcoes_produto else ["(sem produtos)"])
turno_nome   = col3.selectbox("Turno", TURNOS)
capacidade_ref = st.number_input("Capacidade de produção (referência):", min_value=1, value=100, step=5)

if st.button("Gerar Previsão", type="primary", use_container_width=True):
    if not opcoes_produto:
        st.error("Nenhum produto disponível. Verifique os dados carregados.")
    else:
        with st.spinner("Calculando..."):
            if _api_ok:
                produto_id = opcoes_produto.get(produto_nome)
                turno_id   = TURNOS_ID[turno_nome]
                resultado  = solicitar_previsao(data_sel, produto_id, turno_id)
                if resultado is None:
                    st.warning("API não respondeu — usando simulação de fallback.")
                    resultado = simular_previsao(data_sel, produto_nome, turno_nome)
            else:
                resultado = simular_previsao(data_sel, produto_nome, turno_nome)

        if resultado:
            qtd = resultado["quantidade_prevista"]

            r1, r2, r3 = st.columns(3)
            r1.metric("Quantidade Prevista",  f"{qtd:.1f} unidades")
            r2.metric("Modelo",               resultado.get("modelo_utilizado", "—"))
            r3.metric("Ocupação estimada",    f"{qtd / capacidade_ref * 100:.0f}%")

            st.plotly_chart(gauge_risco(qtd, capacidade_ref), use_container_width=False)

            df_hist    = carregar_historico_vendas()
            media_hist = 0.0
            if not df_hist.empty and "produto" in df_hist.columns and "quantidade_vendida" in df_hist.columns:
                h          = df_hist[df_hist["produto"] == produto_nome]
                media_hist = float(h["quantidade_vendida"].mean()) if not h.empty else 0.0
            exibir_alerta(classificar_risco(qtd, media_hist))
        else:
            st.error("Não foi possível gerar a previsão.")

st.markdown("---")
st.markdown("### Previsões em Lote")
df_prev = carregar_previsoes_arquivo()
if not df_prev.empty:
    st.dataframe(df_prev.head(300), use_container_width=True, hide_index=True)
else:
    st.info("Execute `make pipeline` para gerar o arquivo de previsões em lote.")
