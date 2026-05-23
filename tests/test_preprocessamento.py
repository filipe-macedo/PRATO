import pytest
import pandas as pd
from src.preprocessamento import (
    padronizar_datas, padronizar_turnos, sinalizar_inconsistencias,
    separar_treino_teste, criar_features_temporais,
)


def test_padronizar_datas_formato_br(df_vendas_valido):
    df = df_vendas_valido.copy()
    df["data"] = ["15/01/2024", "15/01/2024", "16/01/2024", "16/01/2024", "17/01/2024"]
    resultado = padronizar_datas(df)
    assert pd.api.types.is_datetime64_any_dtype(resultado["data"])
    assert resultado["data"].isna().sum() == 0


def test_separar_treino_teste_ordem_cronologica(df_vendas_valido):
    """Garante separação cronológica — nunca aleatória."""
    treino, teste = separar_treino_teste(df_vendas_valido, proporcao_treino=0.6)
    assert treino["data"].max() <= teste["data"].min()


def test_padronizar_turnos_normaliza_variacao():
    df = pd.DataFrame({"turno": ["Almoço", "ALMOÇO", "almoço", "almoco"]})
    resultado = padronizar_turnos(df)
    assert (resultado["turno"] == "almoco").all()


def test_sinalizar_inconsistencias_detecta_negativo(df_vendas_com_problemas):
    resultado = sinalizar_inconsistencias(df_vendas_com_problemas)
    assert "flag_quantidade_negativa" in resultado.columns
    assert resultado["flag_quantidade_negativa"].any()


def test_criar_features_temporais_colunas(df_vendas_valido):
    resultado = criar_features_temporais(df_vendas_valido)
    for col in ["dia_semana", "mes", "ano", "is_fim_de_semana", "is_feriado"]:
        assert col in resultado.columns
