.PHONY: install run-api run-dashboard test lint pipeline help setup-db

install:
	pip install -r requirements.txt

run-api:
	uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

run-dashboard:
	cd dashboard && streamlit run Inicio.py

pipeline:
	python data/external/gerar_feriados.py
	python -m src.pipeline_dados --entrada data/samples/vendas_exemplo.csv
	python -m src.modelos
	python -m src.avaliacao

test:
	pytest tests/ -v --cov=src --cov=app --cov-report=term-missing

lint:
	ruff check src/ app/ dashboard/ integrador/ tests/
	ruff format --check src/ app/ dashboard/ integrador/ tests/

lint-fix:
	ruff check --fix src/ app/ dashboard/ integrador/ tests/
	ruff format src/ app/ dashboard/ integrador/ tests/

setup-db:
	python -c "from app.database import engine, Base; Base.metadata.create_all(engine)"

help:
	@echo "Comandos disponiveis:"
	@echo "  make install        Instala dependencias"
	@echo "  make run-api        Inicia API FastAPI (porta 8000)"
	@echo "  make run-dashboard  Inicia dashboard Streamlit (porta 8501)"
	@echo "  make pipeline       Executa pipeline completo de dados + treino + avaliacao"
	@echo "  make test           Executa testes com cobertura"
	@echo "  make lint           Verifica qualidade do codigo"
	@echo "  make lint-fix       Corrige automaticamente problemas de lint"
	@echo "  make setup-db       Cria tabelas no banco de dados"
