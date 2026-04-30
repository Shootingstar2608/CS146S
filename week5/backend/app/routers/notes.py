from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import select
from sqlalchemy.orm import Session

from ..db import get_db
from ..models import Note
from ..schemas import ExtractionResult, NoteCreate, NoteRead, NoteUpdate
from ..services.extract import extract_action_items, extract_hashtags

router = APIRouter(prefix="/notes", tags=["notes"])


@router.get("/", response_model=list[NoteRead])
def list_notes(db: Session = Depends(get_db)) -> list[NoteRead]:
    rows = db.execute(select(Note)).scalars().all()
    return [NoteRead.model_validate(row) for row in rows]


@router.post("/", response_model=NoteRead, status_code=201)
def create_note(payload: NoteCreate, db: Session = Depends(get_db)) -> NoteRead:
    note = Note(title=payload.title, content=payload.content)
    db.add(note)
    db.flush()
    db.refresh(note)
    return NoteRead.model_validate(note)


@router.get("/search/", response_model=list[NoteRead])
def search_notes(q: Optional[str] = None, db: Session = Depends(get_db)) -> list[NoteRead]:
    if not q:
        rows = db.execute(select(Note)).scalars().all()
    else:
        rows = (
            db.execute(select(Note).where((Note.title.contains(q)) | (Note.content.contains(q))))
            .scalars()
            .all()
        )
    return [NoteRead.model_validate(row) for row in rows]


@router.get("/{note_id}", response_model=NoteRead)
def get_note(note_id: int, db: Session = Depends(get_db)) -> NoteRead:
    note = db.get(Note, note_id)
    if not note:
        raise HTTPException(status_code=404, detail="Note not found")
    return NoteRead.model_validate(note)


@router.put("/{note_id}", response_model=NoteRead)
def update_note(note_id: int, payload: NoteUpdate, db: Session = Depends(get_db)) -> NoteRead:
    note = db.get(Note, note_id)
    if not note:
        raise HTTPException(status_code=404, detail="Note not found")

    if payload.title is not None:
        note.title = payload.title
    if payload.content is not None:
        note.content = payload.content

    db.add(note)
    db.flush()
    db.refresh(note)
    return NoteRead.model_validate(note)


@router.delete("/{note_id}", status_code=204)
def delete_note(note_id: int, db: Session = Depends(get_db)) -> None:
    note = db.get(Note, note_id)
    if not note:
        raise HTTPException(status_code=404, detail="Note not found")
    db.delete(note)
    db.flush()


@router.post("/{note_id}/extract", response_model=ExtractionResult)
def extract_from_note(
    note_id: int,
    apply: bool = Query(False, description="Persist extracted items when true"),
    db: Session = Depends(get_db),
) -> ExtractionResult:
    note = db.get(Note, note_id)
    if not note:
        raise HTTPException(status_code=404, detail="Note not found")

    hashtags = extract_hashtags(note.content)
    actions = extract_action_items(note.content)

    if apply:
        from ..models import ActionItem

        for desc in actions:
            item = ActionItem(description=desc, completed=False)
            db.add(item)
        db.flush()

    return ExtractionResult(hashtags=hashtags, action_items=actions)
