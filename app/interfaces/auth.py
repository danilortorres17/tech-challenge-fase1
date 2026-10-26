"""Autenticação: login, logout e proteção das rotas administrativas.

Expõe POST /auth/token (devolve um JWT), POST /auth/logout (revoga o token
atual) e a dependência `usuario_atual`, que as rotas administrativas usam para
exigir um token válido e não revogado. As senhas são verificadas por hash.
"""
from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from jwt import InvalidTokenError

from app.infrastructure.observabilidade import auditar
from app.infrastructure.repositorio_auditoria import RepositorioAuditoriaSQLAlchemy
from app.infrastructure.repositorio_usuario import (
    RepositorioTokenRevogadoSQLAlchemy,
    RepositorioUsuarioSQLAlchemy,
)
from app.infrastructure.seguranca import criar_token_acesso, decodificar_token
from app.infrastructure.senhas import verificar_senha
from app.interfaces.dependencias import (
    obter_repositorio_auditoria,
    obter_repositorio_token_revogado,
    obter_repositorio_usuario,
)

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="auth/token")

router = APIRouter(prefix="/auth", tags=["autenticação"])


@router.post("/token", summary="Autentica e devolve um token de acesso (JWT)")
def login(
    form: OAuth2PasswordRequestForm = Depends(),
    repo_usuario: RepositorioUsuarioSQLAlchemy = Depends(obter_repositorio_usuario),
    repo_auditoria: RepositorioAuditoriaSQLAlchemy = Depends(obter_repositorio_auditoria),
):
    usuario = repo_usuario.buscar_por_usuario(form.username)
    if usuario is None or not verificar_senha(form.password, usuario.senha_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Usuário ou senha inválidos.",
            headers={"WWW-Authenticate": "Bearer"},
        )
    token = criar_token_acesso(usuario.usuario, usuario.papel)
    auditar(repo_auditoria, ator=usuario.usuario, evento="login")
    # "bearer" é o tipo de token padrão do OAuth2, não um segredo.
    return {"access_token": token, "token_type": "bearer"}  # nosec B105


@router.post("/logout", summary="Encerra a sessão, revogando o token atual")
def logout(
    token: str = Depends(oauth2_scheme),
    repo_revogados: RepositorioTokenRevogadoSQLAlchemy = Depends(
        obter_repositorio_token_revogado
    ),
):
    try:
        dados = decodificar_token(token)
    except InvalidTokenError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Token inválido ou expirado."
        )
    jti = dados.get("jti")
    if jti:
        repo_revogados.revogar(jti)
    return {"detail": "Sessão encerrada."}


def usuario_atual(
    token: str = Depends(oauth2_scheme),
    repo_revogados: RepositorioTokenRevogadoSQLAlchemy = Depends(
        obter_repositorio_token_revogado
    ),
) -> str:
    """Valida o token (assinatura, expiração e revogação) e devolve o usuário."""
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
    jti = dados.get("jti")
    if sub is None or jti is None:
        raise erro
    if repo_revogados.esta_revogado(jti):
        raise erro
    return sub
