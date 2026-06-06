"""
api/notify.py — живое сообщение в группе: удаляет старое, шлёт новое
"""

import os, json, sys, urllib.request
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from http.server import BaseHTTPRequestHandler
import database as db
from auth import verify_init_data, AuthError

BOT_TOKEN    = os.getenv("BOT_TOKEN", "")
BOT_USERNAME = os.getenv("BOT_USERNAME", "")
BOT_APP_NAME = os.getenv("BOT_APP_NAME", "app")
WEBAPP_URL   = os.getenv("WEBAPP_URL", "")


def tg(method: str, payload: dict) -> dict:
    req = urllib.request.Request(
        f"https://api.telegram.org/bot{BOT_TOKEN}/{method}",
        data=json.dumps(payload).encode(),
        headers={"Content-Type": "application/json"},
        method="POST"
    )
    try:
        with urllib.request.urlopen(req) as r:
            return json.loads(r.read())
    except Exception as e:
        print(f"tg error {method}: {e}")
        return {"ok": False}


def open_list_button(chat_id) -> dict | None:
    cid = str(chat_id)
    if cid.startswith("-") and BOT_USERNAME and BOT_APP_NAME:
        start_param = "g" + cid.lstrip("-")
        return {"text": "🛒 Адкрыць спіс", "url": f"https://t.me/{BOT_USERNAME}/{BOT_APP_NAME}?startapp={start_param}"}
    elif WEBAPP_URL:
        return {"text": "🛒 Адкрыць спіс", "web_app": {"url": f"{WEBAPP_URL}?user_id={chat_id}"}}
    return None


def build_message(chat_id: int) -> str | None:
    items = db.get_items(chat_id)
    active = [i for i in items if not i["done"]]
    if not active:
        return None

    groups = {}
    for item in active:
        groups.setdefault(item["added_by"], []).append(item)

    lines = []
    for actor, actor_items in groups.items():
        lines.append(f"🔔 *{actor}* дадаў/ла ў спіс:")
        for item in actor_items:
            name = item["name"]
            if item["taken_by"]:
                lines.append(f"• ~{name}~ 🟠")
            else:
                lines.append(f"• {name}")
        lines.append("")

    return "\n".join(lines).strip()


def update_group_message(chat_id: int):
    lock_key = abs(chat_id) % 2147483647

    try:
        with db.get_conn() as conn:
            with conn.cursor() as cur:
                cur.execute("SELECT pg_try_advisory_lock(%s)", (lock_key,))
                acquired = cur.fetchone()[0]
            if not acquired:
                return

            try:
                old_msg_id = db.get_list_message_id(chat_id)

                if old_msg_id:
                    tg("deleteMessage", {"chat_id": chat_id, "message_id": old_msg_id})
                    db.set_list_message_id(chat_id, None)

                text = build_message(chat_id)
                if not text:
                    return

                payload = {
                    "chat_id": chat_id,
                    "text": text,
                    "parse_mode": "MarkdownV2",
                }
                btn = open_list_button(chat_id)
                if btn:
                    payload["reply_markup"] = {"inline_keyboard": [[btn]]}

                result = tg("sendMessage", payload)
                if result.get("ok"):
                    db.set_list_message_id(chat_id, result["result"]["message_id"])
            finally:
                with conn.cursor() as cur:
                    cur.execute("SELECT pg_advisory_unlock(%s)", (lock_key,))
    except Exception as e:
        print(f"update_group_message error: {e}")


class handler(BaseHTTPRequestHandler):

    def _json(self, data, status=200):
        body = json.dumps(data).encode()
        self.send_response(status)
        self.send_header("Content-Type", "application/json")
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "POST,OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type,X-Init-Data")
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

        data          = self._body()
        chat_id       = data.get("chat_id")
        action        = data.get("action", "")
        group_chat_id = data.get("group_chat_id")

        if not chat_id or not action:
            self._json({"ok": False, "error": "missing fields"})
            return

        target_id = int(group_chat_id) if group_chat_id else None
        if not target_id or not str(target_id).startswith("-"):
            self._json({"ok": True, "skipped": True})
            return

        settings = db.get_settings(target_id)
        if not settings.get(f"notif_{action}", True):
            self._json({"ok": True, "skipped": True})
            return

        if action == "expense":
            actor  = data.get("user", "Удзельнік")
            amount = data.get("amount", "")
            name   = data.get("name", "")
            tg("sendMessage", {
                "chat_id": target_id,
                "text": f"💰 *{actor}* дадаў/ла выдатак: *{amount} р* — {name}",
                "parse_mode": "Markdown",
            })
            self._json({"ok": True})
            return

        update_group_message(target_id)
        self._json({"ok": True})

    def log_message(self, *args):
        pass
