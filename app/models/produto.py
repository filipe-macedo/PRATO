from sqlalchemy import Column, Integer, String, Numeric, Boolean
from app.database import Base


class Produto(Base):
    __tablename__ = "produtos"

    id = Column(Integer, primary_key=True, index=True)
    nome = Column(String(150), nullable=False, unique=True, index=True)
    categoria = Column(String(100), nullable=True)
    preco_unitario = Column(Numeric(10, 2), nullable=True)
    ativo = Column(Boolean, default=True, nullable=False)
