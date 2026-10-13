"""Autenticação: login e proteção das rotas administrativas.

Expõe POST /auth/token (devolve um JWT) e a dependência `usuario_atual`, que
as rotas administrativas usam para exigir um token válido.
"""
from __future__ import annotations

import hmac

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from jwt import InvalidTokenError

from app.config import settings
from app.infrastructure.seguranca import criar_token_acesso, decodificar_token

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="auth/token")

router = APIRouter(prefix="/auth", tags=["autenticação"])


@router.post("/token", summary="Autentica e devolve um token de acesso (JWT)")
def login(form: OAuth2PasswordRequestForm = Depends()):
    usuario_ok = hmac.compare_digest(form.username, settings.admin_usuario)
    senha_ok = hmac.compare_digest(form.password, settings.admin_senha)
    if not (usuario_ok and senha_ok):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Usuário ou senha inválidos.",
            headers={"WWW-Authenticate": "Bearer"},
        )
    token = criar_token_acesso(form.username)
    # "bearer" é o tipo de token padrão do OAuth2, não um segredo.
    return {"access_token": token, "token_type": "bearer"}  # nosec B105


def usuario_atual(token: str = Depends(oauth2_scheme)) -> str:
    """Valida o token e devolve o identificador do usuário autenticado."""
    erro = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Token inválido ou expirado.",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        dados = decodificar_token(token)
    except InvalidTokenError:
        raise erro
    sub = dados.get("sub")
    if sub is None:
        raise erro
    return sub
