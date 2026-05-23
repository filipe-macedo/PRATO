from typing import Generator, Annotated
from fastapi import Depends, HTTPException, status
import joblib
import json
from pathlib import Path
from sqlalchemy.orm import Session
from app.database import SessionLocal
from app.config import configuracoes

_modelo_cache: dict = {}


def get_db() -> Generator[Session, None, None]:
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def _carregar_modelo() -> dict:
    if "modelo" not in _modelo_cache:
        caminho = Path(configuracoes.caminho_modelo)
        if not caminho.exists():
            raise FileNotFoundError(
                f"Modelo não encontrado em '{caminho}'. "
                "Execute 'make pipeline' antes de iniciar a API."
            )
        _modelo_cache["modelo"] = joblib.load(caminho)
        caminho_meta = caminho.with_name(caminho.stem + "_metadados.json")
        if caminho_meta.exists():
            with open(caminho_meta, encoding="utf-8") as f:
                _modelo_cache["metadados"] = json.load(f)
        else:
            _modelo_cache["metadados"] = {"nome": caminho.stem}
    return _modelo_cache


def get_modelo() -> dict:
    try:
        return _carregar_modelo()
    except FileNotFoundError as exc:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=str(exc),
        )


DbSession = Annotated[Session, Depends(get_db)]
ModeloDep = Annotated[dict, Depends(get_modelo)]
