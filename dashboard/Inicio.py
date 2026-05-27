import sys
from datetime import datetime
from pathlib import Path

import streamlit as st
import plotly.graph_objects as go

_ROOT = Path(__file__).resolve().parent.parent
_DASH = Path(__file__).resolve().parent
for _p in [str(_ROOT), str(_DASH)]:
    if _p not in sys.path:
        sys.path.insert(0, _p)

from componentes.carregador import api_disponivel, carregar_metricas
from componentes.estilos import aplicar_estilos
from componentes.sidebar import renderizar_sidebar

st.set_page_config(
    page_title="PRATO — Previsão de Demanda",
    page_icon="favicon.png" if Path(_DASH / "favicon.png").exists() else None,
    layout="wide",
    initial_sidebar_state="expanded",
)

_api_ok = api_disponivel()
aplicar_estilos()
renderizar_sidebar(mostrar_upload=True)


# ═══════════════════════════════════════════════════════════════════
#  DADOS DEMO — usados quando a API não está disponível
# ═══════════════════════════════════════════════════════════════════
_DEMO: dict = {
    "Almoço": {
        "kpi": {"total": 2450, "acuracia": 94.2, "reducao": 23, "economia": 1450},
        "proxima_atualizacao": "16:45",
        "tendencia": "+15%",
        "horarios": [
            ("11:00", 120,  95),
            ("12:00", 285, 260),
            ("12:30", 340, 310),
            ("13:00", 310, 330),
            ("13:30", 220, 195),
            ("14:00", 150, 140),
            ("14:30",  80,  85),
            ("15:00",  45,  50),
        ],
        "pratos": [
            ( 1, "Moqueca de Peixe",     "Frutos do Mar",  52, 96, "+8%"),
            ( 2, "Frango Grelhado",      "Carnes",         48, 91, "+3%"),
            ( 3, "Risoto de Funghi",     "Massas",         41, 88, "+12%"),
            ( 4, "Picanha na Brasa",     "Carnes",         38, 85, "+5%"),
            ( 5, "Salmão ao Molho Dill", "Peixes",         35, 82, "+2%"),
            ( 6, "Fettuccine Carbonara", "Massas",         30, 79, "-4%"),
            ( 7, "Lasanha Bolonhesa",    "Massas",         27, 76, "-7%"),
            ( 8, "Tilápia Grelhada",     "Peixes",         25, 74, "+1%"),
            ( 9, "Strogonoff Bovino",    "Carnes",         22, 71, "-2%"),
            (10, "Sopa do Dia",          "Sopas",          18, 68, "+6%"),
        ],
        "alertas": [
            ("red",    "Previsão alta para 'Água de Coco'",
             "Demanda 40% acima da média — repor estoque antes das 11h"),
            ("yellow", "Estoque de 'Moqueca' próximo do limite",
             "Verificar ingredientes frescos com fornecedor"),
            ("green",  "Eficiência operacional acima de 90%",
             "Turno dentro dos parâmetros ideais"),
        ],
        "insights": [
            ("Pré-prepare 50% mais 'Moqueca de Peixe' hoje",
             "Tendência histórica indica pico às 12h30 nas quintas-feiras"),
            ("Considere promoção em 'Lasanha Bolonhesa'",
             "Previsão 15% abaixo da média — desconto pode estimular vendas"),
            ("Aumente a equipe de atendimento às 12:30",
             "Pico de demanda previsto com 94% de confiança pelo modelo"),
        ],
    },
    "Café": {
        "kpi": {"total": 820, "acuracia": 91.5, "reducao": 18, "economia": 480},
        "proxima_atualizacao": "10:00",
        "tendencia": "+7%",
        "horarios": [
            ("06:00",  45,  38),
            ("07:00", 120, 110),
            ("07:30", 185, 200),
            ("08:00", 210, 190),
            ("08:30", 150, 165),
            ("09:00",  80,  72),
            ("09:30",  30,  35),
        ],
        "pratos": [
            ( 1, "Pão de Queijo",        "Padaria",     200, 95, "+10%"),
            ( 2, "Tapioca Recheada",     "Padaria",     150, 90, "+18%"),
            ( 3, "Açaí com Granola",     "Frutas",      120, 85,  "+5%"),
            ( 4, "Ovo Mexido",           "Proteínas",   100, 82,  "+3%"),
            ( 5, "Iogurte Parfait",      "Laticínios",   80, 78,  "-2%"),
            ( 6, "Panqueca de Aveia",    "Padaria",      60, 75,  "+7%"),
            ( 7, "Smoothie Verde",       "Bebidas",      50, 72, "+12%"),
            ( 8, "Torrada Integral",     "Padaria",      40, 70,  "-5%"),
            ( 9, "Queijo Coalho Grelh.", "Laticínios",   35, 68,  "+1%"),
            (10, "Mingau de Aveia",      "Cereais",      30, 65,  "-3%"),
        ],
        "alertas": [
            ("yellow", "Pico previsto às 07:30",
             "Reforçar equipe de atendimento no horário de rush matinal"),
            ("green",  "Estoque de pão de queijo suficiente",
             "Produção cobre demanda estimada com folga de 15%"),
        ],
        "insights": [
            ("Prepare lotes de tapioca a cada 20 min",
             "Demanda crescente — produção contínua reduz tempo de espera"),
            ("Promova o smoothie verde hoje",
             "Temperatura alta prevista — bebidas frescas com +18% de procura"),
        ],
    },
    "Jantar": {
        "kpi": {"total": 1890, "acuracia": 92.8, "reducao": 21, "economia": 1120},
        "proxima_atualizacao": "22:00",
        "tendencia": "+9%",
        "horarios": [
            ("18:00",  80,  65),
            ("19:00", 220, 205),
            ("19:30", 310, 330),
            ("20:00", 380, 365),
            ("20:30", 350, 340),
            ("21:00", 280, 270),
            ("21:30", 180, 190),
            ("22:00",  90,  85),
        ],
        "pratos": [
            ( 1, "Filé ao Molho Madeira", "Carnes",         65, 94, "+12%"),
            ( 2, "Massa ao Pesto",        "Massas",         58, 89,  "+6%"),
            ( 3, "Salmão Grelhado",       "Peixes",         50, 87,  "+9%"),
            ( 4, "Costela na Brasa",      "Carnes",         45, 84, "+15%"),
            ( 5, "Risoto de Camarão",     "Frutos do Mar",  40, 81,  "+4%"),
            ( 6, "Nhoque ao Sugo",        "Massas",         35, 78,  "-3%"),
            ( 7, "Frango à Parmegiana",   "Carnes",         30, 75,  "+2%"),
            ( 8, "Tilápia ao Limão",      "Peixes",         28, 73,  "-1%"),
            ( 9, "Salada Caesar",         "Saladas",        22, 70,  "+8%"),
            (10, "Caldo Verde",           "Sopas",          18, 67,  "-2%"),
        ],
        "alertas": [
            ("red",    "Alta demanda prevista para as 20:00",
             "Pico 25% acima da média — garantir mise en place completo até 19h"),
            ("yellow", "Reservas acima da capacidade às 20:30",
             "Confirmar reservas e preparar lista de espera"),
            ("green",  "Estoque de carnes dentro do planejado",
             "Sem necessidade de reposição urgente"),
        ],
        "insights": [
            ("Inicie o mise en place às 16:00 para o pico das 20h",
             "Histórico de sextas indica demanda 25% acima da média semanal"),
            ("Considere abrir lista de espera para 20:30",
             "Capacidade máxima esperada entre 20:00 e 20:30"),
        ],
    },
    "24h": {
        "kpi": {"total": 5160, "acuracia": 93.1, "reducao": 21, "economia": 3050},
        "proxima_atualizacao": "23:59",
        "tendencia": "+11%",
        "horarios": [
            ("06:00",  45,  38),
            ("07:00", 120, 110),
            ("08:00", 210, 190),
            ("09:00",  80,  72),
            ("11:00", 120,  95),
            ("12:00", 285, 260),
            ("12:30", 340, 310),
            ("13:00", 310, 330),
            ("14:00", 150, 140),
            ("18:00",  80,  65),
            ("19:00", 220, 205),
            ("20:00", 380, 365),
            ("21:00", 280, 270),
            ("22:00",  90,  85),
        ],
        "pratos": [
            ( 1, "Moqueca de Peixe",      "Frutos do Mar",  52, 96, "+8%"),
            ( 2, "Frango Grelhado",       "Carnes",         48, 91, "+5%"),
            ( 3, "Filé ao Molho Madeira", "Carnes",         45, 89, "+12%"),
            ( 4, "Risoto de Funghi",      "Massas",         41, 87, "+3%"),
            ( 5, "Pão de Queijo",         "Padaria",        40, 85, "+10%"),
            ( 6, "Salmão Grelhado",       "Peixes",         38, 83, "+9%"),
            ( 7, "Picanha na Brasa",      "Carnes",         35, 81, "+7%"),
            ( 8, "Tapioca Recheada",      "Padaria",        30, 79, "+18%"),
            ( 9, "Massa ao Pesto",        "Massas",         28, 77, "+6%"),
            (10, "Costela na Brasa",      "Carnes",         25, 75, "+15%"),
        ],
        "alertas": [
            ("red",    "Pico crítico às 12:30 e 20:00",
             "Dois momentos de alta demanda — planejar equipe para ambos os turnos"),
            ("yellow", "'Água de Coco' — repor estoque antes das 11h",
             "Demanda 40% acima da média no turno do almoço"),
            ("green",  "Acurácia geral do modelo: 93.1%",
             "Previsões dentro do intervalo de confiança esperado"),
        ],
        "insights": [
            ("Planeje reforço de equipe para 12:30 e 20:00",
             "Dois momentos de alta demanda concentrada ao longo do dia"),
            ("Priorize reposição de proteínas nobres antes do almoço",
             "Moqueca e filé são os mais demandados nos dois picos do dia"),
            ("Considere promoção de 'Lasanha' entre 14h e 17h",
             "Janela de baixa demanda — desconto pode estimular vendas no intervalo"),
        ],
    },
}


