"""Pydantic schemas for request validation and API responses."""

from __future__ import annotations

from datetime import date

from pydantic import BaseModel, ConfigDict, EmailStr, Field, field_validator, model_validator


def _blank_to_none(value: str | None) -> str | None:
    if value is None:
        return None
    stripped = value.strip()
    return stripped or None


class StudentBase(BaseModel):
    """Shared student fields used by create and update requests."""

    name: str = Field(..., min_length=1, examples=["Aisha Khan"])
    date_of_birth: date = Field(..., examples=["2004-03-15"])
    email: EmailStr | None = Field(default=None, examples=["aisha.khan@example.com"])
    phone: str | None = Field(default=None, examples=["5550101234"])
    course: str | None = Field(default=None, examples=["Computer Science"])
    address: str | None = Field(default=None, examples=["12 Maple Street, Springfield"])
    enrollment_date: date | None = Field(default=None, examples=["2023-08-01"])

    @field_validator("name")
    @classmethod
    def name_must_not_be_blank(cls, value: str) -> str:
        cleaned = value.strip()
        if not cleaned:
            raise ValueError("Student name cannot be empty or whitespace only.")
        return cleaned

    @field_validator("phone", "course", "address")
    @classmethod
    def optional_text_must_not_be_blank(cls, value: str | None) -> str | None:
        return _blank_to_none(value)

    @model_validator(mode="after")
    def require_email_or_phone(self) -> StudentBase:
        if not self.email and not self.phone:
            raise ValueError("Provide at least one contact method: email or phone.")
        return self


class StudentCreate(StudentBase):
    """Payload for creating a student."""


class StudentUpdate(StudentBase):
    """Payload for replacing an existing student's details (PUT)."""


class StudentResponse(BaseModel):
    """Student record returned by the API."""

    model_config = ConfigDict(from_attributes=True)

    student_id: int
    name: str
    date_of_birth: date
    email: EmailStr | None = None
    phone: str | None = None
    course: str | None = None
    address: str | None = None
    enrollment_date: date | None = None


class StudentListResponse(BaseModel):
    """Paginated list of students."""

    total: int
    skip: int
    limit: int
    items: list[StudentResponse]


class MessageResponse(BaseModel):
    """Simple success or status message."""

    message: str
    student_id: int | None = None


class AskRequest(BaseModel):
    """Natural-language question about student records (optional AI endpoint)."""

    question: str = Field(..., min_length=3, examples=["How many students are there?"])


class AskResponse(BaseModel):
    """Answer grounded in retrieved student records."""

    question: str
    answer: str
    used_ollama: bool
    matched_count: int
    records: list[StudentResponse]
