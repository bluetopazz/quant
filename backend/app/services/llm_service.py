from __future__ import annotations

from macro_intel.config.settings import Settings


def llm_status() -> dict[str, str]:
    settings = Settings.from_env()
    return {
        "base_url": settings.llm_base_url,
        "model": settings.llm_model,
    }
