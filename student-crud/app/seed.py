"""Insert fictional demo students without creating duplicates.

Run from the student-crud folder:

    python -m app.seed
"""

from __future__ import annotations

from datetime import date

from app.crud import create_student, get_student_by_email
from app.database import get_db, init_db

# Fictional records only. Emails use example.com and phone numbers are fake.
DUMMY_STUDENTS = [
    {
        "name": "Aisha Khan",
        "date_of_birth": date(2004, 3, 15),
        "email": "aisha.khan@example.com",
        "phone": "5550101001",
        "course": "Computer Science",
        "address": "12 Maple Street, Springfield",
        "enrollment_date": date(2023, 8, 1),
    },
    {
        "name": "Liam Patel",
        "date_of_birth": date(2005, 7, 22),
        "email": "liam.patel@example.com",
        "phone": "5550101002",
        "course": "Information Technology",
        "address": "88 Oak Avenue, Riverside",
        "enrollment_date": date(2024, 1, 15),
    },
    {
        "name": "Sofia Ramirez",
        "date_of_birth": date(2003, 11, 2),
        "email": "sofia.ramirez@example.com",
        "phone": "5550101003",
        "course": "Business Administration",
        "address": "5 River Road, Lakeside",
        "enrollment_date": date(2022, 9, 5),
    },
    {
        "name": "Noah Chen",
        "date_of_birth": date(2006, 1, 9),
        "email": "noah.chen@example.com",
        "phone": None,
        "course": "Computer Science",
        "address": "41 Pine Court, Hilltown",
        "enrollment_date": date(2024, 8, 20),
    },
    {
        "name": "Maya Singh",
        "date_of_birth": date(2004, 5, 30),
        "email": None,
        "phone": "5550101005",
        "course": "Mechanical Engineering",
        "address": "19 Cedar Lane, Brookfield",
        "enrollment_date": date(2023, 8, 1),
    },
    {
        "name": "Ethan Brooks",
        "date_of_birth": date(2002, 12, 18),
        "email": "ethan.brooks@example.com",
        "phone": "5550101006",
        "course": "Electrical Engineering",
        "address": "77 Sunset Blvd, Fairview",
        "enrollment_date": date(2021, 9, 1),
    },
    {
        "name": "Priya Nair",
        "date_of_birth": date(2005, 4, 4),
        "email": "priya.nair@example.com",
        "phone": "5550101007",
        "course": "Data Science",
        "address": "3 Harbor Way, Seaview",
        "enrollment_date": date(2024, 1, 10),
    },
    {
        "name": "Owen Gallagher",
        "date_of_birth": date(2003, 8, 27),
        "email": "owen.gallagher@example.com",
        "phone": "5550101008",
        "course": "Civil Engineering",
        "address": "60 Hillcrest Drive, Millbrook",
        "enrollment_date": date(2022, 8, 15),
    },
    {
        "name": "Hana Suzuki",
        "date_of_birth": date(2006, 6, 12),
        "email": "hana.suzuki@example.com",
        "phone": "5550101009",
        "course": "Information Technology",
        "address": "14 Blossom Street, Greenfield",
        "enrollment_date": date(2024, 9, 2),
    },
    {
        "name": "Jamal Wright",
        "date_of_birth": date(2001, 2, 14),
        "email": "jamal.wright@example.com",
        "phone": "5550101010",
        "course": "Business Administration",
        "address": "9 Liberty Plaza, Midtown",
        "enrollment_date": date(2020, 9, 1),
    },
    {
        "name": "Elena Rossi",
        "date_of_birth": date(2004, 9, 21),
        "email": "elena.rossi@example.com",
        "phone": "5550101011",
        "course": "Computer Science",
        "address": "27 Villa Lane, Northpark",
        "enrollment_date": date(2023, 1, 20),
    },
    {
        "name": "Arjun Mehta",
        "date_of_birth": date(2005, 10, 8),
        "email": "arjun.mehta@example.com",
        "phone": "5550101012",
        "course": "Data Science",
        "address": "101 Campus Road, Westend",
        "enrollment_date": date(2024, 8, 12),
    },
    {
        "name": "Chloe Dubois",
        "date_of_birth": date(2003, 3, 3),
        "email": "chloe.dubois@example.com",
        "phone": None,
        "course": "Graphic Design",
        "address": "8 Artist Row, Oldtown",
        "enrollment_date": date(2022, 2, 1),
    },
    {
        "name": "Diego Alvarez",
        "date_of_birth": date(2007, 7, 7),
        "email": "diego.alvarez@example.com",
        "phone": "5550101014",
        "course": "Computer Science",
        "address": "55 Canyon Drive, Sunridge",
        "enrollment_date": date(2025, 1, 6),
    },
    {
        "name": "Fatima El-Sayed",
        "date_of_birth": date(2002, 5, 19),
        "email": "fatima.elsayed@example.com",
        "phone": "5550101015",
        "course": "Nursing",
        "address": "22 Garden Court, Eastwood",
        "enrollment_date": date(2021, 8, 25),
    },
]


def seed_students() -> tuple[int, int]:
    """Insert dummy students. Returns (inserted_count, skipped_count)."""
    init_db()
    inserted = 0
    skipped = 0

    with get_db() as connection:
        for student in DUMMY_STUDENTS:
            email = student.get("email")
            if email and get_student_by_email(connection, email):
                skipped += 1
                continue
            existing = connection.execute(
                "SELECT student_id FROM students WHERE name = ? AND date_of_birth = ?",
                (student["name"], student["date_of_birth"].isoformat()),
            ).fetchone()
            if existing:
                skipped += 1
                continue
            create_student(connection, student)
            inserted += 1

    return inserted, skipped


def main() -> None:
    inserted, skipped = seed_students()
    print(f"Seed complete. Inserted {inserted} student(s), skipped {skipped} existing record(s).")


if __name__ == "__main__":
    main()
