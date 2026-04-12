import re


def extract_action_items(text: str) -> list[str]:
    """Extract action items from text.

    Lines ending with '!' or starting with 'TODO:' (case-insensitive)
    are considered action items.
    """
    lines = [line.strip("- ") for line in text.splitlines() if line.strip()]
    return [line for line in lines if line.endswith("!") or line.lower().startswith("todo:")]


def extract_tags(text: str) -> list[str]:
    """Extract hashtag-style tags from text.

    Finds all occurrences of '#word' patterns in the text.
    Returns a deduplicated list of tags (without the '#' prefix),
    in the order they first appear.
    """
    tags = re.findall(r"#(\w+)", text)
    # Deduplicate while preserving order
    seen: set[str] = set()
    unique_tags: list[str] = []
    for tag in tags:
        lower_tag = tag.lower()
        if lower_tag not in seen:
            seen.add(lower_tag)
            unique_tags.append(tag)
    return unique_tags
