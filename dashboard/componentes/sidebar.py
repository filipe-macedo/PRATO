"""
sidebar.py
Sidebar compartilhada entre todas as páginas do dashboard PRATO.
Usa st.page_link para controle total da posição dos links de navegação.
"""

import streamlit as st
from componentes.carregador import api_disponivel


_PAGINAS = [
    ("Inicio.py",                     "Início"),
    ("pages/1_Historico_Vendas.py",   "Histórico de Vendas"),
    ("pages/2_Previsao_Demanda.py",   "Previsão de Demanda"),
    ("pages/4_Previsto_Realizado.py", "Previsto × Realizado"),
    ("pages/5_Apoio_Decisao.py",      "Apoio à Decisão"),
]


def renderizar_sidebar(mostrar_upload: bool = False) -> None:
    """
    Ordem: logo + status → nav links → upload (opcional) → rodapé.
    mostrar_upload=True apenas na página Início.
    """
    with st.sidebar:

        # ── 1. Logo ───────────────────────────────────────────────────────
        st.markdown("""
            <div style="padding:1rem 0 1rem 0">
                <span style="font-size:1.45rem;font-weight:800;color:#f1f5f9;
                             letter-spacing:-0.02em;font-family:sans-serif">PRATO</span>
                <span style="color:#27AE60;font-size:1.1rem;margin-left:3px">&#9679;</span>
                <div style="font-size:0.7rem;color:#475569;margin-top:4px;
                            font-weight:500;letter-spacing:0.05em;
                            text-transform:uppercase">
                    Previsão de Demanda
                </div>
            </div>
        """, unsafe_allow_html=True)

        # ── 2. Status — só mostra quando API está conectada ──────────────
        if api_disponivel():
            st.success("API Backend online")

        st.markdown("---")

        # ── 3. Navegação ──────────────────────────────────────────────────
        for caminho, label in _PAGINAS:
            try:
                st.page_link(caminho, label=label)
            except Exception:
                pass  # ignora se o arquivo não for encontrado

        # ── 4. Upload (só na página Início) ───────────────────────────────
        if mostrar_upload:
            st.markdown("---")
            st.markdown("**Usar seus próprios dados**")
            arquivo = st.file_uploader(
                "CSV ou Excel",
                type=["csv", "xlsx", "xls"],
                label_visibility="collapsed",
            )
            if arquivo:
                from componentes.carregador import carregar_csv_usuario
                df = carregar_csv_usuario(arquivo)
                if df is not None:
                    st.session_state["df_vendas"] = df
                    st.success(f"{len(df):,} registros carregados.")

        # ── 5. Rodapé ─────────────────────────────────────────────────────
        st.markdown("---")
        st.caption("v1.0.0 · github.com/filipe-macedo/PRATO")
