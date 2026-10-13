"""Repositórios SQLAlchemy das entidades de cadastro.

Cada um implementa o contrato genérico RepositorioCrud e traduz entre a
entidade de domínio e o modelo ORM correspondente.
"""
from __future__ import annotations

from decimal import Decimal
from uuid import UUID

from sqlalchemy.orm import sessionmaker

from app.domain.cadastros import Cliente, Peca, Servico, Veiculo
from app.domain.repositorios import RepositorioCrud
from app.domain.value_objects import CpfCnpj, Dinheiro, Placa
from app.infrastructure.db.models import (
    ClienteModel,
    PecaModel,
    ServicoModel,
    VeiculoModel,
)


class RepositorioClienteSQLAlchemy(RepositorioCrud[Cliente]):
    def __init__(self, session_factory: sessionmaker) -> None:
        self._sf = session_factory

    def salvar(self, item: Cliente) -> None:
        with self._sf() as s:
            m = s.get(ClienteModel, str(item.id)) or ClienteModel(id=str(item.id))
            m.documento = item.documento.valor
            m.nome = item.nome
            s.add(m)
            s.commit()

    def buscar_por_id(self, item_id: UUID) -> Cliente | None:
        with self._sf() as s:
            m = s.get(ClienteModel, str(item_id))
            return Cliente(CpfCnpj(m.documento), m.nome, UUID(m.id)) if m else None

    def listar(self) -> list[Cliente]:
        with self._sf() as s:
            return [
                Cliente(CpfCnpj(m.documento), m.nome, UUID(m.id))
                for m in s.query(ClienteModel).all()
            ]

    def remover(self, item_id: UUID) -> bool:
        with self._sf() as s:
            m = s.get(ClienteModel, str(item_id))
            if m is None:
                return False
            s.delete(m)
            s.commit()
            return True


class RepositorioVeiculoSQLAlchemy(RepositorioCrud[Veiculo]):
    def __init__(self, session_factory: sessionmaker) -> None:
        self._sf = session_factory

    def salvar(self, item: Veiculo) -> None:
        with self._sf() as s:
            m = s.get(VeiculoModel, str(item.id)) or VeiculoModel(id=str(item.id))
            m.placa = item.placa.valor
            m.marca = item.marca
            m.modelo = item.modelo
            m.ano = item.ano
            m.cliente_id = str(item.cliente_id) if item.cliente_id else None
            s.add(m)
            s.commit()

    def buscar_por_id(self, item_id: UUID) -> Veiculo | None:
        with self._sf() as s:
            m = s.get(VeiculoModel, str(item_id))
            return self._para_dominio(m) if m else None

    def listar(self) -> list[Veiculo]:
        with self._sf() as s:
            return [self._para_dominio(m) for m in s.query(VeiculoModel).all()]

    def remover(self, item_id: UUID) -> bool:
        with self._sf() as s:
            m = s.get(VeiculoModel, str(item_id))
            if m is None:
                return False
            s.delete(m)
            s.commit()
            return True

    @staticmethod
    def _para_dominio(m: VeiculoModel) -> Veiculo:
        return Veiculo(
            placa=Placa(m.placa),
            marca=m.marca,
            modelo=m.modelo,
            ano=m.ano,
            cliente_id=UUID(m.cliente_id) if m.cliente_id else None,
            id=UUID(m.id),
        )


class RepositorioServicoSQLAlchemy(RepositorioCrud[Servico]):
    def __init__(self, session_factory: sessionmaker) -> None:
        self._sf = session_factory

    def salvar(self, item: Servico) -> None:
        with self._sf() as s:
            m = s.get(ServicoModel, str(item.id)) or ServicoModel(id=str(item.id))
            m.descricao = item.descricao
            m.preco_valor = str(item.preco.valor)
            m.moeda = item.preco.moeda
            s.add(m)
            s.commit()

    def buscar_por_id(self, item_id: UUID) -> Servico | None:
        with self._sf() as s:
            m = s.get(ServicoModel, str(item_id))
            return self._para_dominio(m) if m else None

    def listar(self) -> list[Servico]:
        with self._sf() as s:
            return [self._para_dominio(m) for m in s.query(ServicoModel).all()]

    def remover(self, item_id: UUID) -> bool:
        with self._sf() as s:
            m = s.get(ServicoModel, str(item_id))
            if m is None:
                return False
            s.delete(m)
            s.commit()
            return True

    @staticmethod
    def _para_dominio(m: ServicoModel) -> Servico:
        return Servico(m.descricao, Dinheiro(Decimal(m.preco_valor), m.moeda), UUID(m.id))


class RepositorioPecaSQLAlchemy(RepositorioCrud[Peca]):
    def __init__(self, session_factory: sessionmaker) -> None:
        self._sf = session_factory

    def salvar(self, item: Peca) -> None:
        with self._sf() as s:
            m = s.get(PecaModel, str(item.id)) or PecaModel(id=str(item.id))
            m.descricao = item.descricao
            m.preco_valor = str(item.preco.valor)
            m.moeda = item.preco.moeda
            m.estoque = item.estoque
            s.add(m)
            s.commit()

    def buscar_por_id(self, item_id: UUID) -> Peca | None:
        with self._sf() as s:
            m = s.get(PecaModel, str(item_id))
            return self._para_dominio(m) if m else None

    def listar(self) -> list[Peca]:
        with self._sf() as s:
            return [self._para_dominio(m) for m in s.query(PecaModel).all()]

    def remover(self, item_id: UUID) -> bool:
        with self._sf() as s:
            m = s.get(PecaModel, str(item_id))
            if m is None:
                return False
            s.delete(m)
            s.commit()
            return True

    @staticmethod
    def _para_dominio(m: PecaModel) -> Peca:
        return Peca(
            m.descricao, Dinheiro(Decimal(m.preco_valor), m.moeda), m.estoque, UUID(m.id)
        )
