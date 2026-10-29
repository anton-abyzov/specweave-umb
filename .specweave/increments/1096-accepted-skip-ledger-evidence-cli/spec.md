# Accepted-skip ledger evidence (CLI)

## Problem

Anton decided on October 27, 2026 that an acceptance check needing an installation or license he does not have may close as "Skipped (accepted)", with the exact reason, who accepted it, when, and his authorization, and that it must never count as verified. The CLI ledger cannot record that today. `specweave task skip` stores only a reason, `by` and time, at task level. There is no AC-level or check-level waiver and no field for the accepting person or the authorization. SpecWithCode's ThreadIncrementProgress (owned by the 1095/#899 presentation thread) derives AC "skipped" from task states alone, so it cannot show who accepted what. 0922 AC-03 "wonder-full-shown-when-entitled" is the first real case and has only a free-text ledger note.

## Scope

In: one append-only `accept-skip` ledger event scoped to one AC id and one named check id; `specweave ac accept-skip` and `specweave ac list`; a per-AC `acceptance` disposition and waiver list in `task list --json`, `verify --json`, `pickup --json` and `reports/verify.{md,json}`; the closure rule for skipped-accepted ACs; a short section in the sw-done skill; completions; unit tests. Backfill of 0922 AC-03 after merge.

Out: a task-level waiver variant, check-level pass/fail receipts, revoking a waiver, a "closed-as-is, unobserved" disposition (0922 AC-02 Decline keeps its ledger note), any app change, release or deployment.

## Acceptance Criteria

