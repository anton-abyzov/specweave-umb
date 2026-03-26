# Architecture Plan: Hooks CLI Delegation

## ADR Reference

New ADR: `0247-hooks-cli-delegation.md` — Records the decision to migrate from bash hook scripts to TypeScript CLI handlers via `specweave hook <event>`.

Related ADRs:
- `0060-hook-performance-optimization.md` — Three-tier performance approach (still applies)
- `0070-hook-consolidation.md` — Consolidated dispatchers (now replaced by CLI)
- `0156-hook-registration-single-source.md` — hooks.json as SSOT (preserved)
- `0189-resilient-hook-execution.md` — Error isolation patterns (ported to TS)
- `0230-userpromptsubmit-hook-additionalcontext-fix.md` — additionalContext pattern (ported)

## 1. System Overview

### Current State
- 63 bash scripts (704 KB) in `plugins/specweave/hooks/`
- Deeply nested: `universal/`, `v2/dispatchers/`, `v2/guards/`, `v2/handlers/`, `v2/detectors/`, `v2/integrations/`, `v2/lib/`, `v2/queue/`, `lib/`, `_archive/`, `tests/`
- `hooks.json` routes events through `universal/run-hook.sh` -> `fail-fast-wrapper.sh` -> actual handler
- Heavy reliance on `jq`, `bash`, `grep`, `sed` -- breaks on Windows, fragile on macOS
- `plugin-copier.ts` (lines 907-933) copies all hook files to `~/.claude/hooks/` on install

### Target State
- 11 TypeScript handler files in `src/core/hooks/handlers/`
- `hooks.json` routes all events to `specweave hook <event-type>` CLI command
- `specweave` is globally installed via npm -- available on all platforms
- Hook stdin piped to handler, handler writes JSON to stdout
- Zero bash dependency for hook execution

## 2. Component Architecture

### 2.1 CLI Command Entry Point

**File**: `src/cli/commands/hook.ts`

```
specweave hook <event-type>
```

- Registered in `bin/specweave.js` as: `program.command('hook <event-type>')`
- Reads stdin (JSON from Claude Code), passes to hook-router
- Outputs JSON to stdout (Claude Code hook response)
- Must exit 0 always (crash prevention)

**Design**: Thin wrapper -- delegates to `hook-router.ts` immediately. No option parsing beyond event-type.

### 2.2 Hook Router

**File**: `src/core/hooks/handlers/hook-router.ts`

Responsibilities:
1. Read stdin as JSON (with timeout guard -- 5s max)
2. Resolve project root (walk up from cwd, find `.specweave/config.json`)
3. Check `SPECWEAVE_DISABLE_HOOKS=1` for global kill switch
4. Dynamic import the correct handler based on event-type
5. Execute handler, return JSON result
6. Wrap everything in try/catch -- always output valid JSON

**Event-type to Handler mapping**:

| Event Type | Handler Module | Default Response |
|---|---|---|
| `user-prompt-submit` | `user-prompt-submit.ts` | `{"decision":"approve"}` |
| `pre-tool-use` | `pre-tool-use.ts` | `{"decision":"allow"}` |
| `post-tool-use` | `post-tool-use.ts` | `{"continue":true}` |
| `post-tool-use-analytics` | `post-tool-use-analytics.ts` | (exit 0, no output) |
| `session-start` | `session-start.ts` | `{"continue":true}` |
| `pre-compact` | `pre-compact.ts` | `{"continue":true}` |
| `stop-reflect` | `stop-reflect.ts` | `{"decision":"approve"}` |
| `stop-auto` | `stop-auto.ts` | `{"decision":"approve"}` |
| `stop-sync` | `stop-sync.ts` | `{"decision":"approve"}` |

**Dynamic import pattern** (fast startup):
```typescript
const handlers: Record<string, () => Promise<{ handle: HandlerFn }>> = {
  'user-prompt-submit': () => import('./user-prompt-submit.js'),
  'pre-tool-use': () => import('./pre-tool-use.js'),
  // ...only the requested handler is loaded
};
```

### 2.3 Handler Interface

Every handler exports a `handle` function:

