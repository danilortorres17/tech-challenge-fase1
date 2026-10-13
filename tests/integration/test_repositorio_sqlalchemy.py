"""Teste de integração do repositório SQLAlchemy (SQLite em memória).

Prova que salvar e recuperar uma Ordem de Serviço (com cliente/veículo/peças
referenciados) preserva o estado, e que a aprovação baixa o estoque.
"""
from decimal import Decimal

import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.application.casos_uso import (
    AcaoOrdem,
    AprovarOrdemServico,
    AvancarStatusDaOrdem,
    ConsultarOrdemServico,
    CriarOrdemServico,
    IncluirPecaNaOrdem,
    IncluirServicoNaOrdem,
)
from app.domain.cadastros import Cliente, Peca, Servico, Veiculo
from app.domain.status_os import StatusOS
from app.domain.value_objects import CpfCnpj, Dinheiro, Placa
from app.infrastructure.db.base import Base
from app.infrastructure.repositorio_sqlalchemy import RepositorioOrdemServicoSQLAlchemy
from app.infrastructure.repositorios_crud import (
    RepositorioClienteSQLAlchemy,
    RepositorioPecaSQLAlchemy,
    RepositorioServicoSQLAlchemy,
    RepositorioVeiculoSQLAlchemy,
)


@pytest.fixture
def ctx():
    engine = create_engine(
        "sqlite://", connect_args={"check_same_thread": False},
        poolclass=StaticPool, future=True,
    )
    Base.metadata.create_all(engine)
    factory = sessionmaker(bind=engine, expire_on_commit=False, future=True)

    class Ambiente:
        os = RepositorioOrdemServicoSQLAlchemy(factory)
        cli = RepositorioClienteSQLAlchemy(factory)
        vei = RepositorioVeiculoSQLAlchemy(factory)
        serv = RepositorioServicoSQLAlchemy(factory)
        peca = RepositorioPecaSQLAlchemy(factory)

    amb = Ambiente()
    amb.cliente = Cliente(CpfCnpj("111.444.777-35"), "Maria")
    amb.veiculo = Veiculo(Placa("ABC1D23"), "VW", "Gol", 2020)
    amb.servico = Servico("Alinhamento", Dinheiro(Decimal("90.00")))
    amb.peca_obj = Peca("Filtro", Dinheiro(Decimal("35.50")), 10)
    amb.cli.salvar(amb.cliente)
    amb.vei.salvar(amb.veiculo)
    amb.serv.salvar(amb.servico)
    amb.peca.salvar(amb.peca_obj)
    return amb


def _criar(ctx):
    return CriarOrdemServico(ctx.os, ctx.cli, ctx.vei).executar(
        ctx.cliente.id, ctx.veiculo.id
    )


def test_salva_e_recupera_com_itens(ctx) -> None:
    ordem_id = _criar(ctx)
    IncluirServicoNaOrdem(ctx.os, ctx.serv).executar(ordem_id, ctx.servico.id)
    IncluirPecaNaOrdem(ctx.os, ctx.peca).executar(ordem_id, ctx.peca_obj.id, 2)

    ordem = ConsultarOrdemServico(ctx.os).executar(ordem_id)
    assert ordem.status == StatusOS.RECEBIDA
    assert ordem.cliente_id == ctx.cliente.id
    assert ordem.calcular_orcamento().valor == Decimal("161.00")


def test_aprovacao_baixa_estoque_persistido(ctx) -> None:
    ordem_id = _criar(ctx)
    IncluirPecaNaOrdem(ctx.os, ctx.peca).executar(ordem_id, ctx.peca_obj.id, 4)
    avancar = AvancarStatusDaOrdem(ctx.os)
    avancar.executar(ordem_id, AcaoOrdem.INICIAR_DIAGNOSTICO)
    avancar.executar(ordem_id, AcaoOrdem.ENVIAR_APROVACAO)
    AprovarOrdemServico(ctx.os, ctx.peca).executar(ordem_id)

    assert ConsultarOrdemServico(ctx.os).executar(ordem_id).status == StatusOS.EM_EXECUCAO
    assert ctx.peca.buscar_por_id(ctx.peca_obj.id).estoque == 6  # 10 - 4


def test_listar(ctx) -> None:
    _criar(ctx)
    assert len(ctx.os.listar()) == 1
