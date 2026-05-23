# Dicionário de Dados — PRATO

## 1. Arquivo de entrada (`data/samples/vendas_exemplo.csv`)

| Campo | Tipo | Obrigatório | Descrição | Exemplo |
|-------|------|:-----------:|-----------|---------|
| `data` | date | ✅ | Data da venda. Aceita ISO (YYYY-MM-DD) ou BR (DD/MM/YYYY) | `2024-03-15` |
| `produto` | string | ✅ | Nome do produto/prato | `prato_executivo` |
| `turno` | string | ✅ | Período de serviço normalizado | `almoco` |
| `quantidade_vendida` | float | ✅ | Unidades vendidas no turno (≥ 0) | `45.0` |
| `categoria` | string | ❌ | Categoria do produto | `prato_principal` |
| `preco_unitario` | float | ❌ | Preço unitário em R$ | `35.90` |

**Valores aceitos para `turno`:**

| Variações aceitas | Valor normalizado |
|-------------------|-------------------|
| almoço, almoco, ALMOÇO, lunch | `almoco` |
| jantar, JANTAR, janta, dinner | `jantar` |
| cafe, café, cafe_manha, breakfast | `cafe_manha` |
| lanche, snack | `lanche` |

---

## 2. Tabelas do Banco de Dados

### `categorias`

| Coluna | Tipo SQL | Restrições | Descrição |
|--------|----------|------------|-----------|
| `id` | INTEGER | PK, AUTOINCREMENT | Identificador |
| `nome` | TEXT | NOT NULL, UNIQUE | Nome da categoria |
| `descricao` | TEXT | — | Descrição livre |

### `produtos`

| Coluna | Tipo SQL | Restrições | Descrição |
|--------|----------|------------|-----------|
| `id` | INTEGER | PK | Identificador |
| `nome` | TEXT | NOT NULL, UNIQUE | Nome do produto |
| `categoria_id` | INTEGER | FK → categorias | Categoria |
| `preco_unitario` | REAL | CHECK ≥ 0 | Preço em R$ |
| `ativo` | INTEGER | DEFAULT 1 | 1=ativo, 0=inativo |

### `turnos`

| Coluna | Tipo SQL | Restrições | Descrição |
|--------|----------|------------|-----------|
| `id` | INTEGER | PK | Identificador |
| `nome` | TEXT | NOT NULL, UNIQUE | Nome normalizado |
| `hora_inicio` | TEXT | — | HH:MM |
| `hora_fim` | TEXT | — | HH:MM |

### `vendas`

| Coluna | Tipo SQL | Restrições | Descrição |
|--------|----------|------------|-----------|
| `id` | INTEGER | PK | Identificador |
| `data` | DATE | NOT NULL | Data da venda |
| `produto_id` | INTEGER | FK → produtos | Produto vendido |
| `turno_id` | INTEGER | FK → turnos | Turno da venda |
| `quantidade_vendida` | REAL | NOT NULL, CHECK ≥ 0 | Unidades vendidas |
| `preco_unitario` | REAL | — | Preço no momento da venda |
| `receita_total` | REAL | calculado | quantidade × preco |
| `criado_em` | DATETIME | DEFAULT now | Timestamp de registro |

**Restrição UNIQUE:** `(data, produto_id, turno_id)` — um registro por combinação.

### `calendario`

| Coluna | Tipo SQL | Descrição |
|--------|----------|-----------|
| `data` | DATE (PK) | Data |
| `dia_semana` | INTEGER | 0=segunda … 6=domingo |
| `is_fim_de_semana` | INTEGER | 0 ou 1 |
| `is_feriado` | INTEGER | 0 ou 1 |
| `nome_feriado` | TEXT | Nome do feriado (se aplicável) |
| `mes` | INTEGER | 1–12 |
| `ano` | INTEGER | — |
| `trimestre` | INTEGER | 1–4 |

### `historico_previsoes`

| Coluna | Tipo SQL | Descrição |
|--------|----------|-----------|
| `id` | INTEGER (PK) | Identificador |
| `data_previsao` | DATE | Data prevista |
| `produto_id` | INTEGER (FK) | Produto |
| `turno_id` | INTEGER (FK) | Turno |
| `quantidade_prevista` | REAL | Previsão do modelo (≥ 0) |
| `modelo_utilizado` | TEXT | Nome do modelo serializado |
| `gerado_em` | DATETIME | Timestamp de geração |

---

## 3. Features de Machine Learning

### Features de entrada (`src/modelos.py → FEATURES_BASE`)

| Feature | Fonte | Descrição |
|---------|-------|-----------|
| `dia_semana` | calendario | 0=segunda … 6=domingo |
| `mes` | calendario | 1–12 |
| `ano` | calendario | Ano |
| `is_fim_de_semana` | calendario | Binária |
| `is_feriado` | calendario | Binária |
| `lag_1d` | vendas (.shift(1)) | Vendas do dia anterior |
| `lag_7d` | vendas (.shift(7)) | Vendas de 7 dias atrás |
| `media_movel_7d` | vendas (.shift(1).rolling(7)) | Média móvel 7 dias |
| `media_movel_14d` | vendas (.shift(1).rolling(14)) | Média móvel 14 dias |
| `produto_cod` | encoding | Código inteiro do produto |
| `turno_cod` | encoding | Código inteiro do turno |

### Colunas **proibidas** como features (vazamento de dados)

| Coluna | Motivo |
|--------|--------|
| `receita_total` | Calculada a partir da quantidade (target) |
| `quantidade_cancelada` | Informação futura / não disponível em produção |

---

## 4. Saídas do Pipeline (`data/processed/`)

| Arquivo | Conteúdo |
|---------|----------|
| `vendas_tratado.csv` | Dataset completo pós-preprocessamento |
| `vendas_treino.csv` | Primeiros 80% (cronológico) |
| `vendas_teste.csv` | Últimos 20% (cronológico) |
| `mapeamentos_categoricos.json` | Dicionários produto→código, turno→código |
| `auditoria_flags.csv` | Linhas sinalizadas com inconsistências |

---

## 5. Outputs de Avaliação (`outputs/`)

| Arquivo | Conteúdo |
|---------|----------|
| `avaliacao/metricas_*.json` | MAE, RMSE, R², MAPE por modelo |
| `avaliacao/residuos_*.png` | Gráficos de análise de resíduos |
| `metricas/comparacao_modelos.csv` | Tabela comparativa todos os modelos |
| `previsoes/previsoes_*.csv` | Previsões geradas pelo modelo em produção |
