from pydantic import BaseModel


class RespostaPadrao(BaseModel):
    mensagem: str
    sucesso: bool = True


class ErroPadrao(BaseModel):
    detalhe: str
    campo: str | None = None
