"""Casos de uso da Ordem de Serviço (camada de aplicação).

Orquestram o fluxo: carregam o agregado pelo repositório, pedem a ele a mudança
de estado (a regra vive no domínio) e persistem o resultado. A OS referencia o
cliente, o veículo, os serviços e as peças cadastrados (por id); a aprovação dá
baixa automática no estoque das peças.
"""
from __future__ import annotations

from collections import defaultdict
from enum import Enum
from uuid import UUID

from app.domain.cadastros import Cliente, Peca, Servico, Veiculo
from app.domain.exceptions import OrdemNaoEncontrada, RegistroNaoEncontrado
from app.domain.ordem_servico import OrdemServico
from app.domain.repositorios import OrdemServicoRepositorio, RepositorioCrud


class AcaoOrdem(str, Enum):
    """Ações que avançam o status da OS, mapeadas aos métodos do agregado."""

    INICIAR_DIAGNOSTICO = "iniciar_diagnostico"
    ENVIAR_APROVACAO = "enviar_para_aprovacao"
    APROVAR = "aprovar"
    REJEITAR = "rejeitar"
    CONCLUIR = "concluir_execucao"
    ENTREGAR = "entregar"


class _CasoDeUsoDeOrdem:
    """Base: casos de uso que só precisam do repositório de OS."""

    def __init__(self, repositorio: OrdemServicoRepositorio) -> None:
        self._repo = repositorio

    def _carregar(self, ordem_id: UUID) -> OrdemServico:
        ordem = self._repo.buscar_por_id(ordem_id)
        if ordem is None:
            raise OrdemNaoEncontrada(f"Ordem de serviço não encontrada: {ordem_id}")
        return ordem


class CriarOrdemServico:
    """Cria a OS referenciando um cliente e um veículo já cadastrados."""

    def __init__(
        self,
        repositorio: OrdemServicoRepositorio,
        repo_cliente: RepositorioCrud[Cliente],
        repo_veiculo: RepositorioCrud[Veiculo],
    ) -> None:
        self._repo = repositorio
        self._repo_cliente = repo_cliente
        self._repo_veiculo = repo_veiculo

    def executar(self, cliente_id: UUID, veiculo_id: UUID, moeda: str = "BRL") -> UUID:
        cliente = self._repo_cliente.buscar_por_id(cliente_id)
        if cliente is None:
            raise RegistroNaoEncontrado(f"Cliente não encontrado: {cliente_id}")
        veiculo = self._repo_veiculo.buscar_por_id(veiculo_id)
        if veiculo is None:
            raise RegistroNaoEncontrado(f"Veículo não encontrado: {veiculo_id}")
        ordem = OrdemServico(
            cliente.documento, veiculo.placa, moeda,
            cliente_id=cliente_id, veiculo_id=veiculo_id,
        )
        self._repo.salvar(ordem)
        return ordem.id


class IncluirServicoNaOrdem(_CasoDeUsoDeOrdem):
    """Inclui um serviço do catálogo na OS."""

    def __init__(
        self, repositorio: OrdemServicoRepositorio, repo_servico: RepositorioCrud[Servico]
    ) -> None:
        super().__init__(repositorio)
        self._repo_servico = repo_servico

    def executar(self, ordem_id: UUID, servico_id: UUID) -> None:
        ordem = self._carregar(ordem_id)
        servico = self._repo_servico.buscar_por_id(servico_id)
        if servico is None:
            raise RegistroNaoEncontrado(f"Serviço não encontrado: {servico_id}")
        ordem.incluir_servico(servico.descricao, servico.preco, servico_id=servico_id)
        self._repo.salvar(ordem)


class IncluirPecaNaOrdem(_CasoDeUsoDeOrdem):
    """Inclui uma peça do catálogo na OS (sem baixar estoque ainda)."""

    def __init__(
        self, repositorio: OrdemServicoRepositorio, repo_peca: RepositorioCrud[Peca]
    ) -> None:
        super().__init__(repositorio)
        self._repo_peca = repo_peca

    def executar(self, ordem_id: UUID, peca_id: UUID, quantidade: int) -> None:
        ordem = self._carregar(ordem_id)
        peca = self._repo_peca.buscar_por_id(peca_id)
        if peca is None:
            raise RegistroNaoEncontrado(f"Peça não encontrada: {peca_id}")
        ordem.incluir_peca(peca.descricao, peca.preco, quantidade, peca_id=peca_id)
        self._repo.salvar(ordem)


class AprovarOrdemServico(_CasoDeUsoDeOrdem):
    """Aprova o orçamento e dá baixa no estoque das peças referenciadas.

    Verifica o estoque de TODAS as peças antes de aplicar qualquer baixa
    (check-then-apply): se faltar saldo de qualquer uma, nada é alterado.
    """

    def __init__(
        self, repositorio: OrdemServicoRepositorio, repo_peca: RepositorioCrud[Peca]
    ) -> None:
        super().__init__(repositorio)
        self._repo_peca = repo_peca

    def executar(self, ordem_id: UUID) -> OrdemServico:
        ordem = self._carregar(ordem_id)

        # Agrega a quantidade necessária por peça (evita baixa dupla).
        necessario: dict[UUID, int] = defaultdict(int)
        for item in ordem.itens_peca:
            if item.peca_id is not None:
                necessario[item.peca_id] += item.quantidade

        # Carrega e dá baixa em memória (lança EstoqueInsuficiente se faltar).
        pecas_atualizadas: list[Peca] = []
        for peca_id, quantidade in necessario.items():
            peca = self._repo_peca.buscar_por_id(peca_id)
            if peca is None:
                raise RegistroNaoEncontrado(f"Peça não encontrada: {peca_id}")
            peca.baixar_estoque(quantidade)
            pecas_atualizadas.append(peca)

        # Só persiste depois que todas as baixas foram validadas.
        for peca in pecas_atualizadas:
            self._repo_peca.salvar(peca)
        ordem.aprovar()
        self._repo.salvar(ordem)
        return ordem


class AvancarStatusDaOrdem(_CasoDeUsoDeOrdem):
    """Avança o status da OS para as ações que não envolvem estoque."""

    def executar(self, ordem_id: UUID, acao: AcaoOrdem) -> OrdemServico:
        ordem = self._carregar(ordem_id)
        getattr(ordem, acao.value)()
        self._repo.salvar(ordem)
        return ordem


class ConsultarOrdemServico(_CasoDeUsoDeOrdem):
    def executar(self, ordem_id: UUID) -> OrdemServico:
        return self._carregar(ordem_id)


class ListarOrdensServico(_CasoDeUsoDeOrdem):
    def executar(self) -> list[OrdemServico]:
        return self._repo.listar()


class CalcularTempoMedioExecucao(_CasoDeUsoDeOrdem):
    """Tempo médio de execução das OS que já passaram por execução e finalização."""

    def executar(self) -> dict[str, float | int]:
        duracoes = [
            o.duracao_execucao_segundos
            for o in self._repo.listar()
            if o.duracao_execucao_segundos is not None
        ]
        if not duracoes:
            return {"amostras": 0, "tempo_medio_segundos": 0.0}
        return {
            "amostras": len(duracoes),
            "tempo_medio_segundos": sum(duracoes) / len(duracoes),
        }
