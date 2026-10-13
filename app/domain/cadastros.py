"""Entidades de cadastro (gestão administrativa): Cliente, Veículo, Serviço, Peça.

São entidades com identidade própria (id) e mutáveis — manipuladas pelos CRUDs.
Validações de formato ficam nos objetos de valor (CpfCnpj, Placa, Dinheiro).
"""
from __future__ import annotations

from dataclasses import dataclass, field
from uuid import UUID, uuid4

from app.domain.exceptions import EstoqueInsuficiente, QuantidadeInvalida
from app.domain.value_objects import CpfCnpj, Dinheiro, Placa


@dataclass
class Cliente:
    documento: CpfCnpj
    nome: str
    id: UUID = field(default_factory=uuid4)


@dataclass
class Veiculo:
    placa: Placa
    marca: str
    modelo: str
    ano: int
    cliente_id: UUID | None = None
    id: UUID = field(default_factory=uuid4)


@dataclass
class Servico:
    descricao: str
    preco: Dinheiro
    id: UUID = field(default_factory=uuid4)


@dataclass
class Peca:
    descricao: str
    preco: Dinheiro
    estoque: int = 0
    id: UUID = field(default_factory=uuid4)

    def __post_init__(self) -> None:
        if self.estoque < 0:
            raise QuantidadeInvalida("O estoque não pode ser negativo.")

    def adicionar_estoque(self, quantidade: int) -> None:
        if quantidade <= 0:
            raise QuantidadeInvalida("A quantidade deve ser positiva.")
        self.estoque += quantidade

    def baixar_estoque(self, quantidade: int) -> None:
        if quantidade <= 0:
            raise QuantidadeInvalida("A quantidade deve ser positiva.")
        if quantidade > self.estoque:
            raise EstoqueInsuficiente(
                f"Estoque insuficiente: saldo {self.estoque}, baixa {quantidade}."
            )
        self.estoque -= quantidade
