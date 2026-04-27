# Tasks — 0796 Session-Start Banner Notifier for Plugin/Skill Updates

> Dependency order: **doctor flags** (T-001) → **config schema** (T-002) → **banner-state module** (T-003) → **banner-check module** (T-004) → **handler integration** (T-005) → **unit tests** (T-006, T-007) → **integration test** (T-008) → **performance gate** (T-009) → **manual verification** (T-010)

---

## Phase 1: Foundation — Doctor flags + Config schema

### T-001: Add `--quiet` flag to specweave doctor (ADR 0796-04)
**User Story**: US-005 | **Satisfies ACs**: AC-US5-01, AC-US5-02, AC-US5-03, AC-US5-04, AC-US5-06 | **Project**: specweave
**Status**: [x] completed

**Implementation**:
- In `repositories/anton-abyzov/specweave/src/core/doctor/types.ts` (lines 36-42), add `quiet?: boolean` to `DoctorOptions` interface
- In `repositories/anton-abyzov/specweave/src/cli/commands/doctor.ts` (lines 40-67), add `.option('--quiet', 'Suppress all stdout output')` to the commander registration
- In the `doctor` command action, guard the two print branches:
  ```ts
  if (options.quiet) {
    // suppress — exit code still reflects summary.failures
  } else if (options.json) {
    console.log(JSON.stringify(report, null, 2));
  } else {
    console.log(formatDoctorReport(report, options.verbose));
  }
  ```
- Exit code (0 = pass, 1 = failures > 0) must be preserved in all flag combinations
- Verify `--quick --quiet --json` compose correctly: JSON output, fast checkers only, exit code from failures
- No changes to `runDoctor()` itself — `quiet` is CLI-layer only

**Test Plan**:
- File: `repositories/anton-abyzov/specweave/src/core/doctor/__tests__/doctor-quiet-flag.test.ts`
- Given: mock project with one outdated plugin, call doctor CLI action with `{ quiet: true, quick: true }` → When: action runs → Then: no output captured on stdout, exit code still reflects warn/fail count
- Given: `{ quiet: false, json: true }` → Then: JSON printed on stdout, no other text
- Given: `{ quiet: true }` → Then: neither formatted text nor JSON on stdout; `report` object still returned
- Given: existing doctor tests without `quiet` → Then: all still pass (no regressions)

---

### T-002: Extend config schema with `hooks.banner` (ADR 0796-04, FR-004)
**User Story**: US-003 | **Satisfies ACs**: AC-US3-01, AC-US3-02, AC-US3-04, AC-US3-05, AC-US3-06 | **Project**: specweave
**Status**: [x] completed

**Implementation**:
- In `repositories/anton-abyzov/specweave/src/core/config/types.ts`, add:
  ```ts
  export interface BannerHookConfig {
    disabled?: boolean;       // default: false
    throttleHours?: number;   // default: 24, min: 1, max: 168
  }
  ```
- Extend `RootConfig` (or equivalent top-level type) to include:
  ```ts
  hooks?: HookConfiguration & {
    banner?: BannerHookConfig;
  };
  ```
- In the config schema validator (find via `grep -r "hooks" src/core/config/ --include="*.ts" -l`), add validation: `disabled` must be boolean if present; `throttleHours` must be number in [1, 168] if present; unknown keys under `hooks.banner` are tolerated (forward compatibility)
- `specweave config set hooks.banner.disabled true` must write the value and print confirmation — verify existing `config set` command handles nested dot-paths; add support if missing

**Test Plan**:
- File: `repositories/anton-abyzov/specweave/src/core/config/__tests__/config-banner-schema.test.ts`
- Given: config JSON with `{ hooks: { banner: { disabled: true } } }` → When: parsed → Then: no validation error, `config.hooks.banner.disabled === true`
- Given: `{ hooks: { banner: { disabled: "yes" } } }` → Then: validation error — `disabled` must be boolean
- Given: `{ hooks: { banner: { throttleHours: 48 } } }` → Then: valid, parsed as number
- Given: `{ hooks: { banner: { unknownFutureKey: 42 } } }` → Then: no error (tolerant)
- Given: config with no `hooks` key → Then: `config.hooks?.banner?.disabled` evaluates as `undefined` (falsy = banner enabled by default)

---

## Phase 2: Core modules

