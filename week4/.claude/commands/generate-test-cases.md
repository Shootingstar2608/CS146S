---
name: generate-test-cases
description: Analyze a module and generate comprehensive test cases for uncovered code paths
---

Analyze the module at `$ARGUMENTS` and generate comprehensive test cases.

## Steps

1. **Read the target module** at `$ARGUMENTS` and identify all public functions, classes, and API endpoints (including HTTP method, path, parameters, request body, and response model).

2. **Read existing tests** in `backend/tests/` to identify which functions/endpoints already have test coverage. Pay attention to:
   - Which endpoints are tested (GET, POST, PUT, DELETE)
   - Which edge cases are covered (empty input, not found, duplicates, boundary values)
   - Which error paths are covered (400, 404, 422 responses)

3. **Identify coverage gaps** — list all untested or under-tested paths:
   - Missing happy-path tests for endpoints
   - Missing edge-case tests (empty strings, very long input, special characters)
   - Missing error-path tests (404 for nonexistent IDs, 422 for invalid payloads)
   - Missing boundary tests (min/max values, empty lists)

4. **Generate new test functions** following these conventions:
   - Use the `client` fixture from `conftest.py`
   - Name tests descriptively: `test_{action}_{scenario}` (e.g., `test_delete_note_not_found`)
   - Each test should be independent and self-contained
   - Include both the action and assertion in each test
   - Follow the existing code style (see `backend/CLAUDE.md`)

5. **Write the tests** to the appropriate test file in `backend/tests/`. Append new tests — do NOT delete or modify existing tests.

6. **Run the test suite**:
   ```bash
   PYTHONPATH=. pytest -q backend/tests --maxfail=3 -x
   ```

7. **If any tests fail**, analyze the failure:
   - If the test expectation is wrong, fix the test
   - If the implementation has a bug, note it but keep the test as-is (it's documenting expected behavior)
   - Re-run until all tests pass

8. **Run lint check**:
   ```bash
   ruff check .
   ```
   Fix any lint issues found.

9. **Summarize results**:
   - List all new test functions added
   - Report test results (passed/failed counts)
   - Note any implementation bugs discovered
   - Suggest next steps if coverage is still incomplete
