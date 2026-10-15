"""SQLite connection helpers and table creation.

The database file is created automatically the first time the app starts.
Override the path with the DATABASE_PATH environment variable (used by tests).
"""

from __future__ import annotations

import os
import sqlite3
from collections.abc import Generator
from contextlib import contextmanager
from pathlib import Path

from dotenv import load_dotenv

load_dotenv()

DEFAULT_DB_PATH = "students.db"


def get_db_path() -> str:
    """Return the SQLite file path from the environment or the default."""
    return os.getenv("DATABASE_PATH", DEFAULT_DB_PATH)


def get_connection() -> sqlite3.Connection:
    """Open a SQLite connection with row access by column name."""
    db_path = get_db_path()
    parent = Path(db_path).parent
    if parent and str(parent) not in (".", ""):
        parent.mkdir(parents=True, exist_ok=True)

    connection = sqlite3.connect(db_path, check_same_thread=False)
    connection.row_factory = sqlite3.Row
    connection.execute("PRAGMA foreign_keys = ON")
    return connection


@contextmanager
def get_db() -> Generator[sqlite3.Connection, None, None]:
    """Yield a connection and always close it afterwards."""
    connection = get_connection()
    try:
        yield connection
        connection.commit()
    except Exception:
        connection.rollback()
        raise
    finally:
        connection.close()


def init_db() -> None:
    """Create the students table if it does not already exist."""
    with get_db() as connection:
        connection.execute(
            """
            CREATE TABLE IF NOT EXISTS students (
                student_id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                date_of_birth TEXT NOT NULL,
                email TEXT UNIQUE,
                phone TEXT,
                course TEXT,
                address TEXT,
                enrollment_date TEXT
            )
            """
        )
        connection.execute(
            """
            CREATE UNIQUE INDEX IF NOT EXISTS idx_students_email
            ON students(email)
            WHERE email IS NOT NULL
            """
        )
