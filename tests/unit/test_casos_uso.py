"""Testes dos casos de uso da Ordem de Serviço (camada de aplicação)."""
from decimal import Decimal
from uuid import uuid4

import pytest

from app.application.casos_uso import (
    AcaoOrdem,
    AvancarStatusDaOrdem,
    ConsultarOrdemServico,
    CriarOrdemServico,
    IncluirPecaNaOrdem,
    IncluirServicoNaOrdem,
)
from app.domain.exceptions import OrdemNaoEncontrada, TransicaoInvalida
from app.domain.status_os import StatusOS
from app.domain.value_objects import Dinheiro
from app.infrastructure.repositorio_memoria import RepositorioOrdemServicoEmMemoria


@pytest.fixture
def repo() -> RepositorioOrdemServicoEmMemoria:
    return RepositorioOrdemServicoEmMemoria()


def test_criar_persiste_ordem_recebida(repo) -> None:
    ordem_id = CriarOrdemServico(repo).executar("111.444.777-35", "ABC1D23")
    ordem = ConsultarOrdemServico(repo).executar(ordem_id)
    assert ordem.status == StatusOS.RECEBIDA


def test_incluir_itens_e_calcular_orcamento(repo) -> None:
    ordem_id = CriarOrdemServico(repo).executar("111.444.777-35", "ABC1D23")
    IncluirServicoNaOrdem(repo).executar(ordem_id, "Troca de óleo", Dinheiro(Decimal("120.00")))
    IncluirPecaNaOrdem(repo).executar(ordem_id, "Filtro", Dinheiro(Decimal("35.50")), 2)
    ordem = ConsultarOrdemServico(repo).executar(ordem_id)
    assert ordem.calcular_orcamento().valor == Decimal("191.00")


def test_fluxo_completo_via_casos_uso(repo) -> None:
    ordem_id = CriarOrdemServico(repo).executar("111.444.777-35", "ABC1D23")
    IncluirServicoNaOrdem(repo).executar(ordem_id, "Alinhamento", Dinheiro(Decimal("90.00")))
    avancar = AvancarStatusDaOrdem(repo)
    avancar.executar(ordem_id, AcaoOrdem.INICIAR_DIAGNOSTICO)
    avancar.executar(ordem_id, AcaoOrdem.ENVIAR_APROVACAO)
    avancar.executar(ordem_id, AcaoOrdem.APROVAR)
    avancar.executar(ordem_id, AcaoOrdem.CONCLUIR)
    ordem = avancar.executar(ordem_id, AcaoOrdem.ENTREGAR)
    assert ordem.status == StatusOS.ENTREGUE
    assert ordem.aprovado is True


def test_ordem_inexistente_lanca_erro(repo) -> None:
    with pytest.raises(OrdemNaoEncontrada):
        ConsultarOrdemServico(repo).executar(uuid4())


def test_acao_invalida_para_status_propaga_erro(repo) -> None:
    ordem_id = CriarOrdemServico(repo).executar("111.444.777-35", "ABC1D23")
    with pytest.raises(TransicaoInvalida):
        AvancarStatusDaOrdem(repo).executar(ordem_id, AcaoOrdem.APROVAR)
