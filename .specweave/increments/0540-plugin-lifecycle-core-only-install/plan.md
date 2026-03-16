# Plan: Plugin Lifecycle — Core-Only Install + Stale Cache Cleanup

## Overview

Four changes to existing files, no new modules. All changes are in the `specweave` repo under `repositories/anton-abyzov/specweave/`.

```
refresh-plugins.ts ──────── core-only default + --plugin flag
       |
update.ts ──────────────── pass core-only to refreshPluginsCommand
       |
cleanup-stale-plugins.ts ── multi-marketplace cache scan + disk cleanup
       |
user-prompt-submit.sh ───── restore on-demand plugin install block
       |
llm-plugin-detector.ts ──── already functional (dormant), no changes needed
claude-plugin-enabler.ts ── already supports single-plugin enable, no changes needed
```

## Architecture Decisions

### D1: Core plugin identity — hardcoded name, not marketplace flag

The spec suggests `core: true` flag in marketplace.json OR hardcoded name. Decision: **hardcoded `sw` constant** in refresh-plugins.ts.

**Why**: Adding a `core` field to marketplace.json requires schema changes, validation, and downstream consumers to understand a new field. The core plugin is definitionally singular and stable -- it has been `sw` since inception and will remain so. A constant is simpler, testable, and explicit.

**Trade-off**: If core ever changes, one constant update vs. config-driven. Acceptable -- this is a once-ever event.

### D2: On-demand loading reactivation — hook calls `specweave refresh-plugins --plugin <name>`

The hook currently has a `REMOVED (v1.0.535)` block where on-demand installation used to be. The `llm-plugin-detector.ts` already detects which plugins a prompt needs (the `.plugins` array in detect-intent output). The hook already parses this JSON.

**Reactivation approach**: In the hook's removed block (line ~1194), restore a section that:
1. Reads the `plugins` array from the LLM detect-intent JSON output
2. For each detected plugin, checks if it is already installed (cache dir exists OR .claude/skills/ dir exists)
3. If not installed, calls `specweave refresh-plugins --plugin <name>` (new flag from US-002)
4. Writes a session-scoped marker file to prevent re-installation (idempotency per AC-US4-04)

**Why not call `claude plugin install` directly from the hook**: The hook runs as bash within Claude Code's sandbox. `specweave refresh-plugins --plugin` is a single CLI call that handles both native and direct-copy modes, settings enablement, and error handling. Reusing it avoids duplicating install logic in shell.

**Why not call `llm-plugin-detector.ts` Node API directly**: The hook is bash, and `detect-intent` is already being called. The plugin list is already in the JSON response. No additional Node process needed.

### D3: Multi-marketplace cache cleanup — directory scan, not hardcoded list

`cleanup-stale-plugins.ts` currently hardcodes `marketplace === 'specweave'`. The fix:
1. Scan `~/.claude/plugins/cache/` for subdirectories (each is a marketplace)
2. For each marketplace, resolve its `marketplace.json` from the local marketplaces directory
3. Compare cache subdirectories against the marketplace's plugin list
4. Remove stale settings.json entries AND stale cache directories

**marketplace.json resolution**: Each marketplace's source is at `~/.claude/plugins/marketplaces/<marketplace>/.claude-plugin/marketplace.json`. If this file exists, use it. If not, skip the marketplace (per AC-US3-03). No remote fetches during cleanup -- this keeps it fast and safe.

### D4: `--plugin` flag precedence over `--all`

Per spec AC-US2-03, `--plugin` takes precedence when combined with `--all`. This is the least-surprising behavior: the user explicitly named a plugin, so honor that specificity.

## Component Changes

### C1: `refresh-plugins.ts` — Core-only default + `--plugin` flag

**Current behavior**: Iterates `allPlugins` from marketplace.json, installs each one.

**New behavior**:

```typescript
const CORE_PLUGIN = 'sw';

interface RefreshPluginsOptions {
  verbose?: boolean;
  force?: boolean;
  all?: boolean;           // install ALL plugins (was incorrectly deprecated)
  plugin?: string;         // NEW: install a single named plugin
  quiet?: boolean;         // NEW: suppress console output (for hook usage)
}
```

Logic change in `refreshPluginsCommand`:
1. If `options.plugin` is set: filter `allPlugins` to just that one (error if not found)
2. Else if `options.all` is set: install all (current behavior)
3. Else (default): filter to `CORE_PLUGIN` only
4. After install, existing non-core plugins are left in place (no uninstall step)
5. If `options.quiet`, suppress all console.log output

The `@deprecated` comment on `all` is removed. `--all` is now the explicit opt-in for full install.

**Validation for `--plugin`**: If the named plugin is not in marketplace.json, print available names and exit with code 1 (process.exitCode = 1).

### C2: `update.ts` — Pass through core-only

**Current behavior**: Calls `refreshPluginsCommand({ all: options.all, ... })`.

**New behavior**: No functional change needed. The `all` flag already flows through. Without `--all`, refresh now defaults to core-only. The existing `--all` option on `update` already maps correctly.

One minor change: update the JSDoc comment on `RefreshPluginsOptions.all` from `@deprecated` to active documentation.

### C3: `cleanup-stale-plugins.ts` — Multi-marketplace + disk cleanup

**Extended `CleanupResult`**:
```typescript
export interface CleanupResult {
  success: boolean;
  removedCount: number;
  removedPlugins: string[];         // settings.json entries removed
  removedCacheDirs: string[];       // NEW: cache directories removed from disk
  error?: string;
}
```

**New logic added after existing settings.json cleanup**:

