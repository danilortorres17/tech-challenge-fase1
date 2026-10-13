"""Testes de integração da API REST (via TestClient).

Sobe a aplicação FastAPI com o repositório apontando para um SQLite em memória
e a autenticação desativada (sobrescrita), para focar no fluxo de negócio.
A segurança em si é testada em test_auth.py.
"""
import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.infrastructure.db.base import Base
from app.infrastructure.repositorio_sqlalchemy import RepositorioOrdemServicoSQLAlchemy
from app.interfaces.auth import usuario_atual
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
    app.dependency_overrides[obter_repositorio] = lambda: repo
    app.dependency_overrides[usuario_atual] = lambda: "teste"
    yield TestClient(app)
    app.dependency_overrides.clear()


def _criar(client: TestClient) -> str:
    resposta = client.post(
        "/ordens-servico",
        json={"documento_cliente": "111.444.777-35", "placa": "ABC1D23"},
    )
    assert resposta.status_code == 201
    return resposta.json()["id"]


def test_criar_e_consultar(client) -> None:
    ordem_id = _criar(client)
    resposta = client.get(f"/ordens-servico/{ordem_id}")
    assert resposta.status_code == 200
    assert resposta.json()["status"] == "Recebida"


def test_fluxo_completo_via_api(client) -> None:
    ordem_id = _criar(client)
    client.post(
        f"/ordens-servico/{ordem_id}/servicos",
        json={"descricao": "Troca de óleo", "preco": "120.00"},
    )
    client.post(
        f"/ordens-servico/{ordem_id}/pecas",
        json={"descricao": "Filtro", "preco_unitario": "35.50", "quantidade": 2},
    )
    assert client.get(f"/ordens-servico/{ordem_id}").json()["orcamento"] == "191.00"

    for acao in [
        "iniciar_diagnostico",
        "enviar_para_aprovacao",
        "aprovar",
        "concluir_execucao",
        "entregar",
    ]:
        r = client.post(f"/ordens-servico/{ordem_id}/status", json={"acao": acao})
        assert r.status_code == 200

    assert client.get(f"/ordens-servico/{ordem_id}").json()["status"] == "Entregue"


def test_documento_invalido_retorna_400(client) -> None:
    resposta = client.post(
        "/ordens-servico",
        json={"documento_cliente": "123", "placa": "ABC1D23"},
    )
    assert resposta.status_code == 400


def test_ordem_inexistente_retorna_404(client) -> None:
    resposta = client.get("/ordens-servico/00000000-0000-0000-0000-000000000000")
    assert resposta.status_code == 404


def test_transicao_invalida_retorna_400(client) -> None:
    ordem_id = _criar(client)
    resposta = client.post(
        f"/ordens-servico/{ordem_id}/status", json={"acao": "aprovar"}
    )
    assert resposta.status_code == 400


def test_listar(client) -> None:
    _criar(client)
    resposta = client.get("/ordens-servico")
    assert resposta.status_code == 200
    assert len(resposta.json()) == 1


def test_tempo_medio_execucao(client) -> None:
    ordem_id = _criar(client)
    client.post(
        f"/ordens-servico/{ordem_id}/servicos",
        json={"descricao": "Alinhamento", "preco": "90.00"},
    )
    for acao in ["iniciar_diagnostico", "enviar_para_aprovacao", "aprovar", "concluir_execucao"]:
        client.post(f"/ordens-servico/{ordem_id}/status", json={"acao": acao})

    resposta = client.get("/relatorios/tempo-medio-execucao")
    assert resposta.status_code == 200
    corpo = resposta.json()
    assert corpo["amostras"] == 1
    assert "tempo_medio_formatado" in corpo
