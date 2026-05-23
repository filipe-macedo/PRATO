from sqlalchemy import Column, Integer, Numeric, Date, DateTime, ForeignKey
from sqlalchemy.sql import func
from app.database import Base


class Venda(Base):
    __tablename__ = "vendas"

    id = Column(Integer, primary_key=True, index=True)
    data = Column(Date, nullable=False, index=True)
    produto_id = Column(Integer, ForeignKey("produtos.id"), nullable=False, index=True)
    turno_id = Column(Integer, ForeignKey("turnos.id"), nullable=False, index=True)
    quantidade_vendida = Column(Numeric(10, 2), nullable=False)
    preco_unitario = Column(Numeric(10, 2), nullable=True)
    receita_total = Column(Numeric(12, 2), nullable=True)
    criado_em = Column(DateTime, server_default=func.now(), nullable=False)
