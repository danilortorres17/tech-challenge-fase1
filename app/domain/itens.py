"""Itens que compõem uma Ordem de Serviço: serviços e peças.

São entidades internas do agregado OrdemServico. Imutáveis — qualquer mudança
é feita adicionando/removendo itens na OS, não editando o item no lugar.
"""
from __future__ import annotations

from dataclasses import dataclass

from app.domain.exceptions import QuantidadeInvalida
from app.domain.value_objects import Dinheiro


@dataclass(frozen=True)
class ItemServico:
    """Um serviço executado (ex.: troca de óleo), com o preço da mão de obra."""

    descricao: str
    preco: Dinheiro


@dataclass(frozen=True)
class ItemPeca:
    """Uma peça/insumo usado na OS, com preço unitário e quantidade."""

    descricao: str
    preco_unitario: Dinheiro
    quantidade: int

    def __post_init__(self) -> None:
        if self.quantidade <= 0:
            raise QuantidadeInvalida("A quantidade da peça deve ser maior que zero.")

    def subtotal(self) -> Dinheiro:
        return self.preco_unitario.multiplicar(self.quantidade)
