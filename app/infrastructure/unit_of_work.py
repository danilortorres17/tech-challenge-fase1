"""Unidade de Trabalho (Unit of Work) com SQLAlchemy.

Abre uma única sessão e disponibiliza os repositórios de OS e de Peça ligados a
ela. Ao sair do `with` sem erro, confirma tudo de uma vez (commit); se houver
exceção, desfaz tudo (rollback). É o que garante a atomicidade da aprovação.
"""
from __future__ import annotations

from sqlalchemy.orm import sessionmaker

from app.domain.repositorios import UnidadeDeTrabalho
from app.infrastructure.repositorio_sqlalchemy import RepositorioOrdemServicoSQLAlchemy
from app.infrastructure.repositorios_crud import RepositorioPecaSQLAlchemy


class UnidadeDeTrabalhoSQLAlchemy(UnidadeDeTrabalho):
    def __init__(self, session_factory: sessionmaker) -> None:
        self._session_factory = session_factory
        self._session = None

    def __enter__(self) -> "UnidadeDeTrabalhoSQLAlchemy":
        self._session = self._session_factory()
        self.ordens = RepositorioOrdemServicoSQLAlchemy(session=self._session)
        self.pecas = RepositorioPecaSQLAlchemy(session=self._session)
        return self

    def __exit__(self, exc_type, exc, tb) -> None:
        try:
            super().__exit__(exc_type, exc, tb)
        finally:
            self._session.close()
            self._session = None

    def commit(self) -> None:
        self._session.commit()

    def rollback(self) -> None:
        self._session.rollback()
