"""Schemas Pydantic — o contrato de entrada e saída da API.

Separados das entidades de domínio: traduzem JSON <-> tipos do domínio.
Valores monetários trafegam como texto com 2 casas, para não perder precisão.
"""
from __future__ import annotations

from decimal import Decimal

from pydantic import BaseModel, Field

from app.application.casos_uso import AcaoOrdem


# --- entrada ---
class CriarOrdemIn(BaseModel):
    documento_cliente: str = Field(examples=["111.444.777-35"])
    placa: str = Field(examples=["ABC1D23"])
    moeda: str = "BRL"


class IncluirServicoIn(BaseModel):
    descricao: str = Field(examples=["Troca de óleo"])
    preco: Decimal = Field(examples=["120.00"])


class IncluirPecaIn(BaseModel):
    descricao: str = Field(examples=["Filtro de óleo"])
    preco_unitario: Decimal = Field(examples=["35.50"])
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
    status: str
    aprovado: bool | None
    moeda: str
    orcamento: str
    itens_servico: list[ItemServicoOut]
    itens_peca: list[ItemPecaOut]
