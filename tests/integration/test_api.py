"""Testes de integração da API REST (via TestClient).

Sobe a aplicação com os repositórios apontando para um SQLite em memória e a
autenticação desativada (sobrescrita), para focar no fluxo de negócio.
A segurança é testada em test_auth.py.
"""
import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.infrastructure.db.base import Base
from app.infrastructure.repositorio_sqlalchemy import RepositorioOrdemServicoSQLAlchemy
from app.infrastructure.repositorios_crud import (
    RepositorioClienteSQLAlchemy,
    RepositorioPecaSQLAlchemy,
    RepositorioServicoSQLAlchemy,
    RepositorioVeiculoSQLAlchemy,
)
from app.interfaces.auth import usuario_atual
from app.interfaces.dependencias import (
    obter_repositorio,
    obter_repositorio_cliente,
    obter_repositorio_peca,
    obter_repositorio_servico,
    obter_repositorio_veiculo,
)
from app.main import app


@pytest.fixture
def client() -> TestClient:
    engine = create_engine(
        "sqlite://", connect_args={"check_same_thread": False},
        poolclass=StaticPool, future=True,
    )
    Base.metadata.create_all(engine)
    factory = sessionmaker(bind=engine, expire_on_commit=False, future=True)
    app.dependency_overrides[obter_repositorio] = lambda: RepositorioOrdemServicoSQLAlchemy(factory)
    app.dependency_overrides[obter_repositorio_cliente] = lambda: RepositorioClienteSQLAlchemy(factory)
    app.dependency_overrides[obter_repositorio_veiculo] = lambda: RepositorioVeiculoSQLAlchemy(factory)
    app.dependency_overrides[obter_repositorio_servico] = lambda: RepositorioServicoSQLAlchemy(factory)
    app.dependency_overrides[obter_repositorio_peca] = lambda: RepositorioPecaSQLAlchemy(factory)
    app.dependency_overrides[usuario_atual] = lambda: "teste"
    yield TestClient(app)
    app.dependency_overrides.clear()


def _id_cliente(client) -> str:
    r = client.post("/clientes", json={"documento": "111.444.777-35", "nome": "Maria"})
    return r.json()["id"]


def _id_veiculo(client) -> str:
    r = client.post(
        "/veiculos", json={"placa": "ABC1D23", "marca": "VW", "modelo": "Gol", "ano": 2020}
    )
    return r.json()["id"]


def _id_servico(client) -> str:
    r = client.post("/servicos", json={"descricao": "Alinhamento", "preco": "90.00"})
    return r.json()["id"]


def _id_peca(client, estoque: int = 10) -> str:
    r = client.post("/pecas", json={"descricao": "Filtro", "preco": "35.50", "estoque": estoque})
    return r.json()["id"]


def _criar_os(client) -> str:
    r = client.post(
        "/ordens-servico",
        json={"cliente_id": _id_cliente(client), "veiculo_id": _id_veiculo(client)},
    )
    assert r.status_code == 201
    return r.json()["id"]


def test_criar_e_consultar(client) -> None:
    ordem_id = _criar_os(client)
    r = client.get(f"/ordens-servico/{ordem_id}")
    assert r.status_code == 200
    assert r.json()["status"] == "Recebida"
    assert r.json()["cliente_id"] is not None


def test_fluxo_completo_com_baixa_de_estoque(client) -> None:
    ordem_id = _criar_os(client)
    servico_id = _id_servico(client)
    peca_id = _id_peca(client, estoque=10)

    client.post(f"/ordens-servico/{ordem_id}/servicos", json={"servico_id": servico_id})
    client.post(
        f"/ordens-servico/{ordem_id}/pecas",
        json={"peca_id": peca_id, "quantidade": 3},
    )
    assert client.get(f"/ordens-servico/{ordem_id}").json()["orcamento"] == "196.50"  # 90 + 35.50*3

    for acao in ["iniciar_diagnostico", "enviar_para_aprovacao", "aprovar", "concluir_execucao", "entregar"]:
        r = client.post(f"/ordens-servico/{ordem_id}/status", json={"acao": acao})
        assert r.status_code == 200

    assert client.get(f"/ordens-servico/{ordem_id}").json()["status"] == "Entregue"
    # estoque baixado na aprovação: 10 - 3 = 7
    assert client.get(f"/pecas/{peca_id}").json()["estoque"] == 7


def test_aprovar_sem_estoque_retorna_400(client) -> None:
    ordem_id = _criar_os(client)
    peca_id = _id_peca(client, estoque=1)
    client.post(f"/ordens-servico/{ordem_id}/pecas", json={"peca_id": peca_id, "quantidade": 5})
    client.post(f"/ordens-servico/{ordem_id}/status", json={"acao": "iniciar_diagnostico"})
    client.post(f"/ordens-servico/{ordem_id}/status", json={"acao": "enviar_para_aprovacao"})
    r = client.post(f"/ordens-servico/{ordem_id}/status", json={"acao": "aprovar"})
    assert r.status_code == 400
    assert client.get(f"/pecas/{peca_id}").json()["estoque"] == 1  # inalterado


def test_cliente_inexistente_retorna_404(client) -> None:
    r = client.post(
        "/ordens-servico",
        json={"cliente_id": "00000000-0000-0000-0000-000000000000", "veiculo_id": _id_veiculo(client)},
    )
    assert r.status_code == 404


def test_ordem_inexistente_retorna_404(client) -> None:
    r = client.get("/ordens-servico/00000000-0000-0000-0000-000000000000")
    assert r.status_code == 404


def test_transicao_invalida_retorna_400(client) -> None:
    ordem_id = _criar_os(client)
    r = client.post(f"/ordens-servico/{ordem_id}/status", json={"acao": "aprovar"})
    assert r.status_code == 400


def test_listar(client) -> None:
    _criar_os(client)
    r = client.get("/ordens-servico")
    assert r.status_code == 200
    assert len(r.json()) == 1


def test_tempo_medio_execucao(client) -> None:
    ordem_id = _criar_os(client)
    client.post(f"/ordens-servico/{ordem_id}/servicos", json={"servico_id": _id_servico(client)})
    for acao in ["iniciar_diagnostico", "enviar_para_aprovacao", "aprovar", "concluir_execucao"]:
        client.post(f"/ordens-servico/{ordem_id}/status", json={"acao": acao})
    r = client.get("/relatorios/tempo-medio-execucao")
    assert r.status_code == 200
    assert r.json()["amostras"] == 1
