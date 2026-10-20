"""Implementações em memória dos repositórios.

Adaptadores usados em testes (e para desenvolvimento rápido), enquanto o banco
real não entra. Guardam tudo em dicionários.
"""
from __future__ import annotations

from typing import Generic, TypeVar
from uuid import UUID

from app.domain.ordem_servico import OrdemServico
from app.domain.repositorios import (
    OrdemServicoRepositorio,
    RepositorioCrud,
    UnidadeDeTrabalho,
)

T = TypeVar("T")


class RepositorioOrdemServicoEmMemoria(OrdemServicoRepositorio):
    def __init__(self) -> None:
        self._dados: dict[UUID, OrdemServico] = {}

    def salvar(self, ordem: OrdemServico) -> None:
        self._dados[ordem.id] = ordem

    def buscar_por_id(self, ordem_id: UUID) -> OrdemServico | None:
        return self._dados.get(ordem_id)

    def listar(self) -> list[OrdemServico]:
        return list(self._dados.values())


class RepositorioCrudEmMemoria(RepositorioCrud[T], Generic[T]):
    """CRUD genérico em memória (para Cliente, Veículo, Serviço, Peça)."""

    def __init__(self) -> None:
        self._dados: dict[UUID, T] = {}

    def salvar(self, item: T) -> None:
        self._dados[item.id] = item  # type: ignore[attr-defined]

    def buscar_por_id(self, item_id: UUID) -> T | None:
        return self._dados.get(item_id)

    def listar(self) -> list[T]:
        return list(self._dados.values())

    def remover(self, item_id: UUID) -> bool:
        if item_id in self._dados:
            del self._dados[item_id]
            return True
        return False


class UnidadeDeTrabalhoEmMemoria(UnidadeDeTrabalho):
    """Unidade de Trabalho para testes: agrupa repositórios em memória.

    Como os repositórios em memória guardam os próprios objetos, não há uma
    transação real para confirmar ou desfazer - commit/rollback são no-ops. A
    atomicidade da aprovação, nos testes, é garantida pela conferência prévia de
    saldo no caso de uso (nada é baixado se faltar estoque em qualquer peça).
    """

    def __init__(
        self,
        ordens: OrdemServicoRepositorio,
        pecas: RepositorioCrud,
    ) -> None:
        self.ordens = ordens
        self.pecas = pecas

    def commit(self) -> None:  # pragma: no cover - sem transação em memória
        pass

    def rollback(self) -> None:  # pragma: no cover - sem transação em memória
        pass
