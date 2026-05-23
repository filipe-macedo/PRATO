from sqlalchemy.orm import Session
from app.models.venda import Venda
from app.schemas.venda import VendaCriar


def registrar_venda(entrada: VendaCriar, db: Session) -> Venda:
    receita = None
    if entrada.preco_unitario is not None:
        receita = entrada.quantidade_vendida * entrada.preco_unitario

    venda = Venda(
        data=entrada.data,
        produto_id=entrada.produto_id,
        turno_id=entrada.turno_id,
        quantidade_vendida=entrada.quantidade_vendida,
        preco_unitario=entrada.preco_unitario,
        receita_total=receita,
    )
    db.add(venda)
    db.commit()
    db.refresh(venda)
    return venda
