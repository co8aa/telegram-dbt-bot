import sqlite3
import logging
from datetime import datetime
from config import DATABASE_URL

logger = logging.getLogger(__name__)


def get_conn():
    conn = sqlite3.connect(DATABASE_URL)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    conn = get_conn()
    c = conn.cursor()
    c.execute("""
        CREATE TABLE IF NOT EXISTS users (
            user_id   INTEGER PRIMARY KEY,
            username  TEXT,
            first_name TEXT,
            joined_at DATETIME DEFAULT CURRENT_TIMESTAMP
        )
    """)
    c.execute("""
        CREATE TABLE IF NOT EXISTS diary (
            id         INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id    INTEGER,
            emotion    TEXT,
            intensity  INTEGER,
            situation  TEXT,
            thoughts   TEXT,
            impulse    TEXT,
            timestamp  DATETIME DEFAULT CURRENT_TIMESTAMP
        )
    """)
    c.execute("""
        CREATE TABLE IF NOT EXISTS skill_log (
            id        INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id   INTEGER,
            skill     TEXT,
            rating    INTEGER,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
        )
    """)
    conn.commit()
    conn.close()
    logger.info("DB initialised")


def upsert_user(user_id: int, username: str, first_name: str):
    conn = get_conn()
    conn.execute(
        "INSERT OR IGNORE INTO users (user_id, username, first_name) VALUES (?,?,?)",
        (user_id, username, first_name),
    )
    conn.commit()
    conn.close()


def add_diary_entry(user_id: int, emotion: str, intensity: int,
                    situation: str, thoughts: str, impulse: str):
    conn = get_conn()
    conn.execute(
        """INSERT INTO diary (user_id, emotion, intensity, situation, thoughts, impulse)
           VALUES (?,?,?,?,?,?)""",
        (user_id, emotion, intensity, situation, thoughts, impulse),
    )
    conn.commit()
    conn.close()


def get_diary_entries(user_id: int, limit: int = 7):
    conn = get_conn()
    rows = conn.execute(
        """SELECT emotion, intensity, situation, thoughts, timestamp
           FROM diary WHERE user_id=? ORDER BY timestamp DESC LIMIT ?""",
        (user_id, limit),
    ).fetchall()
    conn.close()
    return rows


def add_skill_log(user_id: int, skill: str, rating: int):
    conn = get_conn()
    conn.execute(
        "INSERT INTO skill_log (user_id, skill, rating) VALUES (?,?,?)",
        (user_id, skill, rating),
    )
    conn.commit()
    conn.close()


def get_week_stats(user_id: int):
    conn = get_conn()
    rows = conn.execute(
        """SELECT emotion, COUNT(*) as cnt FROM diary
           WHERE user_id=? AND timestamp >= datetime('now','-7 days')
           GROUP BY emotion ORDER BY cnt DESC LIMIT 5""",
        (user_id,),
    ).fetchall()
    conn.close()
    return rows
