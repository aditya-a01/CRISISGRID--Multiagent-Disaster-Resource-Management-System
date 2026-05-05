# CrisisGrid

CrisisGrid is a FastAPI-based simulation backend for multi-agent crisis response.
It models autonomous infrastructure actors (hospital, water, power, emergency) that negotiate and allocate limited resources over time.

## Highlights

- Autonomous agents with configurable behavior, risk tolerance, and cooperation profiles
- Resource allocation and bidding logic for constrained crisis scenarios
- Dependency-aware simulation to reduce cascading service failures
- REST API for simulations, events, allocations, logs, and analytics
- Dual persistence paths: SQLAlchemy (SQLite/PostgreSQL) and MongoDB modules
- Included Postman collection for endpoint testing

## Tech Stack

- Python
- FastAPI
- SQLAlchemy + Pydantic
- MongoDB (optional backend path)
- Pytest

## Repository Layout

```
app/
	core/         # Simulation engine and decision logic
	database/     # SQLAlchemy sessions, repositories, utilities
	mongo_db/     # MongoDB connection, schemas, repositories, analytics
	models/       # SQLAlchemy models
	routers/      # API route handlers
	schemas/      # Request and response contracts
frontend/       # Lightweight frontend for local interaction
tests/          # Unit and integration tests
main.py         # FastAPI app bootstrap
config.py       # Environment-driven settings
```

## Quick Start

### 1) Create and activate a virtual environment

Windows (Git Bash):

```bash
python -m venv .venv
source .venv/Scripts/activate
```

Linux/macOS:

```bash
python -m venv .venv
source .venv/bin/activate
```

### 2) Install dependencies

```bash
pip install -r requirements.txt
```

### 3) Configure environment variables

```bash
cp .env.example .env
```

Update `.env` with your preferred database settings.

### 4) Run the API

```bash
python -m uvicorn main:app --reload
```

Server URLs:

- API: http://127.0.0.1:8000
- OpenAPI docs: http://127.0.0.1:8000/docs
- ReDoc: http://127.0.0.1:8000/redoc

## Test

```bash
pytest -v
```

## API and Data References

- API contract: `API_CONTRACT.md`
- SQL schema docs: `DATABASE_SCHEMA.md`
- MongoDB schema docs: `MONGODB_SCHEMA.md`
- MongoDB implementation notes: `MONGODB_IMPLEMENTATION.md`
- Postman collection: `postman_collection.json`

## Notes

- Local SQLite database files are ignored by Git via `.gitignore`.
- Line endings are normalized via `.gitattributes` to keep commits clean across OSes.
