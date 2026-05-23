# PRATO — Sistema de Previsão de Demanda em Restaurantes

[![Python](https://img.shields.io/badge/Python-3.11%2B-blue)](https://www.python.org)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.111%2B-009688)](https://fastapi.tiangolo.com)
[![Streamlit](https://img.shields.io/badge/Streamlit-1.35%2B-FF4B4B)](https://streamlit.io)
[![License: MIT](https://img.shields.io/badge/License-MIT-green)](LICENSE)

Sistema de inteligência artificial para **previsão de demanda por produto, data e turno**
em restaurantes, com apoio à decisão operacional para gestão de estoque, compras e escala de cozinha.

---

## Visão Geral

```
Dados → [Pipeline de tratamento] → [Modelos ML] → [API + Dashboard]
```

| Camada | Módulo | Tecnologia |
|---|---|---|
| Ingestão e tratamento | `src/` | Pandas, NumPy |
| Modelagem preditiva | `src/modelos.py` | Scikit-learn, XGBoost |
| API REST | `app/` | FastAPI, SQLAlchemy |
| Interface interativa | `dashboard/` | Streamlit, Plotly |
| Integração PDV/Estoque | `integrador/` | Padrão Adapter |

---

## Requisitos

- Python **3.11** ou superior
- Git

---

## Instalação

```bash
# 1. Clonar o repositório
git clone https://github.com/filipe-macedo/prato.git
cd prato

# 2. Criar e ativar ambiente virtual
python -m venv .venv

# Linux/macOS
source .venv/bin/activate

# Windows (PowerShell)
.venv\Scripts\Activate.ps1

# 3. Instalar dependências
pip install -r requirements.txt

# 4. Configurar variáveis de ambiente
cp .env.example .env

# 5. Inicializar banco de dados
python -c "from app.database import engine, Base; Base.metadata.create_all(engine)"
```

---

## Execução Rápida (dados de exemplo)

```bash
# Gerar dados sintéticos de demonstração
python data/samples/gerar_dados_exemplo.py

# Executar pipeline completo: dados → treino → avaliação
make pipeline

# Iniciar API (Terminal 1)
make run-api
# Acesse: http://localhost:8000/docs

# Iniciar dashboard (Terminal 2)
make run-dashboard
# Acesse: http://localhost:8501
```

---

## Execução com Dados Reais

```bash
# Coloque seu arquivo em data/raw/
# Colunas obrigatórias: data, produto, turno, quantidade_vendida

python -m src.pipeline_dados --entrada data/raw/SEU_ARQUIVO.csv
python -m src.modelos
python -m src.avaliacao
```

---

## Formato dos Dados de Entrada

| Campo | Tipo | Obrigatório | Exemplo |
|---|---|---|---|
| `data` | DATE | Sim | `2024-07-15` ou `15/07/2024` |
| `produto` | TEXT | Sim | `prato_executivo` |
| `turno` | TEXT | Sim | `almoco`, `jantar`, `cafe_manha` |
| `quantidade_vendida` | NUMERIC | Sim | `42` |
| `categoria` | TEXT | Não | `prato_principal` |
| `preco_unitario` | NUMERIC | Não | `35.90` |

> Turnos aceitos: `almoco`, `jantar`, `cafe_manha`, `lanche` e variações com acento
> ou maiúsculas — o pipeline normaliza automaticamente.

---

## Métricas de Aceitação do Modelo

| Métrica | Aprovado | Atenção |
|---|---|---|
| MAE relativo | ≤ 15% | ≤ 30% |
| R² | ≥ 0.50 | ≥ 0.30 |
| Ganho MAE sobre baseline | ≥ 15% | ≥ 5% |
| MAPE | ≤ 25% | ≤ 40% |

---

## Estrutura do Projeto

```
prato/
├── app/            # API REST (FastAPI)
├── dashboard/      # Interface (Streamlit)
├── data/           # Dados — brutos NÃO versionados
│   ├── external/   # Feriados nacionais (dado público)
│   └── samples/    # Dados fictícios para demonstração
├── database/       # DDL e scripts SQL
├── docs/           # Documentação técnica
├── integrador/     # Conectores PDV e estoque
├── models/         # Modelos treinados (NÃO versionados)
├── notebooks/      # Análise exploratória
├── outputs/        # Métricas e previsões geradas (NÃO versionados)
├── src/            # Pipeline de Machine Learning
└── tests/          # Testes automatizados
```

---

## Comandos Disponíveis

```bash
make install        # Instala dependências
make run-api        # Inicia API FastAPI (porta 8000)
make run-dashboard  # Inicia dashboard Streamlit (porta 8501)
make pipeline       # Executa pipeline completo
make test           # Executa testes com cobertura
make lint           # Verifica qualidade do código
make setup-db       # Cria tabelas no banco de dados
make help           # Lista todos os comandos
```

---

## Testes

```bash
pytest tests/ -v --cov=src --cov=app
```

---

## Documentação

| Documento | Localização |
|---|---|
| Documentação técnica completa (ABNT) | `docs/documentacao_tecnica.md` |
| Arquitetura da solução | `docs/arquitetura.md` |
| Dicionário de dados | `docs/dicionario_dados.md` |
| Guia de contribuição | `docs/guia_contribuicao.md` |
| API interativa (Swagger) | `http://localhost:8000/docs` |

---

## Limitações da Versão 1.0

- Integração com PDV apenas via upload manual (CSV/Excel)
- Sem autenticação de usuários na API
- Previsões pontuais (sem intervalo de confiança)
- Reatreino do modelo é manual
- Volume mínimo recomendado: 90 dias de histórico

---

## Licença

[MIT License](LICENSE) — Copyright (c) 2026 Filipe Macedo
