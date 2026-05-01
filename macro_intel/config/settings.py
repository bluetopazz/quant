from __future__ import annotations

from dataclasses import dataclass
import os


@dataclass(frozen=True)
class Settings:
    """Runtime settings for the intelligence suite."""

    fred_api_key: str | None
    llm_base_url: str
    llm_model: str
    embed_model: str
    mongo_uri: str
    mongo_db: str
    request_timeout_seconds: int = 180

    @classmethod
    def from_env(cls) -> "Settings":
        timeout_raw = os.getenv("MACRO_INTEL_TIMEOUT_SECONDS", "180")
        try:
            timeout = int(timeout_raw)
        except ValueError:
            timeout = 180

        return cls(
            fred_api_key=os.getenv("FRED_API_KEY"),
            llm_base_url=os.getenv("LLM_BASE_URL", "http://127.0.0.1:11434"),
            llm_model=os.getenv("LLM_MODEL", "qwen2.5:7b"),
            embed_model=os.getenv("EMBED_MODEL", "avr/sfr-embedding-mistral"),
            mongo_uri=os.getenv("MONGO_URI", "mongodb://localhost:27017/"),
            mongo_db=os.getenv("MONGO_DB", "quant_macro"),
            request_timeout_seconds=max(timeout, 1),
        )

    def require_fred_api_key(self) -> str:
        if not self.fred_api_key:
            raise ValueError("FRED_API_KEY is required for FRED-backed workflows.")
        return self.fred_api_key
