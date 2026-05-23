from fastapi import APIRouter, HTTPException, Query
from app.dependencies import DbSession
from app.models.produto import Produto
from app.schemas.produto import ProdutoCriar, ProdutoResposta

router = APIRouter(prefix="/produtos", tags=["Produtos"])


@router.get("/", response_model=list[ProdutoResposta], summary="Lista produtos")
def listar_produtos(
    db: DbSession,
    apenas_ativos: bool = Query(True),
    categoria: str | None = Query(None),
):
    query = db.query(Produto)
    if apenas_ativos:
        query = query.filter(Produto.ativo.is_(True))
    if categoria:
        query = query.filter(Produto.categoria.ilike(f"%{categoria}%"))
    return query.order_by(Produto.nome).all()


@router.get("/{produto_id}", response_model=ProdutoResposta, summary="Consulta produto por ID")
def consultar_produto(produto_id: int, db: DbSession):
    produto = db.query(Produto).filter(Produto.id == produto_id).first()
    if not produto:
        raise HTTPException(status_code=404, detail="Produto não encontrado.")
    return produto


@router.post("/", response_model=ProdutoResposta, status_code=201, summary="Cadastra produto")
def cadastrar_produto(entrada: ProdutoCriar, db: DbSession):
    if db.query(Produto).filter(Produto.nome == entrada.nome).first():
        raise HTTPException(status_code=409, detail="Produto com este nome já existe.")
    produto = Produto(**entrada.model_dump())
    db.add(produto)
    db.commit()
    db.refresh(produto)
    return produto
