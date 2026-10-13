"""Schemas Pydantic dos cadastros (entrada e saída da API)."""
from __future__ import annotations

from decimal import Decimal

from pydantic import BaseModel, Field


# --- Cliente ---
class ClienteIn(BaseModel):
    documento: str = Field(examples=["111.444.777-35"])
    nome: str = Field(examples=["Maria Oliveira"])


class ClienteOut(BaseModel):
    id: str
    documento: str
    nome: str


# --- Veículo ---
class VeiculoIn(BaseModel):
    placa: str = Field(examples=["ABC1D23"])
    marca: str = Field(examples=["Volkswagen"])
    modelo: str = Field(examples=["Gol"])
    ano: int = Field(examples=[2020])
    cliente_id: str | None = None


class VeiculoOut(BaseModel):
    id: str
    placa: str
    marca: str
    modelo: str
    ano: int
    cliente_id: str | None


# --- Serviço ---
class ServicoIn(BaseModel):
    descricao: str = Field(examples=["Troca de óleo"])
    preco: Decimal = Field(examples=["120.00"])


class ServicoOut(BaseModel):
    id: str
    descricao: str
    preco: str
    moeda: str


# --- Peça ---
class PecaIn(BaseModel):
    descricao: str = Field(examples=["Filtro de óleo"])
    preco: Decimal = Field(examples=["35.50"])
    estoque: int = Field(default=0, ge=0, examples=[10])


class PecaOut(BaseModel):
    id: str
    descricao: str
    preco: str
    moeda: str
    estoque: int


class EstoqueIn(BaseModel):
    quantidade: int = Field(gt=0, examples=[5])
