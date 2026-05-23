"""
startup_api.py
Executado antes de subir a API no Render (ou qualquer servidor).
Garante que o pipeline de dados rodou e o modelo treinado existe.
"""

import sys
import os
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

# ── Caminhos ────────────────────────────────────────────────────────────────
MODELO       = ROOT / os.getenv("CAMINHO_MODELO", "models/modelo_final.pkl")
DADOS_BRUTOS = ROOT / "data" / "samples" / "vendas_exemplo.csv"
DIR_PROC     = ROOT / "data" / "processed"
TREINO_CSV   = DIR_PROC / "vendas_treino.csv"
TESTE_CSV    = DIR_PROC / "vendas_teste.csv"


def log(msg: str) -> None:
    print(f"[startup] {msg}", flush=True)


# ── 1. Pipeline de dados ─────────────────────────────────────────────────────
if not TREINO_CSV.exists():
    log("Dados processados não encontrados — rodando pipeline...")
    DIR_PROC.mkdir(parents=True, exist_ok=True)

    result = subprocess.run(
        [sys.executable, str(ROOT / "src" / "pipeline_dados.py"),
         "--entrada", str(DADOS_BRUTOS),
         "--saida",   str(DIR_PROC) + "/"],
        cwd=str(ROOT),
    )

    if result.returncode != 0:
        log("ERRO no pipeline de dados — abortando.")
        sys.exit(1)
    log("Pipeline concluído.")
else:
    log(f"Dados já processados: {TREINO_CSV}")


# ── 2. Treinamento dos modelos ───────────────────────────────────────────────
if not MODELO.exists():
    log("Modelo não encontrado — iniciando treinamento (pode levar ~2 min)...")
    MODELO.parent.mkdir(parents=True, exist_ok=True)

    # Muda para a raiz do projeto (salvar_modelo usa caminhos relativos)
    os.chdir(str(ROOT))

    from src.modelos import treinar_todos_modelos
    treinar_todos_modelos(
        caminho_treino=str(TREINO_CSV),
        caminho_teste=str(TESTE_CSV),
    )
    log(f"Modelo salvo em: {MODELO}")
else:
    log(f"Modelo já existe: {MODELO}")


log("Startup concluído — API pronta para iniciar.")