# ═══════════════════════════════════════════════════════════════════
#  HELPERS — HTML e gráfico
# ═══════════════════════════════════════════════════════════════════

def _kpi_card(titulo: str, valor: str, unidade: str,
              subtitulo: str, tendencia: str, cor: str) -> str:
    """Retorna HTML de um card KPI com borda colorida à esquerda."""
    cor_t = "#27AE60" if str(tendencia).startswith("+") else "#E74C3C"
    return (
        f'<div style="background:#fff;border-left:4px solid {cor};border-radius:10px;'
        f'padding:1.1rem 1.3rem;box-shadow:0 2px 8px rgba(44,62,80,0.08);height:100%">'
        f'<div style="font-size:0.68rem;font-weight:700;color:#95a5a6;'
        f'text-transform:uppercase;letter-spacing:0.08em;margin-bottom:0.4rem">{titulo}</div>'
        f'<div style="display:flex;align-items:baseline;gap:0.35rem;flex-wrap:wrap">'
        f'<span style="font-size:2.1rem;font-weight:800;color:#2C3E50;line-height:1.1">'
        f'{valor}</span>'
        f'<span style="font-size:0.8rem;color:#95a5a6;font-weight:500">{unidade}</span>'
        f'</div>'
        f'<div style="margin-top:0.45rem;display:flex;align-items:center;gap:0.4rem">'
        f'<span style="font-size:0.78rem;color:{cor_t};font-weight:700">{tendencia}</span>'
        f'<span style="font-size:0.75rem;color:#95a5a6">{subtitulo}</span>'
        f'</div>'
        f'</div>'
    )


