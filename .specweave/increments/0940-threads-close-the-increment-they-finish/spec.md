# Threads close the increment they finish

## Problem

Agent threads open SpecWeave increments, but the same flow never tells them to verify and close the increment when their work is done. Evidence (2026-10-19): a SpecWithCode thread's checklist read "Opened increment 0939 for the work ... Test, open PRs, merge, release", with no verify or close step. In the umbrella, 0935 and 0936 are still `active` with every task done, and 0930-0934 shipped through PRs with no ledger `done` lines at all.

Causes:
- AGENTS.md "The loop" step 4 (verify, review, complete) has no trigger, and step 5 sends every stop to handoff.
- `specweave task done` on the last task says only "Next: specweave verify".
- The plugin's only end-of-turn hook (Stop) runs in auto mode only, so ordinary sessions and threads get no close nudge.
- Studio's starter cards ("Continue increment NNNN", "Pick up the handoff") and its coordinator and worker prompts never mention verify or complete.

## Scope

In: the loop text in the AGENTS.md template, `task done`/`skip`/`next` output, pickup hints, a once-per-session Stop-hook close nudge outside auto mode, the auto Stop loop ignoring closed increments, and Studio's starter cards and worker/coordinator prompts. Out: closing the umbrella's old open increments, which is separate cleanup.

## Acceptance Criteria

- [ ] AC-01: The AGENTS.md loop that tells agents to open an increment also tells them that a plan or checklist for it ends with "verify and close NNNN". When the last task is done or skipped, they run `specweave verify`, a fresh-context review and `specweave complete` in the same session without asking. Handoff applies only while tasks remain.
- [ ] AC-02: When `specweave task done` or `task skip` finishes the last open task, it prints the full close chain (verify, review, complete), and `task next` with nothing left prints the same chain.
- [ ] AC-03: Outside auto mode, the Stop hook reminds the session that finished an increment's last task through the CLI, once (it blocks a single stop), to verify and close it. Other sessions in the folder are never blocked, it never fires for a closed increment, and every other stop costs nothing (no worker spawn).
- [ ] AC-04: In auto mode, the Stop loop stops blocking once the increment is completed or abandoned.
- [ ] AC-05: In SpecWithCode, the "Continue increment" and "Pick up the handoff" starter cards, plus the worker and coordinator prompts, tell the thread to verify and close the increment once its tasks are done, without asking.

## Approach

specweave (`develop`):
- `src/templates/AGENTS.md.template` loop.
- `src/cli/commands/task.ts` close message, plus a marker `.specweave/state/close-pending.json` (`{ "<id>": { "at": iso, "session": CLAUDE_CODE_SESSION_ID } }`) written when the last task turns terminal inside a Claude Code session.
- `src/core/increment/close-pending.ts` (new) holds the marker read/write/prune.
- `src/core/hooks/handlers/stop.ts`: the non-auto branch reminds only the session named in the marker (stdin `session_id`), once, and never when `stop_hook_active`. Entries are pruned when the increment is closed (legacy spellings included), reopened, or older than 24h.
- `plugins/specweave/hooks/run.mjs` fast path lets Stop through only when a marker entry names this session.
- `src/core/session/pickup.ts` hints.
- `skills/sw-do`, `skills/sw-increment`, `skills/sw-handoff` say the same.

Studio (`main`): `packages/shared/src/projectStarterSuggestions.ts`, `apps/server/src/project/ProjectWorkspaceService.ts`.

Rejected: a Stop nudge for every active-with-all-tasks-done increment. It would block unrelated sessions in a shared folder and spawn a worker on every turn.

## Decisions

### Asked
- none
### Defaulted (change any before sw-do)
- D-01: Only the session that finished the last task is reminded, once (review found a folder-wide nudge would push unrelated and headless sessions into extra turns) → session-scoped.
- D-02: Markers older than 24h are dropped; pickup's "/sw:done" hint covers older ones → 24h.

## Tasks

### T-01 Loop text and skills end with verify and close
- AC: AC-01 | Files: src/templates/AGENTS.md.template, skills/sw-do/SKILL.md, skills/sw-increment/SKILL.md, skills/sw-handoff/SKILL.md, tests/unit/cli/helpers/init/instruction-templates.test.ts | Test: npx vitest run tests/unit/cli/helpers/init tests/unit/skills

### T-02 task done/skip/next print the close chain and mark close-pending
- AC: AC-02 | Files: src/cli/commands/task.ts, src/core/increment/close-pending.ts, src/core/session/pickup.ts, tests/unit/core/increment/close-pending.test.ts | Test: npx vitest run tests/unit/core/increment/close-pending.test.ts

### T-03 Stop hook nudges once outside auto mode; auto loop ignores closed increments
- AC: AC-03, AC-04 | Files: src/core/hooks/handlers/stop.ts, plugins/specweave/hooks/run.mjs, tests/unit/core/hooks/handlers/stop.test.ts, tests/unit/hooks/run-mjs.test.ts | Test: npx vitest run tests/unit/core/hooks/handlers/stop.test.ts tests/unit/hooks/run-mjs.test.ts

### T-04 SpecWithCode cards and prompts close the increment
- AC: AC-05 | Files: packages/shared/src/projectStarterSuggestions.ts, apps/server/src/project/ProjectWorkspaceService.ts (specwithcode-dev) | Test: vp test run src/projectStarterSuggestions.test.ts (packages/shared) and src/project/ProjectWorkspaceService.test.ts (apps/server)
