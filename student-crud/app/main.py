"""FastAPI application entry point."""

from __future__ import annotations

from contextlib import asynccontextmanager

from fastapi import FastAPI

from app.database import init_db
from app.routers import ai, students


@asynccontextmanager
async def lifespan(_app: FastAPI):
    """Create the SQLite database and students table on startup."""
    init_db()
    yield


app = FastAPI(
    title="Student Database Management API",
    description=(
        "Beginner-friendly REST API for creating, viewing, updating, filtering, "
        "and deleting student records stored in SQLite. Open /docs to try every "
        "endpoint in the browser. An optional /ai/ask endpoint is available if "
        "a local Ollama model is running; the core CRUD API does not require it."
    ),
    version="1.0.0",
    lifespan=lifespan,
)

app.include_router(students.router)
app.include_router(ai.router)


@app.get("/", tags=["Health"])
def root() -> dict[str, str]:
    """Simple health check and documentation hint."""
    return {
        "message": "Student Database Management API is running.",
        "docs": "/docs",
        "students": "/students",
    }
