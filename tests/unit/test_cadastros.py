"""Testes unitários das entidades de cadastro (estoque da Peça e ano do Veículo)."""
from datetime import datetime, timezone
from decimal import Decimal

import pytest

from app.domain.cadastros import Peca, Veiculo
from app.domain.exceptions import AnoInvalido, EstoqueInsuficiente, QuantidadeInvalida
from app.domain.value_objects import Dinheiro, Placa


def nova_peca(estoque: int = 0) -> Peca:
    return Peca("Filtro", Dinheiro(Decimal("35.50")), estoque)


def test_adicionar_estoque() -> None:
    peca = nova_peca(5)
    peca.adicionar_estoque(10)
    assert peca.estoque == 15


def test_baixar_estoque() -> None:
    peca = nova_peca(10)
    peca.baixar_estoque(4)
    assert peca.estoque == 6


def test_baixa_maior_que_saldo_lanca_erro() -> None:
    with pytest.raises(EstoqueInsuficiente):
        nova_peca(2).baixar_estoque(5)


@pytest.mark.parametrize("quantidade", [0, -3])
def test_quantidade_invalida(quantidade: int) -> None:
    with pytest.raises(QuantidadeInvalida):
        nova_peca(10).adicionar_estoque(quantidade)


def test_estoque_inicial_negativo_lanca_erro() -> None:
    with pytest.raises(QuantidadeInvalida):
        nova_peca(-1)


def test_veiculo_ano_valido() -> None:
    veiculo = Veiculo(Placa("ABC1D23"), "VW", "Gol", 2020)
    assert veiculo.ano == 2020


@pytest.mark.parametrize("ano", [1500, 1899, 3000])
def test_veiculo_ano_invalido_lanca_erro(ano: int) -> None:
    with pytest.raises(AnoInvalido):
        Veiculo(Placa("ABC1D23"), "VW", "Gol", ano)


def test_veiculo_aceita_modelo_do_ano_seguinte() -> None:
    proximo_ano = datetime.now(timezone.utc).year + 1
    veiculo = Veiculo(Placa("ABC1D23"), "VW", "Gol", proximo_ano)
    assert veiculo.ano == proximo_ano