```
Phase 1 (existing, extended): Settings cleanup
  - Scan ~/.claude/plugins/cache/ for marketplace subdirs
  - For each marketplace, resolve marketplace.json from
    ~/.claude/plugins/marketplaces/<marketplace>/.claude-plugin/marketplace.json
  - If unresolvable, skip (log warning if verbose)
  - Compare settings.json enabledPlugins against valid plugins for EACH marketplace
  - Remove stale entries

Phase 2 (new): Cache directory cleanup
  - For each marketplace with a resolved manifest:
    - List subdirs under ~/.claude/plugins/cache/<marketplace>/
    - If a subdir name is not in that marketplace's plugin list, remove it
    - Symlinks: remove the symlink itself, not the target
```

**Safety**: The `REMOVED_PLUGINS` hardcoded set is kept as a secondary safety net for the specweave marketplace specifically.

### C4: `user-prompt-submit.sh` — Restore on-demand plugin install

Replace the `REMOVED (v1.0.535)` comment block (lines 1194-1201) with an on-demand install section.

**Pseudocode**:
```bash
# ON-DEMAND PLUGIN INSTALL (v1.0.540 - restored)
DETECTED_PLUGINS=$(echo "$JSON_OUTPUT" | jq -r '.plugins[]? // empty' 2>/dev/null)
if [[ -n "$DETECTED_PLUGINS" ]]; then
  CACHE_BASE="${HOME}/.claude/plugins/cache/specweave"
  SKILLS_BASE="${SW_PROJECT_ROOT:-.}/.claude/skills"
  SESSION_MARKER_DIR="${TMPDIR:-/tmp}/specweave-ondemand-$$"
  mkdir -p "$SESSION_MARKER_DIR" 2>/dev/null

  while IFS= read -r PLUGIN_NAME; do
    [[ -z "$PLUGIN_NAME" ]] && continue
    [[ "$PLUGIN_NAME" == "sw" ]] && continue  # core always installed

    # Idempotency: skip if already installed or already attempted this session
    if [[ -d "$CACHE_BASE/$PLUGIN_NAME" ]] || \
       [[ -d "$SKILLS_BASE/$PLUGIN_NAME" ]] || \
       [[ -f "$SESSION_MARKER_DIR/$PLUGIN_NAME" ]]; then
      continue
    fi

    # Install via CLI (handles both native and direct-copy modes)
    specweave refresh-plugins --plugin "$PLUGIN_NAME" --quiet 2>/dev/null &
    touch "$SESSION_MARKER_DIR/$PLUGIN_NAME" 2>/dev/null

    AUTOLOAD_PLUGINS_MSG="${AUTOLOAD_PLUGINS_MSG}Installed plugin: ${PLUGIN_NAME} (on-demand).
"
  done <<< "$DETECTED_PLUGINS"

  # Wait for background installs (max 5s timeout)
  WAIT_PID=$!
  if [[ -n "$WAIT_PID" ]]; then
    ( sleep 5 && kill $WAIT_PID 2>/dev/null ) &
    TIMEOUT_PID=$!
    wait $WAIT_PID 2>/dev/null
    kill $TIMEOUT_PID 2>/dev/null
  fi
fi
```

**Key details**:
- Background install with bounded wait to avoid blocking the hook response
- Session marker uses `$$` (PID) which is unique per Claude Code session
- Falls back gracefully: if `specweave` CLI unavailable, the existing guard at line 1112 already prevents reaching this code
- Checks both cache dir (native install) and skills dir (direct-copy mode) for installed state

### C5: Commander registration updates

In the `refresh-plugins` command registration (wherever Commander options are set), add:
```
.option('--plugin <name>', 'Install a specific plugin by name')
.option('-q, --quiet', 'Suppress output (for hooks)')
```

## Task Sequence

### T-001: Add `--plugin`, `--quiet` flags and core-only default to refresh-plugins.ts
**US**: US-001, US-002 | **ACs**: AC-US1-01, AC-US1-02, AC-US1-03, AC-US2-01, AC-US2-02, AC-US2-03

### T-002: Verify update.ts pass-through and update docs
**US**: US-001 | **AC**: AC-US1-04

### T-003: Extend cleanup-stale-plugins.ts for multi-marketplace + disk cleanup
**US**: US-003 | **ACs**: AC-US3-01, AC-US3-02, AC-US3-03, AC-US3-04

### T-004: Restore on-demand plugin loading in user-prompt-submit.sh
**US**: US-004 | **ACs**: AC-US4-01, AC-US4-02, AC-US4-03, AC-US4-04

## Testing Strategy

All tests use Vitest. Key test scenarios:

- **refresh-plugins**: mock marketplace.json, verify only `sw` installed by default, verify `--all` installs all, verify `--plugin foo` installs one, verify `--plugin bad` errors with available names list
- **cleanup-stale-plugins**: mock cache directory structure with multiple marketplaces, verify dynamic discovery, verify stale dir removal, verify skip on missing manifest, verify symlink handling
- **hook (manual)**: verify on-demand install triggers when LLM detects plugins, verify idempotency, verify graceful degradation

## Risks and Mitigations

| Risk | Mitigation |
|------|------------|
| On-demand `wait` blocks hook response | Bounded 5s timeout; install runs in background; worst case user gets plugin on next prompt |
| Session PID marker stale across restarts | PID changes per session; stale markers in /tmp auto-cleaned by OS |
| Removing cache dirs while Claude Code reads them | Use atomic rename: rename dir first, then remove renamed dir |
| `--quiet` leaks errors to stderr | Redirect stderr to /dev/null in hook invocation |

## Dependencies

No new npm packages. No new modules. All changes modify existing files only.

## Domain Skill Delegation

No domain skills needed. This is CLI infrastructure -- all TypeScript/bash, no frontend or backend service work.
