"""Itens que compõem uma Ordem de Serviço: serviços e peças.

São entidades internas do agregado OrdemServico. Imutáveis — qualquer mudança
é feita adicionando/removendo itens na OS, não editando o item no lugar.
Podem referenciar (por id) um item do catálogo de cadastros (Serviço/Peça).
"""
from __future__ import annotations

from dataclasses import dataclass
from uuid import UUID

from app.domain.exceptions import QuantidadeInvalida
from app.domain.value_objects import Dinheiro


@dataclass(frozen=True)
class ItemServico:
    """Um serviço executado (ex.: troca de óleo), com o preço da mão de obra."""

    descricao: str
    preco: Dinheiro
    servico_id: UUID | None = None


@dataclass(frozen=True)
class ItemPeca:
    """Uma peça/insumo usado na OS, com preço unitário e quantidade."""

    descricao: str
    preco_unitario: Dinheiro
    quantidade: int
    peca_id: UUID | None = None

    def __post_init__(self) -> None:
        if self.quantidade <= 0:
            raise QuantidadeInvalida("A quantidade da peça deve ser maior que zero.")

    def subtotal(self) -> Dinheiro:
        return self.preco_unitario.multiplicar(self.quantidade)
