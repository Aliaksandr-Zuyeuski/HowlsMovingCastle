"""
api/settings.py — API для настроек уведомлений
"""

import os, json, sys
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from http.server import BaseHTTPRequestHandler
from urllib.parse import urlparse, parse_qs
import database as db


class handler(BaseHTTPRequestHandler):

    def _json(self, data, status=200):
        body = json.dumps(data, ensure_ascii=False).encode()
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
        qs = parse_qs(urlparse(self.path).query)
        chat_id = int(qs.get("chat_id", [0])[0])
        self._json(db.get_settings(chat_id))

    def do_POST(self):
        qs = parse_qs(urlparse(self.path).query)
        chat_id = int(qs.get("chat_id", [0])[0])
        data = self._body()
        db.save_settings(chat_id, data)
        self._json({"ok": True})

    def log_message(self, *args):
        pass
