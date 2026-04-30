# Warp Drive Automation: Test Runner with Coverage & Flaky Re-run

## Overview

A Warp Drive **saved prompt** that runs the project test suite with coverage reporting and automatic flaky-test retries.

## Warp Drive Configuration

### Saved Prompt

**Name:** `Test Runner — Week 5`  
**Description:** Run pytest with coverage and retry flaky tests  

**Prompt Template:**
```
Run the test suite for the Week 5 project with coverage and flaky-test retries.

Steps:
1. cd to the week5 directory
2. Run: bash scripts/test-runner.sh --retry {{retry_count:2}} --cov-min {{min_coverage:60}}
3. If tests fail after retries, analyze the failure output and suggest fixes
4. Summarize: total tests, passed, failed, coverage percentage

Constraints:
- Use PYTHONPATH=. prefix
- Only modify files in week5/
- Do not auto-fix without confirmation
```

**Parameters:**
| Parameter | Default | Description |
|-----------|---------|-------------|
| `retry_count` | 2 | Max retry attempts for flaky tests |
| `min_coverage` | 60 | Minimum acceptable coverage % |

### Warp Rule

**Name:** `week5-test-conventions`  
**Scope:** Files in `week5/backend/tests/`  

```yaml
name: week5-test-conventions
description: Enforce test conventions for the Week 5 starter app
rules:
  - All test functions must start with test_
  - Use the `client` fixture from conftest.py for API tests
  - Assert response status codes before inspecting body
  - Test both success and error (400/404/422) scenarios
  - Use descriptive test names: test_{action}_{scenario}
```

## Helper Script

**Path:** `scripts/test-runner.sh`

```bash
./scripts/test-runner.sh --retry 3 --cov-min 70
```

Features:
- Runs `pytest` with `-q --tb=short`
- Retries only previously-failed tests (`--lf`) up to N times
- Pretty-printed summary with pass/fail status
- Non-zero exit code on failure (CI-friendly)

## Inputs / Outputs

| | Description |
|---|---|
| **Input** | `retry_count` (int), `min_coverage` (int) |
| **Output** | Test results summary, coverage report, pass/fail exit code |
