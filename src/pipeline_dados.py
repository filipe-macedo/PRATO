"""Orquestrador do pipeline de dados M1 + M2."""

import argparse
import json
from pathlib import Path
import pandas as pd

from src.ingestao import carregar_dados, validar_colunas, inspecionar_dados
from src.preprocessamento import (
    padronizar_datas, padronizar_texto, padronizar_turnos,
    tratar_valores_ausentes, sinalizar_inconsistencias,
    agregar_por_granularidade, criar_features_temporais,
    criar_features_lag, codificar_variaveis_categoricas,
    separar_treino_teste, exportar_dados,
)
from src.config import (
    COLUNAS_OBRIGATORIAS, CAMINHO_DADOS_TRATADOS, PROPORCAO_TREINO
)


def executar_pipeline(
    caminho_entrada: str,
    caminho_saida: str = CAMINHO_DADOS_TRATADOS,
    incluir_lags: bool = True,
    manter_flags: bool = False,
) -> dict:
    print("\n========== PRATO — Pipeline de Dados ==========")

    # Etapa 1: Carregamento
    print("[1/9] Carregando dados...")
    df = carregar_dados(caminho_entrada)
    print(f"      {len(df):,} registros carregados.")

    # Etapa 2: Validação de colunas
    print("[2/9] Validando colunas obrigatórias...")
    ok, ausentes = validar_colunas(df)
    if not ok:
        raise ValueError(f"Colunas obrigatórias ausentes: {ausentes}")
    inspecao = inspecionar_dados(df)
    print(f"      Shape: {inspecao['shape']} | Duplicatas: {inspecao['duplicatas']}")

    # Etapa 3: Padronização de datas
    print("[3/9] Padronizando datas...")
    df = padronizar_datas(df)

    # Etapa 4: Padronização de textos
    print("[4/9] Padronizando textos e turnos...")
    df = padronizar_texto(df, ["produto", "turno", "categoria"])
    df = padronizar_turnos(df)

    # Etapa 5: Valores ausentes
    print("[5/9] Tratando valores ausentes...")
    df = tratar_valores_ausentes(df)
    df["quantidade_vendida"] = pd.to_numeric(df["quantidade_vendida"], errors="coerce").fillna(0)

    # Etapa 6: Flags de inconsistência
    print("[6/9] Sinalizando inconsistências...")
    df = sinalizar_inconsistencias(df)
    flags = {c: int(df[c].sum()) for c in df.columns if c.startswith("flag_")}
    print(f"      Flags: {flags}")

    # Etapa 7: Agregação
    print("[7/9] Agregando por data/produto/turno...")
    df = agregar_por_granularidade(df)

    # Etapa 8: Feature engineering
    print("[8/9] Criando features temporais e de defasagem...")
    df = criar_features_temporais(df)
    if incluir_lags:
        df = criar_features_lag(df)

    # Etapa 9: Codificação e separação
    print("[9/9] Codificando variáveis e separando treino/teste...")
    df, mapeamentos = codificar_variaveis_categoricas(df)
    df_treino, df_teste = separar_treino_teste(df, PROPORCAO_TREINO)

    if not manter_flags:
        colunas_flag = [c for c in df.columns if c.startswith("flag_")]
        df_auditoria = df[["data", "produto", "turno"] + colunas_flag].copy()
        df_treino = df_treino.drop(columns=colunas_flag, errors="ignore")
        df_teste = df_teste.drop(columns=colunas_flag, errors="ignore")
        df = df.drop(columns=colunas_flag, errors="ignore")
    else:
        df_auditoria = pd.DataFrame()

    # Exportação
    Path(caminho_saida).mkdir(parents=True, exist_ok=True)
    exportar_dados(df_treino, df_teste, df, caminho_saida)

    with open(f"{caminho_saida}mapeamentos_categoricos.json", "w", encoding="utf-8") as f:
        json.dump(mapeamentos, f, ensure_ascii=False, indent=2)

    if not df_auditoria.empty:
        df_auditoria.to_csv(f"{caminho_saida}auditoria_flags.csv", index=False)

    resumo = {
        "registros_entrada": inspecao["shape"][0],
        "registros_treino": len(df_treino),
        "registros_teste": len(df_teste),
        "features": [c for c in df_treino.columns if c not in ["data", "produto", "turno"]],
        "flags": flags,
    }
    print("\n========== Pipeline concluído com sucesso ==========")
    print(f"  Treino: {resumo['registros_treino']:,} | Teste: {resumo['registros_teste']:,}")
    return resumo


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Pipeline de dados PRATO")
    parser.add_argument("--entrada", required=True, help="Caminho do arquivo de entrada")
    parser.add_argument("--saida", default=CAMINHO_DADOS_TRATADOS, help="Pasta de saída")
    parser.add_argument("--sem-lags", action="store_true", help="Desativa features de lag")
    parser.add_argument("--manter-flags", action="store_true", help="Mantém colunas de flag")
    args = parser.parse_args()

    executar_pipeline(
        caminho_entrada=args.entrada,
        caminho_saida=args.saida,
        incluir_lags=not args.sem_lags,
        manter_flags=args.manter_flags,
    )
