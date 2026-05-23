# Guia de Contribuição — PRATO

Obrigado pelo interesse em contribuir! Este documento descreve o fluxo de trabalho esperado.

---

## Pré-requisitos

- Python 3.11+
- Git configurado com nome e e-mail
- Fork do repositório em `github.com/<seu-usuario>/prato`

---

## Configuração do ambiente

```bash
# 1. Clone seu fork
git clone https://github.com/<seu-usuario>/prato.git
cd prato

# 2. Crie e ative o ambiente virtual
python -m venv .venv
# Windows
.venv\Scripts\activate
# Linux/macOS
source .venv/bin/activate

# 3. Instale as dependências
pip install -r requirements.txt

# 4. Configure variáveis de ambiente
cp .env.example .env
# Edite .env se necessário (nunca comite o .env real)
```

---

## Estratégia de branches

```
main        ← produção estável (protegida)
develop     ← integração (base para PRs)
feat/*      ← novas funcionalidades
fix/*       ← correções de bugs
hotfix/*    ← correções urgentes em produção
```

**Regra:** nunca comite diretamente em `main` ou `develop`.

```bash
# Criar branch de feature
git checkout develop
git pull origin develop
git checkout -b feat/nome-da-feature

# Criar branch de bugfix
git checkout -b fix/descricao-do-bug
```

---

## Convenção de commits

Seguimos [Conventional Commits](https://www.conventionalcommits.org/pt-br/):

```
feat:     nova funcionalidade
fix:      correção de bug
docs:     alteração apenas em documentação
test:     adição ou correção de testes
refactor: refatoração sem mudança de comportamento
perf:     melhoria de performance
chore:    manutenção (deps, CI, configurações)
```

**Exemplos:**
```
feat: adicionar endpoint POST /previsoes/lote
fix: corrigir fallback zero-safe em BaselinePrevisao
docs: atualizar dicionário de dados com coluna receita_total
test: adicionar test_treinar_xgboost_retorna_pipeline
```

---

## Fluxo de Pull Request

1. Faça suas alterações na branch de feature.
2. Execute os testes localmente:
   ```bash
   make test
   make lint
   ```
3. Garanta que não há arquivos sensíveis no commit:
   - Sem `.env` real
   - Sem `data/raw/*.csv` (dados reais)
   - Sem `models/*.pkl`
   - Sem `*.db`

4. Abra o PR para a branch `develop` (não para `main`).
5. Preencha o template de PR com: motivação, o que mudou, como testar.
6. Aguarde aprovação de ao menos 1 revisor.

---

## Padrões de código

- **Formatação:** `ruff format .` (PEP 8, linha máx. 100 chars)
- **Linting:** `ruff check .`
- **Docstrings:** NumPy style para funções públicas
- **Tipos:** type hints obrigatórios em funções públicas
- **Testes:** pytest com fixtures em `conftest.py`; mínimo 80% de cobertura em novos módulos

```bash
# Verificar tudo de uma vez
make lint
make test
```

---

## Segurança de dados (LGPD)

- **Nunca** comite dados reais de clientes ou vendas.
- `data/samples/` contém apenas dados **sintéticos** gerados com `np.random.seed(42)`.
- Campos sensíveis (`numero_pedido`, `operador_id`) são anonimizados via SHA-256 antes de qualquer persistência.
- Dúvidas? Abra uma Issue antes de implementar qualquer feature que envolva dados pessoais.

---

## Reportar bugs

Use o template de Issue em `.github/ISSUE_TEMPLATE/bug_report.md`:

- Descreva o comportamento esperado × observado
- Inclua o traceback completo
- Informe versão do Python e sistema operacional
- **Nunca** inclua dados reais de restaurantes no report

---

## Sugestões de features

Use `.github/ISSUE_TEMPLATE/feature_request.md`. Descreva:

- Problema que resolve
- Proposta de solução
- Alternativas consideradas
- Impacto nos módulos existentes

---

## Dúvidas

Abra uma Discussion no GitHub ou entre em contato via Issues com a label `question`.
