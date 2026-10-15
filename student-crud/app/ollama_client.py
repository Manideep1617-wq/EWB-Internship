"""Optional local Ollama helper.

Student records are always loaded with parameterized SQL in crud.py.
The model is never allowed to invent or execute SQL.
"""

from __future__ import annotations

import json
import os
import re
from datetime import date

import httpx

from app import crud

OLLAMA_GENERATE_PATH = "/api/generate"


class OllamaUnavailableError(Exception):
    """Raised when the local Ollama server cannot be reached."""


def parse_question_filters(question: str) -> dict:
    """Turn a natural-language question into safe list_students filters."""
    text = question.lower()
    filters: dict = {"name": None, "course": None, "dob_from": None, "dob_to": None}

    after_match = re.search(r"born after (\d{4})", text)
    if after_match:
        year = int(after_match.group(1))
        filters["dob_from"] = date(year + 1, 1, 1)

    before_match = re.search(r"born before (\d{4})", text)
    if before_match:
        year = int(before_match.group(1))
        filters["dob_to"] = date(year - 1, 12, 31)

    in_year = re.search(r"born in (\d{4})", text)
    if in_year:
        year = int(in_year.group(1))
        filters["dob_from"] = date(year, 1, 1)
        filters["dob_to"] = date(year, 12, 31)

    course_match = re.search(
        r"(?:in|studying|taking|enrolled in)\s+(computer science|information technology|"
        r"data science|business administration|mechanical engineering|"
        r"electrical engineering|civil engineering|graphic design|nursing)",
        text,
    )
    if course_match:
        filters["course"] = course_match.group(1)

    named = re.search(r"(?:named|called)\s+([a-z][a-z\s'-]{1,40})", text)
    if named:
        filters["name"] = named.group(1).strip(" ?.,")

    return filters


def retrieve_records(connection, question: str) -> tuple[int, list[dict]]:
    """Load matching students with parameterized SQL only."""
    filters = parse_question_filters(question)
    return crud.list_students(
        connection,
        name=filters["name"],
        course=filters["course"],
        dob_from=filters["dob_from"],
        dob_to=filters["dob_to"],
        skip=0,
        limit=100,
    )


def fallback_answer(question: str, total: int, records: list[dict]) -> str:
    """Build a grounded answer without calling any model."""
    text = question.lower()
    if "how many" in text or "count" in text:
        return f"There are {total} student record(s) matching this question."
    if not records:
        return "No matching student records were found in the database."
    names = ", ".join(item["name"] for item in records[:20])
    extra = "" if total <= 20 else f" (showing 20 of {total})"
    return f"Matching students ({total}){extra}: {names}."


def ask_ollama(question: str, records: list[dict], total: int) -> str:
    """Send retrieved records to a local Ollama model."""
    base_url = os.getenv("OLLAMA_BASE_URL", "http://127.0.0.1:11434").rstrip("/")
    model = os.getenv("OLLAMA_MODEL", "llama3.2")
    timeout = float(os.getenv("OLLAMA_TIMEOUT_SECONDS", "30"))

    payload = {
        "model": model,
        "stream": False,
        "prompt": (
            "You are a teaching assistant. Answer the user question using ONLY the "
            "student records provided as JSON. If the records do not contain the "
            "answer, say so. Do not invent students. Do not write SQL.\n\n"
            f"Question: {question}\n"
            f"Total matching records: {total}\n"
            f"Records JSON: {json.dumps(records, default=str)}"
        ),
    }

    try:
        response = httpx.post(
            f"{base_url}{OLLAMA_GENERATE_PATH}",
            json=payload,
            timeout=timeout,
        )
        response.raise_for_status()
        data = response.json()
    except (httpx.HTTPError, ValueError) as exc:
        raise OllamaUnavailableError("Ollama is not available.") from exc

    answer = (data.get("response") or "").strip()
    if not answer:
        raise OllamaUnavailableError("Ollama returned an empty response.")
    return answer
