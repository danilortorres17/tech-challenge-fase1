"""Testes do objeto de valor Dinheiro."""
from decimal import Decimal

import pytest

from app.domain.exceptions import MoedaIncompativel, ValorMonetarioInvalido
from app.domain.value_objects import Dinheiro


def test_cria_com_duas_casas() -> None:
    assert Dinheiro(Decimal("10.5")).valor == Decimal("10.50")
    assert str(Dinheiro(Decimal("10.5"))) == "BRL 10.50"


def test_somar_mesma_moeda() -> None:
    total = Dinheiro(Decimal("10.00")).somar(Dinheiro(Decimal("5.50")))
    assert total.valor == Decimal("15.50")


def test_multiplicar_por_quantidade() -> None:
    assert Dinheiro(Decimal("12.00")).multiplicar(3).valor == Decimal("36.00")


def test_valor_negativo_lanca_erro() -> None:
    with pytest.raises(ValorMonetarioInvalido):
        Dinheiro(Decimal("-1.00"))


def test_somar_moedas_diferentes_lanca_erro() -> None:
    with pytest.raises(MoedaIncompativel):
        Dinheiro(Decimal("1.00"), "BRL").somar(Dinheiro(Decimal("1.00"), "USD"))


def test_zero() -> None:
    assert Dinheiro.zero().valor == Decimal("0.00")


def test_igualdade_por_valor() -> None:
    assert Dinheiro(Decimal("9.9")) == Dinheiro(Decimal("9.90"))
