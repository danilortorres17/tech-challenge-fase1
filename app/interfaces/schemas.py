"""Schemas Pydantic - o contrato de entrada e saída da API.

Separados das entidades de domínio: traduzem JSON <-> tipos do domínio.
Valores monetários trafegam como texto com 2 casas, para não perder precisão.
"""
from __future__ import annotations

from decimal import Decimal
from uuid import UUID

from pydantic import BaseModel, Field

from app.application.casos_uso import AcaoOrdem


# --- entrada ---
class CriarOrdemIn(BaseModel):
    cliente_id: UUID = Field(description="id de um cliente cadastrado")
    veiculo_id: UUID = Field(description="id de um veículo cadastrado")
    moeda: str = "BRL"


class IncluirServicoIn(BaseModel):
    servico_id: UUID = Field(description="id de um serviço do catálogo")


class IncluirPecaIn(BaseModel):
    peca_id: UUID = Field(description="id de uma peça do catálogo")
    quantidade: int = Field(examples=[2], gt=0)


class AvancarStatusIn(BaseModel):
    acao: AcaoOrdem


# --- saída ---
class ItemServicoOut(BaseModel):
    descricao: str
    preco: str
    moeda: str


class ItemPecaOut(BaseModel):
    descricao: str
    preco_unitario: str
    moeda: str
    quantidade: int
    subtotal: str


class OrdemServicoOut(BaseModel):
    id: str
    cliente: str
    veiculo: str
    cliente_id: str | None
    veiculo_id: str | None
    status: str
    aprovado: bool | None
    moeda: str
    orcamento: str
    itens_servico: list[ItemServicoOut]
    itens_peca: list[ItemPecaOut]


class TempoMedioOut(BaseModel):
    amostras: int
    tempo_medio_segundos: float
    tempo_medio_formatado: str
