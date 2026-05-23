# Arquitetura do Sistema PRATO

## Visão Geral

O PRATO é composto por quatro camadas independentes que se comunicam por interfaces bem definidas:

```
┌──────────────────────────────────────────────────────────────┐
│                     DASHBOARD (Streamlit)                    │
│  Início · Histórico · Previsão · Métricas · Previsto×Real    │
│                    · Apoio à Decisão                         │
└──────────────────────┬───────────────────────────────────────┘
                       │ HTTP (REST)
┌──────────────────────▼───────────────────────────────────────┐
│                     API (FastAPI)                            │
│  /saude  /produtos  /vendas  /previsoes                      │
│  SQLAlchemy 2.0 · Pydantic v2 · Uvicorn                      │
└──────────────────────┬───────────────────────────────────────┘
                       │ joblib / pandas
┌──────────────────────▼───────────────────────────────────────┐
│              PIPELINE DE ML (src/)                           │
│  ingestao → preprocessamento → baseline → modelos            │
│  → avaliacao → pipeline_dados (orquestrador)                 │
└──────────────────────┬───────────────────────────────────────┘
                       │ CSV / API (estágio 1–3)
┌──────────────────────▼───────────────────────────────────────┐
│              INTEGRADOR (integrador/)                        │
│  CsvConnector · ApiConnector (stub) · validador              │
│  · transformador · executor · log · alertas                  │
└──────────────────────────────────────────────────────────────┘
```

---

## Camadas Detalhadas

### 1. Pipeline de Machine Learning (`src/`)

| Módulo | Responsabilidade |
|--------|-----------------|
| `config.py` | Constantes globais (colunas, mapa de turnos, limiares) |
| `ingestao.py` | Carregamento de CSV/Excel com fallback de encoding |
| `preprocessamento.py` | Limpeza, features temporais, lags, split cronológico |
| `baseline.py` | Previsão hierárquica B1→B4 como referência mínima |
| `modelos.py` | Regressão Linear, Random Forest, XGBoost + CV |
| `avaliacao.py` | MAE, RMSE, R², MAPE, análise de resíduos |
| `pipeline_dados.py` | Orquestrador CLI (9 etapas) |
| `utils_calendario.py` | Cálculo de feriados nacionais (Meeus/Jones/Butcher) |

**Princípio anti-leakage:**
- Split sempre cronológico via `iloc[:n]` / `iloc[n:]`
- Lags calculados com `.shift(1)` antes de qualquer rolling mean
- `receita_total` e `quantidade_cancelada` excluídas das features
- `TimeSeriesSplit` para validação cruzada (sem dados futuros em fold)

### 2. Backend REST (`app/`)

```
app/
├── main.py          ← FastAPI + lifespan + CORS
├── config.py        ← Configuracoes(BaseSettings)
├── database.py      ← engine + SessionLocal + Base
├── dependencies.py  ← get_db(), get_modelo()
├── models/          ← ORM: Produto, Turno, Venda, HistoricoPrevisao
├── schemas/         ← Pydantic v2: validação de entrada/saída
├── routers/         ← Endpoints organizados por domínio
└── services/        ← Lógica de negócio isolada dos routers
```

**Escolhas técnicas:**
- `lifespan` em vez de `@app.on_event` (depreciado no FastAPI ≥0.93)
- `Annotated[Session, Depends(get_db)]` para injeção de dependência
- `PRAGMA foreign_keys=ON` via event listener do SQLAlchemy
- Cache singleton do modelo para evitar I/O a cada requisição

### 3. Dashboard (`dashboard/`)

```
dashboard/
├── Inicio.py              ← Página raiz com KPIs e tendência
├── pages/
│   ├── 1_Historico_Vendas.py
│   ├── 2_Previsao_Demanda.py
│   ├── 3_Metricas_Modelo.py
│   ├── 4_Previsto_Realizado.py
│   └── 5_Apoio_Decisao.py
└── componentes/
    ├── carregador.py      ← API calls + @st.cache_data
    ├── graficos.py        ← Plotly charts
    ├── alertas.py         ← Classificação de risco (±20%)
    └── tabelas.py         ← Styler com cores semafóricas
```

### 4. Integrador (`integrador/`)

Implementa o **Adapter Pattern** para suportar múltiplas origens de dados:

- **Estágio 1 (MVP):** `CsvConnector` — arquivos CSV depositados em `data/incoming/`
- **Estágio 2 (futuro):** Polling automático de diretório/FTP
- **Estágio 3 (futuro):** `ApiConnector` — webhook REST em tempo real

**Fluxo de dados:**
```
Fonte → Conector → Validador → Transformador → data/processed/
                       ↓ (rejeitados)
                 data/quarantine/
```

---

## Banco de Dados

**Desenvolvimento:** SQLite (`prato.db`)  
**Produção:** PostgreSQL (configurar `DATABASE_URL` no `.env`)

**8 tabelas:**

```
categorias ──────────────────────┐
turnos ──────────────────────────┤
produtos ── categoria_id ────────┤
calendario                       │
vendas ── produto_id, turno_id   │
estoque_snapshot ── produto_id   │
movimentacao_estoque ── produto  │
historico_previsoes ── produto   │
```

---

## Segurança e LGPD

| Medida | Implementação |
|--------|--------------|
| Dados sensíveis | SHA-256 em `numero_pedido` e `operador_id` |
| CORS | `ALLOWED_ORIGINS=http://localhost:8501` |
| Secrets | Apenas via variáveis de ambiente (`.env`) |
| Dados reais | `data/raw/` nunca comitado (`.gitignore`) |
| Modelos | `*.pkl` nunca comitado |

---

## Fluxo de Previsão (end-to-end)

```
1. Usuário informa: data, produto, turno
2. Dashboard → POST /previsoes/
3. API busca lags no BD (lag_1d, lag_7d, mm_7d, mm_14d)
4. API monta vetor de features
5. Modelo .pkl prediz → clip(0)
6. API persiste em historico_previsoes
7. Dashboard exibe gauge de risco (±20%)
```
