"""Rotas REST da Ordem de Serviço.

Camada de interface: traduz requisições HTTP em chamadas de casos de uso e
monta as respostas. Não contém regra de negócio.

As rotas administrativas exigem autenticação (JWT). A consulta de andamento de
uma OS é pública — é o acompanhamento do cliente.
"""
from __future__ import annotations

from uuid import UUID

from fastapi import APIRouter, Depends, status

from app.application.casos_uso import (
    AvancarStatusDaOrdem,
    ConsultarOrdemServico,
    CriarOrdemServico,
    IncluirPecaNaOrdem,
    IncluirServicoNaOrdem,
    ListarOrdensServico,
)
from app.domain.ordem_servico import OrdemServico
from app.domain.repositorios import OrdemServicoRepositorio
from app.domain.value_objects import Dinheiro
from app.interfaces.auth import usuario_atual
from app.interfaces.dependencias import obter_repositorio
from app.interfaces.schemas import (
    AvancarStatusIn,
    CriarOrdemIn,
    IncluirPecaIn,
    IncluirServicoIn,
    ItemPecaOut,
    ItemServicoOut,
    OrdemServicoOut,
)

router = APIRouter(prefix="/ordens-servico", tags=["ordens de serviço"])


def _para_saida(ordem: OrdemServico) -> OrdemServicoOut:
    return OrdemServicoOut(
        id=str(ordem.id),
        cliente=ordem.cliente.formatado(),
        veiculo=ordem.veiculo.valor,
        status=ordem.status.value,
        aprovado=ordem.aprovado,
        moeda=ordem.moeda,
        orcamento=f"{ordem.calcular_orcamento().valor:.2f}",
        itens_servico=[
            ItemServicoOut(
                descricao=s.descricao, preco=f"{s.preco.valor:.2f}", moeda=s.preco.moeda
            )
            for s in ordem.itens_servico
        ],
        itens_peca=[
            ItemPecaOut(
                descricao=p.descricao,
                preco_unitario=f"{p.preco_unitario.valor:.2f}",
                moeda=p.preco_unitario.moeda,
                quantidade=p.quantidade,
                subtotal=f"{p.subtotal().valor:.2f}",
            )
            for p in ordem.itens_peca
        ],
    )


@router.post(
    "", status_code=status.HTTP_201_CREATED, response_model=OrdemServicoOut,
    summary="Abre uma nova ordem de serviço (requer autenticação)",
)
def criar(
    dados: CriarOrdemIn,
    repo: OrdemServicoRepositorio = Depends(obter_repositorio),
    usuario: str = Depends(usuario_atual),
):
    ordem_id = CriarOrdemServico(repo).executar(
        dados.documento_cliente, dados.placa, dados.moeda
    )
    return _para_saida(ConsultarOrdemServico(repo).executar(ordem_id))


@router.get(
    "", response_model=list[OrdemServicoOut],
    summary="Lista as ordens de serviço (requer autenticação)",
)
def listar(
    repo: OrdemServicoRepositorio = Depends(obter_repositorio),
    usuario: str = Depends(usuario_atual),
):
    return [_para_saida(o) for o in ListarOrdensServico(repo).executar()]


@router.get(
    "/{ordem_id}", response_model=OrdemServicoOut,
    summary="Consulta o andamento de uma ordem de serviço (público)",
)
def consultar(ordem_id: UUID, repo: OrdemServicoRepositorio = Depends(obter_repositorio)):
    return _para_saida(ConsultarOrdemServico(repo).executar(ordem_id))


@router.post(
    "/{ordem_id}/servicos", response_model=OrdemServicoOut,
    summary="Inclui um serviço na ordem (requer autenticação)",
)
def incluir_servico(
    ordem_id: UUID,
    dados: IncluirServicoIn,
    repo: OrdemServicoRepositorio = Depends(obter_repositorio),
    usuario: str = Depends(usuario_atual),
):
    IncluirServicoNaOrdem(repo).executar(ordem_id, dados.descricao, Dinheiro(dados.preco))
    return _para_saida(ConsultarOrdemServico(repo).executar(ordem_id))


@router.post(
    "/{ordem_id}/pecas", response_model=OrdemServicoOut,
    summary="Inclui uma peça/insumo na ordem (requer autenticação)",
)
def incluir_peca(
    ordem_id: UUID,
    dados: IncluirPecaIn,
    repo: OrdemServicoRepositorio = Depends(obter_repositorio),
    usuario: str = Depends(usuario_atual),
):
    IncluirPecaNaOrdem(repo).executar(
        ordem_id, dados.descricao, Dinheiro(dados.preco_unitario), dados.quantidade
    )
    return _para_saida(ConsultarOrdemServico(repo).executar(ordem_id))


@router.post(
    "/{ordem_id}/status", response_model=OrdemServicoOut,
    summary="Avança o status da ordem (requer autenticação)",
)
def avancar_status(
    ordem_id: UUID,
    dados: AvancarStatusIn,
    repo: OrdemServicoRepositorio = Depends(obter_repositorio),
    usuario: str = Depends(usuario_atual),
):
    ordem = AvancarStatusDaOrdem(repo).executar(ordem_id, dados.acao)
    return _para_saida(ordem)
