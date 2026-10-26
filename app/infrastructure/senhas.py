"""Hash e verificação de senhas (bcrypt).

Detalhe de infraestrutura: as camadas de cima guardam/validam senhas sem saber
qual algoritmo é usado. As senhas nunca são armazenadas em texto puro.
"""
from __future__ import annotations

import bcrypt


def gerar_hash(senha: str) -> str:
    """Gera o hash bcrypt (com salt aleatório) de uma senha."""
    return bcrypt.hashpw(senha.encode("utf-8"), bcrypt.gensalt()).decode("utf-8")


def verificar_senha(senha: str, hash_armazenado: str) -> bool:
    """Confere a senha contra o hash armazenado, em tempo constante."""
    try:
        return bcrypt.checkpw(senha.encode("utf-8"), hash_armazenado.encode("utf-8"))
    except (ValueError, TypeError):
        return False
