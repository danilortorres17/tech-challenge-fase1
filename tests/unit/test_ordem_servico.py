"""Testes do agregado OrdemServico (máquina de status + orçamento)."""
from decimal import Decimal

import pytest

from app.domain.exceptions import OperacaoInvalida, TransicaoInvalida
from app.domain.ordem_servico import OrdemServico
from app.domain.status_os import StatusOS
from app.domain.value_objects import CpfCnpj, Dinheiro, Placa


def nova_os() -> OrdemServico:
    return OrdemServico(CpfCnpj("111.444.777-35"), Placa("ABC1D23"))


def test_nova_os_comeca_recebida() -> None:
    assert nova_os().status == StatusOS.RECEBIDA


def test_calcula_orcamento_servicos_e_pecas() -> None:
    os = nova_os()
    os.incluir_servico("Troca de óleo", Dinheiro(Decimal("120.00")))
    os.incluir_peca("Filtro", Dinheiro(Decimal("35.50")), 2)
    assert os.calcular_orcamento().valor == Decimal("191.00")


def test_fluxo_feliz_ate_entregue() -> None:
    os = nova_os()
    os.incluir_servico("Alinhamento", Dinheiro(Decimal("90.00")))
    os.iniciar_diagnostico()
    os.enviar_para_aprovacao()
    os.aprovar()
    os.concluir_execucao()
    os.entregar()
    assert os.status == StatusOS.ENTREGUE
    assert os.aprovado is True


def test_nao_pode_pular_etapa() -> None:
    os = nova_os()
    with pytest.raises(TransicaoInvalida):
        os.aprovar()  # Recebida -> Em execução direto é inválido


def test_nao_envia_orcamento_vazio() -> None:
    os = nova_os()
    os.iniciar_diagnostico()
    with pytest.raises(OperacaoInvalida):
        os.enviar_para_aprovacao()


def test_nao_altera_itens_depois_de_aprovado() -> None:
    os = nova_os()
    os.incluir_servico("Troca de óleo", Dinheiro(Decimal("120.00")))
    os.iniciar_diagnostico()
    os.enviar_para_aprovacao()
    os.aprovar()
    with pytest.raises(OperacaoInvalida):
        os.incluir_servico("Extra", Dinheiro(Decimal("10.00")))


def test_rejeitar_marca_nao_aprovado() -> None:
    os = nova_os()
    os.incluir_servico("Troca de óleo", Dinheiro(Decimal("120.00")))
    os.iniciar_diagnostico()
    os.enviar_para_aprovacao()
    os.rejeitar()
    assert os.aprovado is False
    assert os.status == StatusOS.AGUARDANDO_APROVACAO


def test_rejeitar_fora_de_aprovacao_lanca_erro() -> None:
    with pytest.raises(TransicaoInvalida):
        nova_os().rejeitar()
