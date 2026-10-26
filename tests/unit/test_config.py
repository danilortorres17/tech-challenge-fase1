"""Testes da configuração: segredo JWT obrigatório em produção."""
import pytest

from app.config import SEGREDO_JWT_PADRAO, ConfiguracaoInvalida, Settings


def test_producao_sem_segredo_falha(monkeypatch) -> None:
    monkeypatch.setenv("APP_ENV", "production")
    monkeypatch.delenv("JWT_SECRET", raising=False)
    with pytest.raises(ConfiguracaoInvalida):
        Settings()


def test_producao_com_segredo_padrao_falha(monkeypatch) -> None:
    monkeypatch.setenv("APP_ENV", "production")
    monkeypatch.setenv("JWT_SECRET", SEGREDO_JWT_PADRAO)
    with pytest.raises(ConfiguracaoInvalida):
        Settings()


def test_producao_com_segredo_proprio_ok(monkeypatch) -> None:
    monkeypatch.setenv("APP_ENV", "production")
    monkeypatch.setenv("JWT_SECRET", "um-segredo-bem-grande-de-verdade-123")
    s = Settings()
    assert s.em_producao is True


def test_desenvolvimento_usa_padrao(monkeypatch) -> None:
    monkeypatch.delenv("APP_ENV", raising=False)
    monkeypatch.delenv("JWT_SECRET", raising=False)
    s = Settings()
    assert s.em_producao is False
    assert s.jwt_secret == SEGREDO_JWT_PADRAO
