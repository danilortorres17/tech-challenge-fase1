"""Exceções da camada de domínio.

Todas herdam de ErroDeDominio, para que as camadas de cima possam tratar
erros de negócio de forma uniforme (ex.: traduzir para HTTP na interface).
"""


class ErroDeDominio(Exception):
    """Erro base de qualquer regra de negócio violada."""


class DocumentoInvalido(ErroDeDominio):
    """CPF ou CNPJ inválido."""


class PlacaInvalida(ErroDeDominio):
    """Placa de veículo em formato inválido."""


class ValorMonetarioInvalido(ErroDeDominio):
    """Valor monetário inválido (ex.: negativo)."""


class MoedaIncompativel(ErroDeDominio):
    """Operação entre valores de moedas diferentes."""


class QuantidadeInvalida(ErroDeDominio):
    """Quantidade de item inválida (ex.: zero ou negativa)."""


class TransicaoInvalida(ErroDeDominio):
    """Mudança de status da Ordem de Serviço que viola o fluxo permitido."""


class OperacaoInvalida(ErroDeDominio):
    """Operação não permitida para o estado atual da Ordem de Serviço."""


class OrdemNaoEncontrada(ErroDeDominio):
    """Ordem de Serviço não localizada pelo identificador informado."""
