# Implementation Plan: Fix Hook Error Reliability

## Overview

Bug fix increment targeting 6 distinct root causes of spurious hook error messages during Claude Code sessions. All fixes are localized edits to existing shell scripts, JSON config files, and state files -- no new components, no architectural changes.

Aligns with existing ADR-0068 (Circuit Breaker Error Isolation), ADR-0060 (Hook Performance Optimization), and ADR-0156 (Hook Registration Single Source).

## Fix Inventory

| # | Root Cause | Fix | Files |
|---|-----------|-----|-------|
| 1 | jq null subtraction in dashboard cache script | Add `// 0` null-coalescing to 6 decrement ops | `update-dashboard-cache.sh` |
| 2 | `close-completed-issues.sh` fires on every Edit/Write | Add `matcher_content` scoped to `.specweave/increments/` | `.claude/settings.json` |
| 3 | Dead `ac-status-sync.sh` hook config entry | Remove config entry, keep script file | `.claude/settings.json` |
| 4 | Stuck circuit breaker blocks GitHub auto-create | Delete state file | `.specweave/state/.hook-circuit-breaker-github-auto-create` |
| 5 | Hookify plugin spawns 2 empty Python processes per tool call | Remove hookify hook entries from project config | `.claude/settings.json` |
| 6 | Version bump | Bump to 1.0.492 | `package.json` (in specweave repo) |

## Implementation Strategy

**Approach**: Direct targeted edits. No abstraction layers, no new patterns.

**Order**: Fixes 1-5 are independent and parallelizable. Fix 6 (version bump) happens last after all others are verified.

### Fix 1: Null-Safe jq Decrements

The script `update-dashboard-cache.sh` has 6 occurrences of `.summary[$key] -= 1` that crash when the key does not exist in the JSON cache. Each must be replaced with the jq null-coalescing pattern:

```bash
# Before (crashes on null)
.summary[$key] -= 1

# After (defaults to 0)
.summary[$key] = ((.summary[$key] // 0) - 1)
```

All 6 occurrences follow the same pattern -- mechanical find-and-replace.

### Fix 2: Scoped PostToolUse Matcher

Add `matcher_content` to the `close-completed-issues.sh` hook config so it only fires on increment file edits:

```json
"matcher_content": ".specweave/increments/"
```

This prevents the hook from executing on every Edit/Write, saving 200-500ms per non-increment operation.

### Fix 3: Remove Dead Hook Entry

Delete the `ac-status-sync.sh` hook config entry from `.claude/settings.json`. The shell script file on disk is preserved for potential future use (per AC-US3-02).

### Fix 4: Delete Stuck Circuit Breaker

```bash
rm -f .specweave/state/.hook-circuit-breaker-github-auto-create
```

File contains value "3" (threshold reached), blocking all GitHub auto-create hooks. Deletion resets the circuit breaker per the pattern documented in ADR-0068.

### Fix 5: Remove Hookify Plugin Entries

Remove all hookify hook entries from project-level config. These spawn Python processes via `hookify run` with no rule files to process -- pure overhead. This is a user config change (project `.claude/settings.json`), not a source code change in the hookify plugin itself.

### Fix 6: NPM Patch Release

Bump `package.json` version to `1.0.492` in the specweave repo. Publish after all fixes land.

## Testing Strategy

- **Fix 1**: Verify jq expressions handle null keys (run script against cache with missing keys)
- **Fix 2**: Verify hook fires on `.specweave/increments/*/tasks.md` edit, does NOT fire on other files
- **Fix 3**: Verify `ac-status-sync.sh` no longer appears in hook execution
- **Fix 4**: Verify circuit breaker file is absent, GitHub auto-create hook executes
- **Fix 5**: Verify no Python/hookify processes spawned during tool calls
- **Fix 6**: Verify `package.json` reads `1.0.492`

## Technical Challenges

None significant. All fixes are straightforward config/script edits with well-understood behavior. The only nuance is ensuring the jq null-coalescing syntax is correct across all 6 occurrences (parentheses placement matters for jq operator precedence).
