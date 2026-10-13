"""Geração e validação de tokens JWT.

Detalhe de infraestrutura: as camadas de cima só pedem "crie um token" ou
"valide este token", sem conhecer a biblioteca por baixo.
"""
from __future__ import annotations

from datetime import datetime, timedelta, timezone

from jose import jwt

from app.config import settings


def criar_token_acesso(sub: str) -> str:
    """Gera um token JWT assinado, com expiração."""
    expira = datetime.now(timezone.utc) + timedelta(minutes=settings.jwt_expira_min)
    payload = {"sub": sub, "exp": expira}
    return jwt.encode(payload, settings.jwt_secret, algorithm=settings.jwt_algoritmo)


def decodificar_token(token: str) -> dict:
    """Valida a assinatura e a expiração, devolvendo o conteúdo do token.

    Lança jose.JWTError (ou subclasses) se o token for inválido ou expirado.
    """
    return jwt.decode(token, settings.jwt_secret, algorithms=[settings.jwt_algoritmo])
