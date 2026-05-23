import pytest
from fastapi.testclient import TestClient
from datetime import date, timedelta
from app.main import app

client = TestClient(app)


def test_saude_retorna_200():
    r = client.get("/saude/")
    assert r.status_code == 200
    assert r.json()["status"] == "operacional"


def test_listar_produtos_retorna_lista():
    r = client.get("/produtos/")
    assert r.status_code == 200
    assert isinstance(r.json(), list)


def test_cadastrar_venda_data_futura_rejeitada():
    amanha = (date.today() + timedelta(days=1)).isoformat()
    r = client.post("/vendas/", json={
        "data": amanha,
        "produto_id": 1,
        "turno_id": 1,
        "quantidade_vendida": 10,
    })
    assert r.status_code == 422


def test_cadastrar_venda_quantidade_negativa_rejeitada():
    r = client.post("/vendas/", json={
        "data": date.today().isoformat(),
        "produto_id": 1,
        "turno_id": 1,
        "quantidade_vendida": -5,
    })
    assert r.status_code == 422
