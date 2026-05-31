"""
api/notify.py — отправка уведомлений в Telegram-чат с учётом настроек
"""

import os, json, sys, urllib.request
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from http.server import BaseHTTPRequestHandler
import database as db
from auth import verify_init_data, AuthError

BOT_TOKEN = os.getenv("BOT_TOKEN", "")


class handler(BaseHTTPRequestHandler):

    def _json(self, data, status=200):
        body = json.dumps(data).encode()
        self.send_response(status)
        self.send_header("Content-Type", "application/json")
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "POST,OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type")
        self.end_headers()
        self.wfile.write(body)

    def _body(self):
        length = int(self.headers.get("Content-Length", 0))
        return json.loads(self.rfile.read(length)) if length else {}

    def do_OPTIONS(self):
        self._json({})

    def do_POST(self):
        try:
            verify_init_data(self.headers.get("X-Init-Data", ""))
        except AuthError as e:
            self._json({"ok": False, "error": str(e)}, status=401)
            return

        data = self._body()

        chat_id = data.get("chat_id")
        action  = data.get("action", "")
        name    = data.get("name", "")
        amount  = data.get("amount", "")
        actor   = data.get("user", "Удзельнік")

        if not chat_id or not action:
            self._json({"ok": False, "error": "missing fields"})
            return

        # Проверяем настройки — нужно ли слать уведомление
        settings = db.get_settings(int(chat_id))
        if not settings.get(f"notif_{action}", True):
            self._json({"ok": True, "skipped": True})
            return

        # Для добавления — если несколько товаров через запятую, делаем список
        if action == "add":
            items = [i.strip() for i in name.split(",") if i.strip()]
            if len(items) > 1:
                bullet_list = "\n".join(f"• {i}" for i in items)
                msg_text = f"🔔 *{actor}* дадаў/ла ў спіс:\n{bullet_list}"
            else:
                msg_text = f"🔔 *{actor}* дадаў/ла: *{name}*"
        else:
            notifications = {
                "take":    f"🙋 *{actor}* бярэ: *{name}*",
                "bought":  f"✅ *{actor}* купіў/ла: *{name}*",
                "delete":  f"🗑 *{actor}* выдаліў/ла: *{name}*",
                "expense": f"💰 *{actor}* дадаў/ла выдатак: *{amount} р* — {name}",
            }
            msg_text = notifications.get(action)

        if not msg_text:
            self._json({"ok": False, "error": "unknown action"})
            return

        payload = json.dumps({
            "chat_id": chat_id,
            "text": msg_text,
            "parse_mode": "Markdown"
        }).encode()

        req = urllib.request.Request(
            f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage",
            data=payload,
            headers={"Content-Type": "application/json"},
            method="POST"
        )
        try:
            with urllib.request.urlopen(req) as resp:
                result = json.loads(resp.read())
                self._json({"ok": result.get("ok", False)})
        except Exception as e:
            print(f"notify error: {e}")
            self._json({"ok": False, "error": str(e)})

    def log_message(self, *args):
        pass