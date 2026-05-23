from pydantic import BaseModel, Field, field_validator, model_validator
from decimal import Decimal
from datetime import date


class VendaBase(BaseModel):
    data: date = Field(..., examples=["2024-07-15"])
    produto_id: int = Field(..., ge=1)
    turno_id: int = Field(..., ge=1)
    quantidade_vendida: Decimal = Field(..., gt=0, decimal_places=2)
    preco_unitario: Decimal | None = Field(None, ge=0, decimal_places=2)


class VendaCriar(VendaBase):
    @field_validator("data")
    @classmethod
    def data_nao_futura(cls, v: date) -> date:
        if v > date.today():
            raise ValueError("Não é possível registrar venda com data futura.")
        return v

    @model_validator(mode="after")
    def calcular_receita(self) -> "VendaCriar":
        return self


class VendaResposta(VendaBase):
    id: int
    receita_total: Decimal | None
    model_config = {"from_attributes": True}
