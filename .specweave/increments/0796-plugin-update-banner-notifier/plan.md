# Implementation Plan: Session-Start Banner Notifier for Plugin/Skill Updates

## Overview

Phase 2 of 0794. Surfaces the existing `PluginCurrencyChecker` and `SkillCurrencyChecker` signals as a proactive banner injected into the user's prompt via `UserPromptSubmit`. Reuses the existing CLI hook delegation (`specweave hook user-prompt-submit`) — **no new hook events**, **no new external services**, **no new daemon**.

The core change is a ~150-line addition to the existing handler at `src/core/hooks/handlers/user-prompt-submit.ts`, gated by a 24h throttle stored in `.specweave/state/banner-last-check.json`. Doctor checkers from 0794 are reused as-is; this increment adds **zero new signals**, only a new surface.

## Architecture

### Components (module-by-module)

| File | Status | Purpose |
|---|---|---|
| `src/core/hooks/handlers/user-prompt-submit.ts` | EXTEND (~+150 LOC) | Add `checkBanner()` helper + integrate into existing `handle` function. |
| `src/core/hooks/handlers/banner-check.ts` | NEW (~200 LOC) | Throttle logic, doctor invocation with timeout, banner formatting. Pure-functional, easy to unit-test. |
| `src/core/hooks/handlers/banner-state.ts` | NEW (~100 LOC) | Read/write `.specweave/state/banner-last-check.json` with atomic-write semantics. |
| `src/core/doctor/types.ts` | EXTEND (+1 field) | Add `quiet?: boolean` to `DoctorOptions` (ADR 0796-04). |
| `src/cli/commands/doctor.ts` | EXTEND (+~10 LOC) | Wire `--quiet` flag, suppress stdout when set (ADR 0796-04). |
| `src/core/config/types.ts` | EXTEND (+~25 LOC) | Add `BannerHookConfig` interface and root-level `hooks.banner` field. |
| `.specweave/state/banner-last-check.json` | NEW (state file) | Schema documented in ADR 0796-02 §"State file". |
| `__tests__/banner-check.test.ts` | NEW | Unit tests for throttle logic + budget assertion. |
| `__tests__/banner-state.test.ts` | NEW | Atomic-write semantics, corrupt-file handling. |
| `__tests__/user-prompt-submit-banner.test.ts` | NEW | Integration of banner into existing handler. |

**No changes to**: `plugins/specweave/hooks/hooks.json` (already registers `UserPromptSubmit`), `init.ts` (hook is already installed by 0794-era init), `hook.ts` CLI entry (safe-default fallback already exists).

### Module 1: `banner-state.ts` (NEW)

Owns the state file. Three exports:

```ts
export interface BannerState {
  version: 1;
  lastCheckAt: string;        // ISO timestamp
  lastResult: {
    pluginUpdates: number;
    skillUpdates: number;
    doctorStatus: 'pass' | 'warn' | 'fail' | 'skip';
  };
  lastBannerShownAt: string | null;
}

export function readBannerState(stateDir: string): BannerState | null;
export function writeBannerStateAtomic(stateDir: string, state: BannerState): void;
export function bannerStatePath(stateDir: string): string;
```

`writeBannerStateAtomic` writes `<stateDir>/banner-last-check.json.tmp` then `fs.renameSync`. `readBannerState` returns `null` on missing/unparseable/wrong-version (forces fresh check, per ADR 0796-02 trigger 2).

### Module 2: `banner-check.ts` (NEW)

Pure-functional banner check. Three exports:

```ts
export async function checkBanner(context: HookContext): Promise<string | null>;
export function isThrottleExpired(state: BannerState | null, context: HookContext): boolean;
export function formatBanner(result: BannerState['lastResult']): string | null;
```

`checkBanner` orchestrates: read state → expiry check → (if expired) run doctor with 800ms timeout + write state → return formatted banner string (or null when zero updates). All errors caught and logged via `logHook`.

`isThrottleExpired` implements ADR 0796-02 Decision 2 — checks the 24h window plus mtimes of `config.json`, `installed_plugins.json`, `vskill.lock`.

`formatBanner` returns `null` when `pluginUpdates + skillUpdates === 0`. Otherwise returns the 6-line text from ADR 0796-01 §"Banner content".

### Module 3: `user-prompt-submit.ts` integration (EXTEND)

One new section inside the existing `handle` function, between the existing context builders and `approveWithContext`:

```ts
// NEW: banner check — fully isolated try/catch (ADR 0796-03 Rule 1)
try {
  const bannerCfg = readJsonSafe(context.configPath, context)?.hooks?.banner;
  if (bannerCfg?.disabled !== true) {
    const banner = await checkBanner(context);
    if (banner) contextParts.push(banner);
  }
} catch (err) {
  logHook(context, 'user-prompt-submit', `banner check error: ${err instanceof Error ? err.message : String(err)}`);
}
```

