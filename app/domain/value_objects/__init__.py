"""Objetos de valor do domínio.

São imutáveis, não têm identidade própria e são comparados pelo valor.
A validação acontece na criação: um objeto de valor nunca existe em estado inválido.
"""
from app.domain.value_objects.cpf_cnpj import CpfCnpj
from app.domain.value_objects.dinheiro import Dinheiro
from app.domain.value_objects.placa import Placa

__all__ = ["CpfCnpj", "Dinheiro", "Placa"]
