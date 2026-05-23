# Documentação Técnica — PRATO
## Sistema de Previsão de Demanda em Restaurantes com uso de Inteligência Artificial

**Versão:** 1.0.0  
**Autor:** Filipe Macedo  
**Data:** 2026  

> **Nota:** Resultados numéricos marcados com `[inserir resultado real após validação]`
> devem ser preenchidos após execução completa do pipeline com dados reais do restaurante.

---

## 1. Introdução

O PRATO é um sistema de apoio à decisão para restaurantes que utiliza técnicas de aprendizado de máquina para prever a demanda diária por produto e turno. O sistema integra um pipeline de dados, modelos preditivos, uma API REST e um dashboard interativo.

### 1.1 Motivação

Restaurantes enfrentam desafios recorrentes de equilíbrio entre oferta e demanda: excesso de produção gera desperdício e custos desnecessários; escassez causa insatisfação e perda de receita. A previsão quantitativa de demanda permite ao gestor antecipar necessidades de compra, escalar equipes adequadamente e reduzir perdas operacionais.

### 1.2 Escopo

- **Incluído no MVP:** previsão por produto × turno × dia; baseline estatístico; modelos supervisionados; API REST; dashboard analítico; integrador CSV (Estágio 1).
- **Fora do escopo MVP:** integração em tempo real com PDV, previsão de estoque automática, app mobile.

### 1.3 Restrições

- Dados de treinamento: histórico mínimo recomendado de 6 meses por produto/turno.
- Ambiente de desenvolvimento: SQLite. Produção: PostgreSQL.
- Conformidade LGPD: nenhum dado pessoal de cliente é ingerido ou armazenado.

---

## 2. Arquitetura do Sistema

O sistema é composto por quatro camadas:

```
Dashboard (Streamlit)
        ↓ HTTP REST
API (FastAPI + SQLAlchemy)
        ↓ joblib / pandas
Pipeline de ML (src/)
        ↓ CSV / API (Estágio 1–3)
Integrador (integrador/)
```

Cada camada é independente e se comunica por interfaces bem definidas (DataFrames pandas para ML; schemas Pydantic para a API; Plotly charts para o dashboard).

Para detalhamento completo, consulte [`docs/arquitetura.md`](arquitetura.md).

---

## 3. Estrutura do Repositório

```
PRATO/
├── src/                    # Pipeline de ML
│   ├── config.py           # Constantes globais
│   ├── ingestao.py         # Carregamento de dados
│   ├── preprocessamento.py # Limpeza e feature engineering
│   ├── baseline.py         # Modelo de referência (B1–B4)
│   ├── modelos.py          # Reg. Linear, Random Forest, XGBoost
│   ├── avaliacao.py        # Métricas e análise de resíduos
│   └── pipeline_dados.py   # Orquestrador CLI
├── app/                    # API REST (FastAPI)
├── dashboard/              # Interface (Streamlit)
├── integrador/             # Módulo de integração com PDV
├── database/               # DDL SQL e seeds
├── data/                   # Dados (raw excluído do git)
├── tests/                  # Testes automatizados
├── docs/                   # Documentação
└── scripts/                # Scripts auxiliares
```

---

## 4. Módulo de Ingestão (`src/ingestao.py`)

### 4.1 Funções principais

| Função | Descrição |
|--------|-----------|
| `carregar_dados(caminho)` | Carrega CSV ou Excel com fallback de encoding (utf-8 → latin-1) |
| `validar_colunas(df)` | Verifica presença das colunas obrigatórias |
| `inspecionar_dados(df)` | Retorna shape, tipos, nulos e duplicatas |

### 4.2 Colunas obrigatórias

`data`, `produto`, `turno`, `quantidade_vendida`

### 4.3 Formatos de data suportados

`YYYY-MM-DD`, `DD/MM/YYYY`, `DD-MM-YYYY`, `YYYY/MM/DD`, `DD.MM.YYYY`, `YYYYMMDD`

---

## 5. Pré-processamento (`src/preprocessamento.py`)

### 5.1 Etapas do pipeline

1. **Padronização de datas** — múltiplos formatos → `datetime64`
2. **Padronização de turnos** — normalização textual via `MAPA_TURNOS` (14 variações)
3. **Tratamento de ausentes** — mediana por `(produto, turno)`; flags de imputação
4. **Sinalização de inconsistências** — Z-score por grupo; flag `quantidade_negativa`
5. **Features temporais** — `dia_semana`, `mes`, `ano`, `is_fim_de_semana`, `is_feriado`
6. **Features de lag** — `lag_1d`, `lag_7d`, `media_movel_7d`, `media_movel_14d`
7. **Codificação categórica** — `produto_cod`, `turno_cod` (inteiros)
8. **Split cronológico** — `iloc[:n]` / `iloc[n:]` (80/20, sem aleatoriedade)