### Module 4: Doctor `--quiet` (ADR 0796-04)

`DoctorOptions.quiet?: boolean` added. CLI command suppresses both `console.log` paths when `quiet: true`. Exit-code behavior unchanged.

### Module 5: Config schema

```ts
// In src/core/config/types.ts, extending RootConfig
export interface BannerHookConfig {
  /** Disable the update banner. Default: false (banner enabled). */
  disabled?: boolean;
  /** Throttle window in hours. Default: 24. Min: 1, Max: 168 (1 week). */
  throttleHours?: number;
}

// Root-level field (NEW; not on existing HookConfiguration which is task-completion oriented)
export interface RootConfig {
  // ... existing fields ...
  hooks?: HookConfiguration & {
    banner?: BannerHookConfig;
  };
}
```

`hooks.banner.disabled = true` opts out (per spec.md). `throttleHours` is an escape hatch — undocumented in v1, useful for testing and future "quiet hours" work (deferred).

## Data Model

### `.specweave/state/banner-last-check.json`

```json
{
  "version": 1,
  "lastCheckAt": "2026-04-27T20:13:20.358Z",
  "lastResult": {
    "pluginUpdates": 2,
    "skillUpdates": 1,
    "doctorStatus": "warn"
  },
  "lastBannerShownAt": "2026-04-27T20:13:20.358Z"
}
```

Versioned (`version: 1`). Future schema changes bump version; readers return `null` on mismatch (treated as missing → fresh check).

### Banner content (injected into `additionalContext`)

```
[SpecWeave] 2 plugin(s) and 1 skill(s) have updates available.
  Run: specweave doctor    (full report)
  Or:  specweave refresh-plugins && vskill update --all    (apply)
  Disable banner: set hooks.banner.disabled = true in .specweave/config.json
```

Pluralization: `1 plugin / N plugins`, `1 skill / N skills`. Singular vs plural tested.

## Sequence Diagrams

### A. Cold-cache prompt (full doctor run)

```
User                Claude Code           specweave hook        runDoctor
 |  prompt           |                     |                      |
 |------------------>|                     |                      |
 |                   |  UserPromptSubmit   |                      |
 |                   |-------------------->|                      |
 |                   |                     | read banner-state    |
 |                   |                     | (missing/expired)    |
 |                   |                     |--------------------->|
 |                   |                     |    full check (~600ms)|
 |                   |                     |<---------------------|
 |                   |                     | write state (atomic) |
 |                   |                     |                      |
 |                   |  approve+banner     |                      |
 |                   |<--------------------|                      |
 |  prompt + banner  |                     |                      |
 |  visible to LLM   |                     |                      |
```

Total: ~600-800 ms. Happens once per 24h per project.

### B. Warm-throttled prompt (immediate exit)

```
User                Claude Code           specweave hook
 |  prompt           |                     |
 |------------------>|                     |
 |                   |  UserPromptSubmit   |
 |                   |-------------------->|
 |                   |                     | read banner-state
 |                   |                     | (within 24h, has cache)
 |                   |                     | format banner from cache
 |                   |  approve+banner     |
 |                   |<--------------------|
 |  prompt + banner  |
```

Total: ~5-15 ms. Banner stays consistent within the 24h window.

### C. Throttle expiry triggering recheck (mtime change)

```
User installs plugin via `specweave refresh-plugins`
   |
   v installed_plugins.json mtime updates
   |
User sends next prompt
   |
   v UserPromptSubmit fires
   |
hook reads banner-state → checks installed_plugins.json mtime > lastCheckAt → throttle expired
   |
runs doctor → fresh banner reflects new install state
```

Implements ADR 0796-02 Decision 2 trigger 4.

### D. Error path (silent exit + log)

```
User                Claude Code           specweave hook        runDoctor
 |  prompt           |                     |                      |
 |------------------>|                     |                      |
 |                   |  UserPromptSubmit   |                      |
 |                   |-------------------->|                      |
 |                   |                     | runDoctor()          |
 |                   |                     |--------------------->|
 |                   |                     |   ... 800ms ...      |
 |                   |                     |   (timeout fires)    |
 |                   |                     | catch + logHook      |
 |                   |                     | NO state update      |
 |                   |  approve (no banner)|                      |
 |                   |<--------------------|                      |
 |  prompt unchanged |                     |                      |
```

Subprocess may continue in background and is reaped when the hook process exits. User sees no error. Next prompt re-attempts.

## Throttle Algorithm Specification

**Inputs**: `state` (BannerState | null), `context` (HookContext), system clock, file mtimes.

**Output**: boolean — `true` = run fresh check, `false` = use cache.

