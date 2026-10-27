"""Autenticação e autorização das rotas administrativas.

Expõe POST /auth/token (devolve um JWT) e POST /auth/logout (revoga o token
atual). A dependência `usuario_atual` exige um token válido e não revogado
(autenticação); `requer_admin` exige, além disso, o papel de administrador no
token (autorização). As senhas são verificadas por hash.
"""
from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from jwt import InvalidTokenError

from app.domain.usuario import PAPEL_ADMIN
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


def _validar_token(
    token: str, repo_revogados: RepositorioTokenRevogadoSQLAlchemy
) -> dict:
    """Valida assinatura, expiração, presença de `sub`/`jti` e revogação."""
    erro = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Token inválido ou expirado.",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        dados = decodificar_token(token)
    except InvalidTokenError:
        raise erro
    if dados.get("sub") is None or dados.get("jti") is None:
        raise erro
    if repo_revogados.esta_revogado(dados["jti"]):
        raise erro
    return dados


def usuario_atual(
    token: str = Depends(oauth2_scheme),
    repo_revogados: RepositorioTokenRevogadoSQLAlchemy = Depends(
        obter_repositorio_token_revogado
    ),
) -> str:
    """Autenticação: devolve o usuário de um token válido e não revogado."""
    return _validar_token(token, repo_revogados)["sub"]


def requer_admin(
    token: str = Depends(oauth2_scheme),
    repo_revogados: RepositorioTokenRevogadoSQLAlchemy = Depends(
        obter_repositorio_token_revogado
    ),
) -> str:
    """Autorização: exige token válido E papel de administrador.

    Autenticar não é autorizar: um token válido sem o papel exigido é recusado
    com 403, separando a identidade (quem é) da permissão (o que pode fazer).
    """
    dados = _validar_token(token, repo_revogados)
    if dados.get("papel") != PAPEL_ADMIN:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Permissão insuficiente para esta operação.",
        )
    return dados["sub"]
