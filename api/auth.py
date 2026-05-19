"""
api/auth.py — проверка Telegram initData (HMAC-SHA256)

Использование в любом handler'е:
    from auth import verify_init_data, AuthError

    def do_POST(self):
        try:
            user = verify_init_data(self.headers.get("X-Init-Data", ""))
        except AuthError as e:
            self._json({"ok": False, "error": str(e)}, status=401)
            return
        # user["id"], user["first_name"] — гарантированно настоящие
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
    """
    Проверяет подпись Telegram initData.
    Возвращает dict с данными пользователя если всё OK.
    Выбрасывает AuthError если подпись неверна или данные отсутствуют.
    """
    if not init_data:
        raise AuthError("initData отсутствует")

    # Парсим строку вида key=value&key=value&hash=...
    parsed = dict(parse_qsl(init_data, keep_blank_values=True))

    received_hash = parsed.pop("hash", None)
    if not received_hash:
        raise AuthError("hash отсутствует в initData")

    # Строим data-check-string: все поля кроме hash, отсортированные по ключу
    data_check_string = "\n".join(
        f"{k}={v}" for k, v in sorted(parsed.items())
    )

    # Ключ = HMAC-SHA256("WebAppData", BOT_TOKEN)
    secret_key = hmac.new(
        b"WebAppData",
        BOT_TOKEN.encode(),
        hashlib.sha256
    ).digest()

    # Ожидаемый hash
    expected_hash = hmac.new(
        secret_key,
        data_check_string.encode(),
        hashlib.sha256
    ).hexdigest()

    if not hmac.compare_digest(expected_hash, received_hash):
        raise AuthError("Подпись initData неверна")

    # Извлекаем user
    user_str = parsed.get("user")
    if not user_str:
        raise AuthError("Поле user отсутствует в initData")

    try:
        user = json.loads(unquote(user_str))
    except Exception:
        raise AuthError("Не удалось распарсить user из initData")

    return user
