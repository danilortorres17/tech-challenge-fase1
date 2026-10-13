"""Casos de uso da Ordem de Serviço (camada de aplicação).

Orquestram o fluxo: carregam o agregado pelo repositório, pedem a ele a mudança
de estado (a regra vive no domínio) e persistem o resultado. Não contêm regra
de negócio — só coordenação.
"""
from __future__ import annotations

from enum import Enum
from uuid import UUID

from app.domain.exceptions import OrdemNaoEncontrada
from app.domain.ordem_servico import OrdemServico
from app.domain.repositorios import OrdemServicoRepositorio
from app.domain.value_objects import CpfCnpj, Dinheiro, Placa


class AcaoOrdem(str, Enum):
    """Ações que avançam o status da OS, mapeadas aos métodos do agregado."""

    INICIAR_DIAGNOSTICO = "iniciar_diagnostico"
    ENVIAR_APROVACAO = "enviar_para_aprovacao"
    APROVAR = "aprovar"
    REJEITAR = "rejeitar"
    CONCLUIR = "concluir_execucao"
    ENTREGAR = "entregar"


class _CasoDeUsoDeOrdem:
    """Base: todos os casos de uso recebem o repositório por injeção."""

    def __init__(self, repositorio: OrdemServicoRepositorio) -> None:
        self._repo = repositorio

    def _carregar(self, ordem_id: UUID) -> OrdemServico:
        ordem = self._repo.buscar_por_id(ordem_id)
        if ordem is None:
            raise OrdemNaoEncontrada(f"Ordem de serviço não encontrada: {ordem_id}")
        return ordem


class CriarOrdemServico(_CasoDeUsoDeOrdem):
    def executar(self, documento_cliente: str, placa: str, moeda: str = "BRL") -> UUID:
        ordem = OrdemServico(CpfCnpj(documento_cliente), Placa(placa), moeda)
        self._repo.salvar(ordem)
        return ordem.id


class IncluirServicoNaOrdem(_CasoDeUsoDeOrdem):
    def executar(self, ordem_id: UUID, descricao: str, preco: Dinheiro) -> None:
        ordem = self._carregar(ordem_id)
        ordem.incluir_servico(descricao, preco)
        self._repo.salvar(ordem)


class IncluirPecaNaOrdem(_CasoDeUsoDeOrdem):
    def executar(
        self, ordem_id: UUID, descricao: str, preco_unitario: Dinheiro, quantidade: int
    ) -> None:
        ordem = self._carregar(ordem_id)
        ordem.incluir_peca(descricao, preco_unitario, quantidade)
        self._repo.salvar(ordem)


class AvancarStatusDaOrdem(_CasoDeUsoDeOrdem):
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
