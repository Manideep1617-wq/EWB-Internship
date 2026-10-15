# Student Database Management REST API

A beginner-friendly FastAPI backend for managing student records. You can create, list, filter, update, and delete students. Data is stored in a local SQLite file (`students.db`) so records remain available after the server restarts.

This project is designed as a college internship assignment: the code is modular, the API is documented in Swagger UI, and automated tests cover the main success and error cases.

## Features

- REST API built with **Python**, **FastAPI**, **Pydantic**, and **Uvicorn**
- Persistent **SQLite** storage (not an in-memory Python list)
- Automatic database and table creation on startup
- Input validation (name, dates, email format, email-or-phone required)
- Duplicate email protection
- Optional filters on the student list (`name`, `course`, date-of-birth range)
- Simple pagination (`skip` and `limit`)
- Interactive docs at `/docs`
- Dummy fictional seed data (no real personal information)
- Automated tests that use a temporary database
- Optional local **Ollama** question-answering endpoint (the CRUD API works without it)

## Prerequisites

- Windows 10 or later
- Python 3.10 or newer (`python --version`)
- `pip` (included with most Python installs)
- Optional: [Ollama](https://ollama.com) only if you want to try the `/ai/ask` endpoint

## Project structure

```
student-crud/
├── app/
│   ├── __init__.py          # Marks app as a Python package
│   ├── main.py              # FastAPI app, startup, and route registration
│   ├── database.py          # SQLite connection helpers and table creation
│   ├── models.py            # Converts database rows into dictionaries
│   ├── schemas.py           # Pydantic request/response validation
│   ├── crud.py              # Parameterized SQL create/read/update/delete
│   ├── seed.py              # Inserts fictional demo students
│   ├── ollama_client.py     # Optional local Ollama helper (CRUD does not need this)
│   └── routers/
│       ├── __init__.py
│       ├── students.py      # /students CRUD endpoints
│       └── ai.py            # Optional /ai/ask endpoint
├── tests/
│   └── test_students.py     # Automated API tests
├── requirements.txt
├── README.md
├── .gitignore
├── .env.example
└── pytest.ini
```

## Installation

Clone the repository, then open **Command Prompt** or **PowerShell** in the project folder:

```powershell
git clone https://github.com/Manideep1617-wq/EWB-Internship.git
cd EWB-Internship\student-crud
```

## Virtual environment setup (Windows)

Create a virtual environment:

```powershell
python -m venv venv
```

Activate it in PowerShell:

```powershell
.\venv\Scripts\Activate.ps1
```

If PowerShell blocks the script, run this once, then try activation again:

```powershell
Set-ExecutionPolicy -Scope CurrentUser RemoteSigned
```

Command Prompt activation:

```cmd
venv\Scripts\activate.bat
```

When the environment is active, your prompt usually starts with `(venv)`.

## Install dependencies

```powershell
pip install -r requirements.txt
```

## Environment file (optional)

Copy the example environment file if you want to change the database path or Ollama settings:

```powershell
copy .env.example .env
```

The application works with the defaults even if you skip this step. Do not put API keys or real student data in `.env`.

## Database initialization

You do **not** need to create the database by hand. When the FastAPI app starts, it:

1. Creates `students.db` in the current working directory (unless `DATABASE_PATH` is set)
2. Creates the `students` table if it does not exist

The API works with an empty database. You can add students through `POST /students` or by running the seed script.

## Seed dummy records

From the `student-crud` folder, with the virtual environment activated:

```powershell
python -m app.seed
```

This inserts 15 fictional students (`@example.com` emails and fake phone numbers). Running the command again skips records that already exist, so you will not get duplicates.

## Start the FastAPI server

From the `student-crud` folder:

```powershell
uvicorn app.main:app --reload
```

You should see output that the server is running on `http://127.0.0.1:8000`.

## Open Swagger UI

In a browser, open:

**http://127.0.0.1:8000/docs**

Use **Try it out** on each endpoint. Alternative docs: **http://127.0.0.1:8000/redoc**

## Example JSON requests

### 1. Create a student — `POST /students`

```json
{
  "name": "Aisha Khan",
  "date_of_birth": "2004-03-15",
  "email": "aisha.khan@example.com",
  "phone": "5550101001",
  "course": "Computer Science",
  "address": "12 Maple Street, Springfield",
  "enrollment_date": "2023-08-01"
}
```

Expected status: **201 Created**. Email or phone is required (at least one).

### 2. List students — `GET /students`

Examples:

- All students: `http://127.0.0.1:8000/students`
- Filter by name: `http://127.0.0.1:8000/students?name=Aisha`
- Filter by course: `http://127.0.0.1:8000/students?course=Computer`
- Date of birth range: `http://127.0.0.1:8000/students?dob_from=2005-01-01&dob_to=2006-12-31`
- Pagination: `http://127.0.0.1:8000/students?skip=0&limit=10`

### 3. Get one student — `GET /students/{student_id}`

Example: `http://127.0.0.1:8000/students/1`

Missing IDs return **404**.

### 4. Update a student — `PUT /students/{student_id}`

```json
{
  "name": "Aisha Khan",
  "date_of_birth": "2004-03-15",
  "email": "aisha.khan@example.com",
  "phone": "5550101999",
  "course": "Data Science",
  "address": "12 Maple Street, Springfield",
  "enrollment_date": "2023-08-01"
}
```

This replaces the stored details. Missing IDs return **404**. Duplicate emails return **409**.

### 5. Delete a student — `DELETE /students/{student_id}`

Example: `DELETE http://127.0.0.1:8000/students/1`

Success returns a message such as `"Student deleted successfully."` Missing IDs return **404**.

## Run automated tests

From the `student-crud` folder, with the virtual environment activated:

```powershell
pytest -q
```

Tests create a temporary SQLite file. They do not delete or overwrite your `students.db`.

## Optional: ask questions with local Ollama

The core API does **not** require Ollama or any internet AI provider.

If you have Ollama installed and a model pulled (for example `ollama pull llama3.2`), you can POST to `/ai/ask`:

```json
{
  "question": "How many students are there?"
}
```

The backend first runs **safe, parameterized SQL** to load matching records. The model only sees those records. It is never allowed to run arbitrary SQL. If Ollama is not running, the endpoint still returns a clear answer built from the database (and reports that Ollama was not used).

## Troubleshooting

| Problem | What to try |
| --- | --- |
| `python` is not recognized | Install Python from python.org and tick **Add Python to PATH**, or try `py -m venv venv` |
| `Activate.ps1` is blocked | Run `Set-ExecutionPolicy -Scope CurrentUser RemoteSigned` |
| Port 8000 already in use | Start with `uvicorn app.main:app --reload --port 8001` |
| `ModuleNotFoundError: app` | Run commands from the `student-crud` folder, not from `app/` |
| Duplicate email error (409) | Choose a different email; emails must be unique when provided |
| 422 validation error | Check name is not blank, dates use `YYYY-MM-DD`, email format is valid, and email or phone is present |
| Database file missing after restart | Start the app from the same folder so it finds `students.db` |
| Tests failed after changing env | Tests set their own `DATABASE_PATH`; run `pytest -q` from `student-crud` |

## Architecture (how data flows)

1. A client (browser, Swagger UI, or another program) sends an HTTP request to Uvicorn.
2. FastAPI matches the URL to a function in `app/routers/students.py`.
3. Pydantic schemas in `app/schemas.py` validate the JSON body or query parameters.
4. The router opens a SQLite connection via `app/database.py`.
5. `app/crud.py` runs **parameterized** `INSERT` / `SELECT` / `UPDATE` / `DELETE` statements. Values are passed as bound parameters (`?`), not concatenated into SQL strings.
6. SQLite writes or reads `students.db` on disk. That is why data survives a server restart.
7. The router returns JSON and an HTTP status code (201, 200, 404, 409, 422, and so on).

```
Client → FastAPI router → Pydantic validation → crud.py SQL → students.db
```

## GitHub submission instructions

Do **not** commit `students.db`, `.env`, virtual environments, or real personal data. `.gitignore` already excludes those files.

This project is published at: https://github.com/Manideep1617-wq/EWB-Internship.git

```powershell
git status
git add .
git commit -m "Add student database CRUD REST API with FastAPI and SQLite."
git push origin main
```

Before you push, confirm `students.db` and `venv/` are not staged.

## License / academic use

This is an educational internship project. All seed records are fictional.
