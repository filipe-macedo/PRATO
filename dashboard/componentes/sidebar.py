"""
sidebar.py
Sidebar compartilhada entre todas as páginas.
Chame renderizar_sidebar() em cada página após aplicar_estilos().
"""

import streamlit as st
from componentes.carregador import api_disponivel


def renderizar_sidebar(mostrar_upload: bool = False) -> None:
    """
    Renderiza o conteúdo fixo da sidebar.
    mostrar_upload=True apenas na página Início.
    """
    with st.sidebar:
        # ── Logo ─────────────────────────────────────────────────────────
        st.markdown("""
            <div style="padding:1rem 0 1.25rem 0">
                <span style="font-size:1.45rem;font-weight:800;color:#f1f5f9;
                             letter-spacing:-0.02em;font-family:sans-serif">PRATO</span>
                <span style="color:#22c55e;font-size:1.1rem;margin-left:3px">&#9679;</span>
                <div style="font-size:0.7rem;color:#475569;margin-top:4px;
                            font-weight:500;letter-spacing:0.05em;text-transform:uppercase">
                    Previsão de Demanda
                </div>
            </div>
        """, unsafe_allow_html=True)

        # ── Status da fonte de dados ──────────────────────────────────────
        _api_ok = api_disponivel()
        if _api_ok:
            st.success("API Backend online")
            if st.button("Atualizar dados"):
                st.cache_data.clear()
        else:
            st.info("Modo demo — dados sintéticos.")
            st.caption("Previsões estimadas com base no histórico de exemplo.")

        # ── Upload (opcional, só na página Início) ────────────────────────
        if mostrar_upload:
            st.markdown("---")
            st.markdown("**Usar seus próprios dados**")
            arquivo = st.file_uploader(
                "Arquivo CSV ou Excel (opcional)",
                type=["csv", "xlsx", "xls"],
                label_visibility="collapsed",
            )
            if arquivo:
                from componentes.carregador import carregar_csv_usuario
                df = carregar_csv_usuario(arquivo)
                if df is not None:
                    st.session_state["df_vendas"] = df
                    st.success(f"{len(df):,} registros carregados.")

        # ── Rodapé ────────────────────────────────────────────────────────
        st.markdown("---")
        st.caption("v1.0.0 · github.com/filipe-macedo/PRATO")
