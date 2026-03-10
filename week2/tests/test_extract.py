import os
import json
import pytest
from unittest.mock import patch, MagicMock

from ..app.services.extract import extract_action_items, extract_action_items_llm


# ========== Tests for extract_action_items (heuristic) ==========

def test_extract_bullets_and_checkboxes():
    text = """
    Notes from meeting:
    - [ ] Set up database
    * implement API extract endpoint
    1. Write tests
    Some narrative sentence.
    """.strip()

    items = extract_action_items(text)
    assert "Set up database" in items
    assert "implement API extract endpoint" in items
    assert "Write tests" in items


# ========== TODO 2: Tests for extract_action_items_llm ==========

def _mock_ollama_response(items: list[str]):
    """Helper: create a mock Ollama chat() response with given items."""
    mock_response = MagicMock()
    mock_response.message.content = json.dumps({"items": items})
    return mock_response


@patch("week2.app.services.extract.chat")
def test_llm_extract_bullet_list(mock_chat):
    """Test LLM extraction with a bullet-point list."""
    mock_chat.return_value = _mock_ollama_response([
        "Set up database",
        "Implement API endpoint",
        "Write tests",
    ])

    text = "- Set up database\n- Implement API endpoint\n- Write tests"
    items = extract_action_items_llm(text)

    assert len(items) == 3
    assert "Set up database" in items
    assert "Implement API endpoint" in items
    assert "Write tests" in items
    mock_chat.assert_called_once()


@patch("week2.app.services.extract.chat")
def test_llm_extract_keyword_prefixed(mock_chat):
    """Test LLM extraction with keyword-prefixed lines (TODO, ACTION)."""
    mock_chat.return_value = _mock_ollama_response([
        "Fix login bug",
        "Update user dashboard",
    ])

    text = "TODO: Fix login bug\nACTION: Update user dashboard"
    items = extract_action_items_llm(text)

    assert len(items) == 2
    assert "Fix login bug" in items
    assert "Update user dashboard" in items


@patch("week2.app.services.extract.chat")
def test_llm_extract_empty_input(mock_chat):
    """Test LLM extraction with empty input — should return [] without calling LLM."""
    items_empty = extract_action_items_llm("")
    items_whitespace = extract_action_items_llm("   ")
    items_none = extract_action_items_llm(None)

    assert items_empty == []
    assert items_whitespace == []
    assert items_none == []
    # LLM should NOT be called for empty inputs
    mock_chat.assert_not_called()


@patch("week2.app.services.extract.chat")
def test_llm_extract_no_action_items(mock_chat):
    """Test LLM extraction when text has no actionable items."""
    mock_chat.return_value = _mock_ollama_response([])

    text = "The weather is nice today. Had a great lunch."
    items = extract_action_items_llm(text)

    assert items == []


@patch("week2.app.services.extract.chat")
def test_llm_extract_mixed_content(mock_chat):
    """Test LLM extraction with a mix of action items and narrative text."""
    mock_chat.return_value = _mock_ollama_response([
        "Buy groceries",
        "Schedule dentist appointment",
    ])

    text = """
    Had a good meeting today. The team discussed project timelines.
    - Buy groceries
    Remember to call mom.
    TODO: Schedule dentist appointment
    """.strip()
    items = extract_action_items_llm(text)

    assert len(items) == 2
    assert "Buy groceries" in items
    assert "Schedule dentist appointment" in items


@patch("week2.app.services.extract.chat")
def test_llm_extract_handles_ollama_error(mock_chat):
    """Test that LLM extraction gracefully handles Ollama errors."""
    mock_chat.side_effect = Exception("Connection refused")

    text = "- Buy milk"
    items = extract_action_items_llm(text)

    # Should return empty list on error, not raise
    assert items == []


# ========== Integration tests: actually call Ollama (requires server running) ==========
# Run with: pytest week2/tests/test_extract.py -m integration

@pytest.mark.integration
def test_llm_real_bullet_list():
    """Integration: LLM should extract action items from a bullet list."""
    text = "- Buy milk\n- Call dentist\n- Fix the login bug"
    items = extract_action_items_llm(text)

    assert isinstance(items, list)
    assert len(items) >= 2  # LLM may phrase differently, but should find items


@pytest.mark.integration
def test_llm_real_keyword_prefixed():
    """Integration: LLM should extract from keyword-prefixed lines."""
    text = "TODO: Write unit tests\nACTION: Deploy to staging\nNEXT: Review PR"
    items = extract_action_items_llm(text)

    assert isinstance(items, list)
    assert len(items) >= 2


@pytest.mark.integration
def test_llm_real_empty_input():
    """Integration: empty input should return empty list without calling LLM."""
    assert extract_action_items_llm("") == []
    assert extract_action_items_llm("   ") == []


@pytest.mark.integration
def test_llm_real_no_actions():
    """Integration: narrative text with no actions should return few or no items."""
    text = "The weather was nice today. I had coffee with a friend."
    items = extract_action_items_llm(text)

    assert isinstance(items, list)
    # LLM is non-deterministic, so we just check it returns a reasonable result
    # (not an absurdly large number of items for simple narrative)
    assert len(items) <= 5
