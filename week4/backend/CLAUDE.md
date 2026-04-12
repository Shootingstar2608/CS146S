# Backend — Development Conventions

## Architecture
```
backend/app/
├── main.py       → App factory, router registration, static mount
├── db.py         → Engine, SessionLocal, get_db() dependency
├── models.py     → SQLAlchemy ORM models (declarative_base)
├── schemas.py    → Pydantic v2 request/response schemas
├── routers/      → One file per resource (notes.py, action_items.py)
└── services/     → Business logic utilities (extract.py)
```

## Database Patterns

### Dependency Injection
All routers receive a database session via FastAPI's `Depends(get_db)`:
```python
from ..db import get_db

@router.get("/")
def list_items(db: Session = Depends(get_db)):
    ...
```

### Transaction Management
- `get_db()` auto-commits on success, auto-rollbacks on exception
- Use `db.flush()` + `db.refresh()` after adding/modifying objects (NOT `db.commit()`)
- The session commit happens automatically when the request completes

### Model Conventions
```python
class MyModel(Base):
    __tablename__ = "my_models"
    id = Column(Integer, primary_key=True, index=True)
    # Required fields: nullable=False
    # Optional fields: nullable=True, default=...
```

## Router Patterns

### Standard CRUD Pattern
```python
router = APIRouter(prefix="/resource", tags=["resource"])

# List all
@router.get("/", response_model=list[ResourceRead])

# Create
@router.post("/", response_model=ResourceRead, status_code=201)

# Get by ID
@router.get("/{id}", response_model=ResourceRead)

# Update
@router.put("/{id}", response_model=ResourceRead)

# Delete
@router.delete("/{id}", status_code=204)
```

### Error Handling
- Use `HTTPException(status_code=404, detail="...")` for not-found errors
- Use `HTTPException(status_code=400, detail="...")` for validation failures
- Always provide informative `detail` messages

## Schema Patterns
```python
# Create schema (input)
class ResourceCreate(BaseModel):
    field: str  # Add Field(..., min_length=1) for validation

# Read schema (output)
class ResourceRead(BaseModel):
    id: int
    field: str
    class Config:
        from_attributes = True  # Enables ORM mode

# Update schema (partial input)
class ResourceUpdate(BaseModel):
    field: str | None = None  # All fields optional for partial updates
```

## Testing Patterns

### Test File Location
Tests live in `backend/tests/` and follow naming: `test_{resource}.py`

### Client Fixture
The `client` fixture in `conftest.py` provides a `TestClient` with an isolated in-memory SQLite database. Each test gets a fresh database.

### Standard Test Pattern
```python
def test_create_and_list(client):
    # Create
    r = client.post("/resource/", json={"field": "value"})
    assert r.status_code == 201
    data = r.json()
    assert data["field"] == "value"

    # List
    r = client.get("/resource/")
    assert r.status_code == 200
    assert len(r.json()) >= 1

def test_not_found(client):
    r = client.get("/resource/9999")
    assert r.status_code == 404

def test_validation_error(client):
    r = client.post("/resource/", json={"field": ""})
    assert r.status_code == 422  # or 400 for custom validation
```

### Running Tests
```bash
# Run all tests
PYTHONPATH=. pytest -q backend/tests

# Run a specific test file
PYTHONPATH=. pytest -q backend/tests/test_notes.py

# Run with verbose output
PYTHONPATH=. pytest -v backend/tests

# Run with coverage
PYTHONPATH=. pytest --cov=backend backend/tests
```

## When Adding a New Feature
1. **Test first**: Write a failing test in `backend/tests/test_*.py`
2. **Schema**: Add/update Pydantic schemas in `schemas.py`
3. **Model**: Update SQLAlchemy models if schema changes needed
4. **Router**: Implement the endpoint in the appropriate router
5. **Verify**: Run `make test` — all tests must pass
6. **Lint**: Run `make format` then `make lint` — must be clean
