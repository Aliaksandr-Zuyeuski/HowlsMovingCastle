import os, json
from http.server import BaseHTTPRequestHandler

BOT_TOKEN  = os.getenv("BOT_TOKEN", "")
WEBAPP_URL = os.getenv("WEBAPP_URL", "")


def make_response(chat_id, text, reply_markup=None):
    """Вернуть ответ напрямую через webhook response."""
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
    if "message" not in update:
        return None

    msg     = update["message"]
    chat_id = msg["chat"]["id"]
    text    = msg.get("text", "")

    if "web_app_data" in msg:
        try:
            payload = json.loads(msg["web_app_data"]["data"])
        except Exception:
            return None
        actor  = msg.get("from", {}).get("first_name", "Участник")
        action = payload.get("action", "")
        name   = payload.get("name", "")
        amount = payload.get("amount", "")
        notifications = {
            "add":     f"🔔 *{actor}* dodał/a: *{name}*",
            "take":    f"🙋 *{actor}* bierze: *{name}*",
            "bought":  f"✅ *{actor}* kupił/a: *{name}*",
            "delete":  f"🗑 *{actor}* usunął/a: *{name}*",
            "expense": f"💰 *{actor}* dodał/a wydatek: *{amount} zł* — {name}",
        }
        msg_text = notifications.get(action)
        if msg_text:
            return make_response(chat_id, msg_text)
        return None

    if text.startswith("/start") or text.startswith("/list"):
        url = f"{WEBAPP_URL}?chat_id={chat_id}"
        chat_type = msg["chat"].get("type", "private")

        if chat_type == "private":
            # В личке — inline кнопка
            reply_markup = {
                "inline_keyboard": [[{
                    "text": "🛒 Открыть список",
                    "web_app": {"url": url}
                }]]
            }
        else:
            # В группе — reply keyboard (кнопка внизу чата)
            reply_markup = {
                "keyboard": [[{
                    "text": "🛒 Открыть список",
                    "web_app": {"url": url}
                }]],
                "resize_keyboard": True,
                "one_time_keyboard": False
            }

        return make_response(
            chat_id,
            "🛒 *Koszyk — wspólne zakupy*\n\nNaciśnij przycisk, aby otworzyć listę:",
            reply_markup=reply_markup
        )

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