### 5.2 Princípio anti-leakage

```python
# CORRETO — shift antes do rolling
df["media_movel_7d"] = df.groupby(["produto", "turno"])["quantidade_vendida"] \
    .transform(lambda s: s.shift(1).rolling(7, min_periods=1).mean())

# PROIBIDO — usa informação do dia corrente
df["media_movel_7d"] = df["quantidade_vendida"].rolling(7).mean()  # ❌
```

---

## 6. Modelos Preditivos (`src/modelos.py`)

### 6.1 Hierarquia de modelos

| Nível | Modelo | Observação |
|-------|--------|------------|
| Baseline B4 | Média histórica por produto × turno × dia_semana | Referência mínima |
| M1 | Regressão Linear (`Pipeline[StandardScaler + LinearRegression]`) | Interpretável |
| M2 | Random Forest (`n_estimators=200`, `max_depth=10`) | Robusto a outliers |
| M3 | XGBoost (`learning_rate=0.05`, early stopping) | Maior capacidade |

### 6.2 XGBoost — estratégia de early stopping

```python
# Validação cruzada: n_estimators fixo em 200 (sem data leakage via eval set)
# Treinamento final: últimos 15% temporais como eval set
n_eval = max(1, int(len(X_train) * 0.15))
X_tr, X_ev = X_train[:-n_eval], X_train[-n_eval:]
y_tr, y_ev = y_train[:-n_eval], y_train[-n_eval:]
modelo.fit(X_tr, y_tr, eval_set=[(X_ev, y_ev)], verbose=False)
```

### 6.3 Features utilizadas

**Base:** `dia_semana`, `mes`, `ano`, `is_fim_de_semana`, `is_feriado`, `lag_1d`, `lag_7d`, `media_movel_7d`, `media_movel_14d`, `produto_cod`, `turno_cod`

**Proibidas (vazamento):** `receita_total`, `quantidade_cancelada`

### 6.4 Validação cruzada

`TimeSeriesSplit(n_splits=5)` — preserva ordem temporal em todos os folds.

---

## 7. Avaliação (`src/avaliacao.py`)

### 7.1 Métricas calculadas

| Métrica | Fórmula | Interpretação |
|---------|---------|---------------|
| MAE | `mean(|y - ŷ|)` | Erro médio absoluto (mesma unidade da venda) |
| RMSE | `sqrt(mean((y-ŷ)²))` | Penaliza erros grandes |
| R² | `1 - SS_res/SS_tot` | Variância explicada (1.0 = perfeito) |
| MAPE | `mean(|y-ŷ|/y) × 100` | Erro percentual médio |
| Bias | `mean(ŷ - y)` | Tendência sistemática |

### 7.2 Critérios de aceitação

| Métrica | Limite | Status |
|---------|--------|--------|
| MAPE | ≤ 15% | `[inserir resultado real após validação]` |
| MAE | ≤ 8 unidades | `[inserir resultado real após validação]` |
| R² | ≥ 0.70 | `[inserir resultado real após validação]` |
| Bias relativo | ≤ ±5% | `[inserir resultado real após validação]` |

### 7.3 Análise de resíduos

- **Teste t** (bias ≠ 0): p-valor `[inserir resultado real após validação]`
- **Pearson** (heterocedasticidade): p-valor `[inserir resultado real após validação]`
- **Shapiro-Wilk** (normalidade): p-valor `[inserir resultado real após validação]`
- **Autocorrelação lag-1**: coeficiente `[inserir resultado real após validação]`

---

## 8. API REST (`app/`)

### 8.1 Endpoints

| Método | Endpoint | Descrição |
|--------|----------|-----------|
| `GET` | `/saude/` | Health check |
| `GET` | `/produtos/` | Listar produtos |
| `GET` | `/produtos/{id}` | Detalhar produto |
| `POST` | `/produtos/` | Cadastrar produto |
| `POST` | `/vendas/` | Registrar venda |
| `GET` | `/vendas/` | Listar vendas (filtros: data, produto, turno) |
| `GET` | `/vendas/{id}` | Detalhar venda |
| `POST` | `/previsoes/` | Gerar previsão individual |
| `POST` | `/previsoes/lote` | Gerar previsões em lote (máx. 365) |
| `GET` | `/previsoes/historico` | Consultar histórico de previsões |

