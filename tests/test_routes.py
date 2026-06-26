"""Testes de integração Flask."""

from app import create_app


def test_index_redirects():
    app = create_app()
    client = app.test_client()
    response = client.get("/")
    assert response.status_code == 302
    assert "/contratos" in response.location


def test_list_contracts():
    app = create_app()
    client = app.test_client()
    response = client.get("/contratos")
    assert response.status_code == 200
    assert b"Contratos gerados" in response.data


def test_api_empresa():
    app = create_app()
    client = app.test_client()
    response = client.get("/api/empresas-contratadas/1")
    assert response.status_code == 200
    data = response.get_json()
    assert "company_name" in data
