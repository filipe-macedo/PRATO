from fastapi import APIRouter, HTTPException, Query
from datetime import date
from app.dependencies import DbSession
from app.models.venda import Venda
from app.schemas.venda import VendaCriar, VendaResposta
from app.services.venda_service import registrar_venda

router = APIRouter(prefix="/vendas", tags=["Vendas"])


@router.post("/", response_model=VendaResposta, status_code=201, summary="Registra uma venda")
def criar_venda(entrada: VendaCriar, db: DbSession):
    return registrar_venda(entrada, db)


@router.get("/", response_model=list[VendaResposta], summary="Lista vendas com filtros")
def listar_vendas(
    db: DbSession,
    data_inicio: date | None = Query(None),
    data_fim: date | None = Query(None),
    produto_id: int | None = Query(None),
    turno_id: int | None = Query(None),
    limite: int = Query(200, ge=1, le=1000),
):
    query = db.query(Venda)
    if data_inicio:
        query = query.filter(Venda.data >= data_inicio)
    if data_fim:
        query = query.filter(Venda.data <= data_fim)
    if produto_id:
        query = query.filter(Venda.produto_id == produto_id)
    if turno_id:
        query = query.filter(Venda.turno_id == turno_id)
    return query.order_by(Venda.data.desc()).limit(limite).all()


@router.get("/{venda_id}", response_model=VendaResposta, summary="Consulta venda por ID")
def consultar_venda(venda_id: int, db: DbSession):
    venda = db.query(Venda).filter(Venda.id == venda_id).first()
    if not venda:
        raise HTTPException(status_code=404, detail="Venda não encontrada.")
    return venda
