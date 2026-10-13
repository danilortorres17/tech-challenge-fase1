"""Testes da rota de health check.

Primeiro teste do projeto: prova que a aplicação sobe e responde.
Usa o TestClient do FastAPI (não precisa subir servidor nem banco).
"""
from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


def test_health_retorna_ok() -> None:
    resposta = client.get("/health")
    assert resposta.status_code == 200
    assert resposta.json() == {"status": "ok"}


def test_raiz_responde() -> None:
    resposta = client.get("/")
    assert resposta.status_code == 200
    assert "mensagem" in resposta.json()
