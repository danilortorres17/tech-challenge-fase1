"""Objeto de valor Placa - identificação do veículo.

Aceita o formato antigo (AAA9999) e o Mercosul (AAA9A99). Normaliza para
maiúsculas e sem separadores.
"""
from __future__ import annotations

import re
from dataclasses import dataclass

from app.domain.exceptions import PlacaInvalida

_ANTIGA = re.compile(r"^[A-Z]{3}\d{4}$")
_MERCOSUL = re.compile(r"^[A-Z]{3}\d[A-Z]\d{2}$")


@dataclass(frozen=True)
class Placa:
    """Placa de veículo, validada na criação."""

    valor: str

    def __post_init__(self) -> None:
        normalizada = re.sub(r"[\s-]", "", (self.valor or "")).upper()
        if not (_ANTIGA.match(normalizada) or _MERCOSUL.match(normalizada)):
            raise PlacaInvalida(f"Placa inválida: {self.valor!r}")
        object.__setattr__(self, "valor", normalizada)

    @property
    def mercosul(self) -> bool:
        return bool(_MERCOSUL.match(self.valor))

    def __str__(self) -> str:
        return self.valor
