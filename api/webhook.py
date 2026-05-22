import os, json, urllib.request
from http.server import BaseHTTPRequestHandler

BOT_TOKEN  = os.getenv("BOT_TOKEN", "")
WEBAPP_URL = os.getenv("WEBAPP_URL", "")


def send_message(chat_id, text, reply_markup=None):
    """Отправить сообщение через Telegram Bot API (для уведомлений из группы)."""
    payload = {
        "chat_id": chat_id,
        "text": text,
        "parse_mode": "Markdown"
    }
    if reply_markup:
        payload["reply_markup"] = reply_markup

    data = json.dumps(payload).encode()
    req = urllib.request.Request(
        f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage",
        data=data,
        headers={"Content-Type": "application/json"},
        method="POST"
    )
    try:
        urllib.request.urlopen(req)
    except Exception as e:
        print(f"send_message error: {e}")


def make_response(chat_id, text, reply_markup=None):
    """Вернуть ответ напрямую через webhook response (только для личных сообщений)."""
    resp = {
        "method": "sendMessage",
        "chat_id": chat_id,
        "text": text,
        "parse_mode": "Markdown"
    }
    if reply_markup:
        resp["reply_markup"] = reply_markup
    return resp


def handle_update(update):
    # ── 1. Обычное сообщение ──────────────────────────────────────────────────
    if "message" in update:
        msg      = update["message"]
        chat_id  = msg["chat"]["id"]
        chat_type = msg["chat"].get("type", "private")  # private / group / supergroup
        text     = msg.get("text", "")

        # Данные из WebApp — приходят ТОЛЬКО в личке
        if "web_app_data" in msg:
            try:
                payload = json.loads(msg["web_app_data"]["data"])
            except Exception:
                return None

            actor  = msg.get("from", {}).get("first_name", "Участник")
            action = payload.get("action", "")
            name   = payload.get("name", "")
            amount = payload.get("amount", "")
            # chat_id группы передаётся из WebApp в payload
            group_chat_id = payload.get("group_chat_id")

            notifications = {
                "add":     f"🔔 *{actor}* dodał/a: *{name}*",
                "take":    f"🙋 *{actor}* bierze: *{name}*",
                "bought":  f"✅ *{actor}* kupił/a: *{name}*",
                "delete":  f"🗑 *{actor}* usunął/a: *{name}*",
                "expense": f"💰 *{actor}* dodał/a wydatek: *{amount} zł* — {name}",
            }

            msg_text = notifications.get(action)
            if msg_text:
                if group_chat_id:
                    # Уведомить группу через отдельный запрос к API
                    send_message(group_chat_id, msg_text)
                # Подтвердить пользователю в личке
                return make_response(chat_id, msg_text)
            return None

        # Команды /start и /list
        if text.startswith("/start") or text.startswith("/list"):
            if chat_type == "private":
                # В личке — WebApp. Если пришли через deep link (/start group_-100xxx),
                # передаём group_chat_id чтобы уведомления шли в группу
                parts = text.split(maxsplit=1)
                param = parts[1] if len(parts) > 1 else ""
                if param.startswith("group_"):
                    try:
                        group_chat_id = int(param[len("group_"):])
                        url = f"{WEBAPP_URL}?chat_id={group_chat_id}"
                    except ValueError:
                        url = f"{WEBAPP_URL}?chat_id={chat_id}"
                else:
                    url = f"{WEBAPP_URL}?chat_id={chat_id}"
                reply_markup = {
                    "inline_keyboard": [[{
                        "text": "🛒 Открыть список",
                        "web_app": {"url": url}
                    }]]
                }
            else:
                # В группе — url-кнопка с deep link на личку бота,
                # передаём group_chat_id через /start параметр
                bot_username = os.getenv("BOT_USERNAME", "")
                if bot_username:
                    url = f"https://t.me/{bot_username}?start=group_{chat_id}"
                    reply_markup = {
                        "inline_keyboard": [[{
                            "text": "🛒 Открыть список",
                            "url": url
                        }]]
                    }
                else:
                    # Fallback — прямая ссылка на webapp с chat_id группы
                    url = f"{WEBAPP_URL}?chat_id={chat_id}"
                    reply_markup = {
                        "inline_keyboard": [[{
                            "text": "🛒 Открыть список",
                            "url": url
                        }]]
                    }

            return make_response(
                chat_id,
                "🛒 *Koszyk — wspólne zakupy*\n\nNaciśnij przycisk, aby otworzyć listę:",
                reply_markup=reply_markup
            )

    # ── 2. Inline-запрос (если понадобится в будущем) ─────────────────────────
    # if "inline_query" in update:
    #     pass

    return None


class handler(BaseHTTPRequestHandler):
    def do_POST(self):
        length = int(self.headers.get("Content-Length", 0))
        body   = self.rfile.read(length)
        response_body = b"{}"

        try:
            update = json.loads(body)
            print(f"Update: {json.dumps(update)[:300]}")
            result = handle_update(update)
            if result:
                response_body = json.dumps(result).encode()
        except Exception as e:
            print(f"Error: {e}")

        self.send_response(200)
        self.send_header("Content-Type", "application/json")
        self.end_headers()
        self.wfile.write(response_body)

    def do_GET(self):
        self.send_response(200)
        self.end_headers()
        self.wfile.write(b"Webhook active")

    def log_message(self, *args):
        pass