- [ ] AC-01: `specweave ac accept-skip <AC> [inc] --check <id> --reason <text> --accepted-by <who> --authorization <text> [--accepted-at <date>]` appends exactly one `{"t":"AC-..","e":"accept-skip","by":..,"at":..,"check":..,"reason":..,"acceptedBy":..,"acceptedAt":..,"authorization":..}` line (the ledger's fixed key order; `model` may follow `at`); it refuses (exit 1, nothing written) when reason, accepted-by, authorization or check is missing, when the AC is not declared in spec.md, or when that AC/check pair is already accepted.
- [ ] AC-02: The fold never lets an accept-skip change task state or AC "met"; a duplicate or field-incomplete accept-skip is ignored with a reason; older ledgers without the event fold exactly as before.
- [ ] AC-03: Each AC gets `acceptance`: `met` (met by checkbox or tasks, no waiver), `mixed` (met by checkbox or tasks plus at least one waiver), `skipped-accepted` (not met, at least one waiver, and no covering task is still open, claimed, blocked or stale) or `open`; waivers never raise the met count, and an AC with an unresolved covering task stays `open` with its waivers listed.
- [ ] AC-04: `task list --json`, `verify --json`, `pickup --json` and `reports/verify.{md,json}` expose the per-AC `acceptance` and `waivers` (check, reason, acceptedBy, acceptedAt, authorization, by, at); verify.json adds `acs.skippedAccepted`, `acs.mixed` and a top-level `acceptedSkips` list, and verify.md lists every accepted skip explicitly.
- [ ] AC-05: `specweave verify` is ok and `specweave complete` passes when every AC is met or skipped-accepted (and commands pass); verify.md and the closure info line name the skipped-accepted ACs; this rule is documented in the sw-done skill and the generated plugin copy.
- [ ] AC-06: Completions are regenerated, `npx tsc --noEmit -p .` and `npm run test:unit` pass, and new tests live under `tests/unit/`.

## Approach

1. `src/core/tasks/ledger.ts`: add `accept-skip` to the event types, optional `check`, `reason`, `acceptedBy`, `acceptedAt`, `authorization` fields (fixed key order in `formatLedgerLine`, parsed in `parseLedger`), and an `acceptedSkips` list in the fold. The fold treats it like an increment-level event for task state (no state change); it keeps the first accept-skip per (AC, check) and ignores later duplicates and incomplete ones.
2. New `src/core/tasks/accepted-skip.ts`: `deriveAcAcceptance(acs, board)` adds `acceptance` and `waivers` to each AC entry; shared by verify, task list and pickup.
3. `verify-runner.ts`: `acsOk` accepts skipped-accepted ACs; verify.json gains the new counts, `items[].acceptance/waivers`, `acceptedSkips`; verify.md gets an "Accepted skips" section and an `accepted` cell in the AC table. `describeUncheckedAcs` subtracts skipped-accepted.
4. `closure-gate.ts`: info line names skipped-accepted ACs.
5. New `src/cli/commands/ac.ts` + `bin/specweave.js` `ac <action> [ac] [increment]` (actions `accept-skip`, `list`), following the `card` command's shape; auto-commit like `task skip`.
6. `task list --json` gains `criteria`; `pickup --json` gains `criteria` for the focused increment.
7. `skills/sw-done/SKILL.md` section, `npm run generate:skills`, `node scripts/completions/generate.mjs`.

Rejected: reusing `task skip` (task-level, no identity fields); a second store outside the ledger; counting skipped-accepted toward `acs.done`. Risk: an older CLI reading a new ledger counts the accept-skip line as malformed; that is never fatal.

## Decisions

### Asked
- none (the brief and project memory `accepted-skip-acceptance-preference.md` fix the rules)
### Defaulted (change any before sw-do)
- D-01 Command name → `specweave ac accept-skip` / `specweave ac list`, matching `card <action> [id] [increment]` (reversible).
- D-02 Closure → skipped-accepted ACs permit `specweave complete` and are listed by name in verify.md, verify.json and the closure info line (brief recommendation).
- D-03 Duplicate (AC, check) → first record wins, later ones are ignored with a reason; no revocation (append-only).
- D-04 Without per-check pass receipts, "remaining checks all waived" means no covering task is still unresolved; an AC met by its tasks or checkbox plus a waiver is `mixed`.
### Open
- none

## Tasks

### T-01 Ledger event and fold
- AC: AC-02 | Files: repositories/anton-abyzov/specweave/src/core/tasks/ledger.ts, repositories/anton-abyzov/specweave/tests/unit/core/tasks/accepted-skip.test.ts | Test: cd /Users/antonabyzov/.specwithcode/m4/worktrees/specweave/accepted-skip && npx vitest run tests/unit/core/tasks/accepted-skip.test.ts

### T-02 AC acceptance derivation, verify report and closure gate
- AC: AC-03, AC-04, AC-05 | Files: repositories/anton-abyzov/specweave/src/core/tasks/accepted-skip.ts, repositories/anton-abyzov/specweave/src/core/tasks/verify-runner.ts, repositories/anton-abyzov/specweave/src/core/tasks/closure-gate.ts, repositories/anton-abyzov/specweave/tests/unit/core/tasks/accepted-skip.test.ts | Test: cd /Users/antonabyzov/.specwithcode/m4/worktrees/specweave/accepted-skip && npx vitest run tests/unit/core/tasks/accepted-skip.test.ts

### T-03 CLI command and JSON outputs
- AC: AC-01, AC-04 | Files: repositories/anton-abyzov/specweave/src/cli/commands/ac.ts, repositories/anton-abyzov/specweave/bin/specweave.js, repositories/anton-abyzov/specweave/src/cli/commands/task.ts, repositories/anton-abyzov/specweave/src/core/session/pickup.ts, repositories/anton-abyzov/specweave/tests/unit/cli/commands/ac.test.ts | Test: cd /Users/antonabyzov/.specwithcode/m4/worktrees/specweave/accepted-skip && npx vitest run tests/unit/cli/commands/ac.test.ts

### T-04 Docs, completions, full checks and PR
- AC: AC-05, AC-06 | Files: repositories/anton-abyzov/specweave/skills/sw-done/SKILL.md, repositories/anton-abyzov/specweave/plugins/specweave/skills/, repositories/anton-abyzov/specweave/scripts/completions/ | Test: cd /Users/antonabyzov/.specwithcode/m4/worktrees/specweave/accepted-skip && npx tsc --noEmit -p . && npm run test:unit

### T-05 Verify and close 1096
- AC: AC-06 | Files: .specweave/increments/1096-accepted-skip-ledger-evidence-cli/ | Test: specweave verify 1096
