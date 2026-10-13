"""Rotas REST dos cadastros (gestão administrativa).

CRUD de clientes, veículos, serviços e peças, mais o controle de estoque das
peças. Todas as rotas exigem autenticação (JWT).
"""
from __future__ import annotations

from uuid import UUID, uuid4

from fastapi import APIRouter, Depends, status

from app.application.casos_uso_cadastros import ControleDeEstoque, CrudCadastro
from app.domain.cadastros import Cliente, Peca, Servico, Veiculo
from app.domain.repositorios import RepositorioCrud
from app.domain.value_objects import CpfCnpj, Dinheiro, Placa
from app.interfaces.auth import usuario_atual
from app.interfaces.dependencias import (
    obter_repositorio_cliente,
    obter_repositorio_peca,
    obter_repositorio_servico,
    obter_repositorio_veiculo,
)
from app.interfaces.schemas_cadastros import (
    ClienteIn,
    ClienteOut,
    EstoqueIn,
    PecaIn,
    PecaOut,
    ServicoIn,
    ServicoOut,
    VeiculoIn,
    VeiculoOut,
)

# ------------------------------- Clientes ----------------------------------
clientes = APIRouter(
    prefix="/clientes", tags=["clientes"], dependencies=[Depends(usuario_atual)]
)


def _cliente_out(c: Cliente) -> ClienteOut:
    return ClienteOut(id=str(c.id), documento=c.documento.formatado(), nome=c.nome)


@clientes.post("", status_code=status.HTTP_201_CREATED, response_model=ClienteOut)
def criar_cliente(dados: ClienteIn, repo: RepositorioCrud = Depends(obter_repositorio_cliente)):
    cliente = Cliente(CpfCnpj(dados.documento), dados.nome)
    return _cliente_out(CrudCadastro(repo, "Cliente").criar(cliente))


@clientes.get("", response_model=list[ClienteOut])
def listar_clientes(repo: RepositorioCrud = Depends(obter_repositorio_cliente)):
    return [_cliente_out(c) for c in CrudCadastro(repo, "Cliente").listar()]


@clientes.get("/{cliente_id}", response_model=ClienteOut)
def obter_cliente(cliente_id: UUID, repo: RepositorioCrud = Depends(obter_repositorio_cliente)):
    return _cliente_out(CrudCadastro(repo, "Cliente").obter(cliente_id))


@clientes.put("/{cliente_id}", response_model=ClienteOut)
def atualizar_cliente(
    cliente_id: UUID, dados: ClienteIn, repo: RepositorioCrud = Depends(obter_repositorio_cliente)
):
    cliente = Cliente(CpfCnpj(dados.documento), dados.nome, cliente_id)
    return _cliente_out(CrudCadastro(repo, "Cliente").atualizar(cliente))


@clientes.delete("/{cliente_id}", status_code=status.HTTP_204_NO_CONTENT)
def remover_cliente(cliente_id: UUID, repo: RepositorioCrud = Depends(obter_repositorio_cliente)):
    CrudCadastro(repo, "Cliente").remover(cliente_id)


# ------------------------------- Veículos ----------------------------------
veiculos = APIRouter(
    prefix="/veiculos", tags=["veículos"], dependencies=[Depends(usuario_atual)]
)


def _veiculo_out(v: Veiculo) -> VeiculoOut:
    return VeiculoOut(
        id=str(v.id), placa=v.placa.valor, marca=v.marca, modelo=v.modelo,
        ano=v.ano, cliente_id=str(v.cliente_id) if v.cliente_id else None,
    )


@veiculos.post("", status_code=status.HTTP_201_CREATED, response_model=VeiculoOut)
def criar_veiculo(dados: VeiculoIn, repo: RepositorioCrud = Depends(obter_repositorio_veiculo)):
    veiculo = Veiculo(
        Placa(dados.placa), dados.marca, dados.modelo, dados.ano,
        UUID(dados.cliente_id) if dados.cliente_id else None,
    )
    return _veiculo_out(CrudCadastro(repo, "Veículo").criar(veiculo))


@veiculos.get("", response_model=list[VeiculoOut])
def listar_veiculos(repo: RepositorioCrud = Depends(obter_repositorio_veiculo)):
    return [_veiculo_out(v) for v in CrudCadastro(repo, "Veículo").listar()]


@veiculos.get("/{veiculo_id}", response_model=VeiculoOut)
def obter_veiculo(veiculo_id: UUID, repo: RepositorioCrud = Depends(obter_repositorio_veiculo)):
    return _veiculo_out(CrudCadastro(repo, "Veículo").obter(veiculo_id))


@veiculos.put("/{veiculo_id}", response_model=VeiculoOut)
def atualizar_veiculo(
    veiculo_id: UUID, dados: VeiculoIn, repo: RepositorioCrud = Depends(obter_repositorio_veiculo)
):
    veiculo = Veiculo(
        Placa(dados.placa), dados.marca, dados.modelo, dados.ano,
        UUID(dados.cliente_id) if dados.cliente_id else None, veiculo_id,
    )
    return _veiculo_out(CrudCadastro(repo, "Veículo").atualizar(veiculo))


