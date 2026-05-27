"""
estilos.py
CSS global injetado em todas as páginas do dashboard PRATO.
Chame aplicar_estilos() logo após st.set_page_config().
"""

import streamlit as st

_CSS = """
<style>

/* ═══════════════════════════════════════════════════════════════════════════
   SIDEBAR — fundo escuro (slate #2C3E50)
═══════════════════════════════════════════════════════════════════════════ */
[data-testid="stSidebar"] {
    background-color: #2C3E50 !important;
    border-right: 1px solid #1a252f !important;
}

/* ── Esconde o nav automático do Streamlit multipage ────────────────────── *
   Usamos st.page_link() para controle total da posição e ordem dos links. */
[data-testid="stSidebarNav"] {
    display: none !important;
}

/* ── Sidebar sempre visível — remove botões de collapse/expand ───────────── */
[data-testid="stSidebarCollapseButton"],
[data-testid="stSidebarCollapsedControl"] {
    display: none !important;
}

/* texto genérico */
[data-testid="stSidebar"] p,
[data-testid="stSidebar"] span,
[data-testid="stSidebar"] small,
[data-testid="stSidebar"] .stMarkdown,
[data-testid="stSidebar"] .stMarkdown p {
    color: #95a5a6 !important;
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
    border-color: #1a252f !important;
    margin: 0.75rem 0 !important;
}

/* radio labels */
[data-testid="stSidebar"] label,
[data-testid="stSidebar"] .stRadio > label {
    color: #95a5a6 !important;
}

/* file uploader */
[data-testid="stSidebar"] [data-testid="stFileUploaderDropzone"] {
    background-color: #1a252f !important;
    border-color: #2c3e50 !important;
}

/* botões dentro da sidebar */
[data-testid="stSidebar"] .stButton > button {
    background-color: #1a252f !important;
    color: #f1f5f9 !important;
    border: 1px solid #34495e !important;
    border-radius: 8px !important;
}
[data-testid="stSidebar"] .stButton > button:hover {
    background-color: #243342 !important;
    border-color: #4a6278 !important;
}

/* alertas na sidebar */
[data-testid="stSidebar"] [data-testid="stAlert"] {
    background-color: #1a252f !important;
    border-color: #34495e !important;
    color: #95a5a6 !important;
}
[data-testid="stSidebar"] [data-testid="stAlert"] p {
    color: #95a5a6 !important;
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
    color: #2C3E50 !important;
    letter-spacing: -0.02em !important;
    margin-bottom: 0.1rem !important;
}
h2 {
    font-size: 1.2rem !important;
    font-weight: 600 !important;
    color: #2C3E50 !important;
}
h3 {
    font-size: 0.8rem !important;
    font-weight: 700 !important;
    color: #7f8c8d !important;
    text-transform: uppercase !important;
    letter-spacing: 0.07em !important;
    margin-top: 1.5rem !important;
    margin-bottom: 0.5rem !important;
}


/* ═══════════════════════════════════════════════════════════════════════════
   METRIC CARDS (Streamlit native)
═══════════════════════════════════════════════════════════════════════════ */
[data-testid="metric-container"] {
    background: #ffffff !important;
    border: 1px solid #dde1e7 !important;
    border-radius: 14px !important;
    padding: 1.1rem 1.4rem !important;
    box-shadow: 0 2px 8px rgba(44, 62, 80, 0.08) !important;
}
[data-testid="stMetricLabel"] > div,
[data-testid="stMetricLabel"] label {
    font-size: 0.72rem !important;
    font-weight: 700 !important;
    color: #7f8c8d !important;
    text-transform: uppercase !important;
    letter-spacing: 0.07em !important;
}
[data-testid="stMetricValue"] > div {
    font-size: 1.9rem !important;
    font-weight: 700 !important;
    color: #2C3E50 !important;
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
    background-color: #27AE60 !important;
    border-color: #27AE60 !important;
    color: #ffffff !important;
    font-weight: 600 !important;
}
.stButton > button[kind="primary"]:hover {
    background-color: #219a52 !important;
    border-color: #219a52 !important;
    box-shadow: 0 2px 8px rgba(39, 174, 96, 0.35) !important;
}


/* ═══════════════════════════════════════════════════════════════════════════
   ABAS
═══════════════════════════════════════════════════════════════════════════ */
.stTabs [data-baseweb="tab-list"] {
    gap: 0 !important;
    border-bottom: 2px solid #dde1e7 !important;
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
    color: #7f8c8d !important;
    border-radius: 0 !important;
}
.stTabs [data-baseweb="tab"]:hover {
    color: #2C3E50 !important;
    background: transparent !important;
}
.stTabs [aria-selected="true"] {
    color: #27AE60 !important;
    border-bottom: 2px solid #27AE60 !important;
    font-weight: 700 !important;
}


/* ═══════════════════════════════════════════════════════════════════════════
   EXPANDERS
═══════════════════════════════════════════════════════════════════════════ */
[data-testid="stExpander"] {
    border: 1px solid #dde1e7 !important;
    border-radius: 12px !important;
    overflow: hidden !important;
    background: #ffffff !important;
    box-shadow: 0 1px 4px rgba(44, 62, 80, 0.06) !important;
}
[data-testid="stExpander"] summary {
    background-color: #f8f9fa !important;
    font-weight: 600 !important;
    font-size: 0.875rem !important;
    color: #2C3E50 !important;
    padding: 0.75rem 1rem !important;
}
[data-testid="stExpander"] summary:hover {
    background-color: #ECF0F1 !important;
}
[data-testid="stExpander"] > details > div {
    background: #ffffff !important;
    padding: 1rem !important;
}


/* ═══════════════════════════════════════════════════════════════════════════
   DATAFRAME / TABELAS
═══════════════════════════════════════════════════════════════════════════ */
[data-testid="stDataFrame"] {
    border: 1px solid #dde1e7 !important;
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
    border-color: #dde1e7 !important;
    font-size: 0.875rem !important;
}
[data-baseweb="select"]:hover,
[data-testid="stDateInput"] input:hover {
    border-color: #27AE60 !important;
}


/* ═══════════════════════════════════════════════════════════════════════════
   RADIO — filter bar
═══════════════════════════════════════════════════════════════════════════ */
[data-testid="stRadio"] label {
    font-size: 0.875rem !important;
    font-weight: 500 !important;
}


/* ═══════════════════════════════════════════════════════════════════════════
   MISC
═══════════════════════════════════════════════════════════════════════════ */
hr {
    border-color: #dde1e7 !important;
    margin: 1.25rem 0 !important;
}

/* esconde rodapé e menu hambúrguer */
footer    { visibility: hidden !important; }
#MainMenu { visibility: hidden !important; }

/* esconde barra de ferramentas interna (deploy, running…) */
[data-testid="stToolbar"]      { visibility: hidden !important; }
[data-testid="stStatusWidget"] { visibility: hidden !important; }
[data-testid="stDecoration"]   { display: none !important; }

/* header transparente e sem altura extra */
header {
    background: transparent !important;
    height: auto !important;
}

</style>
"""


def aplicar_estilos() -> None:
    """Injeta o CSS global de identidade visual do PRATO."""
    st.markdown(_CSS, unsafe_allow_html=True)
