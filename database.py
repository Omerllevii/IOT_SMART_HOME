"""SQLite local database layer for KitchenGuard IoT."""
from __future__ import annotations

import sqlite3
from datetime import datetime
from pathlib import Path
from typing import Iterable, Tuple

from config import DB_FILE


def get_connection() -> sqlite3.Connection:
    conn = sqlite3.connect(DB_FILE, check_same_thread=False)
    conn.row_factory = sqlite3.Row
    return conn


def init_db() -> None:
    with get_connection() as conn:
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS sensor_data (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp TEXT NOT NULL,
                sensor TEXT NOT NULL,
                value REAL NOT NULL,
                unit TEXT,
                status TEXT NOT NULL,
                raw_message TEXT
            )
            """
        )
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS events (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp TEXT NOT NULL,
                event_type TEXT NOT NULL,
                message TEXT NOT NULL,
                severity TEXT NOT NULL
            )
            """
        )
        conn.commit()


def now() -> str:
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")


def insert_sensor(sensor: str, value: float, unit: str, status: str, raw_message: str = "") -> None:
    with get_connection() as conn:
        conn.execute(
            """
            INSERT INTO sensor_data(timestamp, sensor, value, unit, status, raw_message)
            VALUES (?, ?, ?, ?, ?, ?)
            """,
            (now(), sensor, value, unit, status, raw_message),
        )
        conn.commit()


def insert_event(event_type: str, message: str, severity: str = "INFO") -> None:
    with get_connection() as conn:
        conn.execute(
            """
            INSERT INTO events(timestamp, event_type, message, severity)
            VALUES (?, ?, ?, ?)
            """,
            (now(), event_type, message, severity),
        )
        conn.commit()


def latest_sensor_values() -> dict:
    query = """
        SELECT sensor, value, unit, status, timestamp
        FROM sensor_data s1
        WHERE id = (
            SELECT MAX(id) FROM sensor_data s2 WHERE s2.sensor = s1.sensor
        )
    """
    with get_connection() as conn:
        rows = conn.execute(query).fetchall()
    return {row["sensor"]: dict(row) for row in rows}


def latest_events(limit: int = 10) -> Iterable[sqlite3.Row]:
    with get_connection() as conn:
        return conn.execute(
            "SELECT * FROM events ORDER BY id DESC LIMIT ?", (limit,)
        ).fetchall()


if __name__ == "__main__":
    init_db()
    print(f"Database is ready: {Path(DB_FILE).resolve()}")