def _alertas_html(alertas: list) -> str:
    """Retorna HTML de uma lista de cards de alerta."""
    partes: list[str] = []
    for tipo, titulo, desc in alertas:
        cor  = {"red": "#E74C3C", "yellow": "#F39C12", "green": "#27AE60"}.get(tipo, "#95a5a6")
        icon = {"red": "⛔", "yellow": "⚠️", "green": "✅"}.get(tipo, "ℹ️")
        partes.append(
            f'<div style="background:#fff;border-left:4px solid {cor};border-radius:8px;'
            f'padding:0.7rem 1rem;margin-bottom:0.5rem;'
            f'box-shadow:0 1px 4px rgba(44,62,80,0.06)">'
            f'<div style="display:flex;align-items:center;gap:0.5rem;margin-bottom:0.15rem">'
            f'<span style="font-size:0.9rem">{icon}</span>'
            f'<span style="font-weight:700;color:#2C3E50;font-size:0.875rem">{titulo}</span>'
            f'</div>'
            f'<div style="font-size:0.78rem;color:#7f8c8d;padding-left:1.6rem">{desc}</div>'
            f'</div>'
        )
    return "\n".join(partes)


def _insights_html(insights: list) -> str:
    """Retorna HTML de uma lista de cards de insight."""
    partes: list[str] = []
    for titulo, desc in insights:
        partes.append(
            f'<div style="background:#fff;border-left:4px solid #27AE60;border-radius:8px;'
            f'padding:0.7rem 1rem;margin-bottom:0.5rem;'
            f'box-shadow:0 1px 4px rgba(44,62,80,0.06)">'
            f'<div style="font-weight:700;color:#2C3E50;font-size:0.875rem;'
            f'margin-bottom:0.15rem">💡 {titulo}</div>'
            f'<div style="font-size:0.78rem;color:#7f8c8d">{desc}</div>'
            f'</div>'
        )
    return "\n".join(partes)


