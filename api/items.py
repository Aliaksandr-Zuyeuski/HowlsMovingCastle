"""
api/items.py — REST API для списка покупок
Vercel вызывает эту функцию для запросов /api/items
"""

import os, json, sys
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from http.server import BaseHTTPRequestHandler
from urllib.parse import urlparse, parse_qs
import database as db


class handler(BaseHTTPRequestHandler):

    def _json(self, data, status=200):
        body = json.dumps(data, ensure_ascii=False, default=str).encode()
        self.send_response(status)
        self.send_header("Content-Type", "application/json")
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "GET,POST,DELETE,OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type")
        self.end_headers()
        self.wfile.write(body)

    def _body(self):
        length = int(self.headers.get("Content-Length", 0))
        return json.loads(self.rfile.read(length)) if length else {}

    def do_OPTIONS(self):
        self._json({})

    def do_GET(self):
        qs = parse_qs(urlparse(self.path).query)
        chat_id = int(qs.get("chat_id", [0])[0])
        self._json(db.get_items(chat_id))

    def do_POST(self):
        qs = parse_qs(urlparse(self.path).query)
        chat_id = int(qs.get("chat_id", [0])[0])
        data = self._body()
        action = qs.get("action", ["add"])[0]

        if action == "add":
            names = [n.strip() for n in data.get("name","").split(",") if n.strip()]
            db.add_items(chat_id, names, data.get("added_by", "?"))
            self._json({"ok": True, "names": names})

        elif action == "take":
            db.take_item(data["id"], data["user"])
            self._json({"ok": True})

        elif action == "release":
            db.release_item(data["id"])
            self._json({"ok": True})

        elif action == "buy":
            db.buy_item(data["id"], data["user"])
            self._json({"ok": True})

        elif action == "delete":
            name = db.delete_item(data["id"])
            self._json({"ok": True, "name": name})

        elif action == "clear":
            n = db.clear_done(chat_id)
            self._json({"ok": True, "removed": n})

    def do_DELETE(self):
        data = self._body()
        name = db.delete_item(data["id"])
        self._json({"ok": True, "name": name})

    def log_message(self, *args):
        pass
