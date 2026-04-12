from backend.app.services.extract import extract_action_items, extract_tags


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


def test_extract_action_items_empty():
    assert extract_action_items("") == []


def test_extract_action_items_no_matches():
    text = "Just a regular note\nWith regular lines"
    assert extract_action_items(text) == []


def test_extract_tags_basic():
    text = "This is a #python note about #fastapi"
    tags = extract_tags(text)
    assert "python" in tags
    assert "fastapi" in tags


def test_extract_tags_empty():
    assert extract_tags("") == []


def test_extract_tags_no_tags():
    assert extract_tags("No tags here") == []


def test_extract_tags_duplicates():
    text = "#python is great, I love #python and #PYTHON"
    tags = extract_tags(text)
    assert len(tags) == 1
    assert tags[0] == "python"


def test_extract_tags_inline():
    text = "Working on #backend and #frontend today #backend"
    tags = extract_tags(text)
    assert tags == ["backend", "frontend"]


def test_extract_tags_with_numbers():
    text = "Using #python3 and #web2024"
    tags = extract_tags(text)
    assert "python3" in tags
    assert "web2024" in tags
