"""Optional natural-language questions about student records."""

from __future__ import annotations

from fastapi import APIRouter, HTTPException, status

from app.database import get_db
from app.ollama_client import (
    OllamaUnavailableError,
    ask_ollama,
    fallback_answer,
    retrieve_records,
)
from app.schemas import AskRequest, AskResponse

router = APIRouter(prefix="/ai", tags=["Optional AI"])


@router.post(
    "/ask",
    response_model=AskResponse,
    summary="Ask a question about students (optional Ollama)",
)
def ask_about_students(payload: AskRequest) -> AskResponse:
    """Retrieve matching students with safe SQL, then optionally ask Ollama."""
    try:
        with get_db() as connection:
            total, records = retrieve_records(connection, payload.question)
    except Exception as exc:  # noqa: BLE001
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Could not look up student records for this question.",
        ) from exc

    used_ollama = False
    try:
        answer = ask_ollama(payload.question, records, total)
        used_ollama = True
    except OllamaUnavailableError:
        answer = fallback_answer(payload.question, total, records)

    return AskResponse(
        question=payload.question,
        answer=answer,
        used_ollama=used_ollama,
        matched_count=total,
        records=records,
    )
