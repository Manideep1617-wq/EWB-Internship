"""Safe, parameterized SQLite operations for student records."""

from __future__ import annotations

import sqlite3
from datetime import date

from app.models import row_to_student


class DuplicateEmailError(Exception):
    """Raised when an email is already stored for another student."""


class StudentNotFoundError(Exception):
    """Raised when a student_id does not exist."""


def _date_to_iso(value: date | None) -> str | None:
    return value.isoformat() if value else None


def _normalize_email(email: str | None) -> str | None:
    if email is None:
        return None
    return str(email).strip().lower()


def create_student(connection: sqlite3.Connection, data: dict) -> dict:
    """Insert a student and return the stored record."""
    values = (
        data["name"],
        _date_to_iso(data["date_of_birth"]),
        _normalize_email(data.get("email")),
        data.get("phone"),
        data.get("course"),
        data.get("address"),
        _date_to_iso(data.get("enrollment_date")),
    )
    try:
        cursor = connection.execute(
            """
            INSERT INTO students (
                name, date_of_birth, email, phone, course, address, enrollment_date
            )
            VALUES (?, ?, ?, ?, ?, ?, ?)
            """,
            values,
        )
    except sqlite3.IntegrityError as exc:
        raise DuplicateEmailError("A student with this email already exists.") from exc

    student_id = cursor.lastrowid
    return get_student(connection, student_id)


def get_student(connection: sqlite3.Connection, student_id: int) -> dict:
    """Return one student or raise StudentNotFoundError."""
    row = connection.execute(
        "SELECT * FROM students WHERE student_id = ?",
        (student_id,),
    ).fetchone()
    if row is None:
        raise StudentNotFoundError(f"Student with id {student_id} was not found.")
    return row_to_student(row)


def list_students(
    connection: sqlite3.Connection,
    *,
    name: str | None = None,
    course: str | None = None,
    dob_from: date | None = None,
    dob_to: date | None = None,
    skip: int = 0,
    limit: int = 50,
) -> tuple[int, list[dict]]:
    """Return (total_count, page_of_students) using optional filters."""
    where_clauses: list[str] = []
    params: list[object] = []

    if name:
        where_clauses.append("LOWER(name) LIKE ?")
        params.append(f"%{name.strip().lower()}%")
    if course:
        where_clauses.append("LOWER(course) LIKE ?")
        params.append(f"%{course.strip().lower()}%")
    if dob_from:
        where_clauses.append("date_of_birth >= ?")
        params.append(dob_from.isoformat())
    if dob_to:
        where_clauses.append("date_of_birth <= ?")
        params.append(dob_to.isoformat())

    where_sql = f"WHERE {' AND '.join(where_clauses)}" if where_clauses else ""

    total_row = connection.execute(
        f"SELECT COUNT(*) AS total FROM students {where_sql}",
        params,
    ).fetchone()
    total = int(total_row["total"]) if total_row else 0

    rows = connection.execute(
        f"""
        SELECT * FROM students
        {where_sql}
        ORDER BY student_id
        LIMIT ? OFFSET ?
        """,
        [*params, limit, skip],
    ).fetchall()

    return total, [row_to_student(row) for row in rows]


def update_student(connection: sqlite3.Connection, student_id: int, data: dict) -> dict:
    """Replace an existing student's details."""
    get_student(connection, student_id)

    values = (
        data["name"],
        _date_to_iso(data["date_of_birth"]),
        _normalize_email(data.get("email")),
        data.get("phone"),
        data.get("course"),
        data.get("address"),
        _date_to_iso(data.get("enrollment_date")),
        student_id,
    )
    try:
        connection.execute(
            """
            UPDATE students
            SET name = ?,
                date_of_birth = ?,
                email = ?,
                phone = ?,
                course = ?,
                address = ?,
                enrollment_date = ?
            WHERE student_id = ?
            """,
            values,
        )
    except sqlite3.IntegrityError as exc:
        raise DuplicateEmailError("A student with this email already exists.") from exc

    return get_student(connection, student_id)


def delete_student(connection: sqlite3.Connection, student_id: int) -> None:
    """Delete a student by id."""
    get_student(connection, student_id)
    connection.execute("DELETE FROM students WHERE student_id = ?", (student_id,))


def get_student_by_email(connection: sqlite3.Connection, email: str) -> dict | None:
    """Return a student with the given email, or None."""
    row = connection.execute(
        "SELECT * FROM students WHERE LOWER(email) = ?",
        (email.strip().lower(),),
    ).fetchone()
    return row_to_student(row) if row else None
