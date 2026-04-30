# Warp Drive Automation: Docs Sync — API.md from OpenAPI

## Overview

A Warp Drive **saved prompt** that auto-generates and updates `docs/API.md` from the live FastAPI `/openapi.json` endpoint, detecting route deltas compared to the previous version.

## Warp Drive Configuration

### Saved Prompt

**Name:** `Docs Sync — API.md`  
**Description:** Generate/update API documentation from OpenAPI spec  

**Prompt Template:**
```
Synchronize the API documentation for the Week 5 project.

Steps:
1. cd to the week5 directory
2. Run: bash scripts/docs-sync.sh --port {{port:8000}}
3. Review the generated docs/API.md
4. Report any route deltas (added/removed/changed endpoints)
5. If there are new endpoints without descriptions, suggest adding summaries to the FastAPI route decorators

Constraints:
- Only update docs/API.md
- Do not modify backend code without confirmation
- If the server is not running, start it temporarily and stop it after
```

**Parameters:**
| Parameter | Default | Description |
|-----------|---------|-------------|
| `port` | 8000 | Port where the FastAPI server is running |

### MCP Server Integration (Optional)

If using the **Git MCP server** with Warp, the docs-sync prompt can be extended:

```
After updating API.md:
1. Use Git MCP to create a branch: docs/api-sync-{date}
2. Stage and commit docs/API.md with message "docs: sync API.md from openapi.json"
3. Prepare PR notes summarizing the route deltas
```

## Helper Script

**Path:** `scripts/docs-sync.sh`

```bash
./scripts/docs-sync.sh --port 8000
```

Features:
- Fetches `/openapi.json` from the running server
- Auto-starts a temporary server if none is running
- Generates a markdown table of all endpoints
- Detects and displays route deltas vs. previous `API.md`
- Idempotent — safe to run repeatedly

## Inputs / Outputs

| | Description |
|---|---|
| **Input** | `port` (int) — server port |
| **Output** | Updated `docs/API.md`, route delta report in stdout |
