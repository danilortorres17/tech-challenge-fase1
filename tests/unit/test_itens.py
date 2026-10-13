"""Testes dos itens da Ordem de Serviço."""
from decimal import Decimal

import pytest

from app.domain.exceptions import QuantidadeInvalida
from app.domain.itens import ItemPeca, ItemServico
from app.domain.value_objects import Dinheiro


def test_item_servico_guarda_preco() -> None:
    item = ItemServico("Troca de óleo", Dinheiro(Decimal("120.00")))
    assert item.preco.valor == Decimal("120.00")


def test_item_peca_subtotal() -> None:
    item = ItemPeca("Filtro de óleo", Dinheiro(Decimal("35.50")), 2)
    assert item.subtotal().valor == Decimal("71.00")


@pytest.mark.parametrize("quantidade", [0, -1])
def test_item_peca_quantidade_invalida(quantidade: int) -> None:
    with pytest.raises(QuantidadeInvalida):
        ItemPeca("Parafuso", Dinheiro(Decimal("1.00")), quantidade)
