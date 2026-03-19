# Architecture Plan: Fix Remaining Hook Reliability Issues

## Overview

Five classes of targeted bug fixes across SpecWeave hook scripts. No new architecture -- each fix is a surgical change to an existing file with a clear before/after pattern.

All changes live under `repositories/anton-abyzov/specweave/plugins/specweave/`.

---

## Fix 1: PreToolUse Early Exit + matcher_content Scoping (US-001, US-003)

### Problem

The PreToolUse hook in `hooks.json` has no `matcher_content` filter, so it fires on **every** Edit/Write operation regardless of target file. The script itself checks `[[ ! -d ".specweave" ]]` using a bare relative path (breaks when cwd is not project root) and invokes jq even when the file is clearly not an increment file. This adds 200-500ms overhead to every file operation.

Additionally, PostToolUse and `.claude/settings.json` use `matcher_content: "\\.specweave/increments/"` which matches string literals *inside* file content (e.g., test files that reference `.specweave/increments/`), not just the `file_path` field.

### Changes

**File: `hooks/hooks.json`**

Add `matcher_content` to PreToolUse entry to match only the file_path field in the JSON input:

```
BEFORE (line 3-11):
{
  "matcher": "Write|Edit",
  "hooks": [...]
}

AFTER:
{
  "matcher": "Write|Edit",
  "matcher_content": "\"file_path\"\\s*:\\s*\"[^\"]*\\.specweave/increments/",
  "hooks": [...]
}
```

Update PostToolUse `matcher_content` to the same file_path-scoped pattern:

```
BEFORE (line 56):
"matcher_content": "\\.specweave/increments/"

AFTER:
"matcher_content": "\"file_path\"\\s*:\\s*\"[^\"]*\\.specweave/increments/"
```

**File: `.claude/settings.json` (umbrella repo)**

Same regex scoping for the PostToolUse entry:

```
BEFORE (line 10):
"matcher_content": "\\.specweave/increments/"

AFTER:
"matcher_content": "\"file_path\"\\s*:\\s*\"[^\"]*\\.specweave/increments/"
```

**File: `hooks/v2/dispatchers/pre-tool-use.sh`**

Replace bare `.specweave` check with walk-up root detection, and add an early file_path extraction to skip non-increment files before jq:

```
BEFORE (lines 22-23):
# Skip if not a SpecWeave project
[[ ! -d ".specweave" ]] && echo '{"decision":"allow"}' && exit 0

AFTER:
# Detect project root via walk-up (cwd may not be root)
_DIR="$PWD"
_LIMIT=0
while [[ "$_DIR" != "/" ]] && [[ ! -d "$_DIR/.specweave" ]] && [[ $_LIMIT -lt 50 ]]; do
  _DIR=$(dirname "$_DIR")
  _LIMIT=$((_LIMIT + 1))
done
[[ ! -d "$_DIR/.specweave" ]] && echo '{"decision":"allow"}' && exit 0

# Fast file_path check: skip non-increment files before jq (< 5ms)
if ! echo "$INPUT" | grep -q '"file_path".*\.specweave/increments/'; then
  echo '{"decision":"allow"}'
  exit 0
fi
```

### Satisfies

- AC-US1-01 (matcher_content in hooks.json)
- AC-US1-02 (early exit before jq)
- AC-US1-03 (walk-up root detection replaces bare relative path)
- AC-US3-01 (PostToolUse matcher_content scoped to file_path)
- AC-US3-02 (PreToolUse matcher_content scoped to file_path)
- AC-US3-03 (.claude/settings.json matcher_content scoped to file_path)
- AC-US3-04 (test file content no longer triggers false positive)

---

## Fix 2: Dashboard Cache Normalization Parity (US-002)

### Problem

`update-dashboard-cache.sh` has a `normalize_status_key()` function that only normalizes status (`planned` -> `planning`). However, `rebuild-dashboard-cache.sh` also normalizes **type** and **priority** via `case` fallbacks:

- Unknown type -> `feature` counter
- Unknown priority -> `P1` counter
- Unknown status -> `backlog` counter

