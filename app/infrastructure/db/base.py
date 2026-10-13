"""Configuração do SQLAlchemy: engine, sessão e base declarativa.

Um único lugar que conhece o banco. Trocar o DATABASE_URL (SQLite, Postgres...)
não exige mudança em domínio nem em casos de uso.
"""
from __future__ import annotations

from sqlalchemy import create_engine
from sqlalchemy.engine import Engine
from sqlalchemy.orm import DeclarativeBase, sessionmaker

from app.config import settings


class Base(DeclarativeBase):
    """Base declarativa de todos os modelos ORM."""


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
