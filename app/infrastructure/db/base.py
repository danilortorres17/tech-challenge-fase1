"""Configuração do SQLAlchemy: engine, sessão e base declarativa.

Um único lugar que conhece o banco. Trocar o DATABASE_URL (SQLite, Postgres...)
não exige mudança em domínio nem em casos de uso.
"""
from __future__ import annotations

from contextlib import contextmanager
from typing import Iterator

from sqlalchemy import create_engine
from sqlalchemy.engine import Engine
from sqlalchemy.orm import DeclarativeBase, Session, sessionmaker

from app.config import settings


class Base(DeclarativeBase):
    """Base declarativa de todos os modelos ORM."""


class RepositorioSQLAlchemy:
    """Base dos repositórios SQLAlchemy: cuida da sessão/transação.

    Dois modos de uso:
    - Recebendo uma `session` pronta (de uma Unidade de Trabalho): opera nela e
      NÃO dá commit — quem abriu a transação decide confirmar ou desfazer tudo.
    - Recebendo apenas o `session_factory` (uso simples de CRUD): abre a própria
      sessão e confirma (commit) a cada operação.
    """

    def __init__(
        self,
        session_factory: sessionmaker | None = None,
        *,
        session: Session | None = None,
    ) -> None:
        self._session_factory = session_factory
        self._session = session

    @contextmanager
    def _sessao(self) -> Iterator[Session]:
        if self._session is not None:
            # Sessão compartilhada: o commit/rollback é da Unidade de Trabalho.
            yield self._session
            return
        session = self._session_factory()
        try:
            yield session
            session.commit()
        finally:
            session.close()


def criar_engine(url: str | None = None) -> Engine:
    url = url or settings.database_url
    connect_args = {"check_same_thread": False} if url.startswith("sqlite") else {}
    return create_engine(url, connect_args=connect_args, future=True)


engine = criar_engine()
SessionLocal = sessionmaker(
    bind=engine, autoflush=False, expire_on_commit=False, future=True
)


def criar_tabelas(eng: Engine | None = None) -> None:
    """Cria as tabelas no banco. Importa os modelos para registrá-los na Base."""
    from app.infrastructure.db import models  # noqa: F401

    Base.metadata.create_all(eng or engine)
