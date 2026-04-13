# Implementation Plan: Hook Transparency & Observability

## Overview

Wire existing observability infrastructure (HookLogger, HookHealthTracker, HealthReporter) into the actual hook execution path, add semantic [GUARD]/[ERROR] prefixes to block messages, and expose hook activity via CLI commands. This is plumbing work — no new architecture needed.

## Architecture

### Component 1: Semantic Prefix Injection (hook-router.ts)
Inject `[GUARD]` or `[ERROR]` prefix at the router level, not in individual guards. The router wraps handler results: if `decision === 'block'` and the handler returned normally, prefix with `[GUARD]`. If the handler threw (caught by router's try/catch), prefix with `[ERROR]`.

### Component 2: Dual-Write Logging (utils.ts + hook-router.ts)
Two logging points:
- **Router-level**: After each handler completes, call `HookLogger.log()` with structured entry (hookName, decision, durationMs, toolName)
- **Enhanced logHook()**: Accept optional `StructuredLogFields` for dual-write when callers provide structured context

Preserves backwards-compatible plaintext `hooks.log` while enabling HookHealthTracker.

### Component 3: CLI Commands (hooks-cmd.ts)
Single new file with three exported commands registered under `specweave hooks`:
- `hooksLogCommand` — reads HookLogger JSONL, formats as table
- `hooksHealthCommand` — runs HookHealthTracker.analyzeAll() through HealthReporter
- `hooksLsCommand` — runs HookScanner.scanHooks() to list discovered hooks

### Component 4: Stale Reference Cleanup
Replace 4 `check-hooks` references with `specweave hooks health`. Fix CLAUDE.md docs URL.

## Dependency Graph

```
Component 1 (prefixes) ──┐
                          ├──> Component 3 (CLI commands)
Component 2 (logging)  ──┘
Component 4 (cleanup) ──── independent, parallel
```

## Key Decisions

1. **No static hook manifest** — use HookScanner (dynamic) for `hooks ls`
2. **Prefix at router, not guards** — future guards get prefixes automatically
3. **[ERROR] only on pre-tool-use** — blocking prompts due to hook bugs is worse than allowing
4. **No tool_input in structured logs** — security: avoid logging file contents/secrets
5. **No new npm dependencies**

## Files to Modify

| File | Change |
|------|--------|
| `src/core/hooks/handlers/hook-router.ts` | Prefix injection + structured logging |
| `src/core/hooks/handlers/pre-tool-use.ts` | Verify guard returns carry resolution hints |
| `src/core/hooks/handlers/utils.ts` | Dual-write via HookLogger |
| `src/cli/commands/hooks-cmd.ts` | New — CLI commands |
| `bin/specweave.js` | Register hooks command group |
| `src/core/hooks/hook-health-tracker.ts` | Fix ghost refs |
| `src/core/hooks/hook-logger.ts` | Fix ghost refs |
| `src/core/hooks/hooks-checker.ts` | Fix ghost refs |
| CLAUDE.md (umbrella) | Fix docs URL |

## Testing Strategy

TDD enforced. Each task has RED (failing test) then GREEN (implementation).
- Unit tests for prefix injection via mocked handlers
- Unit tests for dual-write logging
- Unit tests for CLI commands with fixture log data
- Integration test: grep for zero `check-hooks` references
