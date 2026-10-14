"""Testes dos casos de uso da Ordem de Serviço (camada de aplicação)."""
from decimal import Decimal
from types import SimpleNamespace
from uuid import uuid4

import pytest

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
from app.domain.exceptions import (
    EstoqueInsuficiente,
    OperacaoInvalida,
    OrdemNaoEncontrada,
    RegistroNaoEncontrado,
    TransicaoInvalida,
)
from app.domain.status_os import StatusOS
from app.domain.value_objects import CpfCnpj, Dinheiro, Placa
from app.infrastructure.repositorio_memoria import (
    RepositorioCrudEmMemoria,
    RepositorioOrdemServicoEmMemoria,
    UnidadeDeTrabalhoEmMemoria,
)


@pytest.fixture
def ctx():
    ambiente = SimpleNamespace(
        os=RepositorioOrdemServicoEmMemoria(),
        cli=RepositorioCrudEmMemoria(),
        vei=RepositorioCrudEmMemoria(),
        serv=RepositorioCrudEmMemoria(),
        peca=RepositorioCrudEmMemoria(),
    )
    ambiente.cliente = Cliente(CpfCnpj("111.444.777-35"), "Maria")
    ambiente.veiculo = Veiculo(Placa("ABC1D23"), "VW", "Gol", 2020)
    ambiente.servico = Servico("Alinhamento", Dinheiro(Decimal("90.00")))
    ambiente.peca_obj = Peca("Filtro", Dinheiro(Decimal("35.50")), 10)
    ambiente.cli.salvar(ambiente.cliente)
    ambiente.vei.salvar(ambiente.veiculo)
    ambiente.serv.salvar(ambiente.servico)
    ambiente.peca.salvar(ambiente.peca_obj)
    return ambiente


def _criar(ctx):
    return CriarOrdemServico(ctx.os, ctx.cli, ctx.vei).executar(
        ctx.cliente.id, ctx.veiculo.id
    )


def _aprovar(ctx, ordem_id):
    uow = UnidadeDeTrabalhoEmMemoria(ctx.os, ctx.peca)
    return AprovarOrdemServico(uow).executar(ordem_id)


def test_criar_persiste_ordem_recebida(ctx) -> None:
    ordem_id = _criar(ctx)
    ordem = ConsultarOrdemServico(ctx.os).executar(ordem_id)
    assert ordem.status == StatusOS.RECEBIDA
    assert ordem.cliente_id == ctx.cliente.id
    assert ordem.veiculo_id == ctx.veiculo.id


def test_criar_com_cliente_inexistente_lanca_erro(ctx) -> None:
    with pytest.raises(RegistroNaoEncontrado):
        CriarOrdemServico(ctx.os, ctx.cli, ctx.vei).executar(uuid4(), ctx.veiculo.id)


def test_criar_os_com_veiculo_de_outro_cliente_lanca_erro(ctx) -> None:
    dono = Cliente(CpfCnpj("111.444.777-35"), "Dono")
    ctx.cli.salvar(dono)
    veiculo_do_dono = Veiculo(Placa("XYZ4A56"), "Fiat", "Uno", 2019, cliente_id=dono.id)
    ctx.vei.salvar(veiculo_do_dono)
    # ctx.cliente é outra pessoa → não pode abrir OS com o veículo do dono
    with pytest.raises(OperacaoInvalida):
        CriarOrdemServico(ctx.os, ctx.cli, ctx.vei).executar(
            ctx.cliente.id, veiculo_do_dono.id
        )


def test_incluir_itens_e_calcular_orcamento(ctx) -> None:
    ordem_id = _criar(ctx)
    IncluirServicoNaOrdem(ctx.os, ctx.serv).executar(ordem_id, ctx.servico.id)
    IncluirPecaNaOrdem(ctx.os, ctx.peca).executar(ordem_id, ctx.peca_obj.id, 2)
    ordem = ConsultarOrdemServico(ctx.os).executar(ordem_id)
    assert ordem.calcular_orcamento().valor == Decimal("161.00")  # 90 + 35.50*2


def test_fluxo_completo_da_baixa_no_estoque(ctx) -> None:
    ordem_id = _criar(ctx)
    IncluirPecaNaOrdem(ctx.os, ctx.peca).executar(ordem_id, ctx.peca_obj.id, 3)
    avancar = AvancarStatusDaOrdem(ctx.os)
    avancar.executar(ordem_id, AcaoOrdem.INICIAR_DIAGNOSTICO)
    avancar.executar(ordem_id, AcaoOrdem.ENVIAR_APROVACAO)
    _aprovar(ctx, ordem_id)  # baixa estoque
    avancar.executar(ordem_id, AcaoOrdem.CONCLUIR)
    ordem = avancar.executar(ordem_id, AcaoOrdem.ENTREGAR)

    assert ordem.status == StatusOS.ENTREGUE
    assert ordem.aprovado is True
    assert ctx.peca.buscar_por_id(ctx.peca_obj.id).estoque == 7  # 10 - 3


def test_aprovar_sem_estoque_nao_altera_nada(ctx) -> None:
    peca_rara = Peca("Peça rara", Dinheiro(Decimal("10.00")), 1)
    ctx.peca.salvar(peca_rara)
    ordem_id = _criar(ctx)
    IncluirPecaNaOrdem(ctx.os, ctx.peca).executar(ordem_id, peca_rara.id, 5)
    AvancarStatusDaOrdem(ctx.os).executar(ordem_id, AcaoOrdem.INICIAR_DIAGNOSTICO)
    AvancarStatusDaOrdem(ctx.os).executar(ordem_id, AcaoOrdem.ENVIAR_APROVACAO)
    with pytest.raises(EstoqueInsuficiente):
        _aprovar(ctx, ordem_id)
    assert ctx.peca.buscar_por_id(peca_rara.id).estoque == 1  # inalterado


def test_nao_pode_aprovar_pulando_etapa(ctx) -> None:
    ordem_id = _criar(ctx)
    with pytest.raises(TransicaoInvalida):
        _aprovar(ctx, ordem_id)


def test_ordem_inexistente_lanca_erro(ctx) -> None:
    with pytest.raises(OrdemNaoEncontrada):
        ConsultarOrdemServico(ctx.os).executar(uuid4())
