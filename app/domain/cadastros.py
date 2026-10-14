"""Entidades de cadastro (gestão administrativa): Cliente, Veículo, Serviço, Peça.

São entidades com identidade própria (id) e mutáveis — manipuladas pelos CRUDs.
Validações de formato ficam nos objetos de valor (CpfCnpj, Placa, Dinheiro).
"""
from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from uuid import UUID, uuid4

from app.domain.exceptions import AnoInvalido, EstoqueInsuficiente, QuantidadeInvalida
from app.domain.value_objects import CpfCnpj, Dinheiro, Placa

_ANO_MINIMO = 1900


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

    def __post_init__(self) -> None:
        ano_maximo = datetime.now(timezone.utc).year + 1  # permite modelo do ano seguinte
        if not (_ANO_MINIMO <= self.ano <= ano_maximo):
            raise AnoInvalido(
                f"Ano do veículo fora da faixa ({_ANO_MINIMO}–{ano_maximo}): {self.ano}."
            )


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

    def verificar_saldo(self, quantidade: int) -> None:
        """Valida se há saldo para a baixa, sem alterar o estoque.

        Permite checar todas as peças antes de aplicar qualquer baixa, garantindo
        que uma aprovação nunca descontará só parte das peças.
        """
        if quantidade <= 0:
            raise QuantidadeInvalida("A quantidade deve ser positiva.")
        if quantidade > self.estoque:
            raise EstoqueInsuficiente(
                f"Estoque insuficiente: saldo {self.estoque}, baixa {quantidade}."
            )

    def baixar_estoque(self, quantidade: int) -> None:
        self.verificar_saldo(quantidade)
        self.estoque -= quantidade
