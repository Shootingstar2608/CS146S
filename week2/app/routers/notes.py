"""TODO 3: Refactored notes router with Pydantic schemas and error handling."""

from __future__ import annotations

import logging
from typing import List

from fastapi import APIRouter, HTTPException

from .. import db
from ..schemas import NoteCreateRequest, NoteResponse

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/notes", tags=["notes"])


@router.post("", response_model=NoteResponse)
def create_note(payload: NoteCreateRequest) -> NoteResponse:
    """Create a new note. Content is validated automatically by Pydantic."""
    try:
        note_id = db.insert_note(payload.content.strip())
        note = db.get_note(note_id)
        return NoteResponse(id=note["id"], content=note["content"], created_at=note["created_at"])
    except Exception as e:
        logger.error(f"Failed to create note: {e}")
        raise HTTPException(status_code=500, detail="Failed to create note")


@router.get("/{note_id}", response_model=NoteResponse)
def get_single_note(note_id: int) -> NoteResponse:
    """Retrieve a single note by ID."""
    row = db.get_note(note_id)
    if row is None:
        raise HTTPException(status_code=404, detail="note not found")
    return NoteResponse(id=row["id"], content=row["content"], created_at=row["created_at"])


# TODO 4: Endpoint to retrieve all notes
@router.get("", response_model=List[NoteResponse])
def list_all_notes() -> List[NoteResponse]:
    """Retrieve all notes, ordered by newest first."""
    rows = db.list_notes()
    return [
        NoteResponse(id=r["id"], content=r["content"], created_at=r["created_at"])
        for r in rows
    ]


