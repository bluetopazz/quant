from __future__ import annotations

from dataclasses import dataclass
import os


@dataclass(frozen=True)
class AppSettings:
    api_title: str
    api_version: str
    secret_key: str
    access_token_ttl_minutes: int
    database_url: str
    cors_origins: tuple[str, ...]
    cors_origin_regex: str | None
    admin_username: str
    admin_password: str
    enable_csv_journaling: bool
    enable_intelligence_auto_refresh: bool
    intelligence_refresh_interval_seconds: int

    @classmethod
    def from_env(cls) -> "AppSettings":
        origins_raw = os.getenv("DESK_CORS_ORIGINS", "http://127.0.0.1:3000,http://localhost:3000")
        origins = tuple(origin.strip() for origin in origins_raw.split(",") if origin.strip())
        cors_origin_regex = os.getenv(
            "DESK_CORS_ORIGIN_REGEX",
            r"^https?://(localhost|127\.0\.0\.1)(:\d+)?$",
        ).strip() or None
        ttl_raw = os.getenv("DESK_ACCESS_TOKEN_TTL_MINUTES", "480")
        try:
            ttl = max(5, int(ttl_raw))
        except ValueError:
            ttl = 480
        refresh_interval_raw = os.getenv("DESK_INTELLIGENCE_REFRESH_INTERVAL_SECONDS", "1800")
        try:
            refresh_interval = max(300, int(refresh_interval_raw))
        except ValueError:
            refresh_interval = 1800

        return cls(
            api_title="Macro Relative-Value Intelligence API",
            api_version="0.1.0",
            secret_key=os.getenv("DESK_SECRET_KEY", "dev-secret-change-me"),
            access_token_ttl_minutes=ttl,
            database_url=os.getenv("DESK_DATABASE_URL", "sqlite:///./backend/platform.db"),
            cors_origins=origins,
            cors_origin_regex=cors_origin_regex,
            admin_username=os.getenv("DESK_ADMIN_USERNAME", "operator"),
            admin_password=os.getenv("DESK_ADMIN_PASSWORD", "change-me"),
            enable_csv_journaling=os.getenv("DESK_ENABLE_CSV_JOURNALING", "true").lower() != "false",
            enable_intelligence_auto_refresh=os.getenv("DESK_ENABLE_INTELLIGENCE_AUTO_REFRESH", "false").lower() == "true",
            intelligence_refresh_interval_seconds=refresh_interval,
        )


settings = AppSettings.from_env()
