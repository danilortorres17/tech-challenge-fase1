"""Testes do repositório em memória."""
from uuid import uuid4

from app.domain.ordem_servico import OrdemServico
from app.domain.value_objects import CpfCnpj, Placa
from app.infrastructure.repositorio_memoria import RepositorioOrdemServicoEmMemoria


def nova_os() -> OrdemServico:
    return OrdemServico(CpfCnpj("111.444.777-35"), Placa("ABC1D23"))


def test_salvar_e_buscar() -> None:
    repo = RepositorioOrdemServicoEmMemoria()
    ordem = nova_os()
    repo.salvar(ordem)
    assert repo.buscar_por_id(ordem.id) is ordem


def test_buscar_inexistente_retorna_none() -> None:
    repo = RepositorioOrdemServicoEmMemoria()
    assert repo.buscar_por_id(uuid4()) is None


def test_listar() -> None:
    repo = RepositorioOrdemServicoEmMemoria()
    repo.salvar(nova_os())
    repo.salvar(nova_os())
    assert len(repo.listar()) == 2
