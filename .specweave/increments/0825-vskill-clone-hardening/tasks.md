---
increment: 0825-vskill-clone-hardening
title: "vskill clone hardening"
status: ready-for-review
---

# Tasks: vskill clone hardening

## Dependency Order

Tasks may be done sequentially. Each fix is independent of the others; tests can be written before or after each fix per TDD discipline.

---

### T-001: Add `--yes` flag to Commander registration in `src/index.ts`
**User Story**: US-003
**AC**: AC-US3-01
**Status**: [x] completed
**Owner**: backend

**Test Plan**:
Given the `clone` command in `src/index.ts`
When `.option("-y, --yes", "Auto-confirm all prompts")` is added
Then `node dist/bin.js clone --help` displays the new flag and `node dist/bin.js clone <bogus> --yes --dry-run` plumbs `opts.yes === true` to the orchestrator (verified via console output).

---

### T-002: Extend `confirmPrompt` in `clone-prompts.ts` with TTY check + opts
**User Story**: US-003
**AC**: AC-US3-01, AC-US3-02, AC-US3-03
**Status**: [x] completed
**Owner**: backend

**Test Plan**:
Given the existing `confirmPrompt(question)` function
When the signature is extended to `confirmPrompt(question, { yes?, stdinIsTTY? } = {})`
Then `{yes: true}` returns true without reading stdin; `{stdinIsTTY: false}` returns false and writes the no-TTY error to stderr; `{stdinIsTTY: true}` falls through to the readline path (mocked).

---

### T-003: Plumb `opts.yes` through `runCloneOnce` and `runWholePluginClone` in `clone.ts`
**User Story**: US-003
**AC**: AC-US3-01
**Status**: [x] completed
**Owner**: backend

**Test Plan**:
Given the orchestrator receives `cloneOpts.yes`
When all `confirmPrompt(...)` calls are updated to pass `{ yes: cloneOpts.yes }`
Then a whole-plugin clone with `--yes` skips the listing prompt and proceeds to bulk-clone without reading stdin.

---

### T-004: Implement plugin-root cleanup in `runWholePluginClone` rollback
**User Story**: US-001
**AC**: AC-US1-01, AC-US1-02, AC-US1-03
**Status**: [x] completed
**Owner**: backend

**Test Plan**:
Given `runWholePluginClone` with `targetKind === "new-plugin"` and `completed.length > 0`
When an iteration ≥2 throws
Then after the per-skill cleanup loop, `bestEffortRm(pluginRoot)` is called and the parent plugin directory no longer exists; for `targetKind === "plugin"`, the parent root is preserved; for failure on iteration 1, no extra cleanup runs.

---

### T-005: Implement `.bak` staging for `--force` + `--target plugin` in `runCloneOnce`
**User Story**: US-002
**AC**: AC-US2-01, AC-US2-02, AC-US2-03
**Status**: [x] completed
**Owner**: backend

**Test Plan**:
Given `runCloneOnce` with `force === true` and `targetKind === "plugin"` and an existing `finalDir`
When the live finalDir is renamed to `${finalDir}.bak` before the rename pair, and the manifest rename fails
Then the bak is renamed back to `finalDir` (restore) and the error propagates; on success, `bestEffortRm(bakDir)` runs; if the restore itself fails, a clear warning is logged and `.bak` is preserved.

---

### T-006: Unit tests for extended `confirmPrompt` (clone-prompts.test.ts NEW)
**User Story**: US-003
**AC**: AC-US3-01, AC-US3-02, AC-US3-03
**Status**: [x] completed
**Owner**: testing

**Test Plan**:
Given a new file `src/commands/__tests__/clone-prompts.test.ts`
When 3 unit tests are written: `{yes:true}` → returns true without stdin reads; `{stdinIsTTY:false}` → returns false + stderr message; `{stdinIsTTY:true}` → calls readline path (mocked)
Then all 3 tests pass under `npx vitest run src/commands/__tests__/clone-prompts.test.ts`.

---

### T-007: Integration tests for plugin-root cleanup (US-001)
**User Story**: US-001
**AC**: AC-US1-01, AC-US1-02, AC-US1-03
**Status**: [x] completed
**Owner**: testing

**Test Plan**:
Given the existing `clone.integration.test.ts` harness
When 3 new tests are appended exercising bulk new-plugin failure on iteration 2 (assert pluginRoot removed), bulk new-plugin failure on iteration 1 (assert no rmRf calls beyond per-skill), and bulk add-to-existing-plugin failure on iteration 2 (assert plugin root preserved)
Then all 3 pass and existing tests remain green.

---

### T-008: Integration test for `.bak` staging (US-002)
**User Story**: US-002
**AC**: AC-US2-01, AC-US2-02
**Status**: [x] completed
**Owner**: testing

**Test Plan**:
Given the existing `clone.integration.test.ts` harness
When 2 new tests are added: (a) inject failure on the manifest rename — assert the original skill content is restored at finalDir and `.bak` is removed; (b) inject failure on the restore-rename itself — assert warning is captured and `.bak` exists
Then both tests pass.

---

### T-009: Regression check — full 0822 + 0825 vitest sweep
**User Story**: All
**AC**: AC-US2-03 + general no-regression
**Status**: [x] completed
**Owner**: testing

**Test Plan**:
Given all edits and new tests landed
When `npx vitest run src/clone/ src/installer/__tests__/frontmatter-fork.test.ts src/commands/__tests__/clone.integration.test.ts src/commands/__tests__/clone-prompts.test.ts` is run
Then 0 failures (existing 99 tests + new ~8 tests = ~107 total). Build still passes (`npm run build`). `node dist/bin.js clone --help` shows `--yes/-y`.
