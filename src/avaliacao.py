"""Avaliação completa do modelo: métricas, resíduos, segmentos e relatório."""

import json
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from pathlib import Path
from scipy import stats

CRITERIOS = {
    "mae_relativo_aprovado": 0.15, "mae_relativo_atencao": 0.30,
    "r2_aprovado": 0.50, "r2_atencao": 0.30,
    "ganho_baseline_aprovado": 0.15, "ganho_baseline_atencao": 0.05,
    "bias_relativo_aprovado": 0.03, "bias_relativo_atencao": 0.08,
    "gap_cv_aprovado": 0.10, "gap_cv_atencao": 0.20,
    "mape_aprovado": 25.0, "mape_atencao": 40.0,
}


def calcular_metricas_completas(
    y_real: np.ndarray,
    y_previsto: np.ndarray,
    nome_modelo: str,
) -> dict:
    from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score

    y_prev = np.clip(y_previsto, 0, None)
    residuos = y_prev - y_real
    media_real = y_real.mean()

    mask = y_real > 0
    mape = np.mean(np.abs(residuos[mask] / y_real[mask])) * 100 if mask.any() else np.nan

    percentis = np.percentile(np.abs(residuos), [25, 50, 75, 95])

    def within_pct(p):
        threshold = media_real * p
        return (np.abs(residuos) <= threshold).mean() * 100

    return {
        "nome_modelo": nome_modelo,
        "mae": mean_absolute_error(y_real, y_prev),
        "rmse": np.sqrt(mean_squared_error(y_real, y_prev)),
        "r2": r2_score(y_real, y_prev),
        "mape": mape,
        "bias": residuos.mean(),
        "bias_relativo": residuos.mean() / (media_real + 1e-9),
        "desvio_residuos": residuos.std(),
        "mae_relativo": mean_absolute_error(y_real, y_prev) / (media_real + 1e-9),
        "p25_erro": percentis[0], "p50_erro": percentis[1],
        "p75_erro": percentis[2], "p95_erro": percentis[3],
        "within_10pct_dem": within_pct(0.10),
        "within_20pct_dem": within_pct(0.20),
        "within_50pct_dem": within_pct(0.50),
    }


def analisar_residuos(df: pd.DataFrame) -> dict:
    residuos = (df["quantidade_prevista"] - df["quantidade_vendida"]).values
    y_prev = df["quantidade_prevista"].values

    t_stat, p_bias = stats.ttest_1samp(residuos, 0)
    r_het, p_het = stats.pearsonr(y_prev, np.abs(residuos))

    resultado = {
        "bias_significativo": bool(p_bias < 0.05),
        "p_valor_bias": p_bias,
        "heteroscedasticidade_r": r_het,
        "p_valor_heteroscedasticidade": p_het,
    }

    if len(residuos) <= 5000:
        _, p_norm = stats.shapiro(residuos)
        resultado["residuos_normais"] = bool(p_norm > 0.05)
        resultado["p_valor_normalidade"] = p_norm

    if len(residuos) > 1:
        r_auto, p_auto = stats.pearsonr(residuos[:-1], residuos[1:])
        resultado["autocorrelacao_lag1"] = r_auto
        resultado["p_valor_autocorrelacao"] = p_auto

    return resultado


def verificar_criterios_aceitacao(
    metricas: dict,
    comparacao: dict,
    analise_residuos: dict,
) -> dict:
    def avaliar(valor, lim_aprovado, lim_atencao, menor_melhor=True):
        if menor_melhor:
            if valor <= lim_aprovado:
                return "APROVADO"
            elif valor <= lim_atencao:
                return "ATENCAO"
            return "REPROVADO"
        else:
            if valor >= lim_aprovado:
                return "APROVADO"
            elif valor >= lim_atencao:
                return "ATENCAO"
            return "REPROVADO"

    criterios_resultado = {
        "mae_relativo": {
            "valor": metricas.get("mae_relativo"),
            "situacao": avaliar(metricas.get("mae_relativo", 999),
                                CRITERIOS["mae_relativo_aprovado"],
                                CRITERIOS["mae_relativo_atencao"]),
        },
        "r2": {
            "valor": metricas.get("r2"),
            "situacao": avaliar(metricas.get("r2", -999),
                                CRITERIOS["r2_aprovado"],
                                CRITERIOS["r2_atencao"],
                                menor_melhor=False),
        },
        "mape": {
            "valor": metricas.get("mape"),
            "situacao": avaliar(metricas.get("mape", 999),
                                CRITERIOS["mape_aprovado"],
                                CRITERIOS["mape_atencao"]),
        },
    }

    situacoes = [v["situacao"] for v in criterios_resultado.values()]
    if "REPROVADO" in situacoes:
        veredicto = "REPROVADO"
    elif "ATENCAO" in situacoes:
        veredicto = "ATENCAO"
    else:
        veredicto = "APROVADO"

    return {"veredicto_geral": veredicto, "criterios": criterios_resultado}


