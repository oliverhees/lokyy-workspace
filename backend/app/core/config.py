"""Application configuration — typed via pydantic-settings (no raw os.getenv).

All runtime config is validated here at startup. Add new settings as typed
fields; invalid values fail fast with a clear Pydantic error.
"""
from functools import lru_cache

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=(".env", "../.env"),
        env_file_encoding="utf-8",
        extra="ignore",
        case_sensitive=False,
    )

    # App
    app_env: str = Field(default="development")
    app_bind: str = Field(default="127.0.0.1")
    app_port: int = Field(default=8000, ge=1, le=65535)

    # Database (PostgreSQL + pgvector) — used from T0.3 onward
    database_url: str = Field(
        default="postgresql+psycopg://lokyy:lokyy@localhost:5432/lokyy"
    )

    # Auth & security
    auth_enabled: bool = Field(default=True)
    secret_key: str = Field(default="change_me_generate_a_random_value")
    secure_cookies: bool = Field(default=False)
    # SSRF: allow local/private model endpoints (Ollama etc.). Dangerous ranges
    # (cloud-metadata/link-local) are always blocked regardless of this flag.
    allow_private_model_hosts: bool = Field(default=True)

    # LLM (optional — if unset, /chat uses an echo fallback for dev/demo)
    llm_base_url: str = Field(default="")
    llm_model: str = Field(default="")
    llm_api_key: str = Field(default="")

    # CORS — the PWA talks cross-origin to the backend (local/remote switch)
    allowed_origins: str = Field(default="http://localhost:3000,http://localhost:3008")

    @property
    def cors_origins(self) -> list[str]:
        return [o.strip() for o in self.allowed_origins.split(",") if o.strip()]

    @property
    def is_production(self) -> bool:
        return self.app_env.lower() in {"production", "prod"}

    def security_issues(self) -> list[str]:
        """Insecure-config problems to fail fast on at startup."""
        issues: list[str] = []
        if self.is_production:
            if self.secret_key in ("", "change_me_generate_a_random_value") or len(self.secret_key) < 16:
                issues.append("SECRET_KEY muss in Produktion gesetzt sein (≥16 Zeichen).")
            if not self.secure_cookies:
                issues.append("SECURE_COOKIES muss in Produktion 'true' sein.")
        # never allow credentialed CORS with a wildcard origin
        if "*" in self.cors_origins:
            issues.append("CORS-Origins dürfen mit credentials kein '*' enthalten.")
        return issues


@lru_cache
def get_settings() -> Settings:
    """Cached singleton so settings are parsed/validated exactly once."""
    return Settings()
