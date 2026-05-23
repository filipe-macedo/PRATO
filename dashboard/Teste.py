"""
Teste.py — página mínima para diagnóstico.
Se este arquivo funcionar no Streamlit Cloud, o problema está em Inicio.py.
Se não funcionar, o problema é de infraestrutura (config, Python, etc.).
"""
import sys
import os
import streamlit as st

st.set_page_config(page_title="PRATO — Teste", page_icon="🔧")

st.title("🔧 Diagnóstico PRATO")
st.success("✅ Streamlit está funcionando!")

st.markdown("### Informações do ambiente")
st.code(f"""
Python versão : {sys.version}
Diretório atual: {os.getcwd()}
""")

# Testa importação do pandas
try:
    import pandas as pd
    st.success(f"✅ pandas {pd.__version__}")
except Exception as e:
    st.error(f"❌ pandas: {e}")

# Testa importação do plotly
try:
    import plotly
    st.success(f"✅ plotly {plotly.__version__}")
except Exception as e:
    st.error(f"❌ plotly: {e}")

# Testa importação do componente carregador
st.markdown("### Teste de importações internas")
import sys
from pathlib import Path

_root = Path(__file__).resolve().parent.parent
_dash = Path(__file__).resolve().parent
for _p in [str(_root), str(_dash)]:
    if _p not in sys.path:
        sys.path.insert(0, _p)

try:
    from componentes.carregador import api_disponivel
    st.success("✅ componentes.carregador importado")
except Exception as e:
    st.error(f"❌ componentes.carregador: {e}")
    st.code(f"sys.path:\n" + "\n".join(sys.path[:6]))

try:
    from componentes.graficos import serie_temporal_vendas
    st.success("✅ componentes.graficos importado")
except Exception as e:
    st.error(f"❌ componentes.graficos: {e}")

st.markdown("---")
st.info("Se chegou até aqui, os imports estão OK. O problema era em Inicio.py.")