### 8.2 Validações automáticas (Pydantic v2)

- `data` não pode ser futura → HTTP 422
- `quantidade_vendida` deve ser ≥ 0 → HTTP 422
- `nome` do produto não pode ser vazio → HTTP 422
- Produto/turno inexistente em previsão → HTTP 404

### 8.3 Segurança

- CORS restrito a `ALLOWED_ORIGINS` (padrão: `http://localhost:8501`)
- Secrets exclusivamente via variáveis de ambiente (`.env`)
- `PRAGMA foreign_keys=ON` garante integridade referencial no SQLite

### 8.4 Execução

```bash
uvicorn app.main:app --reload --port 8000
# Documentação interativa: http://localhost:8000/docs
```

---

## 9. Dashboard (`dashboard/`)

### 9.1 Páginas

| Página | Funcionalidade |
|--------|---------------|
| Início | KPIs gerais, tendência 60 dias, resumo de métricas |
| Histórico de Vendas | Série temporal, barras por produto, heatmap dia×turno |
| Previsão de Demanda | Formulário individual, gauge de risco, previsão em lote |
| Métricas do Modelo | Veredicto de aprovação, comparação entre modelos |
| Previsto × Realizado | MAE/RMSE/MAPE calculados, gráficos de dispersão |
| Apoio à Decisão | Alertas de risco, recomendações por turno, checklist |

### 9.2 Classificação de risco

```python
LIMIAR_EXCESSO = 0.20  # previsto > 20% acima do realizado
LIMIAR_FALTA   = 0.20  # previsto > 20% abaixo do realizado

erro_relativo = (previsto - realizado) / realizado
# > +0.20 → EXCESSO (risco de desperdício)
# < -0.20 → FALTA   (risco de ruptura)
# entre   → NORMAL
```

### 9.3 Execução

```bash
streamlit run dashboard/Inicio.py
# Acesso: http://localhost:8501
```

---

## 10. Integrador com PDV (`integrador/`)

### 10.1 Modelo de maturidade (3 estágios)

| Estágio | Mecanismo | Status |
|---------|-----------|--------|
| 1 | CSV manual em `data/incoming/` | ✅ Implementado |
| 2 | Polling automático de diretório/FTP | 🔜 Planejado |
| 3 | Webhook/API REST em tempo real | 🔜 Planejado (stub em `api_connector.py`) |

### 10.2 Fluxo de dados

```
Arquivo CSV → CsvConnector.ler_vendas()
           → validar_vendas()  ← rejeitados → data/quarantine/
           → transformar_vendas()
           → data/processed/
           → log_integracao.registrar_execucao()
```

### 10.3 Conformidade LGPD

- Campos `numero_pedido` e `operador_id` são anonimizados via SHA-256 antes de qualquer persistência.
- Nenhum dado de cliente (nome, CPF, contato) é ingerido pelo sistema.
- Dados brutos de vendas (`data/raw/`) são excluídos do controle de versão.

---

## 11. Banco de Dados

### 11.1 Tecnologias

- **Desenvolvimento:** SQLite (arquivo `prato.db` — não versionado)
- **Produção:** PostgreSQL (configurar `DATABASE_URL` no `.env`)

### 11.2 Tabelas principais

```sql
vendas (
    id, data, produto_id, turno_id,
    quantidade_vendida, preco_unitario, receita_total, criado_em,
    UNIQUE(data, produto_id, turno_id)
)

historico_previsoes (
    id, data_previsao, produto_id, turno_id,
    quantidade_prevista, modelo_utilizado, gerado_em
)
```

### 11.3 Configuração

```bash
# Criar banco e aplicar DDL
make setup-db
# ou manualmente:
sqlite3 prato.db < database/ddl_prato.sql
sqlite3 prato.db < database/ddl_indices.sql
sqlite3 prato.db < database/seed_dados_iniciais.sql
```

---

## 12. Testes Automatizados

### 12.1 Suíte de testes

| Arquivo | Módulo testado | Testes |
|---------|---------------|--------|
| `test_ingestao.py` | `src/ingestao.py` | 4 |
| `test_preprocessamento.py` | `src/preprocessamento.py` | 5 |
| `test_baseline.py` | `src/baseline.py` | 3 |
| `test_modelos.py` | `src/modelos.py` | 8 |
| `test_api.py` | `app/` (FastAPI) | 4 |
| **Total** | | **24** |

### 12.2 Cobertura

