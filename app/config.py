"""Configurações da aplicação.

Lê variáveis de ambiente (de um arquivo .env em produção/local), sem nunca
embutir segredos no código. Veja .env.example para as chaves esperadas.

Em produção (APP_ENV=production) a aplicação se recusa a subir com o segredo
JWT no valor-padrão de desenvolvimento: o segredo precisa ser injetado.
"""
import os

# Valor-padrão usado apenas em desenvolvimento/testes. Em produção ele é
# rejeitado (veja _validar_producao): o JWT_SECRET deve vir do ambiente.
SEGREDO_JWT_PADRAO = "troque-por-um-valor-secreto-bem-grande"


class ConfiguracaoInvalida(RuntimeError):
    """Configuração insegura ou incompleta para o ambiente atual."""


class Settings:
    """Configurações carregadas do ambiente."""

    def __init__(self) -> None:
        self.app_name: str = os.getenv("APP_NAME", "Oficina API")
        self.app_version: str = os.getenv("APP_VERSION", "0.1.0")
        # development (padrão) | production. Em production, as proteções abaixo
        # passam a valer (ex.: segredo JWT obrigatório).
        self.app_env: str = os.getenv("APP_ENV", "development").strip().lower()
        # SQLite por padrão (arquivo local). Trocável por outro banco via env.
        self.database_url: str = os.getenv("DATABASE_URL", "sqlite:///./oficina.db")

        # Autenticação JWT
        self.jwt_secret: str = os.getenv("JWT_SECRET", SEGREDO_JWT_PADRAO)
        self.jwt_algoritmo: str = os.getenv("JWT_ALGORITMO", "HS256")
        self.jwt_expira_min: int = int(os.getenv("JWT_EXPIRA_MIN", "60"))

        # Usuário administrativo de demonstração (semeado na primeira subida).
        self.admin_usuario: str = os.getenv("ADMIN_USUARIO", "admin")
        self.admin_senha: str = os.getenv("ADMIN_SENHA", "admin123")

        self._validar_producao()

    @property
    def em_producao(self) -> bool:
        return self.app_env == "production"

    def _validar_producao(self) -> None:
        """Falha cedo quando o ambiente é inseguro para produção."""
        if not self.em_producao:
            return
        if not self.jwt_secret or self.jwt_secret == SEGREDO_JWT_PADRAO:
            raise ConfiguracaoInvalida(
                "JWT_SECRET precisa ser definido em produção (APP_ENV=production): "
                "o valor-padrão de desenvolvimento não é aceito."
            )


settings = Settings()