### T-003: Create `banner-state.ts` — atomic read/write of throttle state
**User Story**: US-002 | **Satisfies ACs**: AC-US2-01, AC-US2-05, AC-US2-06 | **Project**: specweave
**Status**: [x] completed
**Depends on**: T-002

**Implementation**:
- Create `repositories/anton-abyzov/specweave/src/core/hooks/handlers/banner-state.ts` (~100 LOC)
- Export interface and three functions:
  ```ts
  export interface BannerState {
    version: 1;
    lastCheckAt: string;
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
- `readBannerState`: returns `null` on missing file, unparseable JSON, or `version !== 1` — all treated as "never checked"
- `writeBannerStateAtomic`: write to `<stateDir>/banner-last-check.json.tmp`, then `fs.renameSync(tmp, final)`. Create `stateDir` with `fs.mkdirSync(stateDir, { recursive: true })` before write (AC-US4-08)
- `bannerStatePath`: returns `path.join(stateDir, 'banner-last-check.json')`

**Test Plan**:
- File: `repositories/anton-abyzov/specweave/src/core/hooks/handlers/__tests__/banner-state.test.ts`
- Given: missing state file → When: `readBannerState(dir)` → Then: returns `null`
- Given: file contains `"not json"` → When: `readBannerState(dir)` → Then: returns `null` (no throw)
- Given: file contains valid JSON but `version: 2` → When: `readBannerState(dir)` → Then: returns `null`
- Given: valid BannerState v1 written then read → Then: all fields round-trip byte-for-byte
- Given: `writeBannerStateAtomic` called → Then: `.tmp` file is removed (only the final file remains)
- Given: `stateDir` does not exist → When: `writeBannerStateAtomic` called → Then: directory created and file written (no ENOENT)

---

### T-004: Create `banner-check.ts` — throttle logic, doctor invocation, banner formatter
**User Story**: US-001, US-002, US-004 | **Satisfies ACs**: AC-US1-02, AC-US1-03, AC-US1-04, AC-US2-02, AC-US2-03, AC-US2-04, AC-US2-07, AC-US4-01, AC-US4-02, AC-US4-03, AC-US4-04, AC-US4-06, AC-US4-07, AC-US4-08 | **Project**: specweave
**Status**: [x] completed
**Depends on**: T-001, T-003

**Implementation**:
- Create `repositories/anton-abyzov/specweave/src/core/hooks/handlers/banner-check.ts` (~200 LOC)
- Three exports:
  ```ts
  export async function checkBanner(context: HookContext): Promise<string | null>;
  export function isThrottleExpired(state: BannerState | null, context: HookContext): boolean;
  export function formatBanner(result: BannerState['lastResult']): string | null;
  ```
- `isThrottleExpired` algorithm (ADR 0796-02 Decision 2):
  1. `null` state → true
  2. `state.version !== 1` → true
  3. `Math.abs(Date.now() - Date.parse(state.lastCheckAt)) > THROTTLE_MS` → true (24h default, or `config.hooks.banner.throttleHours * 3600_000`)
  4. `mtime(config.json) > lastCheckAt` → true
  5. `mtime(~/.claude/plugins/installed_plugins.json) > lastCheckAt` → true
  6. `vskill.lock` exists AND `mtime(vskill.lock) > lastCheckAt` → true
  7. Otherwise → false
- `checkBanner` orchestration:
  - Read state via `readBannerState`
  - If not expired: return `formatBanner(state.lastResult)` (cache hit, <10ms path)
  - If expired: call `runDoctor(projectRoot, { quick: true, skipExternal: true })` wrapped in `Promise.race` with 800ms timeout (ADR 0796-03 Rule 2)
  - On success: build new `BannerState`, call `writeBannerStateAtomic`, return `formatBanner(result)`
  - On doctor non-zero exit, non-JSON output, timeout: log via `logHook`, return `null` (no banner, no state write)
  - When `~/.claude/plugins/installed_plugins.json` missing: return `null` silently (AC-US4-07)
- `formatBanner`: returns `null` when `pluginUpdates + skillUpdates === 0`. Otherwise builds the multi-line string per ADR 0796-01 §"Banner content" with correct singular/plural. Format:
  ```
  [SpecWeave] N plugin(s) and M skill(s) have updates available.
    Run: specweave doctor    (full report)
    Or:  specweave refresh-plugins && vskill update --all    (apply)
    Disable banner: set hooks.banner.disabled = true in .specweave/config.json
  ```

**Test Plan**:
- File: `repositories/anton-abyzov/specweave/src/core/hooks/handlers/__tests__/banner-check.test.ts`
- `isThrottleExpired`:
  - Given: `null` state → Then: `true`
  - Given: state `lastCheckAt` 25h ago → Then: `true`
  - Given: state `lastCheckAt` 23h ago, no mtime changes → Then: `false`
  - Given: state `lastCheckAt` 23h ago, `config.json` mtime newer → Then: `true`
  - Given: state `lastCheckAt` 23h ago, `installed_plugins.json` mtime newer → Then: `true`
  - Given: state `lastCheckAt` 23h ago, `vskill.lock` mtime newer → Then: `true`
  - Given: clock skew (negative elapsed via `Math.abs`) → Then: `true` (treated as expired)
- `formatBanner`:
  - Given: `{ pluginUpdates: 0, skillUpdates: 0, doctorStatus: 'pass' }` → Then: `null`
  - Given: `{ pluginUpdates: 1, skillUpdates: 0, doctorStatus: 'warn' }` → Then: contains "1 plugin" (singular), no "skill" mention
  - Given: `{ pluginUpdates: 0, skillUpdates: 2, doctorStatus: 'warn' }` → Then: contains "2 skills" (plural), no "plugin" mention
  - Given: `{ pluginUpdates: 2, skillUpdates: 1, doctorStatus: 'warn' }` → Then: contains both counts
- `checkBanner`:
  - Given: warm cache (not expired), `pluginUpdates: 1` → When: called → Then: returns banner string without invoking runDoctor (verified by spy)
  - Given: expired cache, mocked runDoctor returning valid report → When: called → Then: returns banner, state file updated
  - Given: expired cache, mocked runDoctor throws → When: called → Then: returns `null`, `logHook` called, state file unchanged
  - Given: expired cache, mocked runDoctor delays >800ms → When: called → Then: returns `null` (timeout), state file unchanged
  - Given: `~/.claude/plugins/installed_plugins.json` missing → Then: returns `null` silently

---

### T-005: Integrate banner into `user-prompt-submit.ts` handler + opt-out guard
**User Story**: US-001, US-003, US-004 | **Satisfies ACs**: AC-US1-01, AC-US1-05, AC-US1-07, AC-US3-03, AC-US3-04, AC-US3-05, AC-US4-01 | **Project**: specweave
**Status**: [x] completed
**Depends on**: T-004

**Implementation**:
- In `repositories/anton-abyzov/specweave/src/core/hooks/handlers/user-prompt-submit.ts` (lines 136-190 per ADR reference), add inner try/catch inside the existing `handle` function after the existing `incCtx`/`tddCtx` context builders:
  ```ts
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
- Banner is appended to `contextParts` array (same as existing increment + TDD context) — joined with `\n` before passing to `approveWithContext`
- When `hooks.banner.disabled === true`: inner block exits before calling `checkBanner` — no throttle file read, no doctor call (AC-US3-03)
- Soft cap: if combined `contextParts.join('\n')` exceeds 12KB, drop banner string first (banner is least essential)
- Banner output MUST use `additionalContext` mechanism (stdout of hook process), never `process.stderr.write` or `console.error` (AC-US1-05, ADR 0796-03 Rule 4)
- Hook exits 0 in all cases — no new `process.exit` calls (ADR 0796-03 Rule 3)

