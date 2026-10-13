"""Modelos ORM (SQLAlchemy) — como os dados são guardados no banco.

São separados das entidades de domínio de propósito: o domínio não conhece o
banco. O repositório faz a tradução entre os dois mundos.
Valores monetários são guardados como texto para preservar a precisão decimal.
"""
from typing import List, Optional

from sqlalchemy import Boolean, ForeignKey, Integer, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.infrastructure.db.base import Base


class OrdemServicoModel(Base):
    __tablename__ = "ordens_servico"

    id: Mapped[str] = mapped_column(String(36), primary_key=True)
    cliente: Mapped[str] = mapped_column(String(14))
    veiculo: Mapped[str] = mapped_column(String(7))
    moeda: Mapped[str] = mapped_column(String(3), default="BRL")
    status: Mapped[str] = mapped_column(String(30))
    aprovado: Mapped[Optional[bool]] = mapped_column(Boolean, nullable=True)

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

    ordem: Mapped["OrdemServicoModel"] = relationship(back_populates="itens_servico")


class ItemPecaModel(Base):
    __tablename__ = "itens_peca"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    ordem_id: Mapped[str] = mapped_column(ForeignKey("ordens_servico.id"))
    descricao: Mapped[str] = mapped_column(String(200))
    preco_unitario_valor: Mapped[str] = mapped_column(String(20))
    moeda: Mapped[str] = mapped_column(String(3), default="BRL")
    quantidade: Mapped[int] = mapped_column(Integer)

    ordem: Mapped["OrdemServicoModel"] = relationship(back_populates="itens_peca")
