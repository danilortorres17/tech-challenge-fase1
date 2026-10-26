"""Repositórios de autenticação: usuários e tokens revogados (denylist).

Herdam de RepositorioSQLAlchemy, que gerencia a sessão. Os tokens revogados
sustentam o logout: um jti na denylist deixa de ser aceito.
"""
from __future__ import annotations

from datetime import datetime, timezone
from uuid import UUID

from app.domain.usuario import Usuario
from app.infrastructure.db.base import RepositorioSQLAlchemy
from app.infrastructure.db.models import TokenRevogadoModel, UsuarioModel


class RepositorioUsuarioSQLAlchemy(RepositorioSQLAlchemy):
    def salvar(self, item: Usuario) -> None:
        with self._sessao() as s:
            m = s.get(UsuarioModel, str(item.id)) or UsuarioModel(id=str(item.id))
            m.usuario = item.usuario
            m.senha_hash = item.senha_hash
            m.papel = item.papel
            s.add(m)

    def buscar_por_usuario(self, usuario: str) -> Usuario | None:
        with self._sessao() as s:
            m = s.query(UsuarioModel).filter_by(usuario=usuario).one_or_none()
            if m is None:
                return None
            return Usuario(m.usuario, m.senha_hash, m.papel, UUID(m.id))


class RepositorioTokenRevogadoSQLAlchemy(RepositorioSQLAlchemy):
    def revogar(self, jti: str) -> None:
        with self._sessao() as s:
            if s.get(TokenRevogadoModel, jti) is None:
                s.add(
                    TokenRevogadoModel(jti=jti, revogado_em=datetime.now(timezone.utc))
                )

    def esta_revogado(self, jti: str) -> bool:
        with self._sessao() as s:
            return s.get(TokenRevogadoModel, jti) is not None
