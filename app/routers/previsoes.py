from fastapi import APIRouter, Query
from datetime import date
from app.dependencies import DbSession, ModeloDep
from app.models.previsao import HistoricoPrevisao
from app.schemas.previsao import (
    PrevisaoEntrada, PrevisaoResposta,
    PrevisaoLote, PrevisaoLoteResposta,
)
from app.services.previsao_service import gerar_previsao

router = APIRouter(prefix="/previsoes", tags=["Previsões"])


@router.post("/", response_model=PrevisaoResposta, summary="Gera previsão única")
def prever(entrada: PrevisaoEntrada, modelo: ModeloDep, db: DbSession):
    return gerar_previsao(entrada, modelo, db)


@router.post("/lote", response_model=PrevisaoLoteResposta, summary="Gera previsões em lote")
def prever_lote(payload: PrevisaoLote, modelo: ModeloDep, db: DbSession):
    resultados = [gerar_previsao(e, modelo, db) for e in payload.previsoes]
    return PrevisaoLoteResposta(total=len(resultados), resultados=resultados)


@router.get("/historico", summary="Consulta histórico de previsões")
def historico_previsoes(
    db: DbSession,
    data_inicio: date | None = Query(None),
    data_fim: date | None = Query(None),
    produto_id: int | None = Query(None),
    turno_id: int | None = Query(None),
    limite: int = Query(200, ge=1, le=1000),
):
    query = db.query(HistoricoPrevisao)
    if data_inicio:
        query = query.filter(HistoricoPrevisao.data_previsao >= data_inicio)
    if data_fim:
        query = query.filter(HistoricoPrevisao.data_previsao <= data_fim)
    if produto_id:
        query = query.filter(HistoricoPrevisao.produto_id == produto_id)
    if turno_id:
        query = query.filter(HistoricoPrevisao.turno_id == turno_id)

    registros = query.order_by(HistoricoPrevisao.data_previsao).limit(limite).all()
    return [
        {
            "id": r.id,
            "data_previsao": r.data_previsao.isoformat(),
            "produto_id": r.produto_id,
            "turno_id": r.turno_id,
            "quantidade_prevista": r.quantidade_prevista,
            "modelo_utilizado": r.modelo_utilizado,
            "gerado_em": r.gerado_em.isoformat(),
        }
        for r in registros
    ]
