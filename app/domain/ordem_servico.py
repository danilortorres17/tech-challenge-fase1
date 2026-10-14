"""Agregado Ordem de Serviço — o núcleo do domínio.

A OrdemServico é a raiz do agregado: só ela altera o próprio estado. Quem está
de fora lê (status, orçamento) ou solicita uma mudança por um de seus métodos,
que validam as regras de negócio antes de mudar qualquer coisa.
Pode referenciar o cliente e o veículo cadastrados (por id).
"""
from __future__ import annotations

from datetime import datetime, timezone
from uuid import UUID, uuid4

from app.domain.exceptions import (
    OperacaoInvalida,
    RegistroNaoEncontrado,
    TransicaoInvalida,
)
from app.domain.itens import ItemPeca, ItemServico
from app.domain.status_os import StatusOS, pode_transicionar
from app.domain.value_objects import CpfCnpj, Dinheiro, Placa

_STATUS_EDITAVEIS = (StatusOS.RECEBIDA, StatusOS.EM_DIAGNOSTICO)


def _agora() -> datetime:
    return datetime.now(timezone.utc)


class OrdemServico:
    """Ordem de serviço de uma oficina mecânica."""

    def __init__(
        self,
        cliente: CpfCnpj,
        veiculo: Placa,
        moeda: str = "BRL",
        id: UUID | None = None,
        cliente_id: UUID | None = None,
        veiculo_id: UUID | None = None,
    ) -> None:
        self.id = id or uuid4()
        self.cliente = cliente
        self.veiculo = veiculo
        self.cliente_id = cliente_id
        self.veiculo_id = veiculo_id
        self._moeda = moeda
        self._itens_servico: list[ItemServico] = []
        self._itens_peca: list[ItemPeca] = []
        self._status: StatusOS = StatusOS.RECEBIDA
        self._aprovado: bool | None = None
        self._iniciado_execucao_em: datetime | None = None
        self._finalizado_em: datetime | None = None

    @classmethod
    def reconstituir(
        cls,
        id: UUID,
        cliente: CpfCnpj,
        veiculo: Placa,
        status: StatusOS,
        aprovado: bool | None,
        itens_servico: list[ItemServico],
        itens_peca: list[ItemPeca],
        moeda: str = "BRL",
        iniciado_execucao_em: datetime | None = None,
        finalizado_em: datetime | None = None,
        cliente_id: UUID | None = None,
        veiculo_id: UUID | None = None,
    ) -> "OrdemServico":
        """Reconstrói uma OS a partir de um estado já válido (vindo do banco)."""
        ordem = cls(cliente, veiculo, moeda, id=id, cliente_id=cliente_id, veiculo_id=veiculo_id)
        ordem._status = status
        ordem._aprovado = aprovado
        ordem._itens_servico = list(itens_servico)
        ordem._itens_peca = list(itens_peca)
        ordem._iniciado_execucao_em = iniciado_execucao_em
        ordem._finalizado_em = finalizado_em
        return ordem

    # --- leitura ---
    @property
    def moeda(self) -> str:
        return self._moeda

    @property
    def status(self) -> StatusOS:
        return self._status

    @property
    def aprovado(self) -> bool | None:
        return self._aprovado

    @property
    def iniciado_execucao_em(self) -> datetime | None:
        return self._iniciado_execucao_em

    @property
    def finalizado_em(self) -> datetime | None:
        return self._finalizado_em

    @property
    def duracao_execucao_segundos(self) -> float | None:
        if self._iniciado_execucao_em is None or self._finalizado_em is None:
            return None
        return (self._finalizado_em - self._iniciado_execucao_em).total_seconds()

    @property
    def itens_servico(self) -> tuple[ItemServico, ...]:
        return tuple(self._itens_servico)

    @property
    def itens_peca(self) -> tuple[ItemPeca, ...]:
        return tuple(self._itens_peca)

    # --- composição do orçamento ---
    def incluir_servico(
        self, descricao: str, preco: Dinheiro, servico_id: UUID | None = None
    ) -> None:
        self._exige_status_editavel()
        self._itens_servico.append(ItemServico(descricao, preco, servico_id))

    def incluir_peca(
        self,
        descricao: str,
        preco_unitario: Dinheiro,
        quantidade: int,
        peca_id: UUID | None = None,
    ) -> None:
        self._exige_status_editavel()
        self._itens_peca.append(ItemPeca(descricao, preco_unitario, quantidade, peca_id))

    def remover_servico(self, servico_id: UUID) -> None:
        self._exige_status_editavel()
        for i, item in enumerate(self._itens_servico):
            if item.servico_id == servico_id:
                del self._itens_servico[i]
                return
        raise RegistroNaoEncontrado(f"Serviço não consta nesta OS: {servico_id}")

    def remover_peca(self, peca_id: UUID) -> None:
        self._exige_status_editavel()
        for i, item in enumerate(self._itens_peca):
            if item.peca_id == peca_id:
                del self._itens_peca[i]
                return
        raise RegistroNaoEncontrado(f"Peça não consta nesta OS: {peca_id}")

    def calcular_orcamento(self) -> Dinheiro:
        total = Dinheiro.zero(self._moeda)
        for servico in self._itens_servico:
            total = total.somar(servico.preco)
        for peca in self._itens_peca:
            total = total.somar(peca.subtotal())
        return total

    # --- transições de status (fluxo do negócio) ---
    def iniciar_diagnostico(self) -> None:
        self._mudar_status(StatusOS.EM_DIAGNOSTICO)

    def enviar_para_aprovacao(self) -> None:
        if not self._itens_servico and not self._itens_peca:
            raise OperacaoInvalida(
                "Não é possível enviar um orçamento vazio para aprovação."
            )
        self._mudar_status(StatusOS.AGUARDANDO_APROVACAO)

    def aprovar(self) -> None:
        self._mudar_status(StatusOS.EM_EXECUCAO)
        self._aprovado = True
        self._iniciado_execucao_em = _agora()

    def rejeitar(self) -> None:
        """Cliente recusa o orçamento: a OS vai para o status Rejeitada."""
        self._mudar_status(StatusOS.REJEITADA)
        self._aprovado = False

    def reabrir_diagnostico(self) -> None:
        """Reabre uma OS rejeitada para ajustar o orçamento e reenviar."""
        self._mudar_status(StatusOS.EM_DIAGNOSTICO)
        self._aprovado = None

    def concluir_execucao(self) -> None:
        self._mudar_status(StatusOS.FINALIZADA)
        self._finalizado_em = _agora()

    def entregar(self) -> None:
        self._mudar_status(StatusOS.ENTREGUE)

    # --- regras internas ---
    def _mudar_status(self, novo: StatusOS) -> None:
        if not pode_transicionar(self._status, novo):
            raise TransicaoInvalida(
                f"Transição inválida: {self._status.value} → {novo.value}."
            )
        self._status = novo

    def _exige_status_editavel(self) -> None:
        if self._status not in _STATUS_EDITAVEIS:
            raise OperacaoInvalida(
                f"Não é possível alterar itens com a OS em '{self._status.value}'."
            )
