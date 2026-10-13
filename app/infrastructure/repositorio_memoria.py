"""Implementação em memória do repositório de Ordem de Serviço.

Adaptador de infraestrutura usado para desenvolvimento e testes, enquanto o
banco de dados real (etapa 5) não entra. Guarda tudo num dicionário.
"""
from __future__ import annotations

from uuid import UUID

from app.domain.ordem_servico import OrdemServico
from app.domain.repositorios import OrdemServicoRepositorio


class RepositorioOrdemServicoEmMemoria(OrdemServicoRepositorio):
    def __init__(self) -> None:
        self._dados: dict[UUID, OrdemServico] = {}

    def salvar(self, ordem: OrdemServico) -> None:
        self._dados[ordem.id] = ordem

    def buscar_por_id(self, ordem_id: UUID) -> OrdemServico | None:
        return self._dados.get(ordem_id)

    def listar(self) -> list[OrdemServico]:
        return list(self._dados.values())
