"""Pytest configuration for week2 tests."""


def pytest_configure(config):
    """Register custom markers to avoid warnings."""
    config.addinivalue_line(
        "markers",
        "integration: marks tests that require Ollama server running (deselect with '-m \"not integration\"')",
    )