@veiculos.delete("/{veiculo_id}", status_code=status.HTTP_204_NO_CONTENT)
def remover_veiculo(veiculo_id: UUID, repo: RepositorioCrud = Depends(obter_repositorio_veiculo)):
    CrudCadastro(repo, "Veículo").remover(veiculo_id)


# ------------------------------- Serviços ----------------------------------
servicos = APIRouter(
    prefix="/servicos", tags=["serviços"], dependencies=[Depends(usuario_atual)]
)


def _servico_out(s: Servico) -> ServicoOut:
    return ServicoOut(
        id=str(s.id), descricao=s.descricao,
        preco=f"{s.preco.valor:.2f}", moeda=s.preco.moeda,
    )


@servicos.post("", status_code=status.HTTP_201_CREATED, response_model=ServicoOut)
def criar_servico(dados: ServicoIn, repo: RepositorioCrud = Depends(obter_repositorio_servico)):
    servico = Servico(dados.descricao, Dinheiro(dados.preco))
    return _servico_out(CrudCadastro(repo, "Serviço").criar(servico))


@servicos.get("", response_model=list[ServicoOut])
def listar_servicos(repo: RepositorioCrud = Depends(obter_repositorio_servico)):
    return [_servico_out(s) for s in CrudCadastro(repo, "Serviço").listar()]


@servicos.get("/{servico_id}", response_model=ServicoOut)
def obter_servico(servico_id: UUID, repo: RepositorioCrud = Depends(obter_repositorio_servico)):
    return _servico_out(CrudCadastro(repo, "Serviço").obter(servico_id))


@servicos.put("/{servico_id}", response_model=ServicoOut)
def atualizar_servico(
    servico_id: UUID, dados: ServicoIn, repo: RepositorioCrud = Depends(obter_repositorio_servico)
):
    servico = Servico(dados.descricao, Dinheiro(dados.preco), servico_id)
    return _servico_out(CrudCadastro(repo, "Serviço").atualizar(servico))


@servicos.delete("/{servico_id}", status_code=status.HTTP_204_NO_CONTENT)
def remover_servico(servico_id: UUID, repo: RepositorioCrud = Depends(obter_repositorio_servico)):
    CrudCadastro(repo, "Serviço").remover(servico_id)


# -------------------------------- Peças ------------------------------------
pecas = APIRouter(
    prefix="/pecas", tags=["peças e insumos"], dependencies=[Depends(usuario_atual)]
)


def _peca_out(p: Peca) -> PecaOut:
    return PecaOut(
        id=str(p.id), descricao=p.descricao,
        preco=f"{p.preco.valor:.2f}", moeda=p.preco.moeda, estoque=p.estoque,
    )


@pecas.post("", status_code=status.HTTP_201_CREATED, response_model=PecaOut)
def criar_peca(dados: PecaIn, repo: RepositorioCrud = Depends(obter_repositorio_peca)):
    peca = Peca(dados.descricao, Dinheiro(dados.preco), dados.estoque)
    return _peca_out(CrudCadastro(repo, "Peça").criar(peca))


@pecas.get("", response_model=list[PecaOut])
def listar_pecas(repo: RepositorioCrud = Depends(obter_repositorio_peca)):
    return [_peca_out(p) for p in CrudCadastro(repo, "Peça").listar()]


@pecas.get("/{peca_id}", response_model=PecaOut)
def obter_peca(peca_id: UUID, repo: RepositorioCrud = Depends(obter_repositorio_peca)):
    return _peca_out(CrudCadastro(repo, "Peça").obter(peca_id))


@pecas.put("/{peca_id}", response_model=PecaOut)
def atualizar_peca(
    peca_id: UUID, dados: PecaIn, repo: RepositorioCrud = Depends(obter_repositorio_peca)
):
    peca = Peca(dados.descricao, Dinheiro(dados.preco), dados.estoque, peca_id)
    return _peca_out(CrudCadastro(repo, "Peça").atualizar(peca))


@pecas.delete("/{peca_id}", status_code=status.HTTP_204_NO_CONTENT)
def remover_peca(peca_id: UUID, repo: RepositorioCrud = Depends(obter_repositorio_peca)):
    CrudCadastro(repo, "Peça").remover(peca_id)


@pecas.post("/{peca_id}/estoque/entrada", response_model=PecaOut, summary="Dá entrada no estoque")
def entrada_estoque(
    peca_id: UUID, dados: EstoqueIn, repo: RepositorioCrud = Depends(obter_repositorio_peca)
):
    return _peca_out(ControleDeEstoque(repo).dar_entrada(peca_id, dados.quantidade))


@pecas.post("/{peca_id}/estoque/baixa", response_model=PecaOut, summary="Dá baixa no estoque")
def baixa_estoque(
    peca_id: UUID, dados: EstoqueIn, repo: RepositorioCrud = Depends(obter_repositorio_peca)
):
    return _peca_out(ControleDeEstoque(repo).dar_baixa(peca_id, dados.quantidade))
