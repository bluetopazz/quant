from __future__ import annotations

import base64
from datetime import datetime, timedelta, timezone
import hashlib
import hmac
import os
import secrets

from .config import settings


def hash_password(password: str) -> str:
    salt = secrets.token_bytes(16)
    digest = hashlib.pbkdf2_hmac("sha256", password.encode("utf-8"), salt, 200_000)
    return f"{salt.hex()}${digest.hex()}"


def verify_password(password: str, password_hash: str) -> bool:
    try:
        salt_hex, digest_hex = password_hash.split("$", 1)
    except ValueError:
        return False
    salt = bytes.fromhex(salt_hex)
    expected = bytes.fromhex(digest_hex)
    candidate = hashlib.pbkdf2_hmac("sha256", password.encode("utf-8"), salt, 200_000)
    return hmac.compare_digest(candidate, expected)


def create_access_token(username: str, *, ttl_minutes: int | None = None) -> str:
    ttl = ttl_minutes or settings.access_token_ttl_minutes
    expires_at = int((datetime.now(timezone.utc) + timedelta(minutes=ttl)).timestamp())
    payload = f"{username}:{expires_at}"
    signature = hmac.new(settings.secret_key.encode("utf-8"), payload.encode("utf-8"), hashlib.sha256).hexdigest()
    token = f"{payload}:{signature}"
    return base64.urlsafe_b64encode(token.encode("utf-8")).decode("utf-8")


def decode_access_token(token: str) -> str:
    try:
        decoded = base64.urlsafe_b64decode(token.encode("utf-8")).decode("utf-8")
        username, expires_at_raw, signature = decoded.rsplit(":", 2)
    except Exception as exc:  # pragma: no cover - defensive parsing
        raise ValueError("Invalid token format") from exc

    payload = f"{username}:{expires_at_raw}"
    expected_signature = hmac.new(
        settings.secret_key.encode("utf-8"),
        payload.encode("utf-8"),
        hashlib.sha256,
    ).hexdigest()
    if not hmac.compare_digest(signature, expected_signature):
        raise ValueError("Invalid token signature")

    if int(expires_at_raw) < int(datetime.now(timezone.utc).timestamp()):
        raise ValueError("Token expired")
    return username