def _tabela_top10_html(pratos: list, filtro_cat: str = "Todos os Pratos") -> str:
    """Retorna HTML da tabela Top 10 com badges de ranking e barras de confiança."""
    lista = pratos
    if filtro_cat != "Todos os Pratos":
        filtrados = [p for p in pratos if p[2] == filtro_cat]
        lista = [(i + 1,) + p[1:] for i, p in enumerate(filtrados)]
    if not lista:
        return (
            '<p style="color:#95a5a6;text-align:center;padding:1.5rem 0">'
            "Nenhum prato nessa categoria para o turno selecionado.</p>"
        )
    linhas = ""
    for rank, nome, cat, qtd, conf, trend in lista:
        cor_rank  = "#27AE60" if rank <= 3 else "#7f8c8d"
        bg_rank   = "rgba(39,174,96,0.14)" if rank <= 3 else "#f4f4f4"
        cor_trend = "#27AE60" if trend.startswith("+") else "#E74C3C"
        seta      = "↑" if trend.startswith("+") else "↓"
        num_t     = trend.lstrip("+-")
        c_col     = "#27AE60" if conf >= 90 else ("#F39C12" if conf >= 75 else "#E74C3C")
        linhas += (
            f'<tr style="border-bottom:1px solid #f4f6f8">'
            f'<td style="padding:0.55rem 0.7rem;text-align:center">'
            f'<span style="background:{bg_rank};color:{cor_rank};border-radius:50%;'
            f'width:26px;height:26px;display:inline-flex;align-items:center;'
            f'justify-content:center;font-weight:800;font-size:0.78rem">{rank}</span></td>'
            f'<td style="padding:0.55rem 0.7rem">'
            f'<div style="font-weight:600;color:#2C3E50;font-size:0.875rem">{nome}</div>'
            f'<div style="font-size:0.7rem;color:#95a5a6">{cat}</div></td>'
            f'<td style="padding:0.55rem 0.7rem;text-align:right;font-weight:700;'
            f'color:#2C3E50;font-size:0.95rem">{qtd}</td>'
            f'<td style="padding:0.55rem 0.7rem;min-width:120px">'
            f'<div style="display:flex;align-items:center;gap:0.4rem">'
            f'<div style="flex:1;background:#ecf0f1;border-radius:3px;height:6px">'
            f'<div style="width:{conf}%;background:{c_col};border-radius:3px;height:6px">'
            f'</div></div>'
            f'<span style="font-size:0.72rem;color:{c_col};font-weight:700;'
            f'white-space:nowrap">{conf}%</span></div></td>'
            f'<td style="padding:0.55rem 0.7rem;text-align:center">'
            f'<span style="color:{cor_trend};font-weight:700;font-size:0.875rem">'
            f'{seta} {num_t}</span></td>'
            f'</tr>'
        )
    cabecalho = "".join(
        f'<th style="padding:0.55rem 0.7rem;font-size:0.68rem;color:#95a5a6;'
        f'text-transform:uppercase;letter-spacing:0.07em;font-weight:700;'
        f'text-align:{align}">{label}</th>'
        for label, align in [
            ("#", "center"), ("Prato", "left"), ("Previsão", "right"),
            ("Confiança IA", "left"), ("Tend.", "center"),
        ]
    )
    return (
        '<div style="overflow-x:auto">'
        '<table style="width:100%;border-collapse:collapse;background:#fff;'
        'border-radius:12px;overflow:hidden;box-shadow:0 2px 8px rgba(44,62,80,0.08)">'
        f'<thead><tr style="background:#f8f9fa;border-bottom:2px solid #e9ecef">'
        f'{cabecalho}</tr></thead>'
        f'<tbody>{linhas}</tbody>'
        '</table></div>'
    )


