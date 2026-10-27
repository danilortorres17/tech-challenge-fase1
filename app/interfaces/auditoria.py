"""Rota de consulta da trilha de auditoria (requer autenticação)."""
from __future__ import annotations

from fastapi import APIRouter, Depends

from app.infrastructure.repositorio_auditoria import RepositorioAuditoriaSQLAlchemy
from app.interfaces.auth import requer_admin
from app.interfaces.dependencias import obter_repositorio_auditoria

router = APIRouter(prefix="/auditoria", tags=["auditoria"])


@router.get("", summary="Lista os eventos de auditoria (requer autenticação)")
def listar(
    limite: int = 100,
    repo: RepositorioAuditoriaSQLAlchemy = Depends(obter_repositorio_auditoria),
    usuario: str = Depends(requer_admin),
):
    return repo.listar(limite=limite)
