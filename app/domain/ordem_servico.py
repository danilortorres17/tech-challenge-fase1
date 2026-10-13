"""Agregado Ordem de Serviço — o núcleo do domínio.

A OrdemServico é a raiz do agregado: só ela altera o próprio estado. Quem está
de fora lê (status, orçamento) ou solicita uma mudança por um de seus métodos,
que validam as regras de negócio antes de mudar qualquer coisa.
"""
from __future__ import annotations

from uuid import UUID, uuid4

from app.domain.exceptions import OperacaoInvalida, TransicaoInvalida
from app.domain.itens import ItemPeca, ItemServico
from app.domain.status_os import StatusOS, pode_transicionar
from app.domain.value_objects import CpfCnpj, Dinheiro, Placa

# Status em que ainda é permitido alterar os itens da OS.
_STATUS_EDITAVEIS = (StatusOS.RECEBIDA, StatusOS.EM_DIAGNOSTICO)


class OrdemServico:
    """Ordem de serviço de uma oficina mecânica."""

    def __init__(
        self,
        cliente: CpfCnpj,
        veiculo: Placa,
        moeda: str = "BRL",
        id: UUID | None = None,
    ) -> None:
        self.id = id or uuid4()
        self.cliente = cliente
        self.veiculo = veiculo
        self._moeda = moeda
        self._itens_servico: list[ItemServico] = []
        self._itens_peca: list[ItemPeca] = []
        self._status: StatusOS = StatusOS.RECEBIDA
        self._aprovado: bool | None = None

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
    ) -> "OrdemServico":
        """Reconstrói uma OS a partir de um estado já válido (vindo do banco).

        Diferente do construtor + métodos, aqui não se replica o fluxo: o estado
        persistido já é válido, então ele é restaurado diretamente.
        """
        ordem = cls(cliente, veiculo, moeda, id=id)
        ordem._status = status
        ordem._aprovado = aprovado
        ordem._itens_servico = list(itens_servico)
        ordem._itens_peca = list(itens_peca)
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
    def itens_servico(self) -> tuple[ItemServico, ...]:
        return tuple(self._itens_servico)

    @property
    def itens_peca(self) -> tuple[ItemPeca, ...]:
        return tuple(self._itens_peca)

    # --- composição do orçamento ---
    def incluir_servico(self, descricao: str, preco: Dinheiro) -> None:
        self._exige_status_editavel()
        self._itens_servico.append(ItemServico(descricao, preco))

    def incluir_peca(
        self, descricao: str, preco_unitario: Dinheiro, quantidade: int
    ) -> None:
        self._exige_status_editavel()
        self._itens_peca.append(ItemPeca(descricao, preco_unitario, quantidade))

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

    def rejeitar(self) -> None:
        if self._status != StatusOS.AGUARDANDO_APROVACAO:
            raise TransicaoInvalida(
                "Só é possível rejeitar um orçamento que está aguardando aprovação."
            )
        self._aprovado = False

    def concluir_execucao(self) -> None:
        self._mudar_status(StatusOS.FINALIZADA)

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
