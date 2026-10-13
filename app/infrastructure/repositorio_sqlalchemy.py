"""Repositório de Ordem de Serviço com SQLAlchemy.

Implementa a mesma porta do domínio (OrdemServicoRepositorio), então domínio e
casos de uso não percebem a troca do repositório em memória por este.
Faz a tradução entre o agregado de domínio e os modelos ORM.
"""
from __future__ import annotations

from decimal import Decimal
from uuid import UUID

from sqlalchemy.orm import sessionmaker

from app.domain.itens import ItemPeca, ItemServico
from app.domain.ordem_servico import OrdemServico
from app.domain.repositorios import OrdemServicoRepositorio
from app.domain.status_os import StatusOS
from app.domain.value_objects import CpfCnpj, Dinheiro, Placa
from app.infrastructure.db.models import (
    ItemPecaModel,
    ItemServicoModel,
    OrdemServicoModel,
)


class RepositorioOrdemServicoSQLAlchemy(OrdemServicoRepositorio):
    def __init__(self, session_factory: sessionmaker) -> None:
        self._session_factory = session_factory

    def salvar(self, ordem: OrdemServico) -> None:
        with self._session_factory() as session:
            model = session.get(OrdemServicoModel, str(ordem.id))
            if model is None:
                model = OrdemServicoModel(id=str(ordem.id))
                session.add(model)
            model.cliente = ordem.cliente.valor
            model.veiculo = ordem.veiculo.valor
            model.cliente_id = str(ordem.cliente_id) if ordem.cliente_id else None
            model.veiculo_id = str(ordem.veiculo_id) if ordem.veiculo_id else None
            model.moeda = ordem.moeda
            model.status = ordem.status.value
            model.aprovado = ordem.aprovado
            model.iniciado_execucao_em = ordem.iniciado_execucao_em
            model.finalizado_em = ordem.finalizado_em
            model.itens_servico = [
                ItemServicoModel(
                    descricao=s.descricao,
                    preco_valor=str(s.preco.valor),
                    moeda=s.preco.moeda,
                    servico_id=str(s.servico_id) if s.servico_id else None,
                )
                for s in ordem.itens_servico
            ]
            model.itens_peca = [
                ItemPecaModel(
                    descricao=p.descricao,
                    preco_unitario_valor=str(p.preco_unitario.valor),
                    moeda=p.preco_unitario.moeda,
                    quantidade=p.quantidade,
                    peca_id=str(p.peca_id) if p.peca_id else None,
                )
                for p in ordem.itens_peca
            ]
            session.commit()

    def buscar_por_id(self, ordem_id: UUID) -> OrdemServico | None:
        with self._session_factory() as session:
            model = session.get(OrdemServicoModel, str(ordem_id))
            return self._para_dominio(model) if model else None

    def listar(self) -> list[OrdemServico]:
        with self._session_factory() as session:
            return [self._para_dominio(m) for m in session.query(OrdemServicoModel).all()]

    @staticmethod
    def _para_dominio(model: OrdemServicoModel) -> OrdemServico:
        itens_servico = [
            ItemServico(
                s.descricao,
                Dinheiro(Decimal(s.preco_valor), s.moeda),
                UUID(s.servico_id) if s.servico_id else None,
            )
            for s in model.itens_servico
        ]
        itens_peca = [
            ItemPeca(
                p.descricao,
                Dinheiro(Decimal(p.preco_unitario_valor), p.moeda),
                p.quantidade,
                UUID(p.peca_id) if p.peca_id else None,
            )
            for p in model.itens_peca
        ]
        return OrdemServico.reconstituir(
            id=UUID(model.id),
            cliente=CpfCnpj(model.cliente),
            veiculo=Placa(model.veiculo),
            status=StatusOS(model.status),
            aprovado=model.aprovado,
            itens_servico=itens_servico,
            itens_peca=itens_peca,
            moeda=model.moeda,
            iniciado_execucao_em=model.iniciado_execucao_em,
            finalizado_em=model.finalizado_em,
            cliente_id=UUID(model.cliente_id) if model.cliente_id else None,
            veiculo_id=UUID(model.veiculo_id) if model.veiculo_id else None,
        )
