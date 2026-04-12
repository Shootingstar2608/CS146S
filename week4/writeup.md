# Week 4 Write-up
Tip: To preview this markdown file
- On Mac, press `Command (⌘) + Shift + V`
- On Windows/Linux, press `Ctrl + Shift + V`

## INSTRUCTIONS

Fill out all of the `TODO`s in this file.

## SUBMISSION DETAILS

Name: **Đỗ Hồng Phúc, Nguyễn Phúc Huy, Lê Thanh Tân, Nguyễn Đức Quân** \
Citations: Claude Code best practices (https://www.anthropic.com/engineering/claude-code-best-practices), SubAgents documentation (https://docs.anthropic.com/en/docs/claude-code/sub-agents)

This assignment took us about **10** hours to do.


## YOUR RESPONSES
### Automation #1: Custom Slash Command — `/project:generate-test-cases`
a. Design inspiration (e.g. cite the best-practices and/or sub-agents docs)
> Inspired by the **Claude Code best practices** document, specifically the sections on "Give Claude a way to verify its work" and "Create skills." The best practices recommend building reusable, idempotent workflows as slash commands and using `$ARGUMENTS` for flexible input. The example of a test runner with coverage (Example 1 in the assignment) also influenced this design — but extended to not just *run* tests but *generate* them automatically.

b. Design of each automation, including goals, inputs/outputs, steps
> **Goal**: Automatically analyze a Python module, identify untested code paths, generate comprehensive test cases, run them, and report results.
>
> **Input**: `$ARGUMENTS` — path to the module to analyze (e.g., `backend/app/routers/notes.py`)
>
> **Output**: New test functions appended to the appropriate test file, with a summary of tests added, pass/fail results, and suggested next steps.
>
> **Steps**:
> 1. Read the target module and identify all endpoints/functions
> 2. Read existing tests in `backend/tests/` to identify coverage gaps
> 3. Identify untested paths: missing happy paths, edge cases, error cases, boundary tests
> 4. Generate new test functions following project conventions (using `client` fixture)
> 5. Write tests to the appropriate test file (append only — never modify existing tests)
> 6. Run `PYTHONPATH=. pytest -q backend/tests --maxfail=3 -x`
> 7. If tests fail, analyze and fix; re-run until all pass
> 8. Run `ruff check .` to verify lint compliance
> 9. Summarize results

c. How to run it (exact commands), expected outputs, and rollback/safety notes
> **How to run** (inside Claude Code):
> ```
> /project:generate-test-cases backend/app/routers/notes.py
> ```
>
> **Expected output**: Claude reads `notes.py`, compares with `test_notes.py`, identifies gaps (e.g., missing tests for PUT/DELETE/404/validation), generates test functions, appends them to `test_notes.py`, runs pytest, and reports results like:
> ```
> ✅ Added 8 new tests:
>   - test_get_note_by_id
>   - test_get_note_not_found
>   - test_update_note_title
>   - test_update_note_content
>   - test_update_note_not_found
>   - test_delete_note
>   - test_delete_note_not_found
>   - test_create_note_empty_title
> All 23 tests passed. No lint issues.
> ```
>
> **Rollback**: The command is safe — it only appends tests, never modifies existing ones. To rollback: `git checkout backend/tests/`
>
> **Safety**: Idempotent — running it again skips already-covered paths. Only writes to test files. Uses read-only analysis of production code.

d. Before vs. after (i.e. manual workflow vs. automated workflow)
> **Before (manual)**:
> 1. Developer reads the module manually
> 2. Mentally tracks which functions have tests and which don't
> 3. Writes each test function by hand, looking up pytest fixtures and test patterns
> 4. Runs pytest, debugs failures, iterates
> 5. Total time: 15-30 minutes per module
>
> **After (automated)**:
> 1. Run `/project:generate-test-cases backend/app/routers/notes.py`
> 2. Claude analyzes, generates, runs, and reports — all in one command
> 3. Developer reviews the generated tests and approves
> 4. Total time: 2-3 minutes per module

e. How you used the automation to enhance the starter application
> Used `/project:generate-test-cases` to generate comprehensive test coverage for the notes and action_items routers. The command identified that the original test suite had major gaps:
> - No tests for GET by ID (notes)
> - No tests for 404 error cases
> - No validation tests (empty strings)
> - No tests for the new PUT/DELETE endpoints
>
> After running the command, the test suite went from **4 basic tests** to **23 comprehensive tests** covering happy paths, error paths, edge cases, and validation. This gave confidence that the CRUD enhancements were working correctly.


### Automation #2: `CLAUDE.md` Repository Guidance Files
a. Design inspiration (e.g. cite the best-practices and/or sub-agents docs)
> Inspired by the **"Write an effective CLAUDE.md"** section of the Claude Code best practices. Key recommendations followed:
> - Keep it concise and actionable (not a novel)
> - Document safe commands vs. commands to avoid
> - Include workflow snippets (e.g., "When adding a new endpoint...")
> - Use parent/child `CLAUDE.md` files for hierarchical guidance (root for project overview, `backend/` for backend-specific patterns)
>
> The best practices doc also recommends: "Iterate on CLAUDE.md like a prompt" — treating it as a living document that evolves with the project.

b. Design of each automation, including goals, inputs/outputs, steps
> **Goal**: Provide Claude with persistent, repository-specific context so it follows project conventions automatically — without needing to repeat instructions each session.
>
> **Files created**:
>
> 1. **`week4/CLAUDE.md`** (root level):
>    - Project overview and tech stack
>    - Directory structure map
>    - How to run/test/format/lint (exact commands)
>    - Code style conventions (black, ruff, type hints, relative imports)
>    - Safe vs. unsafe commands
>    - Step-by-step workflow guides (adding endpoints, modifying models, frontend changes)
>
> 2. **`week4/backend/CLAUDE.md`** (backend-specific):
>    - Architecture diagram (routers → models → schemas → services)
>    - Database patterns (dependency injection, transaction management, flush vs commit)
>    - Router CRUD pattern templates
>    - Error handling conventions (HTTPException codes, detail messages)
>    - Schema patterns (Create, Read, Update with Config)
>    - Testing patterns (fixtures, naming, standard assertions)
>    - Step-by-step "When adding a new feature" checklist
>
> **Input**: None — CLAUDE.md files are read automatically when Claude starts a session.
>
> **Output**: Claude follows project conventions consistently without needing reminders.

c. How to run it (exact commands), expected outputs, and rollback/safety notes
> **How to run**: No explicit command needed — `CLAUDE.md` is automatically read by Claude Code when starting any session in the repository. The root `CLAUDE.md` is always loaded, and `backend/CLAUDE.md` is loaded when working with files in `backend/`.
>
> **To verify it's working**: Start a new Claude Code session and ask Claude about project conventions — it should cite the `CLAUDE.md` guidance.
>
> **Rollback**: Simply delete the files: `rm week4/CLAUDE.md week4/backend/CLAUDE.md`
>
> **Safety**: These are purely informational files — they don't execute anything. They guide Claude's behavior through natural language instructions.

d. Before vs. after (i.e. manual workflow vs. automated workflow)
> **Before (manual)**:
> 1. Developer starts a Claude session and types: "Use SQLAlchemy with SQLite, follow black formatting, tests are in backend/tests/, use db.flush() not db.commit()..."
> 2. Each session requires re-explaining the full project context
> 3. Claude might use wrong patterns (e.g., `db.commit()` instead of `db.flush()`)
> 4. Inconsistent coding style across sessions
>
> **After (automated)**:
> 1. Developer starts a Claude session — CLAUDE.md is automatically loaded
> 2. Claude immediately knows: tech stack, file structure, conventions, safe commands
> 3. Every session is consistent — same patterns, same style
> 4. No need to repeat project-specific instructions

e. How you used the automation to enhance the starter application
> The `CLAUDE.md` files served as the foundation for all other automations and app enhancements:
> - When implementing PUT/DELETE endpoints for notes, Claude followed the CRUD router pattern documented in `backend/CLAUDE.md`
> - When writing tests, Claude followed the testing patterns (client fixture, naming convention, assertion style)
> - When adding validation, Claude correctly used `db.flush()` instead of `db.commit()` because the `CLAUDE.md` explicitly documented this pattern
> - The SubAgents (test-agent and code-agent) reference `CLAUDE.md` in their prompts, ensuring they also follow conventions


### *(Optional) Automation #3: SubAgents — TestAgent + CodeAgent TDD Pipeline*
*If you choose to build additional automations, feel free to detail them here!*

a. Design inspiration (e.g. cite the best-practices and/or sub-agents docs)
> Inspired by the **SubAgents documentation** and the assignment's Example 1 (TestAgent + CodeAgent). Key concepts from the docs:
> - "Preserve context by keeping exploration and implementation out of your main conversation"
> - "Enforce constraints by limiting which tools a subagent can use"
> - "Specialize behavior with focused system prompts for specific domains"
>
> Also drew from the best practices section on **"Create custom subagents"**, which shows how to define agents with YAML frontmatter specifying name, description, tools, and model.

b. Design of each automation, including goals, inputs/outputs, steps
> **Goal**: Implement a TDD (Test-Driven Development) pipeline using two cooperating SubAgents.
>
> **TestAgent** (`.claude/agents/test-agent.md`):
> - Role: Senior QA engineer
> - Tools: Read, Glob, Grep, Bash, Write, Edit
> - Model: Sonnet (fast, cost-effective for test writing)
> - Behavior: Reads feature requirements → writes comprehensive failing tests → verifies tests fail → reports
> - Constraints: NEVER implements production code, NEVER modifies existing passing tests
>
> **CodeAgent** (`.claude/agents/code-agent.md`):
> - Role: Senior backend developer
> - Tools: Read, Glob, Grep, Bash, Write, Edit
> - Model: Sonnet
> - Behavior: Reads failing tests → implements minimum production code → runs tests → runs lint → reports
> - Constraints: NEVER modifies test files, writes MINIMUM code to pass tests
>
> **Workflow**:
> 1. User describes a feature (e.g., "Add PUT /notes/{id} to edit notes")
> 2. Invoke TestAgent: write tests defining expected behavior
> 3. Invoke CodeAgent: implement code to pass the tests
> 4. Invoke TestAgent again: verify all tests pass

c. How to run it (exact commands), expected outputs, and rollback/safety notes
> **How to run** (inside Claude Code):
> ```
> # Step 1: Ask TestAgent to write tests
> Use the test-agent to write tests for adding PUT /notes/{id} to update a note's title and content
>
> # Step 2: Ask CodeAgent to implement
> Use the code-agent to implement the code needed to pass the new failing tests
>
> # Step 3: Verify
> Use the test-agent to verify all tests pass
> ```
>
> **Expected output**: TestAgent writes 3-5 test functions → CodeAgent adds the PUT endpoint, NoteUpdate schema, and router logic → all tests pass.
>
> **Rollback**: `git checkout backend/` to revert all changes.
>
> **Safety**: Each agent has a clear, limited mandate. TestAgent can't modify production code; CodeAgent can't modify tests. Both are constrained to the project's tool set.

d. Before vs. after (i.e. manual workflow vs. automated workflow)
> **Before (manual TDD)**:
> 1. Developer writes tests (context: feature requirements + test patterns)
> 2. Developer switches mental mode to implementation
> 3. Developer writes code (context: failing tests + code patterns)
> 4. Developer runs tests, iterates
> 5. Context switching is cognitively expensive
>
> **After (automated TDD)**:
> 1. User describes the feature once
> 2. TestAgent writes comprehensive tests (specialized for QA)
> 3. CodeAgent implements code (specialized for development)
> 4. Each agent has focused context — no context switching overhead
> 5. Clear separation of concerns enforced by tool restrictions

e. How you used the automation to enhance the starter application
> Used the TestAgent + CodeAgent pipeline to implement the Notes CRUD enhancements (Task 5 from TASKS.md):
> - **TestAgent** wrote failing tests for `PUT /notes/{id}` (update title, update content, not found) and `DELETE /notes/{id}` (success, not found)
> - **CodeAgent** implemented the `NoteUpdate` schema, `update_note()` and `delete_note()` router functions, and updated the frontend with edit/delete buttons
> - **TestAgent** verified all 23 tests passed
> This demonstrated the TDD workflow: tests defined the specification, and the implementation was driven entirely by making those tests pass.
