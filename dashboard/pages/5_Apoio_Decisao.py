import sys
from pathlib import Path

_ROOT = Path(__file__).resolve().parent.parent.parent  # PRATO/
_DASH = Path(__file__).resolve().parent.parent          # PRATO/dashboard/
for _p in [str(_ROOT), str(_DASH)]:
    if _p not in sys.path:
        sys.path.insert(0, _p)

import streamlit as st
from componentes.carregador import carregar_historico_vendas, carregar_previsoes_arquivo
from componentes.alertas import resumo_riscos_tabela
from componentes.tabelas import formatar_tabela_riscos

st.set_page_config(page_title="Apoio à Decisão | PRATO", layout="wide")
st.title("🧭 Apoio à Decisão Operacional")

df_hist = carregar_historico_vendas()
df_prev = carregar_previsoes_arquivo()

st.markdown("### Alertas de Risco — Próximo Período")
if not df_prev.empty and not df_hist.empty:
    df_riscos = resumo_riscos_tabela(df_prev, df_hist)
    if not df_riscos.empty:
        n_excesso = (df_riscos["risco"] == "🔴 Excesso").sum()
        n_falta = (df_riscos["risco"] == "🟡 Falta").sum()
        n_normal = (df_riscos["risco"] == "🟢 Normal").sum()
        ra, rb, rc = st.columns(3)
        ra.metric("🔴 Excesso", n_excesso)
        rb.metric("🟡 Falta", n_falta)
        rc.metric("🟢 Normal", n_normal)
        formatar_tabela_riscos(df_riscos)
        st.download_button("⬇ Exportar alertas",
                           df_riscos.to_csv(index=False).encode("utf-8"),
                           "alertas_risco.csv", "text/csv")

st.markdown("---")
st.markdown("### Recomendações por Turno")
RECOMENDACOES = {
    "Almoço ☀": {
        "falta": "Antecipe o pré-preparo desde as 9h. Acione cozinheiros extras se previsão > 120% da média.",
        "excesso": "Reduza quantidade de ingredientes perecíveis. Considere promoção de meia-porção.",
    },
    "Jantar 🌙": {
        "falta": "Confirme reservas com antecedência. Mantenha estoque de ingredientes base disponível.",
        "excesso": "Avalie desconto progressivo após 21h para reduzir sobras.",
    },
    "Café da Manhã 🌅": {
        "falta": "Prepare itens perecíveis somente após confirmação de demanda.",
        "excesso": "Combine com estoque do dia anterior. Reaproveite ingredientes compatíveis.",
    },
    "Lanche 🥪": {
        "falta": "Prepare lotes menores a cada 30 min para garantir frescor.",
        "excesso": "Reduza lote inicial e reponha conforme saída.",
    },
}
for turno, info in RECOMENDACOES.items():
    with st.expander(turno):
        c1, c2 = st.columns(2)
        c1.error(f"**Se houver falta:**\n\n{info['falta']}")
        c2.warning(f"**Se houver excesso:**\n\n{info['excesso']}")

st.markdown("---")
st.markdown("### Checklist Diário de Operações")
st.markdown("""
| Etapa | Responsável | Prazo |
|---|---|---|
| Verificar previsão do dia | Gerente / Cozinha | Até 08h |
| Confirmar estoque de ingredientes | Estoque | Até 09h |
| Ajustar mise en place por turno | Cozinha | 1h antes de cada turno |
| Registrar vendas reais | Caixa / PDV | Durante o turno |
| Comparar previsto × realizado | Gerente | Após fechamento |
| Atualizar base de dados | TI / Dados | Semanalmente |
""")
