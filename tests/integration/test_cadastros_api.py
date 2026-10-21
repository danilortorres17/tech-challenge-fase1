"""Testes de integração dos CRUDs administrativos (via TestClient)."""
import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.infrastructure.db.base import Base
from app.infrastructure.repositorios_crud import (
    RepositorioClienteSQLAlchemy,
    RepositorioPecaSQLAlchemy,
    RepositorioServicoSQLAlchemy,
    RepositorioVeiculoSQLAlchemy,
)
from app.interfaces.auth import usuario_atual
from app.interfaces.dependencias import (
    obter_repositorio_cliente,
    obter_repositorio_peca,
    obter_repositorio_servico,
    obter_repositorio_veiculo,
)
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
    app.dependency_overrides[obter_repositorio_cliente] = lambda: RepositorioClienteSQLAlchemy(factory)
    app.dependency_overrides[obter_repositorio_veiculo] = lambda: RepositorioVeiculoSQLAlchemy(factory)
    app.dependency_overrides[obter_repositorio_servico] = lambda: RepositorioServicoSQLAlchemy(factory)
    app.dependency_overrides[obter_repositorio_peca] = lambda: RepositorioPecaSQLAlchemy(factory)
    app.dependency_overrides[usuario_atual] = lambda: "teste"
    yield TestClient(app)
    app.dependency_overrides.clear()


def test_crud_cliente(client) -> None:
    criado = client.post("/clientes", json={"documento": "111.444.777-35", "nome": "Maria"})
    assert criado.status_code == 201
    cid = criado.json()["id"]

    assert client.get(f"/clientes/{cid}").json()["nome"] == "Maria"
    assert len(client.get("/clientes").json()) == 1

    atualizado = client.put(f"/clientes/{cid}", json={"documento": "111.444.777-35", "nome": "Maria Silva"})
    assert atualizado.json()["nome"] == "Maria Silva"

    assert client.delete(f"/clientes/{cid}").status_code == 204
    assert client.get(f"/clientes/{cid}").status_code == 404


def test_veiculo_com_cliente_inexistente_retorna_404(client) -> None:
    r = client.post(
        "/veiculos",
        json={
            "placa": "ABC1D23", "marca": "VW", "modelo": "Gol", "ano": 2020,
            "cliente_id": "00000000-0000-0000-0000-000000000000",
        },
    )
    assert r.status_code == 404


def test_crud_veiculo(client) -> None:
    criado = client.post(
        "/veiculos",
        json={"placa": "ABC1D23", "marca": "VW", "modelo": "Gol", "ano": 2020},
    )
    assert criado.status_code == 201
    vid = criado.json()["id"]
    assert client.get(f"/veiculos/{vid}").json()["modelo"] == "Gol"
    assert client.delete(f"/veiculos/{vid}").status_code == 204


def test_crud_servico(client) -> None:
    criado = client.post("/servicos", json={"descricao": "Troca de óleo", "preco": "120.00"})
    assert criado.status_code == 201
    assert criado.json()["preco"] == "120.00"


def test_crud_e_estoque_peca(client) -> None:
    criado = client.post("/pecas", json={"descricao": "Filtro", "preco": "35.50", "estoque": 10})
    assert criado.status_code == 201
    pid = criado.json()["id"]
    assert criado.json()["estoque"] == 10

    # entrada
    r = client.post(f"/pecas/{pid}/estoque/entrada", json={"quantidade": 5})
    assert r.json()["estoque"] == 15

    # baixa
    r = client.post(f"/pecas/{pid}/estoque/baixa", json={"quantidade": 4})
    assert r.json()["estoque"] == 11

    # baixa maior que saldo -> 400
    r = client.post(f"/pecas/{pid}/estoque/baixa", json={"quantidade": 999})
    assert r.status_code == 400


def test_documento_invalido_no_cliente_retorna_400(client) -> None:
    r = client.post("/clientes", json={"documento": "123", "nome": "X"})
    assert r.status_code == 400


def test_cadastro_exige_autenticacao() -> None:
    # Sem override de usuario_atual: deve exigir token.
    engine = create_engine(
        "sqlite://", connect_args={"check_same_thread": False},
        poolclass=StaticPool, future=True,
    )
    Base.metadata.create_all(engine)
    factory = sessionmaker(bind=engine, expire_on_commit=False, future=True)
    app.dependency_overrides[obter_repositorio_cliente] = lambda: RepositorioClienteSQLAlchemy(factory)
    try:
        c = TestClient(app)
        r = c.post("/clientes", json={"documento": "111.444.777-35", "nome": "Maria"})
        assert r.status_code == 401
    finally:
        app.dependency_overrides.clear()
