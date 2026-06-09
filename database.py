"""
database.py — работа с базой данных
Поддерживает PostgreSQL (Supabase, Railway, PythonAnywhere и др.)
Переезд на другой сервис: поменяйте только DATABASE_URL
"""

import os
import psycopg2
from psycopg2.extras import RealDictCursor

DATABASE_URL = os.getenv("DATABASE_URL")


def get_conn():
    return psycopg2.connect(DATABASE_URL, cursor_factory=RealDictCursor)


def init_db():
    """Создать таблицы если не существуют."""
    with get_conn() as conn:
        with conn.cursor() as cur:
            cur.execute("""
                CREATE TABLE IF NOT EXISTS items (
                    id SERIAL PRIMARY KEY,
                    chat_id BIGINT NOT NULL,
                    name TEXT NOT NULL,
                    added_by TEXT NOT NULL,
                    taken_by TEXT,
                    done BOOLEAN DEFAULT FALSE,
                    created_at TIMESTAMP DEFAULT NOW()
                );

                CREATE TABLE IF NOT EXISTS expenses (
                    id SERIAL PRIMARY KEY,
                    chat_id BIGINT NOT NULL,
                    paid_by TEXT NOT NULL,
                    amount NUMERIC(10,2) NOT NULL,
                    description TEXT,
                    created_at TIMESTAMP DEFAULT NOW()
                );

                CREATE TABLE IF NOT EXISTS settings (
                    chat_id BIGINT PRIMARY KEY,
                    notif_add     BOOLEAN DEFAULT TRUE,
                    notif_take    BOOLEAN DEFAULT TRUE,
                    notif_bought  BOOLEAN DEFAULT TRUE,
                    notif_delete  BOOLEAN DEFAULT TRUE,
                    notif_expense BOOLEAN DEFAULT TRUE,
                    list_message_id BIGINT DEFAULT NULL
                );
            """)
        conn.commit()


# ── Список покупок ───────────────────────────────────────────────

def get_items(chat_id: int):
    with get_conn() as conn:
        with conn.cursor() as cur:
            cur.execute(
                "SELECT * FROM items WHERE chat_id=%s ORDER BY done ASC, id ASC",
                (chat_id,)
            )
            return [dict(r) for r in cur.fetchall()]


def add_items(chat_id: int, names: list, added_by: str):
    with get_conn() as conn:
        with conn.cursor() as cur:
            for name in names:
                cur.execute(
                    "INSERT INTO items (chat_id, name, added_by) VALUES (%s,%s,%s)",
                    (chat_id, name, added_by)
                )
        conn.commit()


def take_item(item_id: int, taken_by: str):
    with get_conn() as conn:
        with conn.cursor() as cur:
            cur.execute(
                "UPDATE items SET taken_by=%s WHERE id=%s AND taken_by IS NULL",
                (taken_by, item_id)
            )
        conn.commit()


def release_item(item_id: int):
    with get_conn() as conn:
        with conn.cursor() as cur:
            cur.execute("UPDATE items SET taken_by=NULL WHERE id=%s", (item_id,))
        conn.commit()


def buy_item(item_id: int, taken_by: str):
    with get_conn() as conn:
        with conn.cursor() as cur:
            cur.execute(
                "UPDATE items SET done=TRUE, taken_by=COALESCE(taken_by,%s) WHERE id=%s",
                (taken_by, item_id)
            )
        conn.commit()


def delete_item(item_id: int):
    with get_conn() as conn:
        with conn.cursor() as cur:
            cur.execute("SELECT name FROM items WHERE id=%s", (item_id,))
            row = cur.fetchone()
            cur.execute("DELETE FROM items WHERE id=%s", (item_id,))
        conn.commit()
    return row["name"] if row else ""


def clear_done(chat_id: int):
    with get_conn() as conn:
        with conn.cursor() as cur:
            cur.execute(
                "DELETE FROM items WHERE chat_id=%s AND done=TRUE", (chat_id,)
            )
            count = cur.rowcount
        conn.commit()
    return count


# ── Расходы ──────────────────────────────────────────────────────

def get_expenses(chat_id: int):
    with get_conn() as conn:
        with conn.cursor() as cur:
            cur.execute(
                "SELECT * FROM expenses WHERE chat_id=%s ORDER BY id DESC LIMIT 50",
                (chat_id,)
            )
            rows = cur.fetchall()
    result = []
    for r in rows:
        d = dict(r)
        d["amount"] = float(d["amount"])
        d["created_at"] = str(d["created_at"])[:10]
        result.append(d)
    return result


def add_expense(chat_id: int, paid_by: str, amount: float, description: str):
    with get_conn() as conn:
        with conn.cursor() as cur:
            cur.execute(
                "INSERT INTO expenses (chat_id, paid_by, amount, description) VALUES (%s,%s,%s,%s)",
                (chat_id, paid_by, amount, description)
            )
        conn.commit()


def get_balance(chat_id: int):
    with get_conn() as conn:
        with conn.cursor() as cur:
            cur.execute(
                "SELECT paid_by, SUM(amount) as total FROM expenses WHERE chat_id=%s GROUP BY paid_by",
                (chat_id,)
            )
            rows = cur.fetchall()
    totals = {r["paid_by"]: float(r["total"]) for r in rows}
    total_sum = sum(totals.values())
    share = total_sum / len(totals) if totals else 0
    return totals, share


# ── Настройки и message_id ────────────────────────────────────────

def get_settings(chat_id: int) -> dict:
    with get_conn() as conn:
        with conn.cursor() as cur:
            cur.execute("SELECT * FROM settings WHERE chat_id=%s", (chat_id,))
            row = cur.fetchone()
    if row:
        return dict(row)
    return {
        "chat_id": chat_id,
        "notif_add": True,
        "notif_take": True,
        "notif_bought": True,
        "notif_delete": True,
        "notif_expense": True,
        "list_message_id": None,
    }


def save_settings(chat_id: int, settings: dict):
    with get_conn() as conn:
        with conn.cursor() as cur:
            cur.execute("""
                INSERT INTO settings (chat_id, notif_add, notif_take, notif_bought, notif_delete, notif_expense)
                VALUES (%s, %s, %s, %s, %s, %s)
                ON CONFLICT (chat_id) DO UPDATE SET
                    notif_add     = EXCLUDED.notif_add,
                    notif_take    = EXCLUDED.notif_take,
                    notif_bought  = EXCLUDED.notif_bought,
                    notif_delete  = EXCLUDED.notif_delete,
                    notif_expense = EXCLUDED.notif_expense
            """, (
                chat_id,
                settings.get("notif_add", True),
                settings.get("notif_take", True),
                settings.get("notif_bought", True),
                settings.get("notif_delete", True),
                settings.get("notif_expense", True),
            ))
        conn.commit()


def get_list_message_id(chat_id: int) -> int | None:
    with get_conn() as conn:
        with conn.cursor() as cur:
            cur.execute("SELECT list_message_id FROM settings WHERE chat_id=%s", (chat_id,))
            row = cur.fetchone()
    return row["list_message_id"] if row else None


def set_list_message_id(chat_id: int, message_id: int | None):
    with get_conn() as conn:
        with conn.cursor() as cur:
            cur.execute("""
                INSERT INTO settings (chat_id, list_message_id)
                VALUES (%s, %s)
                ON CONFLICT (chat_id) DO UPDATE SET list_message_id = EXCLUDED.list_message_id
            """, (chat_id, message_id))
        conn.commit()
