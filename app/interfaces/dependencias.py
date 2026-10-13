"""Dependências da API (injeção dos repositórios).

Centraliza como as rotas obtêm um repositório. Em testes, estas dependências
são sobrescritas por repositórios apontando para um banco em memória.
"""
from __future__ import annotations

from app.domain.cadastros import Cliente, Peca, Servico, Veiculo
from app.domain.repositorios import OrdemServicoRepositorio, RepositorioCrud
from app.infrastructure.db.base import SessionLocal
from app.infrastructure.repositorio_sqlalchemy import RepositorioOrdemServicoSQLAlchemy
from app.infrastructure.repositorios_crud import (
    RepositorioClienteSQLAlchemy,
    RepositorioPecaSQLAlchemy,
    RepositorioServicoSQLAlchemy,
    RepositorioVeiculoSQLAlchemy,
)


def obter_repositorio() -> OrdemServicoRepositorio:
    return RepositorioOrdemServicoSQLAlchemy(SessionLocal)


def obter_repositorio_cliente() -> RepositorioCrud[Cliente]:
    return RepositorioClienteSQLAlchemy(SessionLocal)


def obter_repositorio_veiculo() -> RepositorioCrud[Veiculo]:
    return RepositorioVeiculoSQLAlchemy(SessionLocal)


def obter_repositorio_servico() -> RepositorioCrud[Servico]:
    return RepositorioServicoSQLAlchemy(SessionLocal)


def obter_repositorio_peca() -> RepositorioCrud[Peca]:
    return RepositorioPecaSQLAlchemy(SessionLocal)
