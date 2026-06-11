import sqlite3
import os
import logging
from datetime import date

logger = logging.getLogger(__name__)

DB_PATH = os.getenv("DB_PATH", "mood_tracker.db")


def get_conn():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys=ON")
    return conn


def init_db():
    conn = get_conn()
    conn.executescript("""
        CREATE TABLE IF NOT EXISTS users (
            user_id       INTEGER PRIMARY KEY,
            username      TEXT NOT NULL DEFAULT '',
            reminder_time TEXT,
            created_at    TEXT NOT NULL DEFAULT (datetime('now'))
        );

        CREATE TABLE IF NOT EXISTS entries (
            id           INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id      INTEGER NOT NULL REFERENCES users(user_id) ON DELETE CASCADE,
            entry_date   TEXT NOT NULL DEFAULT (date('now')),
            mood         INTEGER NOT NULL CHECK(mood BETWEEN 1 AND 5),
            study_hours  REAL NOT NULL CHECK(study_hours >= 0),
            sleep_hours  REAL NOT NULL CHECK(sleep_hours >= 0),
            comment      TEXT,
            created_at   TEXT NOT NULL DEFAULT (datetime('now'))
        );

        CREATE INDEX IF NOT EXISTS idx_entries_user_date
            ON entries(user_id, entry_date DESC);
    """)
    conn.commit()
    conn.close()
    logger.info("База данных готова: %s", DB_PATH)


def ensure_user(user_id: int, username: str):
    conn = get_conn()
    conn.execute(
        "INSERT OR IGNORE INTO users (user_id, username) VALUES (?, ?)",
        (user_id, username)
    )
    conn.commit()
    conn.close()


def get_reminder_time(user_id: int):
    conn = get_conn()
    row = conn.execute(
        "SELECT reminder_time FROM users WHERE user_id = ?", (user_id,)
    ).fetchone()
    conn.close()
    return row["reminder_time"] if row else None


def set_reminder_time(user_id: int, time_str: str):
    conn = get_conn()
    conn.execute(
        "UPDATE users SET reminder_time = ? WHERE user_id = ?",
        (time_str, user_id)
    )
    conn.commit()
    conn.close()


def add_entry(user_id: int, mood: int, study_hours: float,
              sleep_hours: float, comment: str | None):
    today = date.today().isoformat()
    conn = get_conn()
    conn.execute(
        """
        INSERT INTO entries (user_id, entry_date, mood, study_hours, sleep_hours, comment)
        VALUES (?, ?, ?, ?, ?, ?)
        """,
        (user_id, today, mood, study_hours, sleep_hours, comment)
    )
    conn.commit()
    conn.close()


def get_history(user_id: int, limit: int = 10):
    conn = get_conn()
    rows = conn.execute(
        """
        SELECT entry_date, mood, study_hours, sleep_hours, comment
        FROM entries
        WHERE user_id = ?
        ORDER BY id DESC
        LIMIT ?
        """,
        (user_id, limit)
    ).fetchall()
    conn.close()
    return [(r["entry_date"], r["mood"], r["study_hours"], r["sleep_hours"], r["comment"])
            for r in rows]


def get_entries_for_period(user_id: int, days: int):
    conn = get_conn()
    rows = conn.execute(
        """
        SELECT id, entry_date, mood, study_hours, sleep_hours
        FROM entries
        WHERE user_id = ?
          AND entry_date >= date('now', ? || ' days')
        ORDER BY id
        """,
        (user_id, f"-{days}")
    ).fetchall()
    conn.close()
    return [dict(r) for r in rows]


def clear_user_data(user_id: int):
    conn = get_conn()
    conn.execute("DELETE FROM entries WHERE user_id = ?", (user_id,))
    conn.commit()
    conn.close()


def get_all_users_with_reminders():
    conn = get_conn()
    rows = conn.execute(
        "SELECT user_id, reminder_time FROM users WHERE reminder_time IS NOT NULL"
    ).fetchall()
    conn.close()
    return [(r["user_id"], r["reminder_time"]) for r in rows]
