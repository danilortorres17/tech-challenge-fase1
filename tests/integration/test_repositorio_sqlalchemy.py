"""Teste de integração do repositório SQLAlchemy (SQLite em memória).

Prova que salvar e recuperar uma Ordem de Serviço preserva status, itens e
orçamento — o ciclo completo passando pelo banco de verdade.
"""
from decimal import Decimal

import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.application.casos_uso import (
    AcaoOrdem,
    AvancarStatusDaOrdem,
    ConsultarOrdemServico,
    CriarOrdemServico,
    IncluirPecaNaOrdem,
    IncluirServicoNaOrdem,
)
from app.domain.status_os import StatusOS
from app.domain.value_objects import Dinheiro
from app.infrastructure.db.base import Base
from app.infrastructure.repositorio_sqlalchemy import RepositorioOrdemServicoSQLAlchemy


@pytest.fixture
def repo() -> RepositorioOrdemServicoSQLAlchemy:
    engine = create_engine(
        "sqlite://",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
        future=True,
    )
    Base.metadata.create_all(engine)
    factory = sessionmaker(bind=engine, expire_on_commit=False, future=True)
    return RepositorioOrdemServicoSQLAlchemy(factory)


def test_salva_e_recupera_com_itens(repo) -> None:
    ordem_id = CriarOrdemServico(repo).executar("111.444.777-35", "ABC1D23")
    IncluirServicoNaOrdem(repo).executar(ordem_id, "Troca de óleo", Dinheiro(Decimal("120.00")))
    IncluirPecaNaOrdem(repo).executar(ordem_id, "Filtro", Dinheiro(Decimal("35.50")), 2)

    ordem = ConsultarOrdemServico(repo).executar(ordem_id)
    assert ordem.status == StatusOS.RECEBIDA
    assert len(ordem.itens_servico) == 1
    assert len(ordem.itens_peca) == 1
    assert ordem.calcular_orcamento().valor == Decimal("191.00")


def test_persiste_mudanca_de_status(repo) -> None:
    ordem_id = CriarOrdemServico(repo).executar("111.444.777-35", "ABC1D23")
    IncluirServicoNaOrdem(repo).executar(ordem_id, "Alinhamento", Dinheiro(Decimal("90.00")))
    avancar = AvancarStatusDaOrdem(repo)
    avancar.executar(ordem_id, AcaoOrdem.INICIAR_DIAGNOSTICO)
    avancar.executar(ordem_id, AcaoOrdem.ENVIAR_APROVACAO)
    avancar.executar(ordem_id, AcaoOrdem.APROVAR)

    ordem = ConsultarOrdemServico(repo).executar(ordem_id)
    assert ordem.status == StatusOS.EM_EXECUCAO
    assert ordem.aprovado is True


def test_listar_duas_ordens(repo) -> None:
    CriarOrdemServico(repo).executar("111.444.777-35", "ABC1D23")
    CriarOrdemServico(repo).executar("11.222.333/0001-81", "XYZ4B56")
    assert len(repo.listar()) == 2
