from pydantic import BaseModel, Field
from datetime import date


class PrevisaoEntrada(BaseModel):
    data: date = Field(..., examples=["2024-07-20"])
    produto_id: int = Field(..., ge=1)
    turno_id: int = Field(..., ge=1)


class PrevisaoResposta(BaseModel):
    data: date
    produto_id: int
    turno_id: int
    quantidade_prevista: float
    modelo_utilizado: str
    unidade: str = "unidades"


class PrevisaoLote(BaseModel):
    previsoes: list[PrevisaoEntrada] = Field(..., min_length=1, max_length=365)


class PrevisaoLoteResposta(BaseModel):
    total: int
    resultados: list[PrevisaoResposta]
