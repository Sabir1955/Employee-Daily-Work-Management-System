import os
import sqlite3
from contextlib import contextmanager


DATABASE_PATH = os.environ.get("PORTAL_DATABASE", os.path.join(os.path.dirname(__file__), "portal.db"))


@contextmanager
def get_db():
    connection = sqlite3.connect(DATABASE_PATH)
    connection.row_factory = sqlite3.Row
    connection.execute("PRAGMA foreign_keys = ON")
    try:
        yield connection
        connection.commit()
    finally:
        connection.close()


def init_db():
    with get_db() as db:
        db.executescript(
            """
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT UNIQUE NOT NULL,
                password_hash TEXT NOT NULL,
                role TEXT NOT NULL DEFAULT 'employee' CHECK(role IN ('admin', 'employee')),
                is_active INTEGER NOT NULL DEFAULT 1,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP
            );
            CREATE TABLE IF NOT EXISTS files (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                username TEXT NOT NULL,
                folder TEXT NOT NULL CHECK(folder IN ('personal', 'common')),
                original_name TEXT NOT NULL,
                stored_name TEXT UNIQUE NOT NULL,
                size INTEGER NOT NULL,
                uploaded_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY(user_id) REFERENCES users(id) ON DELETE CASCADE
            );
            CREATE TABLE IF NOT EXISTS activity_logs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER,
                username TEXT,
                action TEXT NOT NULL,
                detail TEXT,
                ip TEXT NOT NULL,
                status TEXT NOT NULL CHECK(status IN ('success', 'failed')),
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP
            );
            """
        )