**Test Plan**:
- File: `repositories/anton-abyzov/specweave/src/core/hooks/handlers/__tests__/user-prompt-submit-banner.test.ts`
- Given: no `hooks.banner` in config, warm cache with 1 plugin update → When: handler invoked → Then: `additionalContext` contains banner string
- Given: `hooks.banner.disabled: true` → When: handler invoked → Then: no banner in `additionalContext`, no call to `checkBanner` (spy verified)
- Given: `checkBanner` throws → When: handler invoked → Then: `approveWithContext` still returned (no handler failure), banner absent, `logHook` called
- Given: banner + increment context both present → When: handler invoked → Then: both appear in `additionalContext` joined with `\n`
- Given: zero updates (`checkBanner` returns `null`) → When: handler invoked → Then: no empty string added to `contextParts`
- Given: existing built-in/scope-guard test cases → Then: all still pass (no regressions)

---

## Phase 3: Tests

### T-006: Unit tests — `banner-state.ts` (atomic write edge cases)
**User Story**: US-002 | **Satisfies ACs**: AC-US2-05, AC-US2-06 | **Project**: specweave
**Status**: [x] completed
**Depends on**: T-003

**Implementation**:
- Extend `__tests__/banner-state.test.ts` (from T-003) with concurrent-write scenario:
  - Spawn two parallel `writeBannerStateAtomic` calls with different `lastCheckAt` values
  - Assert final file is one of the two valid states (not corrupted partial JSON)
