import sys
from pathlib import Path

_ROOT = Path(__file__).resolve().parent.parent.parent  # PRATO/
_DASH = Path(__file__).resolve().parent.parent          # PRATO/dashboard/
for _p in [str(_ROOT), str(_DASH)]:
    if _p not in sys.path:
        sys.path.insert(0, _p)

import streamlit as st
import plotly.graph_objects as go
from componentes.carregador import carregar_metricas
from componentes.tabelas import tabela_metricas_modelos

st.set_page_config(page_title="Métricas do Modelo | PRATO", layout="wide")
st.title("📈 Métricas do Modelo")

metricas = carregar_metricas()
if not metricas:
    st.warning("Nenhuma métrica encontrada. Execute:\n```\nmake pipeline\n```")
    st.stop()

criterios = metricas.get("criterios_aceitacao", {})
if criterios:
    veredicto = criterios.get("veredicto_geral", "INDEFINIDO")
    fn = {"APROVADO": st.success, "ATENCAO": st.warning, "REPROVADO": st.error}.get(veredicto, st.info)
    fn(f"**Veredicto Geral do Modelo: {veredicto}**")

st.markdown("### Métricas no Conjunto de Teste")
m = metricas.get("metricas_teste", {})
if m:
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("MAE", f"{m.get('mae', '—'):.2f}" if isinstance(m.get("mae"), float) else "—")
    c2.metric("RMSE", f"{m.get('rmse', '—'):.2f}" if isinstance(m.get("rmse"), float) else "—")
    c3.metric("R²", f"{m.get('r2', '—'):.3f}" if isinstance(m.get("r2"), float) else "—")
    c4.metric("MAPE", f"{m.get('mape', '—'):.1f}%" if isinstance(m.get("mape"), float) else "—")

st.markdown("### Comparação entre Modelos")
df_comp = tabela_metricas_modelos(metricas)
if not df_comp.empty:
    st.dataframe(df_comp, use_container_width=True, hide_index=True)

st.markdown("### Gráficos de Avaliação")
imgs = [
    (_ROOT / "outputs" / "avaliacao" / "residuos_analise.png", "Análise de Resíduos"),
    (_ROOT / "outputs" / "avaliacao" / "curva_cumulativa_erro.png", "Curva Cumulativa"),
]
cols = st.columns(len(imgs))
for col, (caminho, titulo) in zip(cols, imgs):
    if caminho.exists():
        col.image(str(caminho), caption=titulo, use_column_width=True)
    else:
        col.info(f"Execute `make pipeline` para gerar '{titulo}'.")
