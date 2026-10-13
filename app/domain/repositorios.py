"""Portas de persistência (interfaces de repositório).

O domínio declara o que precisa guardar/recuperar; a implementação concreta
fica na infraestrutura. Assim o domínio e os casos de uso não dependem de
banco de dados nenhum — podem ser testados com um repositório em memória.
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
