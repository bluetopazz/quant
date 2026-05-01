from __future__ import annotations

import requests


def ask_llm(
    prompt: str,
    *,
    base_url: str,
    model: str,
    temperature: float = 0.1,
    timeout_seconds: int = 60,
) -> str:
    """Send a prompt to an Ollama-compatible /api/chat endpoint."""

    payload = {
        "model": model,
        "messages": [{"role": "user", "content": prompt}],
        "options": {"temperature": temperature},
        "stream": False,
    }
    response = requests.post(f"{base_url}/api/chat", json=payload, timeout=timeout_seconds)
    response.raise_for_status()
    body = response.json()
    if "message" not in body or "content" not in body["message"]:
        raise RuntimeError("Unexpected /api/chat response structure")
    return body["message"]["content"]