```
1. If state is null → return true (no cache)
2. If state.version !== 1 → return true (schema mismatch)
3. Let elapsed = abs(Date.now() - parseISO(state.lastCheckAt))
4. If elapsed > THROTTLE_HOURS * 3600 * 1000 → return true (window expired)
5. If mtime(.specweave/config.json) > parseISO(state.lastCheckAt) → return true (config change)
6. If mtime(~/.claude/plugins/installed_plugins.json) > parseISO(state.lastCheckAt) → return true (plugin change)
7. If exists(vskill.lock) AND mtime(vskill.lock) > parseISO(state.lastCheckAt) → return true (skill change)
8. Otherwise return false (use cache)
```

THROTTLE_HOURS defaults to 24, configurable via `hooks.banner.throttleHours`.

### Race conditions

**Concurrent windows expiring simultaneously** (per ADR 0796-02 Decision 3): both will run doctor; both write atomically; last-writer-wins. Result is identical between runs (same plugin manifest, same vskill lock). No file lock — accepted as a once-per-24h redundant cost.

**State-file partial write**: prevented by `tmp + rename`. `fs.renameSync` is atomic on POSIX; the reader either sees the old file or the new file, never partial.

**Clock skew backward**: handled by `Math.abs` on elapsed.

**File deletion mid-read**: `readJsonSafe` returns null → trigger 1 fires → fresh check.

## Hook Registration & Migration

The `UserPromptSubmit` hook is **already registered** in `~/.claude/settings.json` for any user that ran `specweave init` after 0188 (when the CLI hook delegation landed). Existing 0794 users have:

```json
"UserPromptSubmit": [{
  "hooks": [{
    "type": "command",
    "command": "bash -c 'command -v specweave &>/dev/null && specweave hook user-prompt-submit || ...'"
  }]
}]
```

This means **zero migration work** for existing installs. When they run `npm i -g specweave@<version-with-0796>`, the next prompt picks up the banner logic automatically.

For users without the hook (very old installs that pre-date the CLI delegation pattern): `specweave init` already writes the hook on (re-)init. Nothing in 0796 needs to touch `init.ts`.

`CLAUDE.md` updates: not required. The banner is self-documenting (lists its own opt-out instruction in the banner text).

## Failure Modes

Codified in ADR 0796-03. Summary:

- All exceptions caught locally inside an inner try/catch. Outer handler still returns `{ decision: "approve" }`.
- 800 ms hard timeout via `Promise.race`. Doctor subprocesses continue in background until parent exit.
- All errors → `HookLogger` → `.specweave/logs/hooks/`. **Never** stderr/console.
- Exit code always 0. No retry. No automatic disable. Throttle gates the next attempt.

## Test Strategy

### Unit tests (Vitest)

`banner-state.test.ts`:
- ✅ Read missing file → null
- ✅ Read corrupt JSON → null
- ✅ Read wrong version → null
- ✅ Round-trip write+read preserves all fields
- ✅ Atomic-write: temp file removed after rename
- ✅ Atomic-write: concurrent writes don't corrupt (spawn 2 parallel writes, assert final file is one of the two valid states)

`banner-check.test.ts`:
- ✅ `isThrottleExpired`: null state → true
- ✅ `isThrottleExpired`: 25h-old state → true
- ✅ `isThrottleExpired`: 23h-old state with newer config.json → true
- ✅ `isThrottleExpired`: 23h-old state, no mtime changes → false
- ✅ `isThrottleExpired`: clock-skew backward → true (via abs)
- ✅ `formatBanner`: zero updates → null
- ✅ `formatBanner`: 1 plugin / 0 skills → singular
- ✅ `formatBanner`: 0 plugins / 2 skills → plural
- ✅ `checkBanner`: warm path completes <50ms (timing assertion)
- ✅ `checkBanner`: cold path with mocked runDoctor completes <800ms
- ✅ `checkBanner`: doctor throws → returns null + logs error + state file unchanged
- ✅ `checkBanner`: doctor times out → returns null + state file unchanged

`user-prompt-submit-banner.test.ts`:
- ✅ Existing tests still pass (no regressions in built-in/scope-guard paths)
- ✅ Banner injected when present
- ✅ `hooks.banner.disabled = true` in config → no banner injected, no doctor call
- ✅ Banner appears alongside increment context (both joined with `\n`)
- ✅ Empty banner (zero updates) does not add empty string to contextParts

`doctor-quiet-flag.test.ts`:
- ✅ `--quiet` suppresses both formatted and JSON output paths
- ✅ Exit code still reflects `summary.failures`

### Integration tests

- ✅ End-to-end via `specweave hook user-prompt-submit < input.json` invocation. Stub plugin/skill state, verify banner string appears in stdout `hookSpecificOutput.additionalContext`.
- ✅ State file created on first run, updated on second run after 24h simulated.
- ✅ Concurrent invocation: spawn 2 hook processes in parallel, both complete with valid output, state file is one of the two atomic states.