def plotar_analise_residuos(df: pd.DataFrame, caminho_saida: str) -> None:
    residuos = df["quantidade_prevista"] - df["quantidade_vendida"]
    fig, axes = plt.subplots(2, 2, figsize=(12, 9))
    fig.suptitle("Análise de Resíduos — PRATO", fontsize=14)

    axes[0, 0].scatter(df["quantidade_prevista"], residuos, alpha=0.4, s=15, color="#E8521A")
    axes[0, 0].axhline(0, color="gray", linestyle="--")
    axes[0, 0].set_xlabel("Previsto")
    axes[0, 0].set_ylabel("Resíduo")
    axes[0, 0].set_title("Resíduos × Previsto")

    stats.probplot(residuos, dist="norm", plot=axes[0, 1])
    axes[0, 1].set_title("Q-Q Plot")

    axes[1, 0].hist(residuos, bins=40, color="#2C7BB6", alpha=0.7, edgecolor="white")
    axes[1, 0].axvline(0, color="#E74C3C", linestyle="--")
    axes[1, 0].set_title("Distribuição dos Resíduos")

    if "data" in df.columns:
        axes[1, 1].plot(pd.to_datetime(df["data"]), residuos, lw=0.8, color="#E8521A")
        axes[1, 1].axhline(0, color="gray", linestyle="--")
        axes[1, 1].set_title("Resíduos ao Longo do Tempo")

    plt.tight_layout()
    plt.savefig(caminho_saida, dpi=120, bbox_inches="tight")
    plt.close()


def executar_avaliacao_completa(
    caminho_previsoes: str = "outputs/previsoes/previsoes_melhor_modelo.csv",
    caminho_baseline: str = "outputs/metricas/baseline_metricas.csv",
) -> dict:
    print("\n========== PRATO — Avaliação Completa ==========")
    Path("outputs/avaliacao").mkdir(parents=True, exist_ok=True)

    df = pd.read_csv(caminho_previsoes, parse_dates=["data"])
    if "quantidade_prevista" not in df.columns:
        raise ValueError("Arquivo de previsões não contém coluna 'quantidade_prevista'.")

    y_real = df["quantidade_vendida"].values
    y_prev = df["quantidade_prevista"].values

    metricas = calcular_metricas_completas(y_real, y_prev, "modelo_final")
    analise = analisar_residuos(df)

    comparacao = {}
    if Path(caminho_baseline).exists():
        df_base = pd.read_csv(caminho_baseline)
        melhor_base = df_base.loc[df_base["mae"].idxmin()]
        comparacao["ganho_mae_pct"] = (melhor_base["mae"] - metricas["mae"]) / melhor_base["mae"]
        comparacao["ganho_rmse_pct"] = (melhor_base["rmse"] - metricas["rmse"]) / melhor_base["rmse"]

    criterios = verificar_criterios_aceitacao(metricas, comparacao, analise)

    relatorio = {
        "metricas_teste": metricas,
        "analise_residuos": analise,
        "comparacao_baseline": comparacao,
        "criterios_aceitacao": criterios,
    }

    with open("outputs/avaliacao/relatorio_avaliacao.json", "w", encoding="utf-8") as f:
        json.dump(relatorio, f, ensure_ascii=False, indent=2)

    plotar_analise_residuos(df, "outputs/avaliacao/residuos_analise.png")

    print(f"\n  MAE: {metricas['mae']:.2f}")
    print(f"  RMSE: {metricas['rmse']:.2f}")
    print(f"  R²: {metricas['r2']:.3f}")
    print(f"  MAPE: {metricas['mape']:.1f}%")
    print(f"  Veredicto: {criterios['veredicto_geral']}")
    print("========== Avaliação concluída ==========")
    return relatorio


if __name__ == "__main__":
    executar_avaliacao_completa()
