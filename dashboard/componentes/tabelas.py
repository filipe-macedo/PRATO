import pandas as pd
import streamlit as st


def tabela_vendas_resumo(df: pd.DataFrame) -> pd.DataFrame:
    cols = ["data", "produto", "turno", "quantidade_vendida", "receita_total"]
    return df[[c for c in cols if c in df.columns]].sort_values("data", ascending=False)


def tabela_metricas_modelos(metricas: dict) -> pd.DataFrame:
    if "modelos" in metricas:
        df = pd.DataFrame(metricas["modelos"])
    elif "metricas_teste" in metricas:
        df = pd.DataFrame([metricas["metricas_teste"]])
    else:
        return pd.DataFrame()
    rename = {"nome": "Modelo", "mae": "MAE", "rmse": "RMSE", "r2": "R²", "mape": "MAPE (%)"}
    return df.rename(columns={k: v for k, v in rename.items() if k in df.columns})


def formatar_tabela_riscos(df: pd.DataFrame) -> None:
    if df.empty:
        st.info("Sem dados suficientes para análise de risco.")
        return

    def colorir(val):
        if "Excesso" in str(val):
            return "background-color: #FADBD8"
        elif "Falta" in str(val):
            return "background-color: #FCF3CF"
        elif "Normal" in str(val):
            return "background-color: #D5F5E3"
        return ""

    df_exib = df.copy()
    if "desvio_pct" in df_exib.columns:
        df_exib["desvio_pct"] = df_exib["desvio_pct"].map("{:+.1f}%".format)
    for col in ["quantidade_prevista", "media_historica"]:
        if col in df_exib.columns:
            df_exib[col] = df_exib[col].map("{:.1f}".format)
    st.dataframe(df_exib.style.map(colorir, subset=["risco"]),
                 use_container_width=True, hide_index=True)
