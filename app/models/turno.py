from sqlalchemy import Column, Integer, String
from app.database import Base


class Turno(Base):
    __tablename__ = "turnos"

    id = Column(Integer, primary_key=True, index=True)
    nome = Column(String(50), nullable=False, unique=True, index=True)
    hora_inicio = Column(String(5), nullable=True)
    hora_fim = Column(String(5), nullable=True)
