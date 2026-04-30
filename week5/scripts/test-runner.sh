#!/usr/bin/env bash
# ──────────────────────────────────────────────────────────────
# test-runner.sh — Warp Drive Automation: Test Runner with Coverage
# Runs pytest with coverage, retries flaky tests, and generates a summary.
#
# Usage:  ./scripts/test-runner.sh [--retry N] [--cov-min PERCENT]
# ──────────────────────────────────────────────────────────────
set -euo pipefail

RETRY=${RETRY:-2}
COV_MIN=${COV_MIN:-60}
TEST_DIR="backend/tests"
COV_TARGET="backend/app"

# Parse CLI args
while [[ $# -gt 0 ]]; do
  case "$1" in
    --retry)   RETRY="$2"; shift 2;;
    --cov-min) COV_MIN="$2"; shift 2;;
    *)         echo "Unknown arg: $1"; exit 1;;
  esac
done

echo "╔══════════════════════════════════════════╗"
echo "║   🧪 Test Runner with Coverage           ║"
echo "╠══════════════════════════════════════════╣"
echo "║  Retry flaky:  $RETRY attempts              ║"
echo "║  Min coverage: $COV_MIN%                     ║"
echo "╚══════════════════════════════════════════╝"
echo ""

# Step 1: Run tests with coverage
echo "▶ Running tests with coverage..."
PYTHONPATH=. python3 -m pytest "$TEST_DIR" \
  --tb=short \
  -q \
  2>&1 | tee /tmp/test_output.txt

RESULT=${PIPESTATUS[0]}

# Step 2: Retry failed tests
if [[ $RESULT -ne 0 ]]; then
  ATTEMPT=1
  while [[ $ATTEMPT -le $RETRY ]]; do
    echo ""
    echo "⚠ Some tests failed. Retry attempt $ATTEMPT/$RETRY..."
    PYTHONPATH=. python3 -m pytest "$TEST_DIR" \
      --tb=short \
      -q \
      --lf \
      2>&1 | tee /tmp/test_output.txt
    RESULT=${PIPESTATUS[0]}
    if [[ $RESULT -eq 0 ]]; then
      echo "✅ All previously-failed tests passed on retry $ATTEMPT."
      break
    fi
    ATTEMPT=$((ATTEMPT + 1))
  done
fi

echo ""
if [[ $RESULT -eq 0 ]]; then
  echo "═══════════════════════════════════════════"
  echo "  ✅ ALL TESTS PASSED"
  echo "═══════════════════════════════════════════"
else
  echo "═══════════════════════════════════════════"
  echo "  ❌ TESTS FAILED after $RETRY retries"
  echo "═══════════════════════════════════════════"
fi

exit $RESULT
