# Week 5 Write-up
Tip: To preview this markdown file
- On Mac, press `Command (⌘) + Shift + V`
- On Windows/Linux, press `Ctrl + Shift + V`

## INSTRUCTIONS

Fill out all of the `TODO`s in this file.

## SUBMISSION DETAILS

Name: **Phuc, Tan, Huy, Quan** \
<!-- SUNet ID: **peter** \ -->
Citations: **Warp University (https://www.warp.dev/university), FastAPI docs, SQLAlchemy docs**

This assignment took me about **5** hours to do. 


## YOUR RESPONSES
### Automation A: Warp Drive saved prompts, rules, MCP servers

a. Design of each automation, including goals, inputs/outputs, steps

> **Automation A1 — Test Runner with Coverage & Flaky Re-run** (Warp Drive Saved Prompt + Rule)
>
> **Goal:** Automate the test workflow — run pytest, collect coverage, and automatically retry flaky tests without manual re-invocation.
>
> **Inputs:** `retry_count` (default: 2) — max retries for failed tests; `min_coverage` (default: 60) — minimum acceptable coverage %.
>
> **Outputs:** Pass/fail summary with test counts, coverage report, non-zero exit code on failure for CI integration.
>
> **Steps:**
> 1. Warp Drive saved prompt invokes `scripts/test-runner.sh` with parameterized `--retry` and `--cov-min` arguments.
> 2. Script runs `pytest -q --tb=short` against `backend/tests`.
> 3. If any test fails, the script automatically re-runs only previously-failed tests (`--lf`) up to N times.
> 4. A formatted summary is printed with ✅/❌ status.
> 5. A companion **Warp Rule** (`week5-test-conventions`) enforces naming conventions and assertion patterns for all test files in `week5/backend/tests/`.
>
> **Automation A2 — Docs Sync: API.md from OpenAPI** (Warp Drive Saved Prompt)
>
> **Goal:** Keep `docs/API.md` synchronized with the actual API by auto-generating it from `/openapi.json`, detecting route deltas.
>
> **Inputs:** `port` (default: 8000) — the server port.
>
> **Outputs:** Updated `docs/API.md` file, stdout delta report showing added/removed/changed routes.
>
> **Steps:**
> 1. Saved prompt invokes `scripts/docs-sync.sh --port 8000`.
> 2. Script checks if the server is running; if not, starts a temporary uvicorn instance.
> 3. Fetches `/openapi.json` via curl.
> 4. Parses the spec with Python, generates a markdown endpoint table.
> 5. Diffs new routes against the previous `API.md` to detect deltas.
> 6. Writes the updated file and stops the temporary server if one was started.

b. Before vs. after (i.e. manual workflow vs. automated workflow)

> **Before (manual):**
> - Test runner: Manually type `make test`, visually scan output for failures, manually re-run failed tests by copy-pasting test names, no coverage tracking.
> - Docs sync: Open browser to `/docs`, manually copy endpoint details, write markdown by hand, no delta detection when routes change.
>
> **After (automated):**
> - Test runner: One saved prompt invocation runs the full cycle — tests + retries + coverage + summary — in under 5 seconds. The Warp Rule ensures new tests follow conventions automatically.
> - Docs sync: One prompt invocation regenerates `API.md`, highlights exactly which routes were added/removed/changed, and the whole process is idempotent.

c. Autonomy levels used for each completed task (what code permissions, why, and how you supervised)

> - **Test runner:** Used Warp's *"Suggest" autonomy level* — the agent suggests the test command and I approve before execution. This is appropriate because tests are read-only and safe, but I wanted to verify the retry count before running.
> - **Docs sync:** Used *"Auto-run" autonomy level* for the script execution since it only writes to `docs/API.md` (a generated file) and has no destructive side effects. I supervised by reviewing the delta output after each run.
> - **Code changes for tasks 3, 4, 6, 7:** Used *"Suggest" autonomy level* — the agent proposed code edits which I reviewed in Warp's diff view before accepting. This ensured no unintended changes to the existing codebase.

d. (if applicable) Multi‑agent notes: roles, coordination strategy, and concurrency wins/risks/failures

> Not directly applicable to Automation A (Warp Drive prompts are single-agent). See Automation B for multi-agent notes.

e. How you used the automation (what pain point it resolves or accelerates)

> - **Test runner:** Eliminates the pain of manually re-running flaky tests. In a codebase with SQLite and file-based state, occasional test flakiness from timing/locking is common. The automated retry catches these without developer intervention. The coverage check ensures new features don't reduce test quality.
> - **Docs sync:** Eliminates documentation drift. Every time a new endpoint is added (e.g., `PUT /notes/{id}`, `POST /action-items/bulk-complete`), the docs-sync automation catches it and updates the reference. The delta detection makes code review faster since reviewers can immediately see which API surface changed.



### Automation B: Multi‑agent workflows in Warp 

a. Design of each automation, including goals, inputs/outputs, steps

> **Multi-Agent Concurrent Task Implementation**
>
> **Goal:** Implement multiple independent TASKS.md tasks simultaneously using separate Warp agent tabs, demonstrating concurrent agentic development.
>
> **Setup:** Two Warp tabs with independent agent sessions, each assigned a self-contained task:
> - **Agent 1 (Tab 1):** Task 3 — Full Notes CRUD with optimistic UI updates (PUT/DELETE endpoints + frontend)
> - **Agent 2 (Tab 2):** Task 4 — Action items filters and bulk complete (filter query params + bulk endpoint + frontend)
>
> **Coordination strategy:** Since Task 3 and Task 4 modify different files (notes router vs. action_items router, different sections of app.js), they can run concurrently without conflicts. Shared files (`schemas.py`, `main.py`) were pre-prepared with all necessary models before launching the agents.
>
> **Steps:**
> 1. Pre-define shared schemas (`NoteUpdate`, `BulkCompleteRequest`) in `schemas.py` to avoid merge conflicts.
> 2. Open Warp Tab 1: Prompt agent to implement Task 3 — add `PUT /notes/{id}` and `DELETE /notes/{id}`, update frontend with edit modal and delete buttons, add tests.
> 3. Open Warp Tab 2: Prompt agent to implement Task 4 — add `GET /action-items?completed=...` filter, `POST /action-items/bulk-complete`, update frontend with filter tabs and bulk UI, add tests.
> 4. Both agents work concurrently. After completion, run the full test suite to verify no conflicts.
> 5. Separately implemented Task 6 (extraction logic) and Task 7 (error handling) as follow-up tasks.

b. Before vs. after (i.e. manual workflow vs. automated workflow)

> **Before (single-agent sequential):**
> - Implement Task 3 fully (router, frontend, tests) → ~20 minutes.
> - Then implement Task 4 fully → ~20 minutes.
> - Total: ~40 minutes sequential.
>
> **After (multi-agent concurrent):**
> - Agent 1 handles Task 3 while Agent 2 handles Task 4 simultaneously.
> - Total wall-clock time: ~22 minutes (limited by the slower task + merge verification).
> - **Speedup: ~1.8x** for two agents on independent tasks.

c. Autonomy levels used for each completed task (what code permissions, why, and how you supervised)

> - Both agents used *"Suggest" autonomy level* for code modifications — each agent proposed changes that I reviewed before accepting.
> - For test execution, I used *"Auto-run"* since `pytest` is non-destructive.
> - I supervised by monitoring both tabs simultaneously in Warp's split-pane view, checking that neither agent modified files outside its assigned scope.

d. (if applicable) Multi‑agent notes: roles, coordination strategy, and concurrency wins/risks/failures

> **Roles:**
> - Agent 1: "Notes CRUD Agent" — responsible for `notes.py` router, note-related frontend code, `test_notes.py`
> - Agent 2: "Action Items Agent" — responsible for `action_items.py` router, action-item frontend code, `test_action_items.py`
>
> **Coordination strategy:**
> - **Pre-partitioned shared dependencies:** `schemas.py` was updated with all new models before launching agents, preventing write conflicts.
> - **File-level isolation:** Each agent was instructed to only modify its assigned files. The frontend (`app.js`) was the highest-risk shared file, so I allocated distinct functions to each agent.
> - **Git worktree consideration:** For a larger project, `git worktree` would allow each agent to work in its own working directory. For this project, file-level partitioning was sufficient.
>
> **Wins:**
> - ~1.8x wall-clock speedup on two independent features.
> - Both agents could run tests independently without blocking each other.
>
> **Risks:**
> - Merge conflicts on shared files (`app.js`, `schemas.py`) — mitigated by pre-preparation.
> - Agents could accidentally duplicate effort or introduce inconsistencies — mitigated by clear task boundaries.
>
> **Failures:**
> - None encountered. The pre-partitioning strategy successfully avoided conflicts.

e. How you used the automation (what pain point it resolves or accelerates)

> Multi-agent workflows resolve the **sequential bottleneck** of implementing independent features one at a time. In a real project with many self-contained tasks (like TASKS.md), spinning up multiple Warp agents can parallelize the work and significantly reduce total development time. The key insight is that careful pre-planning of shared dependencies is essential — spending 5 minutes partitioning files saves 15+ minutes of conflict resolution.

