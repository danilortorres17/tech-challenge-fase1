"""Testes de integração da autenticação JWT.

Verifica o login, a proteção das rotas administrativas e o acesso público à
consulta de andamento.
"""
import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.infrastructure.db.base import Base
from app.infrastructure.repositorio_sqlalchemy import RepositorioOrdemServicoSQLAlchemy
from app.interfaces.dependencias import obter_repositorio
from app.main import app


@pytest.fixture
def client() -> TestClient:
    engine = create_engine(
        "sqlite://",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
        future=True,
    )
    Base.metadata.create_all(engine)
    factory = sessionmaker(bind=engine, expire_on_commit=False, future=True)
    repo = RepositorioOrdemServicoSQLAlchemy(factory)
    # Aqui a autenticação NÃO é sobrescrita — é o que estamos testando.
    app.dependency_overrides[obter_repositorio] = lambda: repo
    yield TestClient(app)
    app.dependency_overrides.clear()


def _token(client: TestClient) -> str:
    resposta = client.post(
        "/auth/token", data={"username": "admin", "password": "admin123"}
    )
    assert resposta.status_code == 200
    return resposta.json()["access_token"]


def test_login_sucesso_retorna_token(client) -> None:
    resposta = client.post(
        "/auth/token", data={"username": "admin", "password": "admin123"}
    )
    assert resposta.status_code == 200
    assert resposta.json()["token_type"] == "bearer"
    assert resposta.json()["access_token"]


def test_login_senha_errada_retorna_401(client) -> None:
    resposta = client.post(
        "/auth/token", data={"username": "admin", "password": "errada"}
    )
    assert resposta.status_code == 401


def test_rota_administrativa_sem_token_retorna_401(client) -> None:
    resposta = client.post(
        "/ordens-servico",
        json={"documento_cliente": "111.444.777-35", "placa": "ABC1D23"},
    )
    assert resposta.status_code == 401


def test_rota_administrativa_com_token_funciona(client) -> None:
    token = _token(client)
    resposta = client.post(
        "/ordens-servico",
        json={"documento_cliente": "111.444.777-35", "placa": "ABC1D23"},
        headers={"Authorization": f"Bearer {token}"},
    )
    assert resposta.status_code == 201


def test_consulta_de_andamento_e_publica(client) -> None:
    token = _token(client)
    criado = client.post(
        "/ordens-servico",
        json={"documento_cliente": "111.444.777-35", "placa": "ABC1D23"},
        headers={"Authorization": f"Bearer {token}"},
    )
    ordem_id = criado.json()["id"]
    # Sem token no GET de andamento:
    resposta = client.get(f"/ordens-servico/{ordem_id}")
    assert resposta.status_code == 200


def test_token_invalido_retorna_401(client) -> None:
    resposta = client.post(
        "/ordens-servico",
        json={"documento_cliente": "111.444.777-35", "placa": "ABC1D23"},
        headers={"Authorization": "Bearer token-falso"},
    )
    assert resposta.status_code == 401
