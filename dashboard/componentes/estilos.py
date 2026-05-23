"""
estilos.py
CSS global injetado em todas as páginas do dashboard PRATO.
Chame aplicar_estilos() logo após st.set_page_config().
"""

import streamlit as st

_CSS = """
<style>

/* ═══════════════════════════════════════════════════════════════════════════
   SIDEBAR — fundo escuro
═══════════════════════════════════════════════════════════════════════════ */
[data-testid="stSidebar"] {
    background-color: #0f172a !important;
    border-right: 1px solid #1e293b !important;
}

/* texto genérico */
[data-testid="stSidebar"] p,
[data-testid="stSidebar"] span,
[data-testid="stSidebar"] small,
[data-testid="stSidebar"] .stMarkdown,
[data-testid="stSidebar"] .stMarkdown p {
    color: #94a3b8 !important;
}

/* títulos */
[data-testid="stSidebar"] h1,
[data-testid="stSidebar"] h2,
[data-testid="stSidebar"] h3,
[data-testid="stSidebar"] strong {
    color: #f1f5f9 !important;
}

/* separadores */
[data-testid="stSidebar"] hr {
    border-color: #1e293b !important;
    margin: 0.75rem 0 !important;
}

/* radio labels */
[data-testid="stSidebar"] label,
[data-testid="stSidebar"] .stRadio > label {
    color: #94a3b8 !important;
}

/* file uploader */
[data-testid="stSidebar"] [data-testid="stFileUploaderDropzone"] {
    background-color: #1e293b !important;
    border-color: #334155 !important;
}

/* botões dentro da sidebar */
[data-testid="stSidebar"] .stButton > button {
    background-color: #1e293b !important;
    color: #e2e8f0 !important;
    border: 1px solid #334155 !important;
    border-radius: 8px !important;
}
[data-testid="stSidebar"] .stButton > button:hover {
    background-color: #273548 !important;
    border-color: #475569 !important;
}

/* nav links (multipage) */
[data-testid="stSidebarNav"] a {
    border-radius: 8px !important;
    margin-bottom: 2px !important;
}
[data-testid="stSidebarNav"] a span {
    color: #94a3b8 !important;
    font-size: 0.875rem !important;
    font-weight: 500 !important;
}
[data-testid="stSidebarNav"] a:hover span {
    color: #e2e8f0 !important;
}
[data-testid="stSidebarNav"] [aria-selected="true"] span {
    color: #22c55e !important;
    font-weight: 600 !important;
}
[data-testid="stSidebarNav"] li[aria-selected="true"] {
    background-color: rgba(34, 197, 94, 0.12) !important;
}

/* alertas na sidebar */
[data-testid="stSidebar"] [data-testid="stAlert"] {
    background-color: #1e293b !important;
    border-color: #334155 !important;
    color: #94a3b8 !important;
}
[data-testid="stSidebar"] [data-testid="stAlert"] p {
    color: #94a3b8 !important;
}


/* ═══════════════════════════════════════════════════════════════════════════
   ÁREA PRINCIPAL
═══════════════════════════════════════════════════════════════════════════ */
.main .block-container {
    padding-top: 1.75rem !important;
    max-width: 1200px !important;
}


/* ═══════════════════════════════════════════════════════════════════════════
   TIPOGRAFIA
═══════════════════════════════════════════════════════════════════════════ */
h1 {
    font-size: 1.6rem !important;
    font-weight: 700 !important;
    color: #0f172a !important;
    letter-spacing: -0.02em !important;
    margin-bottom: 0.1rem !important;
}
h2 {
    font-size: 1.2rem !important;
    font-weight: 600 !important;
    color: #1e293b !important;
}
h3 {
    font-size: 0.8rem !important;
    font-weight: 600 !important;
    color: #64748b !important;
    text-transform: uppercase !important;
    letter-spacing: 0.07em !important;
    margin-top: 1.5rem !important;
    margin-bottom: 0.5rem !important;
}


/* ═══════════════════════════════════════════════════════════════════════════
   METRIC CARDS
═══════════════════════════════════════════════════════════════════════════ */
[data-testid="metric-container"] {
    background: #ffffff !important;
    border: 1px solid #e2e8f0 !important;
    border-radius: 14px !important;
    padding: 1.1rem 1.4rem !important;
    box-shadow: 0 1px 3px rgba(15, 23, 42, 0.06) !important;
}
[data-testid="stMetricLabel"] > div,
[data-testid="stMetricLabel"] label {
    font-size: 0.72rem !important;
    font-weight: 600 !important;
    color: #64748b !important;
    text-transform: uppercase !important;
    letter-spacing: 0.07em !important;
}
[data-testid="stMetricValue"] > div {
    font-size: 1.9rem !important;
    font-weight: 700 !important;
    color: #0f172a !important;
    line-height: 1.2 !important;
}
[data-testid="stMetricDelta"] svg { display: none !important; }
[data-testid="stMetricDelta"] > div {
    font-size: 0.78rem !important;
    font-weight: 600 !important;
}


/* ═══════════════════════════════════════════════════════════════════════════
   BOTÕES
═══════════════════════════════════════════════════════════════════════════ */
.stButton > button {
    border-radius: 8px !important;
    font-weight: 500 !important;
    font-size: 0.875rem !important;
    transition: all 0.15s ease !important;
}
.stButton > button[kind="primary"] {
    background-color: #22c55e !important;
    border-color: #22c55e !important;
    color: #ffffff !important;
    font-weight: 600 !important;
}
.stButton > button[kind="primary"]:hover {
    background-color: #16a34a !important;
    border-color: #16a34a !important;
    box-shadow: 0 2px 8px rgba(34, 197, 94, 0.35) !important;
}


/* ═══════════════════════════════════════════════════════════════════════════
   ABAS
═══════════════════════════════════════════════════════════════════════════ */
.stTabs [data-baseweb="tab-list"] {
    gap: 0 !important;
    border-bottom: 2px solid #e2e8f0 !important;
    background: transparent !important;
}
.stTabs [data-baseweb="tab"] {
    background: transparent !important;
    border: none !important;
    border-bottom: 2px solid transparent !important;
    margin-bottom: -2px !important;
    padding: 0.6rem 1.1rem !important;
    font-size: 0.875rem !important;
    font-weight: 500 !important;
    color: #64748b !important;
    border-radius: 0 !important;
}
.stTabs [data-baseweb="tab"]:hover {
    color: #334155 !important;
    background: transparent !important;
}
.stTabs [aria-selected="true"] {
    color: #22c55e !important;
    border-bottom: 2px solid #22c55e !important;
    font-weight: 600 !important;
}


/* ═══════════════════════════════════════════════════════════════════════════
   EXPANDERS
═══════════════════════════════════════════════════════════════════════════ */
[data-testid="stExpander"] {
    border: 1px solid #e2e8f0 !important;
    border-radius: 12px !important;
    overflow: hidden !important;
    background: #ffffff !important;
    box-shadow: 0 1px 2px rgba(15, 23, 42, 0.04) !important;
}
[data-testid="stExpander"] summary {
    background-color: #f8fafc !important;
    font-weight: 600 !important;
    font-size: 0.875rem !important;
    color: #1e293b !important;
    padding: 0.75rem 1rem !important;
}
[data-testid="stExpander"] summary:hover {
    background-color: #f1f5f9 !important;
}
[data-testid="stExpander"] > details > div {
    background: #ffffff !important;
    padding: 1rem !important;
}


/* ═══════════════════════════════════════════════════════════════════════════
   DATAFRAME / TABELAS
═══════════════════════════════════════════════════════════════════════════ */
[data-testid="stDataFrame"] {
    border: 1px solid #e2e8f0 !important;
    border-radius: 12px !important;
    overflow: hidden !important;
    background: #ffffff !important;
}


/* ═══════════════════════════════════════════════════════════════════════════
   ALERTAS / MENSAGENS
═══════════════════════════════════════════════════════════════════════════ */
[data-testid="stAlert"] {
    border-radius: 10px !important;
    font-size: 0.875rem !important;
}


/* ═══════════════════════════════════════════════════════════════════════════
   INPUTS / SELECTS
═══════════════════════════════════════════════════════════════════════════ */
[data-testid="stDateInput"] input,
[data-testid="stNumberInput"] input,
[data-baseweb="select"] {
    border-radius: 8px !important;
    border-color: #e2e8f0 !important;
    font-size: 0.875rem !important;
}
[data-baseweb="select"]:hover,
[data-testid="stDateInput"] input:hover {
    border-color: #22c55e !important;
}


/* ═══════════════════════════════════════════════════════════════════════════
   MISC
═══════════════════════════════════════════════════════════════════════════ */
hr {
    border-color: #e2e8f0 !important;
    margin: 1.25rem 0 !important;
}

/* esconde rodapé e menu hambúrguer do Streamlit */
footer          { visibility: hidden !important; }
#MainMenu       { visibility: hidden !important; }
header          { visibility: hidden !important; }

/* remove padding excessivo no topo quando header está oculto */
.main .block-container { padding-top: 1.75rem !important; }

</style>
"""


def aplicar_estilos() -> None:
    """Injeta o CSS global de identidade visual do PRATO."""
    st.markdown(_CSS, unsafe_allow_html=True)
