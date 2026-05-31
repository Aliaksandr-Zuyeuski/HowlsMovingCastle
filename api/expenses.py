"""
api/expenses.py — API для расходов и баланса
"""

import os, json, sys
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from http.server import BaseHTTPRequestHandler
from urllib.parse import urlparse, parse_qs
import database as db
from auth import verify_init_data, AuthError


class handler(BaseHTTPRequestHandler):

    def _json(self, data, status=200):
        body = json.dumps(data, ensure_ascii=False, default=str).encode()
        self.send_response(status)
        self.send_header("Content-Type", "application/json")
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "GET,POST,OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type")
        self.end_headers()
        self.wfile.write(body)

    def _body(self):
        length = int(self.headers.get("Content-Length", 0))
        return json.loads(self.rfile.read(length)) if length else {}

    def do_OPTIONS(self):
        self._json({})

    def do_GET(self):
        try:
            verify_init_data(self.headers.get("X-Init-Data", ""))
        except AuthError as e:
            self._json({"ok": False, "error": str(e)}, status=401)
            return
        qs = parse_qs(urlparse(self.path).query)
        chat_id = int(qs.get("chat_id", [0])[0])
        action = qs.get("action", ["list"])[0]

        if action == "balance":
            totals, share = db.get_balance(chat_id)
            self._json({"totals": totals, "share": share})
        else:
            self._json(db.get_expenses(chat_id))

    def do_POST(self):
        try:
            verify_init_data(self.headers.get("X-Init-Data", ""))
        except AuthError as e:
            self._json({"ok": False, "error": str(e)}, status=401)
            return
        qs = parse_qs(urlparse(self.path).query)
        chat_id = int(qs.get("chat_id", [0])[0])
        data = self._body()
        db.add_expense(
            chat_id,
            data.get("paid_by", "?"),
            float(data.get("amount", 0)),
            data.get("description", "")
        )
        self._json({"ok": True})

    def log_message(self, *args):
        pass
