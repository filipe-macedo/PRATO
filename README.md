# PRATO — Restaurant Demand Forecasting System

> An artificial intelligence system for forecasting restaurant product demand by date and shift. Developed as a Capstone Project (*Projeto Integrador*) for the **Systems Analysis and Development Program** at **Senac College -  Pernambuco**.

[![Python](https://img.shields.io/badge/Python-3.11%2B-blue)](https://www.python.org)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.111%2B-009688)](https://fastapi.tiangolo.com)
[![Streamlit](https://img.shields.io/badge/Streamlit-1.35%2B-FF4B4B)](https://streamlit.io)
[![License: MIT](https://img.shields.io/badge/License-MIT-green)](LICENSE)

---

## Project Overview

**PRATO** is a machine learning-based system designed to help restaurants predict product demand more accurately.

The system uses historical sales data to estimate how many units of each product are likely to be sold on specific dates and shifts, such as breakfast, lunch, snack time, and dinner.

Its main goal is to support restaurant managers in making better operational decisions related to inventory, purchasing, food preparation, and kitchen staff planning.

**System flow:**
`Data → Data Processing Pipeline → Machine Learning Models → API + Dashboard`

---

## Key Features

* **Demand Forecasting:** Predicts the expected quantity sold by product, date, and shift.
* **Data Processing Pipeline:** Cleans, normalizes, and prepares restaurant sales data for analysis and training.
* **Machine Learning Models:** Uses predictive models to identify sales patterns and improve forecasting accuracy.
* **Interactive Dashboard:** Displays forecasts, metrics, and visual insights through a user-friendly interface.
* **REST API:** Provides endpoints for integration with other systems, such as POS and inventory tools.
* **POS and Inventory Integration Layer:** Uses the Adapter design pattern to support future integrations with different restaurant systems.

---

## Problem and Solution

Many restaurants still make purchasing and production decisions based only on experience or manual estimates. This can lead to product shortages, food waste, unnecessary costs, and inefficient kitchen planning.

**PRATO** proposes a data-driven solution by using historical sales information to generate demand forecasts. With these predictions, restaurants can prepare the right amount of food, reduce waste, improve stock control, and organize kitchen operations more efficiently.

---

## Tech Stack

| Layer | Module | Technology |
|---|---|---|
| Data Ingestion and Processing | `src/` | Pandas, NumPy |
| Predictive Modeling | `src/modelos.py` | Scikit-learn, XGBoost |
| REST API | `app/` | FastAPI, SQLAlchemy |
| Interactive Interface | `dashboard/` | Streamlit, Plotly |
| POS and Inventory Integration | `integrador/` | Adapter Pattern |

---

## Requirements

Before running the project, make sure you have installed:

* Python **3.11** or higher
* Git
* Pip
* Virtual environment support for Python

---

## Getting Started

Follow these steps to run the project locally.

### 1. Clone the Repository

    git clone https://github.com/filipe-macedo/prato.git
    cd prato

### 2. Create a Virtual Environment

    python -m venv .venv

### 3. Activate the Virtual Environment

Linux/macOS:

    source .venv/bin/activate

Windows PowerShell:

    .venv\Scripts\Activate.ps1

### 4. Install Dependencies

    pip install -r requirements.txt

### 5. Configure Environment Variables

    cp .env.example .env

### 6. Initialize the Database

    python -c "from app.database import engine, Base; Base.metadata.create_all(engine)"

---

## Quick Start With Sample Data

Use the commands below to run the system with demonstration data.

### 1. Generate Sample Data

    python data/samples/gerar_dados_exemplo.py

### 2. Run the Full Pipeline

    make pipeline

This command executes the full process:

Data processing → Model training → Model evaluation

### 3. Start the API

    make run-api

After starting the API, access the interactive documentation at:

`http://localhost:8000/docs`

### 4. Start the Dashboard

Open a second terminal and run:

    make run-dashboard

Then access:

`http://localhost:8501`

---

## Running With Real Data

To use real restaurant data, place your file inside the `data/raw/` directory.

The input file must contain the following required columns:

`data`, `produto`, `turno`, `quantidade_vendida`

Then run:

    python -m src.pipeline_dados --entrada data/raw/YOUR_FILE.csv
    python -m src.modelos
    python -m src.avaliacao

---

## Input Data Format

| Field | Type | Required | Example |
|---|---|---|---|
| `data` | DATE | Yes | `2024-07-15` or `15/07/2024` |
| `produto` | TEXT | Yes | `prato_executivo` |
| `turno` | TEXT | Yes | `almoco`, `jantar`, `cafe_manha` |
| `quantidade_vendida` | NUMERIC | Yes | `42` |
| `categoria` | TEXT | No | `prato_principal` |
| `preco_unitario` | NUMERIC | No | `35.90` |

Accepted shifts include:

`almoco`, `jantar`, `cafe_manha`, `lanche`

The pipeline automatically normalizes accents, uppercase letters, and common variations.

---

## Model Acceptance Metrics

The model is evaluated using the following acceptance criteria:

| Metric | Approved | Warning |
|---|---|---|
| Relative MAE | ≤ 15% | ≤ 30% |
| R² Score | ≥ 0.50 | ≥ 0.30 |
| MAE Improvement Over Baseline | ≥ 15% | ≥ 5% |
| MAPE | ≤ 25% | ≤ 40% |

These metrics help determine whether the prediction model is accurate enough for operational use.

---

## Project Structure

    prato/
    ├── app/            # REST API built with FastAPI
    ├── dashboard/      # Interactive dashboard built with Streamlit
    ├── data/           # Data files - raw data is not versioned
    │   ├── external/   # Public external data, such as national holidays
    │   └── samples/    # Fictional demonstration data
    ├── database/       # SQL scripts and database structure
    ├── docs/           # Technical documentation
    ├── integrador/     # POS and inventory connectors
    ├── models/         # Trained models - not versioned
    ├── notebooks/      # Exploratory data analysis
    ├── outputs/        # Generated metrics and predictions - not versioned
    ├── src/            # Machine Learning pipeline
    └── tests/          # Automated tests

---

## Available Commands

| Command | Description |
|---|---|
| `make install` | Installs project dependencies |
| `make run-api` | Starts the FastAPI API on port 8000 |
| `make run-dashboard` | Starts the Streamlit dashboard on port 8501 |
| `make pipeline` | Runs the full Machine Learning pipeline |
| `make test` | Runs tests with coverage |
| `make lint` | Checks code quality |
| `make setup-db` | Creates database tables |
| `make help` | Lists all available commands |

---

## Testing

To run the automated tests, use:

    pytest tests/ -v --cov=src --cov=app

---

## Documentation

| Document | Location |
|---|---|
| Complete Technical Documentation | `docs/documentacao_tecnica.md` |
| Solution Architecture | `docs/arquitetura.md` |
| Data Dictionary | `docs/dicionario_dados.md` |
| Contribution Guide | `docs/guia_contribuicao.md` |
| Interactive API Documentation | `http://localhost:8000/docs` |

---

## API Documentation

When the API is running locally, the Swagger documentation can be accessed at:

`http://localhost:8000/docs`

This page allows developers to test endpoints, inspect request formats, and understand the available API operations.

---

## Version 1.0 Limitations

The current version has the following limitations:

* POS integration is currently available only through manual CSV or Excel upload.
* The API does not yet include user authentication.
* Forecasts are point estimates and do not include confidence intervals.
* Model retraining is currently manual.
* The recommended minimum dataset size is 90 days of sales history.

---

## Future Improvements

If we had another semester, we would improve the project by implementing:

* Automatic integration with POS and inventory systems.
* User authentication and permission control.
* Forecast confidence intervals.
* Automatic model retraining.
* Advanced reports for restaurant managers.
* Support for multiple restaurant branches.
* Real-time sales monitoring.
* Cloud deployment.

---

## License

This project is licensed under the MIT License.

See the `LICENSE` file for more information.

---

## Authors & Project Team

* Filipe Macedo — Project Development
* Gabriel Coelho — Project Documentation and Review
* Caio Barros — Backend Developer
* Lucas Paulo — Dashboard and Frontend Developer
* Daniel Gois — Machine Learning Pipeline Developer

Academic Advisor / Professor: Prof. Rodrigo Rios de Larrazábal

Tech English Course Professor: Prof. Leonardo Trevas