"""Portas de persistência (interfaces de repositório).

O domínio declara o que precisa guardar/recuperar; a implementação concreta
fica na infraestrutura. Assim o domínio e os casos de uso não dependem de
banco de dados nenhum - podem ser testados com um repositório em memória.
"""
from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Generic, TypeVar
from uuid import UUID

from app.domain.ordem_servico import OrdemServico

T = TypeVar("T")


class OrdemServicoRepositorio(ABC):
    """Contrato de persistência do agregado OrdemServico."""

    @abstractmethod
    def salvar(self, ordem: OrdemServico) -> None: ...

    @abstractmethod
    def buscar_por_id(self, ordem_id: UUID) -> OrdemServico | None: ...

    @abstractmethod
    def listar(self) -> list[OrdemServico]: ...


class RepositorioCrud(ABC, Generic[T]):
    """Contrato genérico de CRUD para as entidades de cadastro."""

    @abstractmethod
    def salvar(self, item: T) -> None: ...

    @abstractmethod
    def buscar_por_id(self, item_id: UUID) -> T | None: ...

    @abstractmethod
    def listar(self) -> list[T]: ...

    @abstractmethod
    def remover(self, item_id: UUID) -> bool: ...


class UnidadeDeTrabalho(ABC):
    """Porta de transação (padrão Unit of Work).

    Agrupa operações de vários repositórios numa única transação: ou todas são
    confirmadas juntas (commit), ou nenhuma é (rollback). Usada como gerenciador
    de contexto:

        with uow:
            uow.ordens.salvar(ordem)
            uow.pecas.salvar(peca)
        # commit automático ao sair sem erro; rollback se houver exceção.

    Os repositórios expostos compartilham a mesma transação.
    """

    ordens: "OrdemServicoRepositorio"
    pecas: "RepositorioCrud"

    def __enter__(self) -> "UnidadeDeTrabalho":
        return self

    def __exit__(self, exc_type, exc, tb) -> None:
        if exc_type is None:
            self.commit()
        else:
            self.rollback()

    @abstractmethod
    def commit(self) -> None: ...

    @abstractmethod
    def rollback(self) -> None: ...
