"""Modelos ORM (SQLAlchemy) — como os dados são guardados no banco.

São separados das entidades de domínio de propósito: o domínio não conhece o
banco. O repositório faz a tradução entre os dois mundos.
Valores monetários são guardados como texto para preservar a precisão decimal.
"""
from datetime import datetime
from typing import List, Optional

from sqlalchemy import Boolean, DateTime, ForeignKey, Integer, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.infrastructure.db.base import Base


# ---------------------------------------------------------------------------
# Ordem de Serviço (agregado) e seus itens
# ---------------------------------------------------------------------------
class OrdemServicoModel(Base):
    __tablename__ = "ordens_servico"

    id: Mapped[str] = mapped_column(String(36), primary_key=True)
    cliente: Mapped[str] = mapped_column(String(14))
    veiculo: Mapped[str] = mapped_column(String(7))
    cliente_id: Mapped[Optional[str]] = mapped_column(String(36), nullable=True)
    veiculo_id: Mapped[Optional[str]] = mapped_column(String(36), nullable=True)
    moeda: Mapped[str] = mapped_column(String(3), default="BRL")
    status: Mapped[str] = mapped_column(String(30))
    aprovado: Mapped[Optional[bool]] = mapped_column(Boolean, nullable=True)
    iniciado_execucao_em: Mapped[Optional[datetime]] = mapped_column(
        DateTime, nullable=True
    )
    finalizado_em: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)

    itens_servico: Mapped[List["ItemServicoModel"]] = relationship(
        back_populates="ordem", cascade="all, delete-orphan", lazy="selectin"
    )
    itens_peca: Mapped[List["ItemPecaModel"]] = relationship(
        back_populates="ordem", cascade="all, delete-orphan", lazy="selectin"
    )


class ItemServicoModel(Base):
    __tablename__ = "itens_servico"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    ordem_id: Mapped[str] = mapped_column(ForeignKey("ordens_servico.id"))
    descricao: Mapped[str] = mapped_column(String(200))
    preco_valor: Mapped[str] = mapped_column(String(20))
    moeda: Mapped[str] = mapped_column(String(3), default="BRL")
    servico_id: Mapped[Optional[str]] = mapped_column(String(36), nullable=True)

    ordem: Mapped["OrdemServicoModel"] = relationship(back_populates="itens_servico")


class ItemPecaModel(Base):
    __tablename__ = "itens_peca"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    ordem_id: Mapped[str] = mapped_column(ForeignKey("ordens_servico.id"))
    descricao: Mapped[str] = mapped_column(String(200))
    preco_unitario_valor: Mapped[str] = mapped_column(String(20))
    moeda: Mapped[str] = mapped_column(String(3), default="BRL")
    quantidade: Mapped[int] = mapped_column(Integer)
    peca_id: Mapped[Optional[str]] = mapped_column(String(36), nullable=True)

    ordem: Mapped["OrdemServicoModel"] = relationship(back_populates="itens_peca")


# ---------------------------------------------------------------------------
# Cadastros (gestão administrativa)
# ---------------------------------------------------------------------------
class ClienteModel(Base):
    __tablename__ = "clientes"

    id: Mapped[str] = mapped_column(String(36), primary_key=True)
    documento: Mapped[str] = mapped_column(String(14))
    nome: Mapped[str] = mapped_column(String(120))


class VeiculoModel(Base):
    __tablename__ = "veiculos"

    id: Mapped[str] = mapped_column(String(36), primary_key=True)
    placa: Mapped[str] = mapped_column(String(7))
    marca: Mapped[str] = mapped_column(String(60))
    modelo: Mapped[str] = mapped_column(String(60))
    ano: Mapped[int] = mapped_column(Integer)
    cliente_id: Mapped[Optional[str]] = mapped_column(String(36), nullable=True)


class ServicoModel(Base):
    __tablename__ = "servicos"

    id: Mapped[str] = mapped_column(String(36), primary_key=True)
    descricao: Mapped[str] = mapped_column(String(200))
    preco_valor: Mapped[str] = mapped_column(String(20))
    moeda: Mapped[str] = mapped_column(String(3), default="BRL")


class PecaModel(Base):
    __tablename__ = "pecas"

    id: Mapped[str] = mapped_column(String(36), primary_key=True)
    descricao: Mapped[str] = mapped_column(String(200))
    preco_valor: Mapped[str] = mapped_column(String(20))
    moeda: Mapped[str] = mapped_column(String(3), default="BRL")
    estoque: Mapped[int] = mapped_column(Integer, default=0)
