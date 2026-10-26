"""Testes de integração da autenticação JWT.

Verifica o login (senha em hash), a proteção das rotas administrativas, o acesso
público à consulta de andamento e a revogação de token no logout.
"""
import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.infrastructure.db.base import Base
from app.infrastructure.repositorio_auditoria import RepositorioAuditoriaSQLAlchemy
from app.infrastructure.repositorio_sqlalchemy import RepositorioOrdemServicoSQLAlchemy
from app.infrastructure.repositorio_usuario import (
    RepositorioTokenRevogadoSQLAlchemy,
    RepositorioUsuarioSQLAlchemy,
)
from app.infrastructure.repositorios_crud import RepositorioClienteSQLAlchemy
from app.infrastructure.startup import semear_admin
from app.interfaces.dependencias import (
    obter_repositorio,
    obter_repositorio_auditoria,
    obter_repositorio_cliente,
    obter_repositorio_token_revogado,
    obter_repositorio_usuario,
)
from app.main import app

_CLIENTE = {"documento": "111.444.777-35", "nome": "Maria"}


@pytest.fixture
def client() -> TestClient:
    engine = create_engine(
        "sqlite://", connect_args={"check_same_thread": False},
        poolclass=StaticPool, future=True,
    )
    Base.metadata.create_all(engine)
    factory = sessionmaker(bind=engine, expire_on_commit=False, future=True)
    # Semeia o admin (senha em hash) no banco de teste.
    semear_admin(factory)
    # A autenticação NÃO é sobrescrita - é o que estamos testando.
    app.dependency_overrides[obter_repositorio] = lambda: RepositorioOrdemServicoSQLAlchemy(factory)
    app.dependency_overrides[obter_repositorio_cliente] = lambda: RepositorioClienteSQLAlchemy(factory)
    app.dependency_overrides[obter_repositorio_usuario] = lambda: RepositorioUsuarioSQLAlchemy(factory)
    app.dependency_overrides[obter_repositorio_token_revogado] = lambda: RepositorioTokenRevogadoSQLAlchemy(factory)
    app.dependency_overrides[obter_repositorio_auditoria] = lambda: RepositorioAuditoriaSQLAlchemy(factory)
    yield TestClient(app)
    app.dependency_overrides.clear()


def _token(client: TestClient) -> str:
    r = client.post("/auth/token", data={"username": "admin", "password": "admin123"})
    assert r.status_code == 200
    return r.json()["access_token"]


def test_login_sucesso_retorna_token(client) -> None:
    r = client.post("/auth/token", data={"username": "admin", "password": "admin123"})
    assert r.status_code == 200
    assert r.json()["token_type"] == "bearer"
    assert r.json()["access_token"]


def test_login_senha_errada_retorna_401(client) -> None:
    r = client.post("/auth/token", data={"username": "admin", "password": "errada"})
    assert r.status_code == 401


def test_login_usuario_inexistente_retorna_401(client) -> None:
    r = client.post("/auth/token", data={"username": "ninguem", "password": "x"})
    assert r.status_code == 401


def test_rota_administrativa_sem_token_retorna_401(client) -> None:
    r = client.post("/clientes", json=_CLIENTE)
    assert r.status_code == 401


def test_rota_administrativa_com_token_funciona(client) -> None:
    r = client.post(
        "/clientes", json=_CLIENTE, headers={"Authorization": f"Bearer {_token(client)}"}
    )
    assert r.status_code == 201


def test_token_invalido_retorna_401(client) -> None:
    r = client.post(
        "/clientes", json=_CLIENTE, headers={"Authorization": "Bearer token-falso"}
    )
    assert r.status_code == 401


def test_logout_revoga_o_token(client) -> None:
    token = _token(client)
    cab = {"Authorization": f"Bearer {token}"}
    # Antes do logout o token funciona.
    assert client.post("/clientes", json=_CLIENTE, headers=cab).status_code == 201
    # Logout revoga a sessão (jti).
    assert client.post("/auth/logout", headers=cab).status_code == 200
    # Depois do logout o mesmo token é recusado.
    assert client.post("/clientes", json=_CLIENTE, headers=cab).status_code == 401


def test_consulta_de_andamento_e_publica(client) -> None:
    # GET de andamento sem token não deve dar 401 (é público). Sem a OS, dá 404.
    r = client.get("/ordens-servico/00000000-0000-0000-0000-000000000000")
    assert r.status_code == 404
