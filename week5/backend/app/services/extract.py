import re


def extract_action_items(text: str) -> list[str]:
    """Extract action items from text.

    Recognised patterns:
    - Lines ending with ``!``
    - Lines starting with ``TODO:`` (case-insensitive)
    - Markdown checkbox ``- [ ] task text``
    """
    items: list[str] = []
    for raw_line in text.splitlines():
        line = raw_line.strip()
        if not line:
            continue
        # Markdown checkbox: - [ ] task text
        m = re.match(r"^-\s*\[\s*\]\s*(.+)$", line)
        if m:
            items.append(m.group(1).strip())
            continue
        # Strip leading list marker for legacy patterns
        cleaned = line.lstrip("- ").strip()
        if cleaned.endswith("!") or cleaned.lower().startswith("todo:"):
            items.append(cleaned)
    return items


def extract_hashtags(text: str) -> list[str]:
    """Extract unique ``#hashtag`` tokens from *text*.

    Returns a deduplicated list preserving first-occurrence order.
    """
    tags: list[str] = []
    seen: set[str] = set()
    for match in re.finditer(r"#(\w+)", text):
        tag = match.group(1).lower()
        if tag not in seen:
            seen.add(tag)
            tags.append(tag)
    return tags
