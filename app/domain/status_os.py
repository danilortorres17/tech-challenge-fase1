"""Status da Ordem de Serviço e as transições permitidas.

A sequência é fixa; cada status só pode avançar para o próximo. Pular etapa
é uma transição inválida (regra de negócio da Aula de DDD).
"""
from __future__ import annotations

from enum import Enum


class StatusOS(str, Enum):
    RECEBIDA = "Recebida"
    EM_DIAGNOSTICO = "Em diagnóstico"
    AGUARDANDO_APROVACAO = "Aguardando aprovação"
    EM_EXECUCAO = "Em execução"
    FINALIZADA = "Finalizada"
    ENTREGUE = "Entregue"
    REJEITADA = "Rejeitada"


# Para cada status, o conjunto de status para os quais ele pode avançar.
# Observações do fluxo:
# - Aguardando aprovação pode seguir para Em execução (aprovado) OU Rejeitada.
# - Rejeitada pode voltar para Em diagnóstico (oficina ajusta o orçamento e reenvia).
TRANSICOES: dict[StatusOS, set[StatusOS]] = {
    StatusOS.RECEBIDA: {StatusOS.EM_DIAGNOSTICO},
    StatusOS.EM_DIAGNOSTICO: {StatusOS.AGUARDANDO_APROVACAO},
    StatusOS.AGUARDANDO_APROVACAO: {StatusOS.EM_EXECUCAO, StatusOS.REJEITADA},
    StatusOS.EM_EXECUCAO: {StatusOS.FINALIZADA},
    StatusOS.FINALIZADA: {StatusOS.ENTREGUE},
    StatusOS.ENTREGUE: set(),
    StatusOS.REJEITADA: {StatusOS.EM_DIAGNOSTICO},
}


def pode_transicionar(de: StatusOS, para: StatusOS) -> bool:
    """Indica se a mudança de status `de` → `para` é permitida."""
    return para in TRANSICOES[de]
