import streamlit as st
import pandas as pd

LIMIAR_EXCESSO = 0.20
LIMIAR_FALTA = 0.20


def classificar_risco(quantidade_prevista: float, media_historica: float) -> dict:
    if media_historica == 0:
        return {"nivel": "indefinido", "emoji": "⚪", "mensagem": "Sem histórico suficiente.", "acao": ""}

    desvio = (quantidade_prevista - media_historica) / media_historica

    if desvio > LIMIAR_EXCESSO:
        return {
            "nivel": "excesso", "emoji": "🔴",
            "mensagem": f"Previsão {desvio*100:.0f}% acima da média. Risco de superprodução.",
            "acao": "Reduza o preparo antecipado ou aumente promoções para escoamento.",
        }
    elif desvio < -LIMIAR_FALTA:
        return {
            "nivel": "falta", "emoji": "🟡",
            "mensagem": f"Previsão {abs(desvio)*100:.0f}% abaixo da média. Risco de ruptura.",
            "acao": "Antecipe compras ou ajuste a capacidade de produção.",
        }
    return {
        "nivel": "normal", "emoji": "🟢",
        "mensagem": "Demanda prevista dentro do padrão histórico.",
        "acao": "Manter planejamento padrão.",
    }


def exibir_alerta(risco: dict):
    if risco["nivel"] == "excesso":
        st.error(f"{risco['emoji']} **Risco de Excesso:** {risco['mensagem']}")
        st.info(f"💡 **Ação sugerida:** {risco['acao']}")
    elif risco["nivel"] == "falta":
        st.warning(f"{risco['emoji']} **Risco de Falta:** {risco['mensagem']}")
        st.info(f"💡 **Ação sugerida:** {risco['acao']}")
    else:
        st.success(f"{risco['emoji']} {risco['mensagem']}")


def resumo_riscos_tabela(df_prev: pd.DataFrame, df_hist: pd.DataFrame) -> pd.DataFrame:
    if df_hist.empty or df_prev.empty:
        return pd.DataFrame()

    medias = (df_hist.groupby(["produto", "turno"])["quantidade_vendida"]
              .mean().reset_index().rename(columns={"quantidade_vendida": "media_historica"}))
    df = df_prev.merge(medias, on=["produto", "turno"], how="left")
    df["desvio_pct"] = ((df["quantidade_prevista"] - df["media_historica"])
                        / df["media_historica"].replace(0, 1)) * 100

    def _nivel(row):
        d = row["desvio_pct"] / 100
        if d > LIMIAR_EXCESSO:
            return "🔴 Excesso"
        elif d < -LIMIAR_FALTA:
            return "🟡 Falta"
        return "🟢 Normal"

    df["risco"] = df.apply(_nivel, axis=1)
    return df[["produto", "turno", "quantidade_prevista", "media_historica", "desvio_pct", "risco"]]
