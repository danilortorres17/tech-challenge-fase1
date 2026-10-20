"""Objeto de valor Dinheiro - valores monetários.

Usa Decimal (nunca float) para evitar erros de arredondamento em preços.
Imutável; operações retornam um novo Dinheiro.
"""
from __future__ import annotations

from dataclasses import dataclass
from decimal import Decimal, ROUND_HALF_UP

from app.domain.exceptions import MoedaIncompativel, ValorMonetarioInvalido

_CENTAVOS = Decimal("0.01")


@dataclass(frozen=True)
class Dinheiro:
    """Quantia monetária com moeda, não negativa, com 2 casas decimais."""

    valor: Decimal
    moeda: str = "BRL"

    def __post_init__(self) -> None:
        valor = self.valor if isinstance(self.valor, Decimal) else Decimal(str(self.valor))
        if valor < 0:
            raise ValorMonetarioInvalido("Valor monetário não pode ser negativo.")
        object.__setattr__(self, "valor", valor.quantize(_CENTAVOS, rounding=ROUND_HALF_UP))

    @classmethod
    def zero(cls, moeda: str = "BRL") -> "Dinheiro":
        return cls(Decimal("0.00"), moeda)

    def somar(self, outro: "Dinheiro") -> "Dinheiro":
        self._exige_mesma_moeda(outro)
        return Dinheiro(self.valor + outro.valor, self.moeda)

    def multiplicar(self, quantidade: int) -> "Dinheiro":
        if quantidade < 0:
            raise ValorMonetarioInvalido("Quantidade não pode ser negativa.")
        return Dinheiro(self.valor * quantidade, self.moeda)

    def _exige_mesma_moeda(self, outro: "Dinheiro") -> None:
        if self.moeda != outro.moeda:
            raise MoedaIncompativel(
                f"Moedas incompatíveis: {self.moeda} e {outro.moeda}."
            )

    def __str__(self) -> str:
        return f"{self.moeda} {self.valor:.2f}"
