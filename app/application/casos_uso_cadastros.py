"""Casos de uso dos cadastros (CRUD) e do controle de estoque.

Um CRUD genérico atende Cliente, Veículo e Serviço. A Peça usa o mesmo CRUD e
ganha operações específicas de estoque (entrada e baixa).
"""
from __future__ import annotations

from typing import Callable, Generic, Optional, TypeVar
from uuid import UUID

from app.domain.cadastros import Peca
from app.domain.exceptions import RegistroDuplicado, RegistroNaoEncontrado
from app.domain.repositorios import RepositorioCrud

T = TypeVar("T")


class CrudCadastro(Generic[T]):
    """CRUD genérico: criar, obter, listar, atualizar e remover.

    Se receber `chave` (uma função que extrai a chave natural do item, p. ex. o
    CPF do cliente ou a placa do veículo), garante que essa chave seja única:
    criar ou atualizar para uma chave já usada por outro registro lança
    RegistroDuplicado.
    """

    def __init__(
        self,
        repositorio: RepositorioCrud[T],
        nome: str = "Registro",
        chave: Optional[Callable[[T], str]] = None,
    ) -> None:
        self._repo = repositorio
        self._nome = nome
        self._chave = chave

    def _garantir_chave_unica(self, item: T) -> None:
        if self._chave is None:
            return
        valor = self._chave(item)
        for existente in self._repo.listar():
            if self._chave(existente) == valor and existente.id != item.id:  # type: ignore[attr-defined]
                raise RegistroDuplicado(
                    f"Já existe {self._nome.lower()} com esse identificador: {valor}"
                )

    def criar(self, item: T) -> T:
        self._garantir_chave_unica(item)
        self._repo.salvar(item)
        return item

    def obter(self, item_id: UUID) -> T:
        item = self._repo.buscar_por_id(item_id)
        if item is None:
            raise RegistroNaoEncontrado(f"{self._nome} não encontrado: {item_id}")
        return item

    def listar(self) -> list[T]:
        return self._repo.listar()

    def atualizar(self, item: T) -> T:
        self.obter(item.id)  # garante que existe
        self._garantir_chave_unica(item)
        self._repo.salvar(item)
        return item

    def remover(self, item_id: UUID) -> None:
        if not self._repo.remover(item_id):
            raise RegistroNaoEncontrado(f"{self._nome} não encontrado: {item_id}")


class ControleDeEstoque:
    """Operações de estoque da Peça (entrada e baixa)."""

    def __init__(self, repositorio: RepositorioCrud[Peca]) -> None:
        self._repo = repositorio

    def _peca(self, peca_id: UUID) -> Peca:
        peca = self._repo.buscar_por_id(peca_id)
        if peca is None:
            raise RegistroNaoEncontrado(f"Peça não encontrada: {peca_id}")
        return peca

    def dar_entrada(self, peca_id: UUID, quantidade: int) -> Peca:
        peca = self._peca(peca_id)
        peca.adicionar_estoque(quantidade)
        self._repo.salvar(peca)
        return peca

    def dar_baixa(self, peca_id: UUID, quantidade: int) -> Peca:
        peca = self._peca(peca_id)
        peca.baixar_estoque(quantidade)
        self._repo.salvar(peca)
        return peca
