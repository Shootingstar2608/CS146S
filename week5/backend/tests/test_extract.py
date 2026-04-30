from backend.app.services.extract import extract_action_items, extract_hashtags


def test_extract_action_items():
    text = """
    This is a note
    - TODO: write tests
    - Ship it!
    Not actionable
    """.strip()
    items = extract_action_items(text)
    assert "TODO: write tests" in items
    assert "Ship it!" in items


def test_extract_checkboxes():
    text = "- [ ] Deploy to prod\n- [ ] Write docs\n- [x] Done already"
    items = extract_action_items(text)
    assert "Deploy to prod" in items
    assert "Write docs" in items
    assert len(items) == 2  # [x] should not match


def test_extract_hashtags():
    text = "Working on #python and #ai today. Also #Python again."
    tags = extract_hashtags(text)
    assert "python" in tags
    assert "ai" in tags
    assert len(tags) == 2  # deduplication


def test_extract_no_hashtags():
    assert extract_hashtags("No tags here") == []


def test_extract_no_action_items():
    assert extract_action_items("Just a regular line") == []


def test_extract_mixed():
    text = """
    #feature request
    - [ ] add dark mode
    - TODO: review PR!
    Some normal text #urgent
    """.strip()
    items = extract_action_items(text)
    tags = extract_hashtags(text)
    assert "add dark mode" in items
    assert "TODO: review PR!" in items
    assert "feature" in tags
    assert "urgent" in tags