The update script passes raw values as jq counter keys, creating phantom entries like `byType["enhancement"]` or `byPriority["medium"]` that don't exist in the rebuild output.

Additionally, when the cache file is missing and the update script falls back to calling rebuild, it uses `$PROJECT_ROOT/plugins/specweave/scripts/rebuild-dashboard-cache.sh` -- a path that assumes `PROJECT_ROOT` is the plugin installation root, not the user's project root. At hook time these are different directories.

### Changes

**File: `scripts/update-dashboard-cache.sh`**

Add `normalize_type_key()` and `normalize_priority_key()` functions after existing `normalize_status_key()`:

```
AFTER normalize_status_key() (line 93):

# Normalize type to canonical counter keys (matches rebuild-dashboard-cache.sh)
# Source of truth: rebuild-dashboard-cache.sh lines 232-240
normalize_type_key() {
  case "$1" in
    feature|hotfix|bug|refactor|experiment|change-request) echo "$1" ;;
    *) echo "feature" ;;
  esac
}

# Normalize priority to canonical counter keys (matches rebuild-dashboard-cache.sh)
# Source of truth: rebuild-dashboard-cache.sh lines 243-249
normalize_priority_key() {
  case "$1" in
    P0|P1|P2|P3) echo "$1" ;;
    high) echo "P0" ;;
    medium) echo "P1" ;;
    low) echo "P2" ;;
    *) echo "P1" ;;
  esac
}
```

Apply normalization to all counter-update paths. Raw values remain in increment data; only counter keys are normalized:

```
BEFORE (line 139-140):
type=$(jq -r '.type // "feature"' "$metadata_file" 2>/dev/null)
priority=$(jq -r '.priority // "P1"' "$metadata_file" 2>/dev/null)

AFTER:
raw_type=$(jq -r '.type // "feature"' "$metadata_file" 2>/dev/null)
raw_priority=$(jq -r '.priority // "P1"' "$metadata_file" 2>/dev/null)
type=$(normalize_type_key "$raw_type")
priority=$(normalize_priority_key "$raw_priority")
```

Fix rebuild fallback path to use `BASH_SOURCE` instead of `PROJECT_ROOT`:

```
BEFORE (line 72):
  bash "$PROJECT_ROOT/plugins/specweave/scripts/rebuild-dashboard-cache.sh" --quiet

AFTER:
  SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
  bash "$SCRIPT_DIR/rebuild-dashboard-cache.sh" --quiet
```

### Satisfies

- AC-US2-01 (priority normalization: "medium" -> "P1")
- AC-US2-02 (type normalization)
- AC-US2-03 (BASH_SOURCE fallback for rebuild path)

---

## Fix 3: jq Null-Coalescing Guards (US-004)

### Problem

Five jq `| length` operations across three scripts crash when the input field is `null` or absent. jq's `null | length` returns an error, not 0.

### Changes

**File: `scripts/auto-status.sh`**

```
BEFORE (lines 132-134):
QUEUE_LENGTH=$(echo "$SESSION" | jq '.incrementQueue | length')
COMPLETED_COUNT=$(echo "$SESSION" | jq '.completedIncrements | length')
FAILED_COUNT=$(echo "$SESSION" | jq '.failedIncrements | length')

AFTER:
QUEUE_LENGTH=$(echo "$SESSION" | jq '.incrementQueue // [] | length')
COMPLETED_COUNT=$(echo "$SESSION" | jq '.completedIncrements // [] | length')
FAILED_COUNT=$(echo "$SESSION" | jq '.failedIncrements // [] | length')
```

**File: `scripts/cancel-auto.sh`**

```
BEFORE (line 54):
COMPLETED=$(echo "$SESSION" | jq -r '.completedIncrements | length')

AFTER:
COMPLETED=$(echo "$SESSION" | jq -r '.completedIncrements // [] | length')
```

**File: `hooks/user-prompt-submit.sh`**

