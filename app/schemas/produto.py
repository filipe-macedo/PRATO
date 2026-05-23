from pydantic import BaseModel, Field, field_validator
from decimal import Decimal


class ProdutoBase(BaseModel):
    nome: str = Field(..., min_length=2, max_length=150)
    categoria: str | None = Field(None, max_length=100)
    preco_unitario: Decimal | None = Field(None, ge=0, decimal_places=2)
    ativo: bool = True


class ProdutoCriar(ProdutoBase):
    @field_validator("nome")
    @classmethod
    def nome_nao_vazio(cls, v: str) -> str:
        return v.strip()


class ProdutoResposta(ProdutoBase):
    id: int
    model_config = {"from_attributes": True}