```typescript
export interface HookInput {
  [key: string]: unknown;
}

export interface HookResult {
  decision?: 'approve' | 'block' | 'allow';
  continue?: boolean;
  reason?: string;
  systemMessage?: string;
  hookSpecificOutput?: {
    hookEventName: string;
    additionalContext?: string;
  };
  [key: string]: unknown;
}

export interface HookContext {
  projectRoot: string;
  stateDir: string;
  logsDir: string;
  configPath: string;
  timestamp: string;
}

export type HandlerFn = (
  input: HookInput,
  context: HookContext,
) => Promise<HookResult>;
```

### 2.4 Shared Utilities

**File**: `src/core/hooks/handlers/utils.ts`

```typescript
// findProjectRoot() - walk up from cwd to find .specweave/config.json
// readStdin(timeoutMs) - read stdin with timeout, parse JSON
// writeResult(result) - JSON.stringify to stdout
// createContext(projectRoot) - build HookContext from projectRoot
// logHook(context, handler, message) - append to .specweave/logs/hooks.log
```

### 2.5 Individual Handlers

#### `user-prompt-submit.ts` (Most complex -- 2550 lines bash -> ~800 lines TS)

Ported logic from `user-prompt-submit.sh`:
1. Ultra-fast early exit if not a SpecWeave project
2. Plugin auto-detection via `detect-intent` (reuses existing `detectIntentCommand`)
3. Discipline validation (scope guard, WIP limits)
4. Context injection via `hookSpecificOutput.additionalContext`
5. Instant command execution (/sw:progress, /sw:status, /sw:jobs, etc.)
6. Context budget management (reads `context-pressure.json`)

**Key reuse**: Calls `detectIntentCommand()` directly from `src/cli/commands/detect-intent.ts` (already TypeScript). The bash version shells out to `specweave detect-intent` as a subprocess -- now it's a direct function call.

#### `pre-tool-use.ts`

Ported from `v2/dispatchers/pre-tool-use.sh` + 11 guard scripts:
1. Fast file_path check -- skip non-increment files
2. Edit tool: status-completion-guard logic (inline)
3. Write tool: spec-template-enforcement-guard + interview-enforcement-guard logic (inline)

All guard logic inlined into this single handler. Guards are simple JSON field checks -- no external dependencies needed.

#### `post-tool-use.ts`

Ported from `v2/dispatchers/post-tool-use.sh` + detectors + handlers:
1. Parse tool result from stdin
2. Lifecycle detection (metadata.json changes -> increment events)
3. Critical events (done/reopened) -> immediate sync via `LivingDocsSync`
4. Other events -> queue to `pending.jsonl` via `queueSyncEvent()`
5. Status line update

**Reuse**: `queueSyncEvent` from `src/core/sync/event-queue.ts`, `LivingDocsSync` from `src/core/living-docs/living-docs-sync.ts`

#### `post-tool-use-analytics.ts`

Ported from `v2/dispatchers/post-tool-use-analytics.sh`:
1. Extract skill/agent info from stdin
2. Write analytics event to `events.jsonl`
3. Fire-and-forget, no stdout output needed

#### `session-start.ts`

Ported from `v2/dispatchers/session-start.sh` + `startup-health-check.sh`:
1. Clear auto-mode.json (session-scoped cleanup)
2. Reset context pressure state
3. Prompt baseline health check (CLAUDE.md + MEMORY.md sizes)
4. Plugin health repair (sw@specweave in settings.json)
5. Agent-type detection and routing
6. Dashboard cache validation
7. Legacy state cleanup

#### `pre-compact.ts`

Ported from `pre-compact.sh`:
1. Read/increment compaction counter from `context-pressure.json`
2. Determine escalation level (elevated -> critical -> emergency)
3. Write `context-pressure.json` and `prompt-health-alert.json`
4. Log compaction event

Simple handler -- ~60 lines TS.

#### `stop-reflect.ts`

Ported from `stop-reflect.sh`:
1. Check if reflect is enabled in config
2. Validate transcript exists and has enough content
3. Call existing `reflectStopCommand()` from `src/cli/commands/reflect-stop.ts`
4. Always approve -- never blocks session exit

