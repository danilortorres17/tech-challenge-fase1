"""Configurações da aplicação.

Lê variáveis de ambiente (de um arquivo .env em produção/local), sem nunca
embutir segredos no código. Veja .env.example para as chaves esperadas.
"""
import os


class Settings:
    """Configurações carregadas do ambiente."""

    def __init__(self) -> None:
        self.app_name: str = os.getenv("APP_NAME", "Oficina API")
        self.app_version: str = os.getenv("APP_VERSION", "0.1.0")
        # SQLite por padrão (arquivo local). Trocável por outro banco via env.
        self.database_url: str = os.getenv("DATABASE_URL", "sqlite:///./oficina.db")

        # Autenticação JWT
        self.jwt_secret: str = os.getenv("JWT_SECRET", "troque-este-segredo-em-producao")
        self.jwt_algoritmo: str = os.getenv("JWT_ALGORITMO", "HS256")
        self.jwt_expira_min: int = int(os.getenv("JWT_EXPIRA_MIN", "60"))

        # Usuário administrativo de demonstração
        self.admin_usuario: str = os.getenv("ADMIN_USUARIO", "admin")
        self.admin_senha: str = os.getenv("ADMIN_SENHA", "admin123")


settings = Settings()
