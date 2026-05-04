---
increment: 0825-vskill-clone-hardening
title: 'vskill clone hardening — partial-rollback, force-plugin restore, --yes flag'
type: bug
priority: P1
status: completed
created: 2026-05-01T00:00:00.000Z
structure: user-stories
test_mode: TDD
coverage_target: 90
---

# Feature: vskill clone hardening — partial-rollback, force-plugin restore, --yes flag

## Problem Statement

The 0822 code-review and grill identified three hardening gaps in `vskill clone`:

1. **HIGH** — When `runWholePluginClone` fails mid-iteration with `--target new-plugin`, the per-skill rollback loop only removes individual skill directories. The parent plugin root (scaffolded by iteration 1's `writeNewPlugin`) is left on disk. Violates AC-US4-03 ("target ends in a clean state on failure").
2. **MEDIUM** — When `--force` + `--target plugin` runs, the orchestrator deletes the live `finalDir` immediately before atomic-renaming the `.tmp` over it. If the subsequent plugin manifest rename fails, the original skill is gone and the staged `.tmp` may have already been consumed. Violates AC-US6-02 ("--force overwrite is atomic — never produces a half-overwritten state").
3. **LOW** — The whole-plugin confirmation prompt uses `process.stdin` synchronously and silently accepts in non-TTY contexts (CI, scripted runs). Violates AC-US4-02 ("prompts the user to proceed before bulk write"). Need `--yes` flag for explicit non-interactive consent and default-deny when TTY is unavailable.

This increment fixes all three. No new features; no module additions; only targeted edits to existing files in `src/commands/clone.ts` and `src/commands/clone-prompts.ts`.

## User Stories

### US-001: Plugin-root cleanup on bulk-clone failure (P1)
**Project**: vskill

**As a** user running `vskill clone --plugin <name> --target new-plugin --plugin-name <new>`
**I want** a failure during the second-or-later iteration to remove the entire scaffolded plugin root (not just the skills inside it)
**So that** I can re-run the clone without first manually deleting a half-scaffolded plugin directory

**Acceptance Criteria**:
- [x] **AC-US1-01**: When `runWholePluginClone` fails on iteration N≥2 with `targetKind === "new-plugin"` and `completed.length > 0`, the rollback removes the parent `pluginRoot` directory in addition to the per-skill cleanup. Verified by an integration test that injects a failure on iteration 2 of a 3-skill bulk new-plugin clone and asserts the plugin root no longer exists on disk.
- [x] **AC-US1-02**: When iteration 1 itself fails (no successful iterations), no extra cleanup runs (existing behavior preserved). Verified by an integration test injecting a failure on iteration 1 — assertion: cleanup does not call `rmRf` on a non-existent pluginRoot, and process exits cleanly.
- [x] **AC-US1-03**: For `targetKind === "plugin"` (existing user-owned plugin), the rollback does NOT remove the plugin root (only the per-skill cleanup runs). Verified by an integration test that fails iteration 2 of a 3-skill bulk add-to-existing-plugin clone — assertion: the user's existing plugin root still exists with its prior content intact.

---

### US-002: Atomic restore for `--force` + `--target plugin` (P1)
**Project**: vskill

**As a** user running `vskill clone <source> --target plugin --plugin <existing> --force` over a pre-existing skill
**I want** the operation to either fully succeed or leave the previous skill intact — never half-overwritten
**So that** a manifest-write failure does not destroy my existing installed skill

**Acceptance Criteria**:
- [x] **AC-US2-01**: Before performing `--force` deletion of the live target skill directory, the orchestrator renames it to `<finalDir>.bak`. Only after both the skill rename AND manifest rename succeed is `<finalDir>.bak` removed via `bestEffortRm`. Verified by an integration test injecting a failure on the manifest rename — assertion: the original skill content is restored at `finalDir` and `.bak` is removed.
- [x] **AC-US2-02**: If the `.bak` restore itself fails (rare — e.g., rename fails on filesystem boundary), a loud warning is logged and `.bak` is left in place for manual recovery. The orchestrator still exits with a non-zero code. Verified by a unit test that injects failure on the restore-rename and asserts the warning is emitted and `.bak` remains.
- [x] **AC-US2-03**: For non-`--force` paths and for `--target standalone` / `--target new-plugin`, behavior is unchanged. Verified by re-running the existing 0822 integration tests — all 17 must still pass.

---

### US-003: Non-interactive consent for whole-plugin clone (P2)
**Project**: vskill

**As a** CI or automation user running `vskill clone --plugin <name>` non-interactively
**I want** the tool to default-deny when no TTY is available and accept `--yes` for explicit non-interactive consent
**So that** scripted runs are predictable and don't accidentally bulk-clone N skills

**Acceptance Criteria**:
- [x] **AC-US3-01**: A new `--yes` (alias `-y`) flag is added to the `clone` command. When set, all interactive confirms (whole-plugin listing, --force overwrite) are auto-approved. Verified by a unit test invoking `confirmPrompt` with `{yes: true}` and asserting it returns `true` without reading stdin.
- [x] **AC-US3-02**: When `process.stdin.isTTY` is falsy AND `--yes` is not given, `confirmPrompt` returns `false` (default-deny) with a clear stderr message: `"refusing to prompt in non-TTY context — re-run with --yes to confirm"`. Verified by a unit test that mocks `process.stdin.isTTY = false` and asserts return value + message.
- [x] **AC-US3-03**: TTY-interactive behavior is unchanged. Verified by a unit test mocking `process.stdin.isTTY = true` and exercising the existing readline path (mocked).

## Functional Requirements

### FR-001: Rollback for new-plugin bulk clone
On failure during iteration N≥2 of `runWholePluginClone` with `targetKind === "new-plugin"`, after per-skill cleanup, also `rmRf` the parent plugin root.

### FR-002: --force + --target plugin .bak staging
Replace the in-place delete-before-rename with: rename live → `.bak`, attempt skill+manifest renames, on failure restore from `.bak`, on success `bestEffortRm(.bak)`.

### FR-003: --yes flag and TTY default-deny
Extend `confirmPrompt` to accept `{yes: boolean, stdinIsTTY: boolean}` options. Wire `--yes` flag through Commander to the orchestrator.

## Success Criteria

- All 3 hardening fixes ship with passing tests
- Existing 0822 test suite (99 tests) remains green — zero regressions
- New tests: ≥1 integration per US (3 minimum) plus ≥2 unit tests for `confirmPrompt`
- `vskill clone --help` shows `--yes` flag
- CI green on the modified `ci.yml` smoke step

## Out of Scope

- Studio UI work
- Any new commands or features
- Refactoring of unrelated code
- Changes to `--target standalone` happy-path

## Dependencies

- Built atop completed 0822 (uses the existing modules and test harness from that increment)