#### `stop-auto.ts`

Ported from `stop-auto-v5.sh`:
1. Read auto-mode.json session marker
2. Check staleness, turn counter, dedup
3. Scan active increments (pending tasks, open ACs)
4. Block with progress context if work remains, approve if complete

Second most complex handler (~277 lines bash -> ~200 lines TS).

#### `stop-sync.ts`

Ported from `stop-sync.sh`:
1. Read pending events from `pending.jsonl`
2. Deduplicate by increment ID
3. Call `LivingDocsSync` + `SyncCoordinator` for each increment
4. Route lifecycle events to living-specs handling
5. Route user-story events to GitHub sync
6. Clean up processed events
7. Always approve -- never blocks

**Reuse**: `LivingDocsSync`, `SyncCoordinator` (both already TypeScript)

## 3. hooks.json (New)

```json
{
  "hooks": {
    "PreToolUse": [
      {
        "matcher": "Write|Edit",
        "matcher_content": "\"file_path\"\\s*:\\s*\"[^\"]*\\.specweave/increments/",
        "hooks": [{ "type": "command", "command": "specweave hook pre-tool-use" }]
      },
      {
        "matcher": "TeamCreate",
        "hooks": [{ "type": "command", "command": "specweave hook pre-tool-use" }]
      }
    ],
    "SessionStart": [
      { "hooks": [{ "type": "command", "command": "specweave hook session-start" }] }
    ],
    "UserPromptSubmit": [
      { "hooks": [{ "type": "command", "command": "specweave hook user-prompt-submit" }] }
    ],
    "PreCompact": [
      { "hooks": [{ "type": "command", "command": "specweave hook pre-compact" }] }
    ],
    "PostToolUse": [
      {
        "matcher": "Edit|Write",
        "matcher_content": "\"file_path\"\\s*:\\s*\"[^\"]*\\.specweave/increments/",
        "hooks": [{ "type": "command", "command": "specweave hook post-tool-use" }]
      },
      {
        "matcher": "Skill|Task",
        "hooks": [{ "type": "command", "command": "specweave hook post-tool-use-analytics" }]
      }
    ],
    "Stop": [
      { "hooks": [
        { "type": "command", "command": "specweave hook stop-reflect", "timeout": 15000 },
        { "type": "command", "command": "specweave hook stop-auto", "timeout": 15000 },
        { "type": "command", "command": "specweave hook stop-sync", "timeout": 15000 }
      ]}
    ]
  }
}
```

## 4. Changes to Existing Files

### 4.1 `bin/specweave.js` -- Add `hook` command

```javascript
program
  .command('hook <event-type>')
  .description('Handle Claude Code hook events (internal)')
  .action(async (eventType) => {
    const { handleHook } = await import('../dist/src/cli/commands/hook.js');
    await handleHook(eventType);
  });
```

### 4.2 `src/utils/plugin-copier.ts` -- Remove hooks copy block

Lines 907-933: Remove the entire block that recursively copies bash scripts from `plugins/*/hooks/` to `~/.claude/hooks/`. The hooks.json file (copied as part of the plugin JSON config, not this block) now delegates to the globally-installed CLI.

### 4.3 `plugins/specweave/hooks/hooks.json` -- Rewrite

Replace current bash delegation with CLI delegation (Section 3 above).

### 4.4 Delete bash scripts

All non-JSON files in `plugins/specweave/hooks/`:
- Root scripts: `user-prompt-submit.sh`, `pre-compact.sh`, `startup-health-check.sh`, `stop-reflect.sh`, `stop-auto-v5.sh`, `stop-sync.sh`, `log-decision.sh`, `llm-judge-validator.sh`, `validate-skill-activations.sh`, `README.md`
- `universal/`: All files (`run-hook.sh`, `fail-fast-wrapper.sh`, `hook-wrapper.sh`, `hook-wrapper.cmd`, `session-start.cmd`, `session-start.ps1`, `dispatcher.mjs`)
- `v2/`: All `.sh` files in all subdirectories (`dispatchers/`, `guards/`, `handlers/`, `detectors/`, `integrations/`, `lib/`, `queue/`, `session-end.sh`)
- `lib/`: All scripts (`score-increment.sh`, etc.)
- `tests/`: Entire directory
- `_archive/`: Entire directory

