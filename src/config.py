"""Constantes e parâmetros centrais do pipeline de dados e modelagem."""

COLUNAS_OBRIGATORIAS = ["data", "produto", "quantidade_vendida", "turno"]
COLUNAS_OPCIONAIS = [
    "categoria", "preco_unitario", "receita_total", "quantidade_cancelada"
]

MAPA_TURNOS = {
    "almoço": "almoco", "almoco": "almoco", "almocer": "almoco",
    "lunch": "almoco", "lanche": "lanche", "snack": "lanche",
    "jantar": "jantar", "dinner": "jantar", "janta": "jantar",
    "cafe_manha": "cafe_manha", "café da manhã": "cafe_manha",
    "cafe da manha": "cafe_manha", "breakfast": "cafe_manha",
    "manha": "cafe_manha",
}

FORMATOS_DATA = [
    "%Y-%m-%d", "%d/%m/%Y", "%d-%m-%Y",
    "%Y/%m/%d", "%d/%m/%y", "%Y%m%d",
]

PROPORCAO_TREINO = 0.8
ZSCORE_LIMITE = 3.0
QUANTIDADE_MINIMA = 0.0

LAGS_DIAS = [1, 7]
JANELAS_MEDIA_MOVEL = [7, 14]

CAMINHO_DADOS_BRUTOS = "data/raw/"
CAMINHO_DADOS_TRATADOS = "data/processed/"
CAMINHO_DADOS_EXTERNOS = "data/external/"
ARQUIVO_FERIADOS = "data/external/feriados_nacionais.csv"