```
BEFORE (line 2191):
PROJECT_COUNT=$(echo "$CONTEXT_JSON" | jq '.projects | length' 2>/dev/null || echo "0")

AFTER:
PROJECT_COUNT=$(echo "$CONTEXT_JSON" | jq '.projects // [] | length' 2>/dev/null || echo "0")
```

Also fix lines 1349 and 1520 (same pattern, different variable):

```
BEFORE (lines 1349, 1520):
ROUTING_SKILLS_COUNT=$(echo "$JSON_OUTPUT" | jq -r '.routing.skills | length // 0' 2>/dev/null)

AFTER:
ROUTING_SKILLS_COUNT=$(echo "$JSON_OUTPUT" | jq -r '.routing.skills // [] | length' 2>/dev/null)
```

Note: The existing pattern `.routing.skills | length // 0` is wrong -- jq evaluates `(length) // 0` which only falls back if `length` returns `null` (it doesn't; it errors on null input). The correct form is `.routing.skills // [] | length` which coalesces before the length call.

Line 2125 already has `// []` -- no change needed there.

### Satisfies

- AC-US4-01 (auto-status.sh: 3 operations)
- AC-US4-02 (cancel-auto.sh: 1 operation)
- AC-US4-03 (user-prompt-submit.sh: line 2191 plus lines 1349 and 1520)

---

## Fix 4: Bare Relative Path Elimination (US-005)

### Problem

Four scripts reference `.specweave/` using bare relative paths that resolve against `$PWD`. When Claude Code or a hook invokes these scripts from a subdirectory, the paths fail silently.

### Changes

**File: `hooks/startup-health-check.sh`**

Replace all bare `.specweave/` references with walk-up detection:

```
BEFORE (lines 10-11):
if [ ! -f ".specweave/config.json" ]; then
    exit 0
fi

AFTER:
# Detect project root via walk-up
_DIR="$PWD"
_LIMIT=0
while [ "$_DIR" != "/" ] && [ ! -d "$_DIR/.specweave" ] && [ $_LIMIT -lt 50 ]; do
  _DIR=$(dirname "$_DIR")
  _LIMIT=$((_LIMIT + 1))
done
if [ ! -f "$_DIR/.specweave/config.json" ]; then
    exit 0
fi
PROJECT_ROOT="$_DIR"
```

Then replace all subsequent bare references:

```
BEFORE (lines 34-35):
AUTO_MODE_FILE=".specweave/state/auto-mode.json"
STATE_DIR=".specweave/state"

AFTER:
AUTO_MODE_FILE="$PROJECT_ROOT/.specweave/state/auto-mode.json"
STATE_DIR="$PROJECT_ROOT/.specweave/state"
```

**File: `hooks/v2/guards/status-completion-guard.sh`**

Add walk-up detection after INPUT read, replace bare paths:

```
BEFORE (lines 41, 54):
AUTO_STATE_FILE=".specweave/state/auto/session.json"
DONE_MARKER=".specweave/state/.sw-done-in-progress"

AFTER (insert walk-up before these lines):
# Detect project root via walk-up
_DIR="$PWD"
_LIMIT=0
while [[ "$_DIR" != "/" ]] && [[ ! -d "$_DIR/.specweave" ]] && [[ $_LIMIT -lt 50 ]]; do
  _DIR=$(dirname "$_DIR")
  _LIMIT=$((_LIMIT + 1))
done
_ROOT="$_DIR"

AUTO_STATE_FILE="$_ROOT/.specweave/state/auto/session.json"
DONE_MARKER="$_ROOT/.specweave/state/.sw-done-in-progress"
```

**File: `hooks/v2/guards/increment-existence-guard.sh`**

Replace bare `.specweave/increments` reference:

```
BEFORE (line 176):
if [[ -d ".specweave/increments" ]]; then

AFTER:
# Detect project root via walk-up
_DIR="$PWD"
_LIMIT=0
while [[ "$_DIR" != "/" ]] && [[ ! -d "$_DIR/.specweave" ]] && [[ $_LIMIT -lt 50 ]]; do
  _DIR=$(dirname "$_DIR")
  _LIMIT=$((_LIMIT + 1))
done
_ROOT="$_DIR"

if [[ -d "$_ROOT/.specweave/increments" ]]; then
```

Also update the `find` commands on lines 182 and 192 to use `$_ROOT`:

```
BEFORE:
  done < <(find .specweave/increments -maxdepth 2 -name "spec.md" 2>/dev/null)

AFTER:
  done < <(find "$_ROOT/.specweave/increments" -maxdepth 2 -name "spec.md" 2>/dev/null)
```

**File: `hooks/v2/dispatchers/pre-tool-use.sh`**

Already covered in Fix 1. The walk-up detection replaces the `[[ ! -d ".specweave" ]]` check. No additional bare paths remain in this file after that fix.

### Satisfies

- AC-US5-01 (startup-health-check.sh)
- AC-US5-02 (status-completion-guard.sh)
- AC-US5-03 (increment-existence-guard.sh)
- AC-US5-04 (pre-tool-use.sh -- handled in Fix 1)

---

## Walk-Up Root Detection Pattern

All four scripts that need root detection use the same inline pattern (spec explicitly states no shared library import for this increment):

```bash
_DIR="$PWD"
_LIMIT=0
while [[ "$_DIR" != "/" ]] && [[ ! -d "$_DIR/.specweave" ]] && [[ $_LIMIT -lt 50 ]]; do
  _DIR=$(dirname "$_DIR")
  _LIMIT=$((_LIMIT + 1))
done
```

Key properties:
- **50-iteration cap** prevents infinite loops on symlink cycles
- **Follows symlinks** via `-d` test (default behavior on both macOS and Linux)
- **Finds nearest ancestor** by walking up from `$PWD`
- **`[[ ]]` vs `[ ]`**: Use `[[ ]]` in bash scripts, `[ ]` in sh-compatible scripts (startup-health-check.sh uses `[ ]`)

---

## Implementation Order

1. **Fix 3** (jq null-coalescing) -- zero-risk, pure safety guards
2. **Fix 4** (bare paths) -- foundation for other fixes, low coupling
3. **Fix 2** (dashboard normalization) -- self-contained, independent of other fixes
4. **Fix 1** (PreToolUse + matcher_content) -- touches hooks.json config and dispatcher, do last for easier testing

---

## Risk Mitigations

| Risk | Mitigation |
|------|------------|
| Scoped regex breaks legitimate triggers | Test regex against all known file_path patterns: absolute paths, relative paths, paths with special chars in directory names |
| Walk-up cap of 50 too low/high | 50 levels exceeds any realistic directory depth; cap prevents runaway loops |
| Normalization functions diverge from rebuild | Comment in each function references rebuild-dashboard-cache.sh as source of truth |
| `// []` changes behavior for non-null non-array | All affected fields are documented as arrays in the session schema; `// []` only activates on null/missing |

---

## Files Modified (Complete List)

| File | Fix | ACs |
|------|-----|-----|
| `plugins/specweave/hooks/hooks.json` | 1 | AC-US1-01, AC-US3-01, AC-US3-02 |
| `plugins/specweave/hooks/v2/dispatchers/pre-tool-use.sh` | 1, 4 | AC-US1-02, AC-US1-03, AC-US5-04 |
| `.claude/settings.json` (umbrella) | 1 | AC-US3-03 |
| `plugins/specweave/scripts/update-dashboard-cache.sh` | 2 | AC-US2-01, AC-US2-02, AC-US2-03 |
| `plugins/specweave/scripts/auto-status.sh` | 3 | AC-US4-01 |
| `plugins/specweave/scripts/cancel-auto.sh` | 3 | AC-US4-02 |
| `plugins/specweave/hooks/user-prompt-submit.sh` | 3 | AC-US4-03 |
| `plugins/specweave/hooks/startup-health-check.sh` | 4 | AC-US5-01 |
| `plugins/specweave/hooks/v2/guards/status-completion-guard.sh` | 4 | AC-US5-02 |
| `plugins/specweave/hooks/v2/guards/increment-existence-guard.sh` | 4 | AC-US5-03 |

No new files. No deleted files. No architecture changes.
