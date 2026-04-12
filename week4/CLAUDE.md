# Modern Software Dev Starter — Week 4

## Project Overview
A full-stack "developer's command center" application with:
- **Backend**: FastAPI (Python) with SQLAlchemy ORM and SQLite database
- **Frontend**: Static HTML/JS/CSS served by FastAPI
- **Testing**: pytest with in-memory SQLite test fixtures
- **Formatting/Linting**: black + ruff via pre-commit hooks

## How to Run
All commands should be run from the `week4/` directory.

```bash
# Start the development server (http://localhost:8000)
make run

# Run the test suite
make test

# Format code with black and auto-fix lint issues
make format

# Check for lint errors without fixing
make lint

# Seed the database (only needed if data/app.db doesn't exist)
make seed
```

## Project Structure
```
week4/
├── backend/
│   ├── app/
│   │   ├── main.py          # FastAPI app entry point, mounts routers & static files
│   │   ├── db.py            # SQLAlchemy engine, session management, seed logic
│   │   ├── models.py        # SQLAlchemy models: Note, ActionItem
│   │   ├── schemas.py       # Pydantic request/response schemas
│   │   ├── routers/
│   │   │   ├── notes.py     # /notes endpoints (CRUD + search)
│   │   │   └── action_items.py  # /action-items endpoints
│   │   └── services/
│   │       └── extract.py   # Text parsing utilities (action items, tags)
│   └── tests/
│       ├── conftest.py      # Shared pytest fixtures (TestClient with temp DB)
│       ├── test_notes.py
│       ├── test_action_items.py
│       └── test_extract.py
├── frontend/
│   ├── index.html           # Main HTML page
│   ├── app.js               # Frontend JavaScript logic
│   └── styles.css           # CSS styles
├── data/
│   ├── seed.sql             # Initial database seed data
│   └── app.db               # SQLite database (auto-created)
├── docs/
│   └── TASKS.md             # Feature backlog / task list
├── Makefile                  # Build/run shortcuts
└── CLAUDE.md                # ← You are here
```

## Code Style & Conventions
- **Formatter**: black (line length default 88)
- **Linter**: ruff — follow all enabled rules
- **Type hints**: Always include return type annotations on functions
- **Imports**: Use relative imports within `backend/app/` (e.g., `from ..db import get_db`)
- **Models**: SQLAlchemy declarative models in `models.py`
- **Schemas**: Pydantic v2 models in `schemas.py` with `model_validate()` for ORM conversion
- **Routers**: Each resource gets its own router file in `routers/`

## Safe Commands (allowlisted)
These commands are safe to run without user confirmation:
- `make test` / `PYTHONPATH=. pytest -q backend/tests`
- `make lint` / `ruff check .`
- `make format` / `black . && ruff check . --fix`
- `cat`, `grep`, `find`, `ls`, `head`, `tail` on project files

## Commands to Avoid
- Do NOT run `rm -rf data/app.db` without explicit user confirmation
- Do NOT install new pip packages without asking
- Do NOT modify `conftest.py` fixture structure without good reason

## Workflow Guidelines
1. **Adding a new endpoint**:
   - Write a failing test first in `backend/tests/`
   - Add the Pydantic schema in `schemas.py` if needed
   - Implement the route in the appropriate router file
   - Run `make test` to verify
   - Run `make format` and `make lint` to clean up

2. **Modifying a model**:
   - Update `models.py` first
   - Update `schemas.py` to match
   - Update affected routers
   - Update or add tests
   - Re-seed if schema changes require it (`make seed`)

3. **Frontend changes**:
   - Edit files in `frontend/` directly
   - Refresh the browser to see changes (no build step needed)
   - Ensure API calls match actual backend endpoints
