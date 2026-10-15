"""Database row helpers.

These functions convert sqlite3.Row objects into plain dictionaries
that Pydantic response models can serialize.
"""

from __future__ import annotations

from sqlite3 import Row
from typing import Any


def row_to_student(row: Row) -> dict[str, Any]:
    """Convert a database row into a student dictionary."""
    return {
        "student_id": row["student_id"],
        "name": row["name"],
        "date_of_birth": row["date_of_birth"],
        "email": row["email"],
        "phone": row["phone"],
        "course": row["course"],
        "address": row["address"],
        "enrollment_date": row["enrollment_date"],
    }