def _grafico_horario(horarios: list) -> go.Figure:
    """Gráfico de área (previsão IA) + linha tracejada (histórico)."""
    horas = [h[0] for h in horarios]
    prev  = [h[1] for h in horarios]
    hist  = [h[2] for h in horarios]

    fig = go.Figure()
    # Previsão IA — área preenchida
    fig.add_trace(go.Scatter(
        x=horas, y=prev,
        name="Previsão IA",
        fill="tozeroy",
        fillcolor="rgba(39,174,96,0.10)",
        line=dict(color="#27AE60", width=2.5),
        mode="lines+markers",
        marker=dict(size=6, color="#27AE60"),
        hovertemplate="%{y} un.<extra>Previsão IA</extra>",
    ))
    # Histórico — linha tracejada cinza
    fig.add_trace(go.Scatter(
        x=horas, y=hist,
        name="Histórico (período anterior)",
        line=dict(color="#bdc3c7", width=1.5, dash="dash"),
        mode="lines",
        hovertemplate="%{y} un.<extra>Histórico</extra>",
    ))
    fig.update_layout(
        height=300,
        margin=dict(l=0, r=0, t=35, b=0),
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font=dict(family="sans-serif", size=12, color="#2C3E50"),
        legend=dict(
            orientation="h",
            yanchor="bottom", y=1.02,
            xanchor="right",  x=1,
            font=dict(size=11),
            bgcolor="rgba(0,0,0,0)",
        ),
        xaxis=dict(
            showgrid=False, showline=True, linecolor="#e9ecef",
            tickfont=dict(size=11, color="#7f8c8d"),
        ),
        yaxis=dict(
            showgrid=True, gridcolor="#f0f0f0",
            showline=False, zeroline=False,
            tickfont=dict(size=11, color="#7f8c8d"),
        ),
    )
    return fig


# ═══════════════════════════════════════════════════════════════════
#  HEADER
# ═══════════════════════════════════════════════════════════════════
col_h, col_ts = st.columns([5, 1])
with col_h:
    st.title("Dashboard de Previsão de Demanda")
    badge_txt = "API Conectada" if _api_ok else "Modo Demo"
    badge_bg  = "rgba(39,174,96,0.12)" if _api_ok else "rgba(243,156,18,0.12)"
    badge_cor = "#27AE60" if _api_ok else "#F39C12"
    st.markdown(
        f'<span style="background:{badge_bg};color:{badge_cor};border-radius:20px;'
        f'padding:0.2rem 0.85rem;font-size:0.78rem;font-weight:700">{badge_txt}</span>',
        unsafe_allow_html=True,
    )
with col_ts:
    st.markdown(
        f'<div style="text-align:right;color:#95a5a6;font-size:0.75rem;'
        f'padding-top:0.9rem">{datetime.now().strftime("%d/%m/%Y %H:%M")}</div>',
        unsafe_allow_html=True,
    )

# ═══════════════════════════════════════════════════════════════════
#  FILTROS
# ═══════════════════════════════════════════════════════════════════
fc1, fc2, fc3, fc4 = st.columns([3, 2, 3, 1])
with fc1:
    turno = st.radio("Turno", ["Almoço", "Café", "Jantar", "24h"], horizontal=True)
with fc2:
    _periodo = st.selectbox("Período", ["Hoje", "Amanhã", "Semana que vem"])
with fc3:
    _categoria = st.selectbox(
        "Categoria",
        [
            "Todos os Pratos", "Carnes", "Massas", "Peixes", "Frutos do Mar",
            "Padaria", "Bebidas", "Saladas", "Sopas",
            "Frutas", "Laticínios", "Proteínas", "Cereais",
        ],
    )
with fc4:
    st.markdown("<br>", unsafe_allow_html=True)
    _atualizar = st.button("Atualizar", use_container_width=True, type="primary")

if _atualizar:
    st.cache_data.clear()
    st.rerun()

