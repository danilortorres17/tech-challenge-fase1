"""Dependências da API (injeção do repositório).

Centraliza como as rotas obtêm um repositório. Em testes, esta dependência é
sobrescrita por um repositório apontando para um banco em memória.
"""
from __future__ import annotations

from app.domain.repositorios import OrdemServicoRepositorio
from app.infrastructure.db.base import SessionLocal
from app.infrastructure.repositorio_sqlalchemy import RepositorioOrdemServicoSQLAlchemy


def obter_repositorio() -> OrdemServicoRepositorio:
    return RepositorioOrdemServicoSQLAlchemy(SessionLocal)
