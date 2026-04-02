"""Application settings loaded from environment / .env file."""

from __future__ import annotations

from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
    )

    # ── App ──────────────────────────────────────────────────────────
    app_name: str = "Zoreza Pro"
    debug: bool = False
    app_tz: str = "America/Mexico_City"
    api_v1_prefix: str = "/api/v1"

    # ── Database ─────────────────────────────────────────────────────
    # SQLite for dev:  sqlite+aiosqlite:///./data/zoreza_pro.db
    # PostgreSQL prod: postgresql+asyncpg://zoreza:zoreza@localhost:5432/zoreza_pro
    database_url: str = "sqlite+aiosqlite:///./data/zoreza_pro.db"
    db_pool_size: int = 10
    db_max_overflow: int = 20

    @property
    def is_sqlite(self) -> bool:
        return self.database_url.startswith("sqlite")

    # ── JWT / Auth ───────────────────────────────────────────────────
    secret_key: str = "CHANGE-ME-in-production-use-openssl-rand-hex-64"
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 60
    refresh_token_expire_days: int = 30

    # ── Business defaults ────────────────────────────────────────────
    default_tolerancia_pesos: float = 30.0
    default_fondo_sugerido: float = 500.0
    default_comision_pct: float = 0.40


@lru_cache
def get_settings() -> Settings:
    return Settings()
