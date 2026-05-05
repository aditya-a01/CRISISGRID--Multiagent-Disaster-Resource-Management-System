# CrisisGrid Backend Engine

Multi-agent crisis response system with autonomous negotiation and resource allocation.

## Features

- **Autonomous Agents**: Hospital, Water, Power, Emergency response agents
- **Real-time Negotiation**: Utility-based bidding system for resource allocation
- **Behavioral AI**: Risk tolerance, cooperation levels, and adaptive decision-making
- **Dependency Management**: Prevents cascading failures with dependency graph
- **System Constraints**: Enforces minimum life-critical requirements
- **Persistence**: Full simulation history with SQLAlchemy + SQLite/PostgreSQL

## Project Structure

```
├── app/
│   ├── models/          # SQLAlchemy ORM models
│   ├── schemas/         # Pydantic request/response schemas
│   ├── core/            # Core simulation engines
│   └── database/        # Database configuration
├── tests/               # Unit and integration tests
├── main.py             # FastAPI application entry point
├── config.py           # Configuration management
└── requirements.txt    # Python dependencies
```

## Installation

```bash
# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Setup environment
cp .env.example .env
```

## Running the Server

```bash
python -m uvicorn main:app --reload
```

API will be available at `http://localhost:8000`
- API Docs: `http://localhost:8000/docs`

## Running Tests

```bash
pytest
pytest -v  # Verbose output
pytest tests/test_agent.py  # Specific file
```

## Development

Currently in Phase 1: Project structure and dependencies
