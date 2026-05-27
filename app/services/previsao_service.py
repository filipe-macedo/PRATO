import numpy as np
import pandas as pd
from datetime import date
from fastapi import HTTPException
from sqlalchemy.orm import Session
from app.models.produto import Produto
from app.models.turno import Turno
from app.models.venda import Venda
from app.models.previsao import HistoricoPrevisao
from app.schemas.previsao import PrevisaoEntrada, PrevisaoResposta

FEATURES_BASE = [
    "produto_cod", "turno_cod", "dia_semana", "mes",
    "semana_do_ano", "trimestre", "is_fim_de_semana", "is_feriado", "ano",
]


def _features_temporais(data: date) -> dict:
    d = pd.Timestamp(data)
    dia_semana = d.dayofweek
    return {
        "dia_semana": dia_semana,
        "mes": d.month,
        "ano": d.year,
        "semana_do_ano": d.isocalendar().week,
        "trimestre": d.quarter,
        "is_fim_de_semana": int(dia_semana >= 5),
        "is_feriado": 0,
    }


def _buscar_lags(db: Session, produto_id: int, turno_id: int, data_alvo: date) -> dict:
    resultado = {}
    for lag, chave in [(1, "lag_1d"), (7, "lag_7d")]:
        data_lag = date.fromordinal(data_alvo.toordinal() - lag)
        venda = db.query(Venda).filter(
            Venda.data == data_lag,
            Venda.produto_id == produto_id,
            Venda.turno_id == turno_id,
        ).first()
        resultado[chave] = float(venda.quantidade_vendida) if venda else np.nan

    for janela, chave in [(7, "media_movel_7d"), (14, "media_movel_14d")]:
        inicio = date.fromordinal(data_alvo.toordinal() - janela)
        vendas = db.query(Venda).filter(
            Venda.produto_id == produto_id,
            Venda.turno_id == turno_id,
            Venda.data >= inicio,
            Venda.data < data_alvo,
        ).all()
        qtds = [float(v.quantidade_vendida) for v in vendas]
        resultado[chave] = np.mean(qtds) if qtds else np.nan

    return resultado


def gerar_previsao(entrada: PrevisaoEntrada, modelo_cache: dict, db: Session) -> PrevisaoResposta:
    modelo = modelo_cache["modelo"]
    metadados = modelo_cache["metadados"]
    nome_modelo = metadados.get("nome", "modelo_final")

    produto = db.query(Produto).filter(Produto.id == entrada.produto_id).first()
    if not produto:
        raise HTTPException(status_code=404, detail=f"Produto id={entrada.produto_id} não encontrado.")

    turno = db.query(Turno).filter(Turno.id == entrada.turno_id).first()
    if not turno:
        raise HTTPException(status_code=404, detail=f"Turno id={entrada.turno_id} não encontrado.")

    features = {
        "produto_cod": entrada.produto_id,
        "turno_cod": entrada.turno_id,
        **_features_temporais(entrada.data),
    }

    features_modelo = getattr(modelo, "feature_names_in_", None)
    if features_modelo is not None and "lag_1d" in features_modelo:
        features.update(_buscar_lags(db, entrada.produto_id, entrada.turno_id, entrada.data))

    colunas = list(features_modelo) if features_modelo is not None else FEATURES_BASE
    X = pd.DataFrame([{col: features.get(col, np.nan) for col in colunas}])
    pred = max(0.0, round(float(modelo.predict(X)[0]), 2))

    db.add(HistoricoPrevisao(
        data_previsao=entrada.data,
        produto_id=entrada.produto_id,
        turno_id=entrada.turno_id,
        quantidade_prevista=pred,
        modelo_utilizado=nome_modelo,
    ))
    db.commit()

    return PrevisaoResposta(
        data=entrada.data,
        produto_id=entrada.produto_id,
        turno_id=entrada.turno_id,
        quantidade_prevista=pred,
        modelo_utilizado=nome_modelo,
    )
