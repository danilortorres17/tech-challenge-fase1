"""Repositório da trilha de auditoria (eventos críticos do sistema)."""
from __future__ import annotations

from datetime import datetime, timezone
from uuid import UUID

from app.infrastructure.db.base import RepositorioSQLAlchemy
from app.infrastructure.db.models import AuditoriaModel


class RepositorioAuditoriaSQLAlchemy(RepositorioSQLAlchemy):
    def registrar(
        self,
        *,
        ator: str,
        evento: str,
        entidade_id: UUID | str | None = None,
        detalhe: str | None = None,
    ) -> None:
        with self._sessao() as s:
            s.add(
                AuditoriaModel(
                    ocorrido_em=datetime.now(timezone.utc),
                    ator=ator,
                    evento=evento,
                    entidade_id=str(entidade_id) if entidade_id is not None else None,
                    detalhe=detalhe,
                )
            )

    def listar(self, limite: int = 100) -> list[dict]:
        with self._sessao() as s:
            registros = (
                s.query(AuditoriaModel)
                .order_by(AuditoriaModel.id.desc())
                .limit(limite)
                .all()
            )
            return [
                {
                    "ocorrido_em": r.ocorrido_em.isoformat() if r.ocorrido_em else None,
                    "ator": r.ator,
                    "evento": r.evento,
                    "entidade_id": r.entidade_id,
                    "detalhe": r.detalhe,
                }
                for r in registros
            ]
