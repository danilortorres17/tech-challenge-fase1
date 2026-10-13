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
    AcaoOrdem,
    AprovarOrdemServico,
    AvancarStatusDaOrdem,
    ConsultarOrdemServico,
    CriarOrdemServico,
    IncluirPecaNaOrdem,
    IncluirServicoNaOrdem,
    ListarOrdensServico,
)
from app.domain.cadastros import Cliente, Peca, Servico, Veiculo
from app.domain.ordem_servico import OrdemServico
from app.domain.repositorios import OrdemServicoRepositorio, RepositorioCrud
from app.interfaces.auth import usuario_atual
from app.interfaces.dependencias import (
    obter_repositorio,
    obter_repositorio_cliente,
    obter_repositorio_peca,
    obter_repositorio_servico,
    obter_repositorio_veiculo,
)
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
        cliente_id=str(ordem.cliente_id) if ordem.cliente_id else None,
        veiculo_id=str(ordem.veiculo_id) if ordem.veiculo_id else None,
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
    summary="Abre uma OS para um cliente e veículo cadastrados (requer autenticação)",
)
def criar(
    dados: CriarOrdemIn,
    repo: OrdemServicoRepositorio = Depends(obter_repositorio),
    repo_cliente: RepositorioCrud[Cliente] = Depends(obter_repositorio_cliente),
    repo_veiculo: RepositorioCrud[Veiculo] = Depends(obter_repositorio_veiculo),
    usuario: str = Depends(usuario_atual),
):
    ordem_id = CriarOrdemServico(repo, repo_cliente, repo_veiculo).executar(
        UUID(dados.cliente_id), UUID(dados.veiculo_id), dados.moeda
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
    summary="Inclui um serviço do catálogo na ordem (requer autenticação)",
)
def incluir_servico(
    ordem_id: UUID,
    dados: IncluirServicoIn,
    repo: OrdemServicoRepositorio = Depends(obter_repositorio),
    repo_servico: RepositorioCrud[Servico] = Depends(obter_repositorio_servico),
    usuario: str = Depends(usuario_atual),
):
    IncluirServicoNaOrdem(repo, repo_servico).executar(ordem_id, UUID(dados.servico_id))
    return _para_saida(ConsultarOrdemServico(repo).executar(ordem_id))


@router.post(
    "/{ordem_id}/pecas", response_model=OrdemServicoOut,
    summary="Inclui uma peça do catálogo na ordem (requer autenticação)",
)
def incluir_peca(
    ordem_id: UUID,
    dados: IncluirPecaIn,
    repo: OrdemServicoRepositorio = Depends(obter_repositorio),
    repo_peca: RepositorioCrud[Peca] = Depends(obter_repositorio_peca),
    usuario: str = Depends(usuario_atual),
):
    IncluirPecaNaOrdem(repo, repo_peca).executar(
        ordem_id, UUID(dados.peca_id), dados.quantidade
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
    repo_peca: RepositorioCrud[Peca] = Depends(obter_repositorio_peca),
    usuario: str = Depends(usuario_atual),
):
    if dados.acao == AcaoOrdem.APROVAR:
        # Aprovar dá baixa no estoque das peças referenciadas.
        ordem = AprovarOrdemServico(repo, repo_peca).executar(ordem_id)
    else:
        ordem = AvancarStatusDaOrdem(repo).executar(ordem_id, dados.acao)
    return _para_saida(ordem)
