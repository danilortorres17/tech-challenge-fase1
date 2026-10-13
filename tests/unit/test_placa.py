"""Testes do objeto de valor Placa."""
import pytest

from app.domain.exceptions import PlacaInvalida
from app.domain.value_objects import Placa


def test_placa_antiga_valida() -> None:
    placa = Placa("abc-1234")
    assert placa.valor == "ABC1234"
    assert placa.mercosul is False


def test_placa_mercosul_valida() -> None:
    placa = Placa("abc1d23")
    assert placa.valor == "ABC1D23"
    assert placa.mercosul is True


@pytest.mark.parametrize(
    "invalida",
    ["AB1234", "ABCD123", "1234ABC", "ABC12A3", "", "ABC-12E"],
)
def test_placa_invalida_lanca_erro(invalida: str) -> None:
    with pytest.raises(PlacaInvalida):
        Placa(invalida)


def test_igualdade_por_valor() -> None:
    assert Placa("ABC1D23") == Placa("abc 1d23")
