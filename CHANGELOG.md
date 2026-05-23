# CHANGELOG — PRATO

Todas as alterações relevantes do projeto são registradas neste arquivo.
Formato baseado em [Keep a Changelog](https://keepachangelog.com/pt-BR/1.0.0/).

## [1.0.0] — 2026-05-21

### Adicionado
- Pipeline completo de ingestão e pré-processamento de dados (`src/`)
- Módulo de feature engineering com lag features e médias móveis
- Quatro estratégias de modelo baseline (B1–B4) com fallback hierárquico
- Modelos supervisionados: Regressão Linear, Random Forest e XGBoost
- Validação cruzada temporal com `TimeSeriesSplit`
- Módulo de avaliação com critérios de aceitação e análise de resíduos
- API REST com FastAPI: endpoints de vendas, produtos e previsões
- Interface interativa com Streamlit: 5 páginas de navegação
- Arquitetura de integração PDV com padrão Adapter e 3 estágios
- Esquema relacional com 8 tabelas (SQLite/PostgreSQL)
- Testes automatizados com Pytest
- CI com GitHub Actions (lint + testes)
- Documentação técnica completa em padrão ABNT

### Limitações conhecidas v1.0
- Sem autenticação de usuários na API
- Integração PDV apenas no Estágio 1 (upload manual)
- Previsões pontuais (sem intervalo de confiança)
- Reatreino manual (sem gatilho automático)
