"""Testes do hash/verificação de senhas (bcrypt)."""
from app.infrastructure.senhas import gerar_hash, verificar_senha


def test_hash_difere_da_senha_e_verifica_ok() -> None:
    h = gerar_hash("segredo-123")
    assert h != "segredo-123"
    assert verificar_senha("segredo-123", h) is True


def test_senha_errada_nao_verifica() -> None:
    h = gerar_hash("segredo-123")
    assert verificar_senha("outra", h) is False


def test_hash_malformado_retorna_false() -> None:
    # Hash inválido não deve levantar exceção, apenas falhar a verificação.
    assert verificar_senha("qualquer", "isto-nao-e-um-hash-bcrypt") is False
