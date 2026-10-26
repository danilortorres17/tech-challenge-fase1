"""Geração e validação de tokens JWT (via PyJWT).

Detalhe de infraestrutura: as camadas de cima só pedem "crie um token" ou
"valide este token", sem conhecer a biblioteca por baixo. Cada token carrega um
identificador único de sessão (jti), que permite revogá-lo no logout.
"""
from __future__ import annotations

from datetime import datetime, timedelta, timezone
from uuid import uuid4

import jwt

from app.config import settings
from app.domain.usuario import PAPEL_ADMIN


def criar_token_acesso(sub: str, papel: str = PAPEL_ADMIN) -> str:
    """Gera um token JWT assinado, com expiração, papel e jti (id de sessão)."""
    agora = datetime.now(timezone.utc)
    payload = {
        "sub": sub,
        "papel": papel,
        "jti": uuid4().hex,
        "iat": agora,
        "exp": agora + timedelta(minutes=settings.jwt_expira_min),
    }
    return jwt.encode(payload, settings.jwt_secret, algorithm=settings.jwt_algoritmo)


def decodificar_token(token: str) -> dict:
    """Valida a assinatura e a expiração, devolvendo o conteúdo do token.

    Lança jwt.InvalidTokenError (ou subclasses) se o token for inválido/expirado.
    """
    return jwt.decode(token, settings.jwt_secret, algorithms=[settings.jwt_algoritmo])
