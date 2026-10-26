"""Rotinas de inicialização (semeadura de dados essenciais).

Mantém o usuário administrativo fora do código: ele é criado no primeiro boot a
partir das variáveis de ambiente (ADMIN_USUARIO/ADMIN_SENHA), com a senha
armazenada já em hash.
"""
from __future__ import annotations

from app.config import settings
from app.domain.usuario import PAPEL_ADMIN, Usuario
from app.infrastructure.repositorio_usuario import RepositorioUsuarioSQLAlchemy
from app.infrastructure.senhas import gerar_hash


def semear_admin(session_factory) -> None:
    """Cria o usuário admin (idempotente) se ainda não existir."""
    repo = RepositorioUsuarioSQLAlchemy(session_factory)
    if repo.buscar_por_usuario(settings.admin_usuario) is not None:
        return
    repo.salvar(
        Usuario(
            usuario=settings.admin_usuario,
            senha_hash=gerar_hash(settings.admin_senha),
            papel=PAPEL_ADMIN,
        )
    )