st.divider()

# ── Dados para o turno selecionado ────────────────────────────────────────────
dados = _DEMO[turno]

# ═══════════════════════════════════════════════════════════════════
#  KPI CARDS
# ═══════════════════════════════════════════════════════════════════
st.markdown("### Resumo do Turno")
k1, k2, k3, k4 = st.columns(4)
kpi = dados["kpi"]

k1.markdown(_kpi_card(
    "Total de Pratos",
    f"{kpi['total']:,}".replace(",", "."),
    "unidades",
    f"previstas · próx. {dados['proxima_atualizacao']}",
    dados["tendencia"],
    "#27AE60",
), unsafe_allow_html=True)

k2.markdown(_kpi_card(
    "Acurácia da IA",
    f"{kpi['acuracia']:.1f}",
    "%",
    "margem de erro ±5%",
    "+0.3%",
    "#3498DB",
), unsafe_allow_html=True)

k3.markdown(_kpi_card(
    "Redução de Desperdício",
    f"{kpi['reducao']}",
    "%",
    "vs. período anterior",
    f"+{kpi['reducao']}%",
    "#9B59B6",
), unsafe_allow_html=True)

k4.markdown(_kpi_card(
    "Economia Estimada",
    f"R$ {kpi['economia']:,}".replace(",", "."),
    "",
    "no período",
    dados["tendencia"],
    "#E67E22",
), unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)

# ═══════════════════════════════════════════════════════════════════
#  GRÁFICO — PREVISÃO DE DEMANDA POR HORÁRIO
# ═══════════════════════════════════════════════════════════════════
st.markdown("### Previsão de Demanda por Horário")
st.plotly_chart(_grafico_horario(dados["horarios"]), use_container_width=True)

# ═══════════════════════════════════════════════════════════════════
#  TOP 10 PRATOS
# ═══════════════════════════════════════════════════════════════════
st.markdown("### Top 10 Pratos — Previsão de Pedidos")
st.markdown(_tabela_top10_html(dados["pratos"], _categoria), unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)

# ═══════════════════════════════════════════════════════════════════
#  TABS — ALERTAS · INSIGHTS · MODELO
# ═══════════════════════════════════════════════════════════════════
tab_a, tab_i, tab_m = st.tabs(
    ["Alertas e Riscos", "Insights Operacionais", "Dados do Modelo"]
)

with tab_a:
    st.markdown(_alertas_html(dados["alertas"]), unsafe_allow_html=True)

with tab_i:
    st.markdown(_insights_html(dados["insights"]), unsafe_allow_html=True)

with tab_m:
    metricas = carregar_metricas()
    m = metricas.get("metricas_teste", {})
    cm1, cm2, cm3, cm4 = st.columns(4)
    cm1.metric("MAE",  f"{m.get('mae',  0):.2f}" if isinstance(m.get("mae"),  float) else "—")
    cm2.metric("RMSE", f"{m.get('rmse', 0):.2f}" if isinstance(m.get("rmse"), float) else "—")
    cm3.metric("R²",   f"{m.get('r2',   0):.3f}" if isinstance(m.get("r2"),   float) else "—")
    cm4.metric("MAPE", f"{m.get('mape', 0):.1f}%" if isinstance(m.get("mape"), float) else "—")
    if metricas.get("modelo"):
        st.caption(f"Modelo: **{metricas['modelo']}**")
    if metricas.get("nota"):
        st.info(metricas["nota"])

# ═══════════════════════════════════════════════════════════════════
#  FOOTER
# ═══════════════════════════════════════════════════════════════════
st.divider()
_sync_txt = "API sincronizada" if _api_ok else "Dados de demonstração"
_sync_cor = "#27AE60" if _api_ok else "#F39C12"
st.markdown(
    f'<div style="display:flex;justify-content:space-between;align-items:center;'
    f'font-size:0.75rem;color:#95a5a6;padding-bottom:0.5rem">'
    f'<span>PRATO v1.0.0 · github.com/filipe-macedo/PRATO</span>'
    f'<span>Última atualização: {datetime.now().strftime("%d/%m/%Y %H:%M")} · '
    f'<span style="color:{_sync_cor};font-weight:700">{_sync_txt}</span></span>'
    f'</div>',
    unsafe_allow_html=True,
)
