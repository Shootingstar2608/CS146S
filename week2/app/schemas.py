"""
TODO 3: Pydantic schemas for well-defined API contracts.

These models replace Dict[str, Any] in endpoints to provide:
- Automatic input validation
- Clear API documentation at /docs
- Type safety throughout the codebase
"""

from __future__ import annotations

from typing import List, Optional

from pydantic import BaseModel, Field


# ========== Note schemas ==========

class NoteCreateRequest(BaseModel):
    """Request body for creating a new note."""
    content: str = Field(..., min_length=1, description="The note content text")


class NoteResponse(BaseModel):
    """Response body for a single note."""
    id: int
    content: str
    created_at: str


# ========== Action Item schemas ==========

class ExtractRequest(BaseModel):
    """Request body for extracting action items from text."""
    text: str = Field(..., min_length=1, description="The text to extract action items from")
    save_note: bool = Field(default=False, description="Whether to also save the text as a note")


class ActionItemResponse(BaseModel):
    """A single action item."""
    id: int
    text: str


class ExtractResponse(BaseModel):
    """Response body after extracting action items."""
    note_id: Optional[int] = None
    items: List[ActionItemResponse]


class MarkDoneRequest(BaseModel):
    """Request body for marking an action item as done/undone."""
    done: bool = Field(default=True, description="Whether the item is done")


class MarkDoneResponse(BaseModel):
    """Response body after marking an action item."""
    id: int
    done: bool


class ActionItemFullResponse(BaseModel):
    """Full action item details (used in list endpoint)."""
    id: int
    note_id: Optional[int] = None
    text: str
    done: bool
    created_at: str
