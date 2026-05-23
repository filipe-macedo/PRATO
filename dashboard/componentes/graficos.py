import plotly.express as px
import plotly.graph_objects as go
import pandas as pd

CORES = {
    "primaria": "#E8521A", "secundaria": "#2C7BB6",
    "sucesso": "#2ECC71", "atencao": "#F39C12",
    "perigo": "#E74C3C", "neutro": "#95A5A6",
}


def serie_temporal_vendas(df: pd.DataFrame, col_valor="quantidade_vendida") -> go.Figure:
    df_agg = df.groupby("data")[col_valor].sum().reset_index()
    fig = px.line(df_agg, x="data", y=col_valor,
                  title="Histórico de Vendas — Quantidade Total por Dia",
                  labels={"data": "Data", col_valor: "Quantidade Vendida"},
                  color_discrete_sequence=[CORES["primaria"]])
    fig.update_traces(line_width=1.8)
    fig.update_layout(hovermode="x unified", plot_bgcolor="white",
                      yaxis=dict(gridcolor="#EEEEEE"))
    return fig


def barras_por_produto(df: pd.DataFrame, top_n: int = 15) -> go.Figure:
    df_prod = (df.groupby("produto")["quantidade_vendida"]
               .sum().sort_values(ascending=True).tail(top_n).reset_index())
    fig = px.bar(df_prod, x="quantidade_vendida", y="produto", orientation="h",
                 title=f"Top {top_n} Produtos por Volume Vendido",
                 color="quantidade_vendida",
                 color_continuous_scale=["#FDEBD0", CORES["primaria"]])
    fig.update_layout(coloraxis_showscale=False, plot_bgcolor="white")
    return fig


def heatmap_dia_turno(df: pd.DataFrame) -> go.Figure:
    nomes_dia = {0: "Seg", 1: "Ter", 2: "Qua", 3: "Qui", 4: "Sex", 5: "Sáb", 6: "Dom"}
    df = df.copy()
    df["dia_semana"] = pd.to_datetime(df["data"]).dt.dayofweek.map(nomes_dia)
    pivot = df.groupby(["dia_semana", "turno"])["quantidade_vendida"].mean().unstack(fill_value=0)
    ordem = [d for d in ["Seg", "Ter", "Qua", "Qui", "Sex", "Sáb", "Dom"] if d in pivot.index]
    pivot = pivot.reindex(ordem)
    return px.imshow(pivot, title="Demanda Média por Dia da Semana e Turno",
                     labels=dict(x="Turno", y="Dia", color="Qtd Média"),
                     color_continuous_scale=["#FFF5EC", CORES["primaria"]], aspect="auto")


def previsto_vs_realizado(df: pd.DataFrame) -> go.Figure:
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=df["data"], y=df["quantidade_vendida"],
                             name="Realizado", mode="lines+markers",
                             line=dict(color=CORES["secundaria"], width=2)))
    fig.add_trace(go.Scatter(x=df["data"], y=df["quantidade_prevista"],
                             name="Previsto", mode="lines+markers",
                             line=dict(color=CORES["primaria"], width=2, dash="dot")))
    fig.update_layout(title="Previsto × Realizado", hovermode="x unified",
                      plot_bgcolor="white", yaxis=dict(gridcolor="#EEEEEE"),
                      legend=dict(orientation="h", yanchor="bottom", y=1.02))
    return fig


def dispersao_previsto_realizado(df: pd.DataFrame) -> go.Figure:
    max_val = max(df["quantidade_vendida"].max(), df["quantidade_prevista"].max())
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=df["quantidade_vendida"], y=df["quantidade_prevista"],
                             mode="markers", marker=dict(color=CORES["primaria"], size=6, opacity=0.6),
                             name="Observações"))
    fig.add_trace(go.Scatter(x=[0, max_val], y=[0, max_val], mode="lines",
                             line=dict(color=CORES["neutro"], dash="dash"), name="Previsão Perfeita"))
    fig.update_layout(title="Dispersão: Previsto × Realizado",
                      xaxis_title="Real", yaxis_title="Previsto", plot_bgcolor="white")
    return fig


def distribuicao_erros(df: pd.DataFrame) -> go.Figure:
    df = df.copy()
    df["erro"] = df["quantidade_prevista"] - df["quantidade_vendida"]
    fig = px.histogram(df, x="erro", nbins=40,
                       title="Distribuição dos Erros de Previsão",
                       color_discrete_sequence=[CORES["secundaria"]])
    fig.add_vline(x=0, line_dash="dash", line_color=CORES["perigo"], annotation_text="Sem erro")
    fig.update_layout(plot_bgcolor="white")
    return fig


def gauge_risco(valor_previsto: float, capacidade: float) -> go.Figure:
    pct = min(valor_previsto / capacidade * 100, 150) if capacidade > 0 else 0
    cor = CORES["sucesso"] if pct <= 80 else CORES["atencao"] if pct <= 100 else CORES["perigo"]
    fig = go.Figure(go.Indicator(
        mode="gauge+number+delta",
        value=valor_previsto,
        delta={"reference": capacidade, "valueformat": ".0f"},
        title={"text": "Previsão vs Capacidade"},
        gauge={
            "axis": {"range": [0, capacidade * 1.5]},
            "bar": {"color": cor},
            "steps": [
                {"range": [0, capacidade * 0.8], "color": "#D5F5E3"},
                {"range": [capacidade * 0.8, capacidade], "color": "#FCF3CF"},
                {"range": [capacidade, capacidade * 1.5], "color": "#FADBD8"},
            ],
            "threshold": {"line": {"color": CORES["perigo"], "width": 3}, "value": capacidade},
        },
        number={"suffix": " un."},
    ))
    fig.update_layout(height=280)
    return fig
