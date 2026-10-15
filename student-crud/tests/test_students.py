"""Automated tests for student CRUD, validation, and error handling.

Tests use a temporary SQLite file so development data in students.db is never touched.
"""

from __future__ import annotations

from collections.abc import Generator

import pytest
from fastapi.testclient import TestClient

from app.database import init_db
from app.main import app


@pytest.fixture()
def client(tmp_path, monkeypatch) -> Generator[TestClient, None, None]:
    db_file = tmp_path / "test_students.db"
    monkeypatch.setenv("DATABASE_PATH", str(db_file))
    monkeypatch.setenv("OLLAMA_BASE_URL", "http://127.0.0.1:9")
    monkeypatch.setenv("OLLAMA_TIMEOUT_SECONDS", "1")
    init_db()
    with TestClient(app) as test_client:
        yield test_client


VALID_STUDENT = {
    "name": "Test Student",
    "date_of_birth": "2004-01-15",
    "email": "test.student@example.com",
    "phone": "5550199999",
    "course": "Computer Science",
    "address": "1 Test Lane",
    "enrollment_date": "2023-08-01",
}


def test_create_student(client: TestClient) -> None:
    response = client.post("/students", json=VALID_STUDENT)
    assert response.status_code == 201
    body = response.json()
    assert body["student_id"] >= 1
    assert body["name"] == "Test Student"
    assert body["email"] == "test.student@example.com"


def test_list_students(client: TestClient) -> None:
    client.post("/students", json=VALID_STUDENT)
    client.post(
        "/students",
        json={
            **VALID_STUDENT,
            "name": "Second Student",
            "email": "second.student@example.com",
            "course": "Data Science",
            "date_of_birth": "2006-05-01",
        },
    )

    response = client.get("/students")
    assert response.status_code == 200
    body = response.json()
    assert body["total"] == 2
    assert len(body["items"]) == 2

    filtered = client.get("/students", params={"course": "Data", "name": "Second"})
    assert filtered.status_code == 200
    assert filtered.json()["total"] == 1

    by_dob = client.get("/students", params={"dob_from": "2006-01-01", "dob_to": "2006-12-31"})
    assert by_dob.json()["total"] == 1

    paged = client.get("/students", params={"skip": 1, "limit": 1})
    assert paged.status_code == 200
    assert len(paged.json()["items"]) == 1
    assert paged.json()["skip"] == 1


def test_retrieve_student(client: TestClient) -> None:
    created = client.post("/students", json=VALID_STUDENT).json()
    response = client.get(f"/students/{created['student_id']}")
    assert response.status_code == 200
    assert response.json()["name"] == "Test Student"


def test_update_student(client: TestClient) -> None:
    created = client.post("/students", json=VALID_STUDENT).json()
    payload = {
        **VALID_STUDENT,
        "name": "Updated Student",
        "course": "Information Technology",
        "phone": "5550188888",
    }
    response = client.put(f"/students/{created['student_id']}", json=payload)
    assert response.status_code == 200
    assert response.json()["name"] == "Updated Student"
    assert response.json()["course"] == "Information Technology"


def test_delete_student(client: TestClient) -> None:
    created = client.post("/students", json=VALID_STUDENT).json()
    student_id = created["student_id"]
    response = client.delete(f"/students/{student_id}")
    assert response.status_code == 200
    assert "deleted" in response.json()["message"].lower()

    missing = client.get(f"/students/{student_id}")
    assert missing.status_code == 404


def test_invalid_input_rejected(client: TestClient) -> None:
    blank_name = client.post("/students", json={**VALID_STUDENT, "name": "   "})
    assert blank_name.status_code == 422

    no_contact = client.post(
        "/students",
        json={
            "name": "No Contact",
            "date_of_birth": "2004-01-01",
            "email": None,
            "phone": None,
        },
    )
    assert no_contact.status_code == 422

    bad_email = client.post("/students", json={**VALID_STUDENT, "email": "not-an-email"})
    assert bad_email.status_code == 422

    bad_date = client.post("/students", json={**VALID_STUDENT, "date_of_birth": "15-01-2004"})
    assert bad_date.status_code == 422

    malformed = client.post("/students", content="{not json", headers={"Content-Type": "application/json"})
    assert malformed.status_code == 422


def test_duplicate_email(client: TestClient) -> None:
    first = client.post("/students", json=VALID_STUDENT)
    assert first.status_code == 201
    duplicate = client.post(
        "/students",
        json={**VALID_STUDENT, "name": "Someone Else", "phone": "5550177777"},
    )
    assert duplicate.status_code == 409
    assert "email" in duplicate.json()["detail"].lower()


def test_missing_student(client: TestClient) -> None:
    assert client.get("/students/9999").status_code == 404
    assert client.put("/students/9999", json=VALID_STUDENT).status_code == 404
    assert client.delete("/students/9999").status_code == 404


def test_phone_only_student_allowed(client: TestClient) -> None:
    response = client.post(
        "/students",
        json={
            "name": "Phone Only",
            "date_of_birth": "2005-02-02",
            "phone": "5550166666",
        },
    )
    assert response.status_code == 201
    assert response.json()["email"] is None


def test_ai_ask_works_without_ollama(client: TestClient) -> None:
    client.post("/students", json=VALID_STUDENT)
    client.post(
        "/students",
        json={
            **VALID_STUDENT,
            "name": "Later Student",
            "email": "later.student@example.com",
            "date_of_birth": "2006-04-01",
        },
    )
    response = client.post("/ai/ask", json={"question": "How many students are there?"})
    assert response.status_code == 200
    body = response.json()
    assert body["matched_count"] == 2
    assert body["used_ollama"] is False
    assert "2" in body["answer"]

    born_after = client.post("/ai/ask", json={"question": "List students born after 2005."})
    assert born_after.status_code == 200
    assert born_after.json()["matched_count"] == 1
    assert born_after.json()["records"][0]["name"] == "Later Student"


def test_persistence_across_connections(client: TestClient) -> None:
    created = client.post("/students", json=VALID_STUDENT).json()
    again = client.get(f"/students/{created['student_id']}")
    assert again.status_code == 200
    assert again.json()["email"] == VALID_STUDENT["email"]
