"""
alertas_integracao.py
Geração de alertas operacionais baseados no histórico de integrações.
Detecta padrões anômalos (taxa de rejeição alta, ausência de dados, erros recorrentes)
e produz lista de alertas para exibição no dashboard ou envio via log.
"""

from __future__ import annotations

import logging
from dataclasses import dataclass
from datetime import datetime, timedelta
from typing import List

from integrador.config_integracao import TAXA_REJEICAO_MAX
from integrador.log_integracao import ler_historico

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Estrutura de alerta
# ---------------------------------------------------------------------------

SEVERIDADE_INFO    = "INFO"
SEVERIDADE_AVISO   = "AVISO"
SEVERIDADE_CRITICO = "CRÍTICO"


@dataclass
class AlertaIntegracao:
    severidade: str
    mensagem:   str
    timestamp:  str
    tipo:       str   # "vendas" | "estoque" | "sistema"


# ---------------------------------------------------------------------------
# Detecção de alertas
# ---------------------------------------------------------------------------

def verificar_alertas(n_registros: int = 50) -> List[AlertaIntegracao]:
    """
    Analisa o histórico de integração e retorna lista de alertas ativos.

    Regras verificadas
    ------------------
    1. Taxa de rejeição média acima de TAXA_REJEICAO_MAX → AVISO.
    2. Nenhuma execução bem-sucedida nas últimas 24 horas → CRÍTICO.
    3. Execução com zero registros ingeridos → INFO.
    4. Três ou mais erros consecutivos do mesmo tipo → CRÍTICO.

    Parameters
    ----------
    n_registros : int
        Quantas entradas recentes do log analisar.

    Returns
    -------
    list of AlertaIntegracao
    """
    historico = ler_historico(n_ultimas=n_registros)
    alertas: List[AlertaIntegracao] = []
    agora = datetime.now()

    if not historico:
        alertas.append(AlertaIntegracao(
            severidade=SEVERIDADE_INFO,
            mensagem="Nenhuma execução de integração registrada ainda.",
            timestamp=agora.isoformat(timespec="seconds"),
            tipo="sistema",
        ))
        return alertas

    # 1. Taxa de rejeição média
    for tipo in ("vendas", "estoque"):
        registros_tipo = [r for r in historico if r.get("tipo") == tipo]
        if registros_tipo:
            taxa_media = sum(r.get("taxa_rejeicao", 0) for r in registros_tipo) / len(registros_tipo)
            if taxa_media > TAXA_REJEICAO_MAX:
                alertas.append(AlertaIntegracao(
                    severidade=SEVERIDADE_AVISO,
                    mensagem=(
                        f"Taxa de rejeição média de {tipo} está em "
                        f"{taxa_media:.1%} (limite: {TAXA_REJEICAO_MAX:.0%})."
                    ),
                    timestamp=agora.isoformat(timespec="seconds"),
                    tipo=tipo,
                ))

    # 2. Ausência de execuções nas últimas 24h
    limite_24h = agora - timedelta(hours=24)
    recentes = [
        r for r in historico
        if _parse_ts(r.get("timestamp", "")) > limite_24h
    ]
    if not recentes:
        alertas.append(AlertaIntegracao(
            severidade=SEVERIDADE_CRITICO,
            mensagem="Nenhuma integração executada nas últimas 24 horas.",
            timestamp=agora.isoformat(timespec="seconds"),
            tipo="sistema",
        ))

    # 3. Execuções com zero registros
    for r in historico[-10:]:
        if r.get("total", 1) == 0:
            alertas.append(AlertaIntegracao(
                severidade=SEVERIDADE_INFO,
                mensagem=f"Execução sem registros ({r.get('tipo', '?')}) em {r.get('timestamp')}.",
                timestamp=agora.isoformat(timespec="seconds"),
                tipo=r.get("tipo", "sistema"),
            ))
            break

    # 4. Erros consecutivos
    for tipo in ("vendas", "estoque"):
        registros_tipo = [r for r in historico if r.get("tipo") == tipo][-5:]
        consecutivos_com_erro = sum(1 for r in registros_tipo if r.get("erros"))
        if consecutivos_com_erro >= 3:
            alertas.append(AlertaIntegracao(
                severidade=SEVERIDADE_CRITICO,
                mensagem=f"{consecutivos_com_erro} execuções consecutivas de {tipo} com erros.",
                timestamp=agora.isoformat(timespec="seconds"),
                tipo=tipo,
            ))

    return alertas


def resumo_alertas(alertas: List[AlertaIntegracao]) -> str:
    """
    Retorna string de resumo legível dos alertas.

    Parameters
    ----------
    alertas : list of AlertaIntegracao

    Returns
    -------
    str
    """
    if not alertas:
        return "✅ Nenhum alerta ativo — integrações operando normalmente."

    linhas = [f"⚠️  {len(alertas)} alerta(s) de integração:\n"]
    for a in alertas:
        icone = {"INFO": "ℹ️", "AVISO": "⚠️", "CRÍTICO": "🔴"}.get(a.severidade, "•")
        linhas.append(f"  {icone} [{a.severidade}] {a.mensagem}")
    return "\n".join(linhas)


# ---------------------------------------------------------------------------
# Helper
# ---------------------------------------------------------------------------

def _parse_ts(ts: str) -> datetime:
    try:
        return datetime.fromisoformat(ts)
    except Exception:
        return datetime.min
