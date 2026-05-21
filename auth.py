"""
auth.py — проверка Telegram initData (HMAC-SHA256)
"""

import os
import hmac
import hashlib
import json
from urllib.parse import unquote, parse_qsl

BOT_TOKEN = os.getenv("BOT_TOKEN", "")


class AuthError(Exception):
    pass


def verify_init_data(init_data: str) -> dict:
    # Для локальной разработки — отключить проверку через SKIP_AUTH=1
    if os.getenv("SKIP_AUTH") == "1":
        return {"id": 0, "first_name": "Dev"}

    if not init_data:
        raise AuthError("initData отсутствует")

    parsed = dict(parse_qsl(init_data, keep_blank_values=True))

    received_hash = parsed.pop("hash", None)
    if not received_hash:
        raise AuthError("hash отсутствует в initData")

    data_check_string = "\n".join(
        f"{k}={v}" for k, v in sorted(parsed.items())
    )

    secret_key = hmac.new(
        b"WebAppData",
        BOT_TOKEN.encode(),
        hashlib.sha256
    ).digest()

    expected_hash = hmac.new(
        secret_key,
        data_check_string.encode(),
        hashlib.sha256
    ).hexdigest()

    if not hmac.compare_digest(expected_hash, received_hash):
        raise AuthError("Подпись initData неверна")

    user_str = parsed.get("user")
    if not user_str:
        raise AuthError("Поле user отсутствует в initData")

    try:
        user = json.loads(unquote(user_str))
    except Exception:
        raise AuthError("Не удалось распарсить user из initData")

    return user
