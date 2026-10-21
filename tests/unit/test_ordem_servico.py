"""Testes do agregado OrdemServico (máquina de status + orçamento)."""
from decimal import Decimal
from uuid import uuid4

import pytest

from app.domain.exceptions import (
    MoedaIncompativel,
    OperacaoInvalida,
    RegistroNaoEncontrado,
    TransicaoInvalida,
)
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


def test_remover_servico_e_peca_recalcula_orcamento() -> None:
    os = nova_os()
    sid, pid = uuid4(), uuid4()
    os.incluir_servico("Alinhamento", Dinheiro(Decimal("90.00")), servico_id=sid)
    os.incluir_peca("Filtro", Dinheiro(Decimal("35.50")), 2, peca_id=pid)
    assert os.calcular_orcamento().valor == Decimal("161.00")

    os.remover_peca(pid)
    assert os.calcular_orcamento().valor == Decimal("90.00")

    os.remover_servico(sid)
    assert os.calcular_orcamento().valor == Decimal("0.00")


def test_item_em_moeda_diferente_da_os_e_recusado() -> None:
    os = OrdemServico(CpfCnpj("111.444.777-35"), Placa("ABC1D23"), moeda="USD")
    with pytest.raises(MoedaIncompativel):
        os.incluir_servico("Troca de óleo", Dinheiro(Decimal("120.00")))  # BRL


def test_remover_item_inexistente_lanca_erro() -> None:
    with pytest.raises(RegistroNaoEncontrado):
        nova_os().remover_servico(uuid4())


def test_nao_remove_item_com_os_fora_de_edicao() -> None:
    os = nova_os()
    sid = uuid4()
    os.incluir_servico("Alinhamento", Dinheiro(Decimal("90.00")), servico_id=sid)
    os.iniciar_diagnostico()
    os.enviar_para_aprovacao()  # sai dos status editáveis
    with pytest.raises(OperacaoInvalida):
        os.remover_servico(sid)


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


def test_rejeitar_muda_status_para_rejeitada() -> None:
    os = nova_os()
    os.incluir_servico("Troca de óleo", Dinheiro(Decimal("120.00")))
    os.iniciar_diagnostico()
    os.enviar_para_aprovacao()
    os.rejeitar()
    assert os.aprovado is False
    assert os.status == StatusOS.REJEITADA


def test_rejeitar_fora_de_aprovacao_lanca_erro() -> None:
    with pytest.raises(TransicaoInvalida):
        nova_os().rejeitar()


def test_reabrir_rejeitada_volta_para_diagnostico_e_permite_reenvio() -> None:
    os = nova_os()
    os.incluir_servico("Troca de óleo", Dinheiro(Decimal("120.00")))
    os.iniciar_diagnostico()
    os.enviar_para_aprovacao()
    os.rejeitar()

    os.reabrir_diagnostico()
    assert os.status == StatusOS.EM_DIAGNOSTICO
    assert os.aprovado is None
    # com a OS reaberta, dá para ajustar o orçamento e reenviar/aprovar
    os.incluir_peca("Correia", Dinheiro(Decimal("50.00")), 1)
    os.enviar_para_aprovacao()
    os.aprovar()
    assert os.status == StatusOS.EM_EXECUCAO
    assert os.aprovado is True


def test_nao_pode_reabrir_fora_de_estado_valido() -> None:
    os = nova_os()
    os.incluir_servico("Troca de óleo", Dinheiro(Decimal("120.00")))
    os.iniciar_diagnostico()
    os.enviar_para_aprovacao()  # Aguardando aprovação não volta direto p/ diagnóstico
    with pytest.raises(TransicaoInvalida):
        os.reabrir_diagnostico()
