"""
api/webhook.py — Telegram бот через webhook
Vercel вызывает эту функцию когда Telegram присылает обновление

Переезд на polling (PythonAnywhere и др.):
  Замените последние строки на run_polling() — см. комментарий внизу
"""

import os, json, sys
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from http.server import BaseHTTPRequestHandler
import database as db

BOT_TOKEN  = os.getenv("BOT_TOKEN")
WEBAPP_URL = os.getenv("WEBAPP_URL")

import urllib.request

def tg_api(method, data):
    """Вызвать метод Telegram Bot API."""
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/{method}"
    req = urllib.request.Request(
        url,
        data=json.dumps(data).encode(),
        headers={"Content-Type": "application/json"}
    )
    try:
        urllib.request.urlopen(req)
    except Exception as e:
        print(f"TG API error: {e}")


def send(chat_id, text, parse_mode="Markdown", reply_markup=None):
    data = {"chat_id": chat_id, "text": text, "parse_mode": parse_mode}
    if reply_markup:
        data["reply_markup"] = reply_markup
    tg_api("sendMessage", data)


def open_app_keyboard():
    return {
        "inline_keyboard": [[{
            "text": "🛒 Открыть список",
            "web_app": {"url": WEBAPP_URL}
        }]]
    }


def handle_update(update):
    """Обработать входящее обновление от Telegram."""

    # Данные из мини-приложения
    if "message" in update:
        msg = update["message"]
        chat_id = msg["chat"]["id"]
        user = msg.get("from", {})
        actor = user.get("first_name") or user.get("username") or "Участник"

        # WebApp data — уведомление в группу
        if "web_app_data" in msg:
            try:
                payload = json.loads(msg["web_app_data"]["data"])
            except Exception:
                return

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
                send(chat_id, msg_text)
            return

        # Обычное сообщение
        text = msg.get("text", "")

        if text == "/start":
            db.init_db()
            send(
                chat_id,
                "🛒 *Koszyk — wspólne zakupy*\n\nNaciśnij przycisk, aby otworzyć listę zakupów:",
                reply_markup=open_app_keyboard()
            )

        elif text == "/list":
            send(chat_id, "Otwórz listę:", reply_markup=open_app_keyboard())


# ── Vercel handler ───────────────────────────────────────────────

class handler(BaseHTTPRequestHandler):
    def do_POST(self):
        length = int(self.headers.get("Content-Length", 0))
        body = self.rfile.read(length)
        try:
            update = json.loads(body)
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


# ── Для переезда на polling (PythonAnywhere, локально) ───────────
# Раскомментируйте и запустите: python api/webhook.py
#
# from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, WebAppInfo
# from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes
#
# async def start(update, ctx):
#     kb = InlineKeyboardMarkup([[InlineKeyboardButton("🛒 Открыть список", web_app=WebAppInfo(url=WEBAPP_URL))]])
#     await update.message.reply_text("🛒 Koszyk", reply_markup=kb)
#
# async def webapp_data(update, ctx):
#     payload = json.loads(update.message.web_app_data.data)
#     actor = update.effective_user.first_name
#     action, name = payload.get("action"), payload.get("name","")
#     msgs = {"add":f"🔔 *{actor}* dodał/a: *{name}*","take":f"🙋 *{actor}* bierze: *{name}*",
#             "bought":f"✅ *{actor}* kupił/a: *{name}*","delete":f"🗑 *{actor}* usunął/a: *{name}*"}
#     if msgs.get(action):
#         await ctx.bot.send_message(update.effective_chat.id, msgs[action], parse_mode="Markdown")
#
# app = Application.builder().token(BOT_TOKEN).build()
# app.add_handler(CommandHandler("start", start))
# app.add_handler(MessageHandler(filters.StatusUpdate.WEB_APP_DATA, webapp_data))
# app.run_polling()