**Keep**: `hooks.json` only.

## 5. New File Structure

```
src/core/hooks/handlers/
  index.ts                        # Barrel export (HandlerFn, HookContext, etc.)
  hook-router.ts                  # stdin -> parse -> dispatch -> stdout
  types.ts                        # HookInput, HookResult, HookContext interfaces
  utils.ts                        # findProjectRoot, readStdin, writeResult
  user-prompt-submit.ts           # Prompt validation, context injection, plugin detection
  pre-tool-use.ts                 # Guards (status-completion, interview-enforcement)
  post-tool-use.ts                # Lifecycle detection, sync queue
  post-tool-use-analytics.ts      # Skill/task analytics tracking
  session-start.ts                # Session init, health check, plugin repair
  pre-compact.ts                  # Context pressure signal
  stop-reflect.ts                 # Session learning extraction
  stop-auto.ts                    # Auto mode completion gate
  stop-sync.ts                    # Batched external sync

src/cli/commands/
  hook.ts                         # CLI command entry point
```

## 6. Performance Constraints

| Constraint | Target | Rationale |
|---|---|---|
| Node.js cold start | <200ms | `specweave hook` runs on every event |
| Handler execution | <500ms typical | Claude Code has hook timeouts (default 60s, Stop 15s) |
| Dynamic import | Load only 1 handler per invocation | Cold start budget |
| No top-level heavy imports | ConfigManager, LivingDocsSync, etc. loaded inside handlers | Startup speed |

**Cold start mitigation** -- two-level lazy loading:
1. `bin/specweave.js` registers `hook` command with async action
2. Action does `await import('../dist/src/cli/commands/hook.js')`
3. `hook.ts` calls `hookRouter()` which does `await import('./handler-name.js')`
4. Only the requested handler and its dependencies load per invocation

## 7. Error Handling Strategy

From ADR-0189 (Resilient Hook Execution), all rules ported to TS:

1. **Never crash** -- top-level try/catch in hook-router returns safe default JSON
2. **Never block unexpectedly** -- handlers that fail return their safe default (approve/allow/continue)
3. **Always log** -- errors written to `.specweave/logs/hooks.log`
4. **Stdin timeout** -- 5s max to read stdin, fail gracefully on timeout
5. **No unhandled rejections** -- `process.on('unhandledRejection')` in hook command entry

## 8. Migration Strategy

### Phase 1: Infrastructure (T-001 to T-003)
Create types, utils, hook-router, and CLI command entry point.

### Phase 2: Handlers (T-004 to T-012)
Implement each handler one at a time, with unit tests.

### Phase 3: Wire up (T-013, T-014)
- Rewrite `hooks.json` to CLI delegation
- Register `hook` command in `bin/specweave.js`

### Phase 4: Clean up (T-015, T-016)
- Remove hooks copy block from `plugin-copier.ts`
- Delete all bash scripts

### Phase 5: Verify (T-017)
- Build passes (`npm run build`)
- All existing tests pass (`npx vitest run`)
- End-to-end: pipe sample stdin through `specweave hook <event>`, verify stdout

## 9. Risk Mitigations

| Risk | Mitigation |
|---|---|
| Node.js cold start too slow | Two-level lazy imports; measure at build time |
| user-prompt-submit regression (2550 lines) | Port section by section; test each section independently |
| Stop hooks timeout (15s) | Background async for reflect; immediate approve for sync |
| specweave not in PATH | npm global install guarantees PATH; tested at install |
| Breaking existing hook behavior | Parity tests: same input -> same output for each handler |

## 10. Testing Strategy

- **Unit tests**: Each handler tested in isolation with mock stdin/context
- **Integration tests**: `hookRouter()` tested with real event routing
- **Parity tests**: Compare bash output vs TS output for identical inputs
- **Performance tests**: Measure cold start time (target <200ms)
- **Test files**: `tests/unit/core/hooks/handlers/*.test.ts`
