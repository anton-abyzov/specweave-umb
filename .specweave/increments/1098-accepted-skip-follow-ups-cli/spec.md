# Accepted-skip follow-ups (CLI)

## Problem

The exact-head review of specweave #2175 (merged as `07d2f34859`, October 27, 2026; `/Users/antonabyzov/.specwithcode/m4/evidence/sweep-reviews-20261026/review-2175-015bf42a3b.md`) shipped it with one medium and three low findings. One waiver for any check closes an AC that no task covers, including an AC whose task cites it in a format the parser ignores, so a real open task is hidden. `pickup --json` drops waivers for increments without tasks. The handoff index and HTML report do not label skipped-accepted ACs. `--reason` and `--authorization` have no length cap.

## Scope

In: refuse `ac accept-skip` on an AC no task covers unless `--uncovered` confirms it; flag such ACs in verify (`acs.items[].uncovered`, verify.md, closure notice); pickup reads accepted skips without a task board; "Accepted skip (not verified)" labels in the handoff index, the HTML handoff report and the handoff doc; length caps on the free-text fields. Out: the 0922 backfill (on hold for the app reader), app changes, release.

## Acceptance Criteria

- [ ] AC-01: `ac accept-skip` on an AC that no task cites exits 1 and writes nothing unless `--uncovered` is passed; with it, the event is written and stderr warns that the waiver closes the whole AC.
- [ ] AC-02: verify.json marks a skipped-accepted AC with no covering task as `uncovered: true`; verify.md and the closure notices name it.
- [ ] AC-03: `pickup --json` reports the same `acceptance` and `waivers` as `ac list` for an increment with ACs but no tasks.
- [ ] AC-04: The handoff index (`handoff --all`), the HTML handoff report and the handoff doc show skipped-accepted ACs labelled "Accepted skip (not verified)", not as open or plain unmet.
- [ ] AC-05: `--check` over 100, `--reason` over 1,000 and `--authorization` over 2,000 characters are refused with nothing written.
- [ ] AC-06: Completions regenerated, `npx tsc --noEmit -p .` and `npm run test:unit` pass, tests under `tests/unit/`.

## Approach

`src/cli/commands/ac.ts` (refusal, `--uncovered`, caps), `bin/specweave.js` (option), `src/core/tasks/accepted-skip.ts` (`uncovered` flag, optional skips list), `verify-runner.ts`, `closure-gate.ts`, `src/core/session/pickup.ts`, `handoff-all.ts`, `handoff-report.ts`, `work-handoff.ts` + `handoff-doc-format.ts`, sw-done skill text, completions.

## Decisions

### Asked
- none
### Defaulted (change any before sw-do)
- D-01 Uncovered AC → refuse by default with an explicit `--uncovered` override (the brief allowed warn or refuse; refusing stops a silent hide). The override is a CLI confirmation only; the event schema is unchanged, and verify flags the AC from the task board.
- D-02 Caps → check 100, reason 1,000, authorization 2,000 characters.
### Open
- none

## Tasks

### T-01 Uncovered refusal, verify flag and caps
- AC: AC-01, AC-02, AC-05 | Files: repositories/anton-abyzov/specweave/src/cli/commands/ac.ts, repositories/anton-abyzov/specweave/src/core/tasks/accepted-skip.ts, repositories/anton-abyzov/specweave/src/core/tasks/verify-runner.ts, repositories/anton-abyzov/specweave/src/core/tasks/closure-gate.ts | Test: cd /Users/antonabyzov/.specwithcode/m4/worktrees/specweave/accepted-skip-followups && npx vitest run tests/unit/cli/commands/ac.test.ts tests/unit/core/tasks/accepted-skip.test.ts

### T-02 Pickup and handoff labels
- AC: AC-03, AC-04 | Files: repositories/anton-abyzov/specweave/src/core/session/pickup.ts, repositories/anton-abyzov/specweave/src/core/session/handoff-all.ts, repositories/anton-abyzov/specweave/src/core/session/handoff-report.ts, repositories/anton-abyzov/specweave/src/core/session/work-handoff.ts | Test: cd /Users/antonabyzov/.specwithcode/m4/worktrees/specweave/accepted-skip-followups && npx vitest run tests/unit/core/session/accepted-skip-labels.test.ts tests/unit/core/tasks/accepted-skip.test.ts

### T-03 Docs, completions, full checks, PR
- AC: AC-06 | Files: repositories/anton-abyzov/specweave/skills/sw-done/SKILL.md, repositories/anton-abyzov/specweave/scripts/completions/ | Test: cd /Users/antonabyzov/.specwithcode/m4/worktrees/specweave/accepted-skip-followups && npx tsc --noEmit -p . && npm run test:unit

### T-04 Verify and close 1098
- AC: AC-06 | Files: .specweave/increments/1098-accepted-skip-follow-ups-cli/ | Test: specweave verify 1098
