from typing import Any, Optional

from pydantic import BaseModel, ConfigDict, Field


# ── Response envelope ────────────────────────────────────────────
class ErrorDetail(BaseModel):
    code: str
    message: str


class ResponseEnvelope(BaseModel):
    ok: bool
    data: Any = None
    error: Optional[ErrorDetail] = None


# ── Notes ────────────────────────────────────────────────────────
class NoteCreate(BaseModel):
    title: str = Field(..., min_length=1, max_length=200)
    content: str = Field(..., min_length=1)


class NoteUpdate(BaseModel):
    title: Optional[str] = Field(None, min_length=1, max_length=200)
    content: Optional[str] = Field(None, min_length=1)


class NoteRead(BaseModel):
    id: int
    title: str
    content: str

    model_config = ConfigDict(from_attributes=True)


# ── Action Items ─────────────────────────────────────────────────
class ActionItemCreate(BaseModel):
    description: str = Field(..., min_length=1)


class ActionItemRead(BaseModel):
    id: int
    description: str
    completed: bool

    model_config = ConfigDict(from_attributes=True)


class BulkCompleteRequest(BaseModel):
    ids: list[int] = Field(..., min_length=1)


# ── Extraction ───────────────────────────────────────────────────
class ExtractionResult(BaseModel):
    hashtags: list[str] = []
    action_items: list[str] = []


# ── Paginated response ──────────────────────────────────────────
class PaginatedResponse(BaseModel):
    items: list[Any]
    total: int
    page: int
    page_size: int
