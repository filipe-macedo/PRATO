"""
config_integracao.py
Configurações e constantes para o módulo de integração com PDV/estoque.
A integração real depende do conector ativo; este arquivo centraliza
parâmetros de comportamento sem acoplamento a nenhum sistema externo.
"""

from pathlib import Path

# ---------------------------------------------------------------------------
# Diretórios de entrada / quarentena
# ---------------------------------------------------------------------------
BASE_DIR = Path(__file__).resolve().parent.parent

DIR_INCOMING_PDV       = BASE_DIR / "data" / "incoming" / "pdv"
DIR_INCOMING_ESTOQUE   = BASE_DIR / "data" / "incoming" / "estoque"
DIR_QUARANTINE_PDV     = BASE_DIR / "data" / "quarantine" / "pdv"
DIR_QUARANTINE_ESTOQUE = BASE_DIR / "data" / "quarantine" / "estoque"
DIR_PROCESSED          = BASE_DIR / "data" / "processed"
DIR_LOGS               = BASE_DIR / "logs"

# Cria diretórios se necessário (sem erro se já existirem)
for _d in [
    DIR_INCOMING_PDV, DIR_INCOMING_ESTOQUE,
    DIR_QUARANTINE_PDV, DIR_QUARANTINE_ESTOQUE,
    DIR_PROCESSED, DIR_LOGS,
]:
    _d.mkdir(parents=True, exist_ok=True)

# ---------------------------------------------------------------------------
# Colunas esperadas nos arquivos de entrada
# ---------------------------------------------------------------------------
COLUNAS_PDV_OBRIGATORIAS = [
    "data",
    "produto",
    "turno",
    "quantidade_vendida",
]

COLUNAS_PDV_OPCIONAIS = [
    "numero_pedido",   # anonimizado via SHA-256 antes de qualquer persistência
    "operador_id",     # anonimizado via SHA-256
    "preco_unitario",
    "categoria",
    "cancelado",
]

COLUNAS_ESTOQUE_OBRIGATORIAS = [
    "data",
    "produto",
    "quantidade_disponivel",
]

# ---------------------------------------------------------------------------
# Comportamento de retentativa e tolerância a falhas
# ---------------------------------------------------------------------------
MAX_TENTATIVAS_API   = 3       # retentativas em caso de erro HTTP
TIMEOUT_API_SEGUNDOS = 15      # timeout por requisição
BACKOFF_SEGUNDOS     = 2       # espera entre tentativas (dobra a cada falha)

# Taxa de rejeição máxima tolerada antes de mover lote para quarentena
TAXA_REJEICAO_MAX    = 0.10    # 10 %

# ---------------------------------------------------------------------------
# Maturidade de integração (modelo de 3 estágios)
# ---------------------------------------------------------------------------
# Estágio 1 — Arquivo CSV manual (MVP)
# Estágio 2 — Polling automático de diretório ou FTP
# Estágio 3 — Webhook / API em tempo real
ESTAGIO_ATIVO = 1  # altere conforme a infraestrutura disponível

# ---------------------------------------------------------------------------
# Campos sujeitos à anonimização LGPD (SHA-256)
# ---------------------------------------------------------------------------
CAMPOS_ANONIMIZAR = ["numero_pedido", "operador_id"]

# ---------------------------------------------------------------------------
# Encoding padrão para leitura de CSVs externos
# ---------------------------------------------------------------------------
ENCODINGS_CSV = ["utf-8", "latin-1", "cp1252"]
