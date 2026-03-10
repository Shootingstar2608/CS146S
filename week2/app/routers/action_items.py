"""TODO 3: Refactored action items router with Pydantic schemas and error handling."""

from __future__ import annotations

import logging
from typing import List, Optional

from fastapi import APIRouter, HTTPException

from .. import db
from ..schemas import (
    ExtractRequest,
    ExtractResponse,
    ActionItemResponse,
    ActionItemFullResponse,
    MarkDoneRequest,
    MarkDoneResponse,
)
from ..services.extract import extract_action_items, extract_action_items_llm

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/action-items", tags=["action-items"])


@router.post("/extract", response_model=ExtractResponse)
def extract(payload: ExtractRequest) -> ExtractResponse:
    """Extract action items from text using heuristic method."""
    try:
        note_id: Optional[int] = None
        if payload.save_note:
            note_id = db.insert_note(payload.text)

        items = extract_action_items(payload.text)
        ids = db.insert_action_items(items, note_id=note_id)
        return ExtractResponse(
            note_id=note_id,
            items=[ActionItemResponse(id=i, text=t) for i, t in zip(ids, items)],
        )
    except Exception as e:
        logger.error(f"Failed to extract action items: {e}")
        raise HTTPException(status_code=500, detail="Failed to extract action items")


# TODO 4: LLM-powered extraction endpoint
@router.post("/extract-llm", response_model=ExtractResponse)
def extract_llm(payload: ExtractRequest) -> ExtractResponse:
    """Extract action items from text using Ollama LLM."""
    try:
        note_id: Optional[int] = None
        if payload.save_note:
            note_id = db.insert_note(payload.text)

        items = extract_action_items_llm(payload.text)
        ids = db.insert_action_items(items, note_id=note_id)
        return ExtractResponse(
            note_id=note_id,
            items=[ActionItemResponse(id=i, text=t) for i, t in zip(ids, items)],
        )
    except Exception as e:
        logger.error(f"Failed to extract action items via LLM: {e}")
        raise HTTPException(status_code=500, detail="Failed to extract action items via LLM")


@router.get("", response_model=List[ActionItemFullResponse])
def list_all(note_id: Optional[int] = None) -> List[ActionItemFullResponse]:
    """List all action items, optionally filtered by note_id."""
    rows = db.list_action_items(note_id=note_id)
    return [
        ActionItemFullResponse(
            id=r["id"],
            note_id=r["note_id"],
            text=r["text"],
            done=bool(r["done"]),
            created_at=r["created_at"],
        )
        for r in rows
    ]


@router.post("/{action_item_id}/done", response_model=MarkDoneResponse)
def mark_done(action_item_id: int, payload: MarkDoneRequest) -> MarkDoneResponse:
    """Mark an action item as done or undone."""
    db.mark_action_item_done(action_item_id, payload.done)
    return MarkDoneResponse(id=action_item_id, done=payload.done)


