"""Objeto de valor CpfCnpj — documento de identificação do cliente.

Aceita CPF (11 dígitos) ou CNPJ (14 dígitos), validando os dígitos
verificadores. Guarda apenas os dígitos; a formatação é derivada.
"""
from __future__ import annotations

import re
from dataclasses import dataclass

from app.domain.exceptions import DocumentoInvalido


def _apenas_digitos(valor: str) -> str:
    return re.sub(r"\D", "", valor or "")


def _digito_cpf(parciais: str) -> int:
    peso = len(parciais) + 1
    soma = sum(int(d) * (peso - i) for i, d in enumerate(parciais))
    resto = (soma * 10) % 11
    return 0 if resto == 10 else resto


def _cpf_valido(num: str) -> bool:
    if len(num) != 11 or num == num[0] * 11:
        return False
    d1 = _digito_cpf(num[:9])
    d2 = _digito_cpf(num[:9] + str(d1))
    return num[9:] == f"{d1}{d2}"


def _digito_cnpj(parciais: str, pesos: list[int]) -> int:
    soma = sum(int(d) * p for d, p in zip(parciais, pesos))
    resto = soma % 11
    return 0 if resto < 2 else 11 - resto


def _cnpj_valido(num: str) -> bool:
    if len(num) != 14 or num == num[0] * 14:
        return False
    pesos1 = [5, 4, 3, 2, 9, 8, 7, 6, 5, 4, 3, 2]
    pesos2 = [6, 5, 4, 3, 2, 9, 8, 7, 6, 5, 4, 3, 2]
    d1 = _digito_cnpj(num[:12], pesos1)
    d2 = _digito_cnpj(num[:12] + str(d1), pesos2)
    return num[12:] == f"{d1}{d2}"


@dataclass(frozen=True)
class CpfCnpj:
    """Documento do cliente (CPF ou CNPJ), validado na criação."""

    valor: str

    def __post_init__(self) -> None:
        num = _apenas_digitos(self.valor)
        if not (_cpf_valido(num) or _cnpj_valido(num)):
            raise DocumentoInvalido(f"Documento inválido: {self.valor!r}")
        object.__setattr__(self, "valor", num)

    @property
    def tipo(self) -> str:
        return "CPF" if len(self.valor) == 11 else "CNPJ"

    def formatado(self) -> str:
        v = self.valor
        if self.tipo == "CPF":
            return f"{v[:3]}.{v[3:6]}.{v[6:9]}-{v[9:]}"
        return f"{v[:2]}.{v[2:5]}.{v[5:8]}/{v[8:12]}-{v[12:]}"

    def __str__(self) -> str:
        return self.formatado()
