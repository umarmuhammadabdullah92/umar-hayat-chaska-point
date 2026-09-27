#!/usr/bin/env bash
# =====================================================================
# Browser tests for the generated site.
#
#   bash test/run.sh
#
# Serves the project over http, loads the test pages into headless
# Chrome, and reads the results back out of the DOM. Exits non-zero if
# anything failed, so it is usable in CI.
#
# The site has no build-time test suite on purpose: nearly everything
# that can break here is visual or interactive, and only a real browser
# can tell you that a dotted leader is on the wrong baseline.
#
# Two passes, because one browser launch cannot be both of these things:
#
#   browser-test.html      the main suite
#   reduced-motion-test    under --force-prefers-reduced-motion
#
# matchMedia cannot be faked from a page, so the reduced-motion pass
# needs its own process with the flag set.
# =====================================================================
set -uo pipefail

PORT="${PORT:-8931}"
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
CHROME="${CHROME:-google-chrome}"

if ! command -v "$CHROME" >/dev/null 2>&1; then
  echo "test/run.sh: no $CHROME on PATH. Set CHROME=/path/to/chrome." >&2
  exit 2
fi

# The site must be up to date before it is tested, or the results are
# about the last build rather than the current source.
if [ "${SKIP_BUILD:-0}" != "1" ]; then
  echo "building..."
  ( cd "$ROOT" && python3 build.py >/dev/null ) || {
    echo "test/run.sh: build.py failed, not running tests against stale HTML" >&2
    exit 1
  }
fi

cd "$ROOT"
python3 "$ROOT/test/serve.py" "$ROOT" "$PORT" >/dev/null 2>&1 &
SERVER=$!
trap 'kill $SERVER 2>/dev/null' EXIT
sleep 1

# No --disable-gpu here on purpose. It switches the compositor off, and
# IntersectionObserver is delivered by the compositor, so every
# scroll-reveal on the page silently stops firing and the suite reports
# the site as broken when it is the test environment that is broken.
CHROME_FLAGS=(--headless --no-sandbox --disable-dev-shm-usage --hide-scrollbars
              --window-size=1280,900 --virtual-time-budget=400000)

fetch() { # fetch <page> [extra flags...]
  local page="$1"; shift
  timeout 600 "$CHROME" "${CHROME_FLAGS[@]}" "$@" \
    --dump-dom "http://127.0.0.1:$PORT/$page" 2>/dev/null
}

report() { # report <label> <dom>  -> prints, returns 0/1
  local label="$1" dom="$2"
  local body
  body="$(printf '%s' "$dom" | python3 -c '
import html, re, sys
doc = sys.stdin.read()
m = re.search(r"<pre id=\"out\">(.*?)</pre>", doc, re.S)
print(html.unescape(m.group(1)) if m else "__NO_RESULTS__")
')"
  if [ "$body" = "__NO_RESULTS__" ]; then
    echo "test/run.sh: $label produced no results. Is the page reachable?" >&2
    return 2
  fi
  echo
  echo "--- $label"
  echo "$body"
  # An exception part way through run() leaves a short but entirely
  # passing summary, because the assertions before the throw all ran and
  # none of them failed. The page says so in the text; without this the
  # suite reports OK while a dozen checks never executed.
  case "$body" in
    *"HARNESS ERROR"*)
      echo >&2
      echo "test/run.sh: $label threw part way through. The pass count above" >&2
      echo "is only what ran before the exception -- treat it as a failure." >&2
      return 1
      ;;
  esac
  # A pass that never finished still prints its running header.
  case "$body" in
    *"==== "*) ;;
    "running")
      # The untouched placeholder. The script never ran at all, which is
      # what a syntax error does: nothing is registered, so not even the
      # .catch that reports a thrown error is in place.
      echo >&2
      echo "test/run.sh: $label never ran a single assertion. That is a" >&2
      echo "syntax error in the test script, not a site failure. Check it" >&2
      echo "with:  sed -n '/<script>/,/<\/script>/p' <page> | node --check" >&2
      return 1
      ;;
    *) echo "(did not finish)" >&2; return 1 ;;
  esac
  case "$body" in
    *FAIL*) return 1 ;;
    *) return 0 ;;
  esac
}

FAILED=0

DOM="$(fetch test/browser-test.html)"
report "main suite" "$DOM" || FAILED=1

DOM="$(fetch test/reduced-motion-test.html --force-prefers-reduced-motion)"
report "reduced motion" "$DOM" || FAILED=1

if [ "$FAILED" -ne 0 ]; then
  echo
  echo "FAILED"
  exit 1
fi
echo
echo "OK"
