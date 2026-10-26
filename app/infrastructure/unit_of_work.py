"""Unidade de Trabalho (Unit of Work) com SQLAlchemy.

Abre uma única sessão e disponibiliza os repositórios de OS e de Peça ligados a
ela. Ao sair do `with` sem erro, confirma tudo de uma vez (commit); se houver
exceção, desfaz tudo (rollback). É o que garante a atomicidade da aprovação.
"""
from __future__ import annotations

from uuid import UUID

from sqlalchemy import update
from sqlalchemy.orm import sessionmaker

from app.domain.repositorios import UnidadeDeTrabalho
from app.infrastructure.db.models import PecaModel
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

    def baixar_estoque(self, peca_id: UUID, quantidade: int) -> bool:
        """UPDATE condicional: só desconta se o saldo atual comportar a baixa.

        A condição `estoque >= quantidade` e o desconto acontecem na mesma
        instrução SQL, de forma atômica - duas aprovações concorrentes nunca
        deixam o estoque negativo. Retorna True se uma linha foi atualizada.
        """
        resultado = self._session.execute(
            update(PecaModel)
            .where(PecaModel.id == str(peca_id), PecaModel.estoque >= quantidade)
            .values(estoque=PecaModel.estoque - quantidade)
        )
        return resultado.rowcount == 1