- Verify `.tmp` file does not persist after successful rename
- Verify `readBannerState` handles `ENOENT` from a deleted file without throwing

**Test Plan**:
- Given: two `writeBannerStateAtomic` calls in parallel, each with distinct data → When: both resolve → Then: `readBannerState` returns a valid `BannerState` (either one, not corrupted)
- Given: `writeBannerStateAtomic` completes → Then: `<stateDir>/banner-last-check.json.tmp` does not exist
- Given: valid state file, then file deleted mid-read (simulated via mock) → When: `readBannerState` called → Then: returns `null`, no throw

---

### T-007: Unit tests — `banner-check.ts` performance budgets
**User Story**: US-001, US-002 | **Satisfies ACs**: AC-US1-06, AC-US2-07 | **Project**: specweave
**Status**: [x] completed
**Depends on**: T-004

**Implementation**:
- In `__tests__/banner-check.test.ts`, add timing assertions:
  - Warm path: call `checkBanner` with a valid non-expired state file. Assert wall-clock < 50ms (run 100 iterations, use p99 or max)
  - Cold path: call `checkBanner` with expired state, mocked `runDoctor` returning instantly. Assert wall-clock < 800ms
- Use `performance.now()` for measurement; skip test if environment is too slow (add `test.skipIf` guard for CI machines with known overhead)
- Doctor quiet-flag test (from T-001): add budget assertion that `specweave doctor --quiet --quick` wall-clock < 800ms in test fixture project

**Test Plan**:
- Given: warm path (state file present, not expired) → When: `checkBanner` called → Then: completes in <50ms
- Given: cold path (state file missing, mocked runDoctor resolves instantly) → When: `checkBanner` called → Then: completes in <800ms (excluding mock startup overhead)
- Given: doctor invoked with `{ quiet: true, quick: true }` → Then: no stdout, completes <800ms

---

### T-008: Integration test — end-to-end hook invocation
**User Story**: US-001, US-002, US-004 | **Satisfies ACs**: AC-US1-02, AC-US1-03, AC-US2-02, AC-US4-02, AC-US4-03 | **Project**: specweave
**Status**: [x] completed
**Depends on**: T-005

**Implementation**:
- Create `repositories/anton-abyzov/specweave/tests/integration/banner-hook-e2e.test.ts`
- Invoke the hook via `specweave hook user-prompt-submit < test-fixtures/hook-input.json` in a tmp project directory with seeded state
- Stub plugin state: tmp HOME with `~/.claude/plugins/installed_plugins.json` showing `sw@1.0.0`, marketplace at `1.0.582` (or use a fixture doctor report)
- Test scenarios:
  1. First run (no state file): banner appears in stdout JSON `hookSpecificOutput.additionalContext`
  2. Second run (state file < 24h): banner from cache, no doctor invoked
  3. Run after `installed_plugins.json` mtime bumped (`touch`): fresh doctor run triggered
  4. Run with `hooks.banner.disabled: true` in config: no banner, hook exits 0
  5. Doctor replaced with a script that exits 1 + prints garbage: hook exits 0, no banner, state file unchanged

**Test Plan**:
- Given: first run with outdated plugin fixture → When: `specweave hook user-prompt-submit < input.json` → Then: stdout JSON contains `additionalContext` with `[SpecWeave]` banner; exit code 0
- Given: second run within 24h (state file written) → Then: `additionalContext` still contains cached banner (from state, not fresh doctor); state file `lastCheckAt` unchanged
- Given: `touch ~/.claude/plugins/installed_plugins.json` then run → Then: doctor re-invoked (state file `lastCheckAt` updated)
- Given: `hooks.banner.disabled: true` → Then: `additionalContext` absent; exit 0; no doctor call
- Given: doctor replaced with failing stub → Then: exit 0; no `additionalContext` key (or empty); no throw

---

## Phase 4: Verification gates

### T-009: Performance gate — warm/cold path budgets (Bash verification)
**User Story**: US-001, US-002 | **Satisfies ACs**: AC-US1-06, AC-US2-07 | **Project**: specweave
**Status**: [x] completed
**Depends on**: T-008

