#!/usr/bin/env bash
# ──────────────────────────────────────────────────────────────
# docs-sync.sh — Warp Drive Automation: Docs Sync
# Generates/updates docs/API.md from the FastAPI /openapi.json
# endpoint, listing all routes with methods, descriptions, and
# highlighting route deltas compared to the previous version.
#
# Usage:  ./scripts/docs-sync.sh [--port PORT]
# ──────────────────────────────────────────────────────────────
set -euo pipefail

PORT=${PORT:-8000}
BASE_URL="http://127.0.0.1:$PORT"
API_MD="docs/API.md"

while [[ $# -gt 0 ]]; do
  case "$1" in
    --port) PORT="$2"; BASE_URL="http://127.0.0.1:$PORT"; shift 2;;
    *)      echo "Unknown arg: $1"; exit 1;;
  esac
done

echo "╔══════════════════════════════════════════╗"
echo "║   📄 Docs Sync — API.md from OpenAPI    ║"
echo "╚══════════════════════════════════════════╝"
echo ""

# Check if server is running
if ! curl -sf "$BASE_URL/openapi.json" > /dev/null 2>&1; then
  echo "⚠ Server not reachable at $BASE_URL. Starting temporarily..."
  PYTHONPATH=. python3 -m uvicorn backend.app.main:app --host 127.0.0.1 --port "$PORT" &
  SERVER_PID=$!
  sleep 2
  STARTED_SERVER=true
else
  STARTED_SERVER=false
fi

# Fetch OpenAPI spec
echo "▶ Fetching /openapi.json..."
SPEC=$(curl -sf "$BASE_URL/openapi.json")

# Save previous routes for delta detection
PREV_ROUTES=""
if [[ -f "$API_MD" ]]; then
  PREV_ROUTES=$(grep -E '^\| `(GET|POST|PUT|DELETE|PATCH)' "$API_MD" 2>/dev/null || true)
fi

# Generate markdown
echo "▶ Generating $API_MD..."
{
  echo "# API Documentation"
  echo ""
  echo "> Auto-generated from \`/openapi.json\` by \`scripts/docs-sync.sh\`"
  echo "> Last updated: $(date -u '+%Y-%m-%d %H:%M:%S UTC')"
  echo ""
  echo "## Endpoints"
  echo ""
  echo "| Method | Path | Summary |"
  echo "|--------|------|---------|"

  echo "$SPEC" | python3 -c "
import sys, json
spec = json.load(sys.stdin)
paths = spec.get('paths', {})
for path in sorted(paths.keys()):
    for method in ['get','post','put','delete','patch']:
        if method in paths[path]:
            info = paths[path][method]
            summary = info.get('summary', info.get('operationId', '-'))
            print(f'| \`{method.upper()}\` | \`{path}\` | {summary} |')
"
} > "$API_MD"

# Delta detection
NEW_ROUTES=$(grep -E '^\| `(GET|POST|PUT|DELETE|PATCH)' "$API_MD" 2>/dev/null || true)

echo ""
if [[ "$PREV_ROUTES" != "$NEW_ROUTES" ]]; then
  echo "📊 Route changes detected:"
  diff <(echo "$PREV_ROUTES") <(echo "$NEW_ROUTES") || true
else
  echo "📊 No route changes detected."
fi

echo ""
echo "✅ $API_MD updated successfully."

# Cleanup
if [[ "$STARTED_SERVER" == "true" ]]; then
  kill $SERVER_PID 2>/dev/null || true
  echo "🛑 Temporary server stopped."
fi
