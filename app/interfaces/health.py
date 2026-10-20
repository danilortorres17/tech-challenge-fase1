"""Rota de health check.

Camada de interface: expõe endpoints HTTP. Não contém regra de negócio -
apenas traduz requisições em respostas. Serve de prova de vida da aplicação.
"""
from fastapi import APIRouter

router = APIRouter(tags=["health"])


@router.get("/health", summary="Verifica se a aplicação está no ar")
def health() -> dict[str, str]:
    """Retorna o status da aplicação."""
    return {"status": "ok"}
