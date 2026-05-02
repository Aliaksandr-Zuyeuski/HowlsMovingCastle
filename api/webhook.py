import os, json
from http.server import BaseHTTPRequestHandler
import urllib.request
import urllib.parse

BOT_TOKEN  = os.getenv("BOT_TOKEN", "")
WEBAPP_URL = os.getenv("WEBAPP_URL", "")


def send_message(chat_id, text, reply_markup=None):
    data = {
        "chat_id": chat_id,
        "text": text,
        "parse_mode": "Markdown"
    }
    if reply_markup:
        data["reply_markup"] = json.dumps(reply_markup)

    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    body = json.dumps(data).encode("utf-8")
    req = urllib.request.Request(
        url, data=body,
        headers={"Content-Type": "application/json"}
    )
    try:
        resp = urllib.request.urlopen(req, timeout=10)
        return resp.read()
    except Exception as e:
        print(f"send_message error: {e}")
        return None


def open_app_keyboard(chat_id):
    url = f"{WEBAPP_URL}?chat_id={chat_id}"
    return {
        "inline_keyboard": [[{
            "text": "🛒 Открыть список",
            "web_app": {"url": url}
        }]]
    }


def handle_update(update):
    if "message" not in update:
        return

    msg     = update["message"]
    chat_id = msg["chat"]["id"]
    text    = msg.get("text", "")

    # WebApp data
    if "web_app_data" in msg:
        try:
            payload = json.loads(msg["web_app_data"]["data"])
        except Exception:
            return
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
            send_message(chat_id, msg_text)
        return

    if text.startswith("/start"):
        send_message(
            chat_id,
            "🛒 *Koszyk — wspólne zakupy*\n\nNaciśnij przycisk, aby otworzyć listę:",
            reply_markup=open_app_keyboard(chat_id)
        )
    elif text.startswith("/list"):
        send_message(
            chat_id,
            "Otwórz listę zakupów:",
            reply_markup=open_app_keyboard(chat_id)
        )


class handler(BaseHTTPRequestHandler):
    def do_POST(self):
        length = int(self.headers.get("Content-Length", 0))
        body   = self.rfile.read(length)
        try:
            update = json.loads(body)
            print(f"Update: {json.dumps(update)[:200]}")
            handle_update(update)
        except Exception as e:
            print(f"Error: {e}")
        self.send_response(200)
        self.end_headers()
        self.wfile.write(b"OK")

    def do_GET(self):
        self.send_response(200)
        self.end_headers()
        self.wfile.write(b"Webhook active")

    def log_message(self, *args):
        pass
