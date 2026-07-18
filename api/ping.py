"""
api/ping.py — keepalive для Supabase, вызывается через Vercel Cron
"""

import sys, os, json
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

import database as db
from http.server import BaseHTTPRequestHandler


class handler(BaseHTTPRequestHandler):

    def do_GET(self):
        try:
            with db.get_conn() as conn:
                with conn.cursor() as cur:
                    cur.execute("SELECT 1")
            body = b'{"ok": true}'
        except Exception as e:
            print(f"ping error: {e}")
            body = b'{"ok": false}'

        self.send_response(200)
        self.send_header("Content-Type", "application/json")
        self.end_headers()
        self.wfile.write(body)

    def log_message(self, *args):
        pass
