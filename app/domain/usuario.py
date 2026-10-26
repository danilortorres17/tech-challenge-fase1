"""Entidade Usuario - credencial administrativa do sistema.

Entidade com identidade própria (id). Guarda apenas o hash da senha, nunca a
senha em texto. O papel (role) habilita um controle de acesso simples.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from uuid import UUID, uuid4

PAPEL_ADMIN = "admin"


@dataclass
class Usuario:
    usuario: str
    senha_hash: str
    papel: str = PAPEL_ADMIN
    id: UUID = field(default_factory=uuid4)
