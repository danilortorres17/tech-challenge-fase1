"""Ponto de entrada da API (FastAPI).

Monta a aplicação, registra as rotas e traduz erros de domínio em respostas
HTTP. O Swagger/OpenAPI é gerado automaticamente e fica em /docs.
"""
from __future__ import annotations

from contextlib import asynccontextmanager

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse

from app.config import settings
from app.domain.exceptions import (
    ErroDeDominio,
    RegistroDuplicado,
    RegistroNaoEncontrado,
)
from app.infrastructure.db.base import criar_tabelas
from app.interfaces import auth, cadastros, health, ordens, relatorios


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Cria as tabelas no banco ao subir a aplicação.
    criar_tabelas()
    yield


def create_app() -> FastAPI:
    app = FastAPI(
        title=settings.app_name,
        version=settings.app_version,
        description=(
            "Sistema Integrado de Atendimento e Execução de Serviços "
            "de uma oficina mecânica - MVP do back-end (Tech Challenge Fase 1)."
        ),
        lifespan=lifespan,
    )

    app.include_router(health.router)
    app.include_router(auth.router)
    app.include_router(ordens.router)
    app.include_router(cadastros.clientes)
    app.include_router(cadastros.veiculos)
    app.include_router(cadastros.servicos)
    app.include_router(cadastros.pecas)
    app.include_router(relatorios.router)

    @app.exception_handler(RegistroNaoEncontrado)
    async def _nao_encontrado(request: Request, exc: RegistroNaoEncontrado):
        return JSONResponse(status_code=404, content={"detail": str(exc)})

    @app.exception_handler(RegistroDuplicado)
    async def _duplicado(request: Request, exc: RegistroDuplicado):
        return JSONResponse(status_code=409, content={"detail": str(exc)})

    @app.exception_handler(ErroDeDominio)
    async def _erro_de_dominio(request: Request, exc: ErroDeDominio):
        return JSONResponse(status_code=400, content={"detail": str(exc)})

    return app


app = create_app()


@app.get("/", tags=["root"], summary="Raiz da API")
def root() -> dict[str, str]:
    """Mensagem simples de boas-vindas com link para a documentação."""
    return {"mensagem": "Oficina API no ar. Documentação em /docs"}