### Manual test (Claude Code session)

1. Install latest specweave with 0796 changes locally (`npm link`).
2. Start a fresh Claude Code conversation in this project.
3. Send any prompt → first run triggers banner if updates exist.
4. Inspect `.specweave/state/banner-last-check.json` — should exist with current timestamp.
5. Send another prompt → no fresh doctor run (verify by `.specweave/logs/hooks/user-prompt-submit.log` showing throttle hit).
6. `touch ~/.claude/plugins/installed_plugins.json` → next prompt re-runs doctor.
7. Set `hooks.banner.disabled = true` in `.specweave/config.json` → next prompt has no banner.

### Performance gates (CI)

- Warm path budget assertion: `<50ms` p99 across 100 invocations.
- Cold path budget assertion: `<800ms` p99 with mocked instant doctor.
- Hook overall p99: existing handler tests already enforce; banner extension must not regress.

## Implementation Phases

### Phase 1: Foundation (T-001..T-003)
- Add `quiet` to `DoctorOptions` + CLI flag (ADR 0796-04). Smallest, lowest-risk change first.
- Extend config schema with `hooks.banner`.
- Create `banner-state.ts` with atomic-write + tests.

### Phase 2: Core (T-004..T-007)
- Implement `banner-check.ts` (throttle + doctor invocation + formatter).
- Wire into `user-prompt-submit.ts` handler.
- Unit + integration tests.

### Phase 3: Polish (T-008..T-010)
- Performance gate tests (warm/cold budget).
- Manual test in Claude Code session.
- Update `.specweave/docs/internal/specs/` living docs (hooks section).

## Technology Stack

- **Language**: TypeScript (existing project).
- **Runtime**: Node.js ≥18 (existing). `fs.renameSync` for atomic writes.
- **Test framework**: Vitest (existing project standard).
- **Logging**: existing `HookLogger` (`src/core/hooks/hook-logger.ts`).
- **Hook protocol**: Claude Code `UserPromptSubmit` JSON contract (existing).

## Architecture Decisions

- ADR 0796-01: `UserPromptSubmit` chosen over SessionStart/SSE/dashboard.
- ADR 0796-02: 24h throttle + mtime invalidation; atomic write, no lockfile.
- ADR 0796-03: silent failure + exit 0; never block prompt.
- ADR 0796-04: doctor flag contract (`--quick` exists, `--quiet` added, `--json` exists).

## Technical Challenges

### Challenge 1: Doctor cost in cold path

`runDoctor()` runs all 10 checkers sequentially. Even with `--quick` (skips network probes), the plugin and skill currency checkers each parse multiple JSON files and (skill checker) shell out to `vskill outdated`. Worst-case observed locally: ~600 ms.

**Solution**: Pass `quick: true, skipExternal: true`. The plugin currency checker is local-only (no network). The skill currency checker shells to `vskill outdated --json` which has its own KV cache and self-skips when `vskill.lock` is missing.

**Risk**: A user with a very large `installed_plugins.json` (>50 plugins) might exceed the 800 ms budget. Mitigation: timeout fires, banner skipped for this prompt, retried on next. Documented in ADR 0796-03.

### Challenge 2: Concurrent Claude windows

Two windows in the same project both expire and both run doctor → 2× cost.

**Solution**: Accept the cost. Once per 24h per project. Lockfile complexity not justified (per ADR 0796-02 Decision 3).

### Challenge 3: Hook output coexisting with existing context injection

The current handler injects active-increment + TDD context. Banner adds another paragraph. Three context parts joined with `\n` could exceed Claude Code's `additionalContext` size budget (~16KB historically).

**Solution**: Banner is at most ~6 lines (~300 chars). Increment context is ~1 line per active increment (typically 1-2). TDD context is 1 line. Total well under budget. Add a soft cap: if combined `additionalContext` >12KB, drop the banner first (banner is least essential).

### Challenge 4: Throttle expiry feels random to users

A user sees a banner Monday, doesn't see one Tuesday despite updates landing. Confusion.

**Solution**: Banner copy explicitly says "available" (cached fact) and lists `specweave doctor` for a fresh on-demand check. The mtime-based invalidation also means installs/refreshes immediately invalidate the cache, so user-initiated state changes are reflected immediately.

## Out of Scope

(Inherited from spec.md, restated for design alignment.)

- Per-plugin snooze/dismiss state.
- "Quiet hours" config (deferred — `throttleHours` field added but undocumented to leave headroom).
- Slack/email digest.
- Banner UI customization (colors, format).
- Cross-project banner aggregation.
- Telemetry on banner views.
