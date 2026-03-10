# Week 2 – Action Item Extractor

A FastAPI + SQLite application that converts free-form notes into actionable items. Supports both **heuristic-based** extraction (regex/pattern matching) and **LLM-powered** extraction (via Ollama).

## Project Structure

```
week2/
├── app/
│   ├── main.py              # FastAPI app entrypoint, CORS, lifespan
│   ├── db.py                # SQLite database layer
│   ├── schemas.py           # Pydantic request/response models
│   ├── routers/
│   │   ├── notes.py         # Notes CRUD endpoints
│   │   └── action_items.py  # Action item extraction & management endpoints
│   └── services/
│       └── extract.py       # Heuristic & LLM extraction logic
├── frontend/
│   └── index.html           # Minimal HTML/JS frontend
├── tests/
│   ├── conftest.py          # Pytest configuration & custom markers
│   └── test_extract.py      # Unit & integration tests
├── data/
│   └── app.db               # SQLite database (auto-created)
├── assignment.md
├── writeup.md
└── README.md
```

## Setup & Installation

### Prerequisites
- Python 3.10+
- [Ollama](https://ollama.com/) installed and running (for LLM extraction)

### Install Dependencies

```bash
pip install fastapi uvicorn pydantic ollama python-dotenv python-multipart
```

### Pull an Ollama Model

```bash
ollama pull llama3.2
```

Verify it's available:
```bash
ollama list
```

## Running the Application

### Start the Server

```bash
cd ~/modern-software-dev-assignments
uvicorn week2.app.main:app --reload
```

### Access the App

| URL | Description |
|-----|-------------|
| http://127.0.0.1:8000 | Frontend UI |
| http://127.0.0.1:8000/docs | Interactive API documentation (Swagger) |

## API Endpoints

### Notes

| Method | Endpoint | Description |
|--------|----------|-------------|
| `POST` | `/notes` | Create a new note |
| `GET` | `/notes` | List all notes |
| `GET` | `/notes/{note_id}` | Get a single note by ID |

### Action Items

| Method | Endpoint | Description |
|--------|----------|-------------|
| `POST` | `/action-items/extract` | Extract action items using heuristic method |
| `POST` | `/action-items/extract-llm` | Extract action items using Ollama LLM |
| `GET` | `/action-items` | List all action items (optionally filter by `note_id`) |
| `POST` | `/action-items/{id}/done` | Mark an action item as done/undone |

### Example Request

```bash
curl -X POST http://127.0.0.1:8000/action-items/extract-llm \
  -H "Content-Type: application/json" \
  -d '{"text": "- Buy milk\nTODO: Fix login bug", "save_note": true}'
```

Response:
```json
{
  "note_id": 1,
  "items": [
    {"id": 1, "text": "Buy milk"},
    {"id": 2, "text": "Fix login bug"}
  ]
}
```

## Running Tests

### Run all tests (mock + integration)
```bash
cd ~/modern-software-dev-assignments/week2
python -m pytest tests/test_extract.py -v
```

### Run only mock tests (fast, no Ollama needed)
```bash
python -m pytest tests/test_extract.py -v -m "not integration"
```

### Run only integration tests (requires Ollama running)
```bash
python -m pytest tests/test_extract.py -v -m integration
```

## Extraction Methods

| Method | How it works | Speed | Accuracy |
|--------|-------------|-------|----------|
| **Heuristic** (`Extract` button) | Regex pattern matching for bullets, keywords, checkboxes | ⚡ Instant | Rigid — only matches known patterns |
| **LLM** (`Extract LLM` button) | Ollama AI understands natural language context | 🐢 1-3s | Flexible — finds implicit action items |
