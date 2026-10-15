# EWB Internship

Internship project: **Student Database Management REST API**.

The application is built with Python, FastAPI, SQLite, and Pydantic. It supports creating, viewing, updating, filtering, and deleting student records.

## Repository structure

```
EWB-Internship/
├── README.md              # This file
└── student-crud/          # FastAPI project (run the app from here)
    ├── app/
    ├── tests/
    ├── requirements.txt
    └── README.md
```

## How to run

```powershell
git clone https://github.com/Manideep1617-wq/EWB-Internship.git
cd EWB-Internship\student-crud
python -m venv venv
.\venv\Scripts\Activate.ps1
pip install -r requirements.txt
uvicorn app.main:app --reload
```

Open Swagger UI: [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs)

Full setup, API examples, and test instructions are in [student-crud/README.md](student-crud/README.md).
