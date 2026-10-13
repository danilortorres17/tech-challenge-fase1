"""Testes unitários das entidades de cadastro (foco no estoque da Peça)."""
from decimal import Decimal

import pytest

from app.domain.cadastros import Peca
from app.domain.exceptions import EstoqueInsuficiente, QuantidadeInvalida
from app.domain.value_objects import Dinheiro


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