```
[inserir resultado real após validação com: pytest --cov=src --cov=app]
```

### 12.3 Casos críticos testados

- **Zero-safe fallback:** `0.0` não deve acionar fallback de hierarquia de baseline
- **Anti-leakage:** split cronológico garante `treino.max_data ≤ teste.min_data`
- **Rejeição de data futura:** API retorna 422 para `data > hoje`
- **Rejeição de quantidade negativa:** API retorna 422 para `quantidade_vendida < 0`
- **Colunas proibidas:** `receita_total` nunca aparece nas features selecionadas

### 12.4 Execução

```bash
make test
# ou
pytest tests/ -v --cov=src --cov=app --cov-report=term-missing
```

---

## 13. Instalação e Configuração

### 13.1 Pré-requisitos

- Python 3.11+
- Git
- 4 GB RAM mínimo (XGBoost com dataset ≥ 100k linhas requer mais)

### 13.2 Instalação

```bash
git clone https://github.com/filipe-macedo/prato.git
cd prato
python -m venv .venv
.venv\Scripts\activate          # Windows
# source .venv/bin/activate     # Linux/macOS
pip install -r requirements.txt
cp .env.example .env
make setup-db
```

### 13.3 Geração de dados de exemplo

```bash
python data/samples/gerar_dados_exemplo.py
# Gera: data/samples/vendas_exemplo.csv (dados 100% sintéticos)
```

### 13.4 Execução do pipeline completo

```bash
make pipeline
# Equivalente a:
python src/pipeline_dados.py \
    --entrada data/samples/vendas_exemplo.csv \
    --saida data/processed/
```

---

## 14. Variáveis de Ambiente

| Variável | Padrão | Descrição |
|----------|--------|-----------|
| `DATABASE_URL` | `sqlite:///./prato.db` | String de conexão do banco |
| `CAMINHO_MODELO` | `models/modelo_final.pkl` | Caminho do modelo serializado |
| `DEBUG` | `true` | Modo debug da API |
| `ALLOWED_ORIGINS` | `http://localhost:8501` | Origens permitidas pelo CORS |

---

## 15. Limitações Conhecidas

1. **Histórico mínimo:** produtos com menos de 30 observações por turno produzem previsões instáveis.
2. **Sazonalidade anual:** o pipeline captura padrões semanais e mensais, mas não tendências anuais de múltiplos anos sem dados suficientes.
3. **Novos produtos:** previsão impossível sem histórico; o baseline retorna média global (B1) como fallback.
4. **XGBoost e séries curtas:** early stopping pode convergir prematuramente com conjuntos de validação < 30 pontos.
5. **Integrador Estágio 3:** `ApiConnector` é um stub; implementação real depende da documentação da API do PDV específico.

---

## 16. Glossário

| Termo | Definição |
|-------|-----------|
| **Turno** | Período de serviço do restaurante (almoço, jantar, café da manhã, lanche) |
| **Baseline B4** | Previsão pela média histórica do produto × turno × dia_semana |
| **Lag** | Valor defasado no tempo (lag_1d = valor de ontem) |
| **Leakage** | Uso indevido de informação futura durante o treinamento |
| **MAE** | Mean Absolute Error — erro médio absoluto |
| **MAPE** | Mean Absolute Percentage Error — erro percentual médio |
| **PDV** | Ponto de Venda — sistema de caixa/gestão do restaurante |
| **LGPD** | Lei Geral de Proteção de Dados Pessoais (Lei 13.709/2018) |
| **SHA-256** | Função hash criptográfica usada para anonimização |
| **TimeSeriesSplit** | Validação cruzada que preserva ordem temporal |

---

## 17. Referências

- CHEN, T.; GUESTRIN, C. **XGBoost: A Scalable Tree Boosting System**. KDD, 2016.
- BREIMAN, L. **Random Forests**. Machine Learning, v. 45, n. 1, p. 5–32, 2001.
- HYNDMAN, R. J.; ATHANASOPOULOS, G. **Forecasting: Principles and Practice**. 3. ed. OTexts, 2021.
- FASTAPI. **FastAPI Documentation**. Disponível em: https://fastapi.tiangolo.com. Acesso em: 2026.
- STREAMLIT. **Streamlit Documentation**. Disponível em: https://docs.streamlit.io. Acesso em: 2026.
- BRASIL. **Lei nº 13.709, de 14 de agosto de 2018** — Lei Geral de Proteção de Dados Pessoais (LGPD). Diário Oficial da União, Brasília, DF, 2018.
