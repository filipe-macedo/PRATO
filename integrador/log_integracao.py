"""
log_integracao.py
Registro estruturado de execuções do pipeline de integração.
Grava JSON-lines em logs/integracao.log para auditoria e monitoramento.
"""

from __future__ import annotations

import json
import logging
import logging.handlers
from datetime import datetime
from pathlib import Path
from typing import List, Optional

from integrador.config_integracao import DIR_LOGS

# ---------------------------------------------------------------------------
# Configuração do logger de integração
# ---------------------------------------------------------------------------
_LOG_FILE = DIR_LOGS / "integracao.log"
_LOG_FILE.parent.mkdir(parents=True, exist_ok=True)

_logger_integracao = logging.getLogger("prato.integracao")

if not _logger_integracao.handlers:
    _handler = logging.handlers.RotatingFileHandler(
        _LOG_FILE,
        maxBytes=5 * 1024 * 1024,   # 5 MB por arquivo
        backupCount=5,
        encoding="utf-8",
    )
    _handler.setFormatter(logging.Formatter("%(message)s"))  # JSON puro
    _logger_integracao.addHandler(_handler)
    _logger_integracao.setLevel(logging.INFO)
    _logger_integracao.propagate = False  # não duplica no logger raiz


# ---------------------------------------------------------------------------
# Função pública
# ---------------------------------------------------------------------------

def registrar_execucao(
    tipo:       str,
    conector:   str,
    total:      int,
    ok:         int,
    rejeitados: int,
    erros:      Optional[List[str]] = None,
    extra:      Optional[dict]      = None,
) -> None:
    """
    Grava uma linha JSON-lines no arquivo de log de integração.

    Parameters
    ----------
    tipo : str
        Tipo de dado ingerido: "vendas" ou "estoque".
    conector : str
        Nome da classe do conector utilizado (ex.: "CsvConnector").
    total : int
        Total de linhas lidas da fonte.
    ok : int
        Linhas aprovadas na validação.
    rejeitados : int
        Linhas rejeitadas na validação.
    erros : list of str, optional
        Mensagens de erro/aviso coletados durante a execução.
    extra : dict, optional
        Metadados adicionais livres.
    """
    registro = {
        "timestamp":   datetime.now().isoformat(timespec="seconds"),
        "tipo":        tipo,
        "conector":    conector,
        "total":       total,
        "ok":          ok,
        "rejeitados":  rejeitados,
        "taxa_rejeicao": round(rejeitados / total, 4) if total > 0 else 0.0,
        "erros":       erros or [],
        **(extra or {}),
    }
    _logger_integracao.info(json.dumps(registro, ensure_ascii=False))


def ler_historico(n_ultimas: int = 50) -> List[dict]:
    """
    Lê as últimas N entradas do log de integração.

    Parameters
    ----------
    n_ultimas : int
        Número de entradas recentes a retornar.

    Returns
    -------
    list of dict
        Entradas do log em ordem cronológica (mais recente por último).
    """
    if not _LOG_FILE.exists():
        return []

    linhas = _LOG_FILE.read_text(encoding="utf-8").strip().splitlines()
    recentes = linhas[-n_ultimas:]

    registros = []
    for linha in recentes:
        try:
            registros.append(json.loads(linha))
        except json.JSONDecodeError:
            continue
    return registros
