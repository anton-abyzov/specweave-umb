# Reopen a completed increment to planned

## Problem

An increment closed too early has no supported way back. `specweave resume` and `specweave start` refuse a `completed` increment. `MetadataManager.updateStatus` allows `completed → active` only, which activates the increment and takes a capacity slot. `doctor --fix-status` treats metadata as the source of truth, so it does not reopen anything either.

Evidence: EasyChamp 1009 (`ps23-public-competition-presentation`) is `completed` after its source-only closure. Its ledger has 15 tasks: 12 done, T-07 blocked, T-08 stale and T-09 open. Those three belong to `ps23-main`. The workspace is at capacity, so 1009 has to be corrected to `planned` without becoming active. The only route today is editing `metadata.json` by hand, which the coordinators rightly refuse (receipt `/Users/antonabyzov/Projects/sw-easychamp/.specweave/reports/1009-qualification-scope-capacity-2026-10-23.md`).

## Scope

In: `specweave reopen <id> --reason <text>`, completed to planned only, with workspace and owner checks, an audit record, JSON output, docs, completions and a changelog entry.

Out: activation (`specweave start` stays the only way to `active`, and its WIP note stays advisory), reopening abandoned increments (`resume` covers them), and running the command on 1009 itself (that belongs to its owner, `ps23-main`).

## Acceptance Criteria

- [ ] AC-01: `specweave --workspace <root> reopen <id> --reason <text>` on a `completed` increment sets `metadata.json` status to `planned`, along with the spec.md frontmatter when the spec has one. The increment never becomes `active`, and the active-increment state is not set.
- [ ] AC-02: The original closure is preserved. `metadata.reopened[]` gains an entry with `from`, `to`, `at`, `by`, `reason`, and the previous `approvedAt`, `closeReason` and `readyForReviewAt`. `ledger.jsonl`, `reports/` and the spec body are byte-identical afterwards.
- [ ] AC-03: The command exits 1 and changes nothing when the reason is empty, when no workspace is given (`--workspace` or `SPECWEAVE_WORKSPACE`), when the increment is not inside that workspace (a wrong root, or an increment folder that resolves outside it), or when the status is not `completed`.
- [ ] AC-04: The command exits 1 and changes nothing when a task is claimed, stale or blocked by an agent other than the caller, and it lists each such task with its owner. Tasks held by the caller do not block it. No flag overrides this check.
- [ ] AC-05: Reopen succeeds and stays `planned` when the workspace is at or over its active limit, and the active count is unchanged. The output names `specweave start <id>` as the separate activation step. Running reopen again on an already-reopened `planned` increment changes nothing and exits 0.
- [ ] AC-06: `--json` prints `{id, root, from, to, at, by, reason, previous, unfinished}`. The commands reference, the shell completions and the CHANGELOG list the command.

## Approach

`src/core/increment/reopen.ts` runs the checks in this order: reason, explicit workspace, realpath containment of the increment folder, status, then foreign owners from the ledger fold. Then `MetadataManager.reopenToPlanned` writes spec.md frontmatter first and `metadata.json` second, the same order `updateStatus` uses. It bypasses `VALID_TRANSITIONS` only for this audited path, so no other caller gains `completed → planned`. `src/cli/commands/reopen.ts` prints the result, and `bin/specweave.js` registers the command.

Rejected: adding `planned` to `VALID_TRANSITIONS[completed]`. It would let `computeTransitionPath` and every `updateStatus` caller reopen silently. Also rejected: a ledger note, because AC-02 keeps the ledger untouched and `metadata.json` already holds the status history.

## Decisions

### Asked
- D-01 Product source owner for this correction → this thread (routed by the SpecWeave coordinator; the 1009 owner runs the command).
### Defaulted (change any before sw-do)
- D-02 The command is named `reopen`, and its target is always `planned`.
- D-03 The workspace must be explicit, with `--workspace` or `SPECWEAVE_WORKSPACE`, because reopening rewrites a closed record.
- D-04 Foreign claimed, stale or blocked tasks always refuse the command. Ownership moves only through the existing `task release --force`.
- D-05 The previous `approvedAt`, `closeReason` and `readyForReviewAt` move into the `reopened[]` entry, so a `planned` increment never shows a completion date.
### Open
- none

## Tasks

### T-01 Reopen core and CLI
- AC: AC-01, AC-02, AC-03, AC-04, AC-05 | Files: repositories/anton-abyzov/specweave/src/core/increment/reopen.ts, repositories/anton-abyzov/specweave/src/core/increment/metadata-manager.ts, repositories/anton-abyzov/specweave/src/core/types/increment-metadata.ts, repositories/anton-abyzov/specweave/src/cli/commands/reopen.ts, repositories/anton-abyzov/specweave/bin/specweave.js, repositories/anton-abyzov/specweave/tests/unit/core/increment/reopen.test.ts | Test: cd repositories/anton-abyzov/specweave && npx vitest run tests/unit/core/increment/reopen.test.ts

### T-02 JSON, docs, completions and changelog
- AC: AC-06 | Files: repositories/anton-abyzov/specweave/scripts/completions/, repositories/anton-abyzov/specweave/docs-site/docs/reference/commands.md, repositories/anton-abyzov/specweave/CHANGELOG.md, repositories/anton-abyzov/specweave/tests/unit/core/increment/reopen.test.ts | Test: cd repositories/anton-abyzov/specweave && npx vitest run tests/unit/core/increment/reopen.test.ts

### T-03 Cross-model review and PR
- AC: AC-01, AC-02, AC-03, AC-04, AC-05, AC-06 | Files: repositories/anton-abyzov/specweave/src/core/increment/reopen.ts | Test: cd repositories/anton-abyzov/specweave && npx tsc --noEmit -p . && npm run test:unit

### T-04 Release and tarball receipt
- AC: AC-01, AC-05 | Files: repositories/anton-abyzov/specweave/CHANGELOG.md | Test: npm view specweave version

### T-05 Verify and close 1045
- AC: AC-01, AC-02, AC-03, AC-04, AC-05, AC-06 | Files: .specweave/increments/1045-reopen-completed-to-planned/ | Test: specweave verify 1045
