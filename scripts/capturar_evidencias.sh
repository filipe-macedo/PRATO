#!/usr/bin/env bash
# =============================================================================
# capturar_evidencias.sh
# Coleta evidências de execução do sistema PRATO para entrega acadêmica.
# Gera um diretório timestampado com logs, métricas e screenshots de texto.
#
# Uso:
#   bash scripts/capturar_evidencias.sh
#   bash scripts/capturar_evidencias.sh --dir outputs/evidencias_v2
# =============================================================================

set -euo pipefail

# ---------------------------------------------------------------------------
# Configuração
# ---------------------------------------------------------------------------
TS=$(date +"%Y%m%d_%H%M%S")
DIR_SAIDA="${1:-outputs/evidencias_${TS}}"

mkdir -p "$DIR_SAIDA"

echo "=================================================="
echo "  PRATO — Captura de Evidências"
echo "  Destino: $DIR_SAIDA"
echo "=================================================="

# ---------------------------------------------------------------------------
# 1. Informações do ambiente
# ---------------------------------------------------------------------------
echo "[1/7] Coletando informações do ambiente..."
{
  echo "=== Python ==="
  python --version

  echo ""
  echo "=== Pacotes instalados ==="
  pip list --format=columns

  echo ""
  echo "=== Sistema operacional ==="
  uname -a 2>/dev/null || echo "Windows (uname não disponível)"

  echo ""
  echo "=== Data/hora da captura ==="
  date
} > "$DIR_SAIDA/ambiente.txt"

# ---------------------------------------------------------------------------
# 2. Estrutura de arquivos do projeto
# ---------------------------------------------------------------------------
echo "[2/7] Mapeando estrutura de arquivos..."
if command -v tree &>/dev/null; then
  tree -I ".venv|__pycache__|*.pyc|*.egg-info|.git" \
       --dirsfirst -a \
       > "$DIR_SAIDA/estrutura_projeto.txt" 2>/dev/null || true
else
  find . \
    -not -path "./.venv/*" \
    -not -path "./.git/*" \
    -not -name "*.pyc" \
    -not -name "__pycache__" \
    | sort > "$DIR_SAIDA/estrutura_projeto.txt"
fi

# ---------------------------------------------------------------------------
# 3. Execução dos testes
# ---------------------------------------------------------------------------
echo "[3/7] Executando testes..."
pytest tests/ \
  --cov=src \
  --cov=app \
  --cov-report=term-missing \
  -v \
  2>&1 | tee "$DIR_SAIDA/resultado_testes.txt" || true

# ---------------------------------------------------------------------------
# 4. Verificação de lint
# ---------------------------------------------------------------------------
echo "[4/7] Verificando lint..."
ruff check . 2>&1 | tee "$DIR_SAIDA/resultado_lint.txt" || true

# ---------------------------------------------------------------------------
# 5. Pipeline de dados (se dados de exemplo existirem)
# ---------------------------------------------------------------------------
echo "[5/7] Executando pipeline de dados com dados de exemplo..."
ARQUIVO_EXEMPLO="data/samples/vendas_exemplo.csv"

if [ -f "$ARQUIVO_EXEMPLO" ]; then
  python src/pipeline_dados.py \
    --entrada "$ARQUIVO_EXEMPLO" \
    --saida data/processed/ \
    2>&1 | tee "$DIR_SAIDA/pipeline_execucao.txt" || true
else
  echo "Arquivo $ARQUIVO_EXEMPLO não encontrado." \
    "Execute primeiro: python data/samples/gerar_dados_exemplo.py" \
    > "$DIR_SAIDA/pipeline_execucao.txt"
fi

# ---------------------------------------------------------------------------
# 6. Copiar métricas e outputs já existentes
# ---------------------------------------------------------------------------
echo "[6/7] Copiando outputs existentes..."
for pasta in outputs/avaliacao outputs/metricas outputs/previsoes; do
  if [ -d "$pasta" ] && [ "$(ls -A $pasta 2>/dev/null)" ]; then
    cp -r "$pasta" "$DIR_SAIDA/"
    echo "  ✓ $pasta copiado."
  fi
done

# ---------------------------------------------------------------------------
# 7. Sumário de arquivos gerados
# ---------------------------------------------------------------------------
echo "[7/7] Gerando sumário..."
{
  echo "=== Evidências capturadas em $TS ==="
  echo ""
  ls -lh "$DIR_SAIDA/"
} | tee "$DIR_SAIDA/SUMARIO.txt"

echo ""
echo "=================================================="
echo "  ✅ Evidências salvas em: $DIR_SAIDA"
echo "=================================================="
