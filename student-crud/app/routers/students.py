"""Student CRUD endpoints."""

from __future__ import annotations

from datetime import date

from fastapi import APIRouter, HTTPException, Query, status

from app import crud
from app.database import get_db
from app.schemas import MessageResponse, StudentCreate, StudentListResponse, StudentResponse, StudentUpdate

router = APIRouter(prefix="/students", tags=["Students"])


def _payload_to_dict(payload: StudentCreate | StudentUpdate) -> dict:
    return payload.model_dump()


@router.post(
    "",
    response_model=StudentResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create a student",
)
def create_student(payload: StudentCreate) -> StudentResponse:
    """Validate the request body and store a new student in SQLite."""
    try:
        with get_db() as connection:
            student = crud.create_student(connection, _payload_to_dict(payload))
    except crud.DuplicateEmailError as exc:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(exc)) from exc
    except Exception as exc:  # noqa: BLE001 - convert unexpected DB errors
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Could not create the student. Please try again.",
        ) from exc
    return student


@router.get(
    "",
    response_model=StudentListResponse,
    summary="List students",
)
def list_students(
    name: str | None = Query(default=None, description="Partial, case-insensitive name match"),
    course: str | None = Query(default=None, description="Partial, case-insensitive course match"),
    dob_from: date | None = Query(default=None, description="Earliest date of birth (YYYY-MM-DD)"),
    dob_to: date | None = Query(default=None, description="Latest date of birth (YYYY-MM-DD)"),
    skip: int = Query(default=0, ge=0, description="Number of records to skip"),
    limit: int = Query(default=50, ge=1, le=100, description="Maximum records to return"),
) -> StudentListResponse:
    """Return students with optional filters and simple pagination."""
    if dob_from and dob_to and dob_from > dob_to:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="dob_from cannot be later than dob_to.",
        )
    try:
        with get_db() as connection:
            total, items = crud.list_students(
                connection,
                name=name,
                course=course,
                dob_from=dob_from,
                dob_to=dob_to,
                skip=skip,
                limit=limit,
            )
    except Exception as exc:  # noqa: BLE001
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Could not retrieve students. Please try again.",
        ) from exc
    return StudentListResponse(total=total, skip=skip, limit=limit, items=items)


@router.get(
    "/{student_id}",
    response_model=StudentResponse,
    summary="Get one student",
)
def get_student(student_id: int) -> StudentResponse:
    """Return a single student by ID."""
    try:
        with get_db() as connection:
            return crud.get_student(connection, student_id)
    except crud.StudentNotFoundError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc
    except Exception as exc:  # noqa: BLE001
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Could not retrieve the student. Please try again.",
        ) from exc


@router.put(
    "/{student_id}",
    response_model=StudentResponse,
    summary="Update a student",
)
def update_student(student_id: int, payload: StudentUpdate) -> StudentResponse:
    """Replace an existing student's details with a validated payload."""
    try:
        with get_db() as connection:
            return crud.update_student(connection, student_id, _payload_to_dict(payload))
    except crud.StudentNotFoundError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc
    except crud.DuplicateEmailError as exc:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(exc)) from exc
    except Exception as exc:  # noqa: BLE001
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Could not update the student. Please try again.",
        ) from exc


@router.delete(
    "/{student_id}",
    response_model=MessageResponse,
    summary="Delete a student",
)
def delete_student(student_id: int) -> MessageResponse:
    """Remove a student record by ID."""
    try:
        with get_db() as connection:
            crud.delete_student(connection, student_id)
    except crud.StudentNotFoundError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc
    except Exception as exc:  # noqa: BLE001
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Could not delete the student. Please try again.",
        ) from exc
    return MessageResponse(message="Student deleted successfully.", student_id=student_id)
