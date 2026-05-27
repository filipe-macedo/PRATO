import pytest
from src.ingestao import carregar_dados, validar_colunas, inspecionar_dados


def test_validar_colunas_completas(df_vendas_valido):
    ok, ausentes = validar_colunas(df_vendas_valido)
    assert ok
    assert ausentes == []


def test_validar_colunas_ausentes(df_vendas_valido):
    df = df_vendas_valido.drop(columns=["turno"])
    ok, ausentes = validar_colunas(df)
    assert not ok
    assert "turno" in ausentes


def test_inspecionar_dados_retorna_shape(df_vendas_valido):
    info = inspecionar_dados(df_vendas_valido)
    assert "shape" in info
    assert info["shape"][0] == len(df_vendas_valido)


def test_carregar_dados_arquivo_inexistente():
    with pytest.raises(FileNotFoundError):
        carregar_dados("arquivo_que_nao_existe.csv")
