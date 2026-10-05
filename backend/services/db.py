"""SQLite wrapper — single-file database."""
import sqlite3
import os
from contextlib import contextmanager
from backend.config import DATA_FOLDER

DB_PATH = os.path.join(DATA_FOLDER, "damagegenx.db")


def init_db():
    with connect() as conn:
        cur = conn.cursor()
        cur.execute("""
            CREATE TABLE IF NOT EXISTS inspections (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                inspection_id TEXT UNIQUE NOT NULL,
                created_at TEXT NOT NULL,
                vehicle_type TEXT NOT NULL,
                dominant_damage TEXT,
                severity_score INTEGER,
                severity_label TEXT,
                hidden_risk REAL,
                hidden_level TEXT,
                repair_action TEXT,
                cost_min INTEGER,
                cost_max INTEGER,
                image_count INTEGER,
                user_id INTEGER,
                latitude REAL,
                longitude REAL
            )
        """)
        cur.execute("""
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT UNIQUE NOT NULL,
                email TEXT,
                password_hash TEXT NOT NULL,
                role TEXT DEFAULT 'inspector',
                created_at TEXT NOT NULL
            )
        """)
        cur.execute("""
            CREATE TABLE IF NOT EXISTS evidence (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                evidence_id TEXT UNIQUE NOT NULL,
                inspection_id TEXT,
                filename TEXT NOT NULL,
                sha256 TEXT NOT NULL,
                size_bytes INTEGER,
                uploaded_at TEXT NOT NULL,
                uploader TEXT
            )
        """)
        conn.commit()


@contextmanager
def connect():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    try:
        yield conn
    finally:
        conn.close()


init_db()