**Implementation**:
- Run the full unit test suite: `npx vitest run --reporter=verbose` in `repositories/anton-abyzov/specweave/`
- Assert all banner-related tests pass, including the timing assertions from T-007
- Run integration test: `npx vitest run tests/integration/banner-hook-e2e.test.ts`
- End-to-end timing check: invoke hook 5× with warm cache, confirm each <50ms via shell timing:
  ```bash
  for i in $(seq 1 5); do
    time specweave hook user-prompt-submit < tests/fixtures/hook-input-warm.json
  done
  ```
- Confirm no regressions in existing handler tests: `npx vitest run src/core/hooks/handlers/`

**Test Plan**:
- Given: all banner unit tests → When: `npx vitest run` → Then: 0 failures
- Given: warm hook invocations × 5 → Then: each real < 100ms (wall-clock, allowing OS overhead)
- Given: existing `user-prompt-submit.test.ts` suite → Then: 0 regressions

---

### T-010: Manual verification gate — live Claude Code session
**User Story**: US-001, US-002, US-003 | **Satisfies ACs**: AC-US1-01, AC-US1-07, AC-US2-02, AC-US3-03 | **Project**: specweave
**Status**: [x] completed
**Depends on**: T-009

**Implementation**:
- Build and link specweave locally: `cd repositories/anton-abyzov/specweave && npm run build && npm link`
- Open a fresh Claude Code session in this project
- Send any prompt → verify banner appears in session context (if plugin/skill updates exist) OR confirm no banner when up to date
- Inspect `.specweave/state/banner-last-check.json` — must exist with current `lastCheckAt` ISO timestamp
- Send a second prompt within the same session → verify throttle hit (no new doctor run, check `.specweave/logs/hooks/user-prompt-submit.log` for throttle message)
- `touch ~/.claude/plugins/installed_plugins.json` → send another prompt → verify fresh doctor run (new `lastCheckAt` in state file)
- Set `hooks.banner.disabled: true` in `.specweave/config.json` → send prompt → verify no banner and no state file write
- This is a manual gate per CLAUDE.md (new UI flow requires human verification)

**Test Plan**:
- Given: fresh Claude Code session with updated specweave → When: first prompt sent → Then: banner visible in context OR confirmed absent when up to date; exit code 0; `.specweave/state/banner-last-check.json` written
- Given: second prompt in same session → Then: throttle file `lastCheckAt` unchanged (no re-run)
- Given: `touch ~/.claude/plugins/installed_plugins.json` → next prompt → Then: state file `lastCheckAt` updated
- Given: `hooks.banner.disabled: true` → next prompt → Then: no banner, no state file change

---

## Task Summary

| Task | User Story | Satisfies ACs | Project | Status |
|------|-----------|---------------|---------|--------|
| T-001: Doctor `--quiet` flag | US-005 | AC-US5-01..04, AC-US5-06 | specweave | [ ] |
| T-002: Config schema `hooks.banner` | US-003 | AC-US3-01, AC-US3-02, AC-US3-04..06 | specweave | [ ] |
| T-003: `banner-state.ts` module | US-002 | AC-US2-01, AC-US2-05, AC-US2-06 | specweave | [ ] |
| T-004: `banner-check.ts` module | US-001, US-002, US-004 | AC-US1-02..04, AC-US2-02..04, AC-US2-07, AC-US4-01..04, AC-US4-06..08 | specweave | [ ] |
| T-005: Handler integration + opt-out | US-001, US-003, US-004 | AC-US1-01, AC-US1-05, AC-US1-07, AC-US3-03..05, AC-US4-01 | specweave | [ ] |
| T-006: banner-state atomic write tests | US-002 | AC-US2-05, AC-US2-06 | specweave | [ ] |
| T-007: banner-check performance tests | US-001, US-002 | AC-US1-06, AC-US2-07 | specweave | [ ] |
| T-008: Integration test e2e | US-001, US-002, US-004 | AC-US1-02, AC-US1-03, AC-US2-02, AC-US4-02, AC-US4-03 | specweave | [ ] |
| T-009: Bash performance gate | US-001, US-002 | AC-US1-06, AC-US2-07 | specweave | [ ] |
| T-010: Manual verification gate | US-001, US-002, US-003 | AC-US1-01, AC-US1-07, AC-US2-02, AC-US3-03 | specweave | [ ] |
