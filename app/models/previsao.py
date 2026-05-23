from sqlalchemy import Column, Integer, String, Float, Date, DateTime, ForeignKey
from sqlalchemy.sql import func
from app.database import Base


class HistoricoPrevisao(Base):
    __tablename__ = "historico_previsoes"

    id = Column(Integer, primary_key=True, index=True)
    data_previsao = Column(Date, nullable=False, index=True)
    produto_id = Column(Integer, ForeignKey("produtos.id"), nullable=False, index=True)
    turno_id = Column(Integer, ForeignKey("turnos.id"), nullable=False, index=True)
    quantidade_prevista = Column(Float, nullable=False)
    modelo_utilizado = Column(String(100), nullable=True)
    gerado_em = Column(DateTime, server_default=func.now(), nullable=False)
