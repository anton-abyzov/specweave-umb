---
increment: 0870-restore-dead-hooks
title: Restore the 6 dead SpecWeave hooks (incl. a real blocking stop-auto)
type: bug
priority: P1
status: completed
created: 2026-06-03T06:30:00.000Z
structure: user-stories
test_mode: TDD
coverage_target: 90
---

# Bug: restore the 6 dead hooks found in 0869 (router/hooks.json parity)

## Overview

0869 proved 6 hooks are dead (router never registers them). This increment restores them
and makes the 0869 guard's `KNOWN_UNROUTED` shrink to empty. 5 are straightforward restores
of self-contained, non-blocking handlers recovered from git (`0f81519b1^`, saved to
`/tmp/dead-hooks/<hook>.ts`). **`stop-auto` is the exception and the centerpiece**: the
recovered version was a non-blocking logging stub, but the live `/sw:auto` skill
(`plugins/specweave/skills/auto/SKILL.md`) requires the Stop hook to **return `decision:block`**
to drive the autonomous loop — so a correct blocking handler must be written, not restored.

## Per-hook decisions (evidence-based)

| Hook | Decision | Notes |
|------|----------|-------|
| `session-start` | **REGISTER (restore)** | recovered handler: clears stale auto-mode files + baseline health check; self-contained, non-blocking. |
| `post-tool-use` | **REGISTER (restore)** | recovered: detects increment-file changes, queues events to `state/pending.jsonl` for `stop-sync`. |
| `post-tool-use-analytics` | **REGISTER (restore)** | recovered: appends Skill/Task analytics to `state/analytics/events.jsonl`; non-blocking. |
| `stop-reflect` | **REGISTER (restore)** | recovered: reflection-enabled check + log; harmless, keeps the Stop pipeline intact (real reflection wiring is a future enhancement). |
| `stop-sync` | **REGISTER (restore)** | recovered: reads `pending.jsonl`, dedups by increment, clears queue; pairs with `post-tool-use`. |
| `stop-auto` | **REGISTER (REWRITE — blocking)** | recovered was non-blocking; implement the real auto-loop blocker per `/sw:auto` SKILL.md. |

## User Stories

### US-001: Restore the 5 non-blocking hooks (P1)
**Project**: specweave

**As a** SpecWeave user relying on session-start cleanup, post-edit event queueing, analytics, and session-end sync
**I want** those 5 hooks to actually run again
**So that** the documented behaviors stop silently no-op'ing.

**Acceptance Criteria**:
- [x] **AC-US1-01**: `session-start`, `post-tool-use`, `post-tool-use-analytics`, `stop-reflect`, `stop-sync` are restored as handler files and registered in `hook-router.ts` `HANDLERS`.
- [x] **AC-US1-02**: Each restored handler has a test that routes through `hookRouter('<name>', stdin)` (NOT a direct handler call) and asserts its observable effect (e.g. analytics event appended, pending event queued/cleared) + that it returns the safe shape and never blocks.
- [x] **AC-US1-03**: Each restored name is removed from `KNOWN_UNROUTED` in `hook-wiring-parity.test.ts`; the 0869 guard passes (parity holds).

### US-002: Implement a real blocking stop-auto for /sw:auto (P1)
**Project**: specweave

**As a** developer running `/sw:auto`
**I want** the Stop hook to block-to-continue while work remains and block-for-closure when done
**So that** autonomous mode actually loops as the skill documents.

**Acceptance Criteria**:
- [x] **AC-US2-01**: `stop-auto` is registered and, when `state/auto-mode.json` is active and non-stale and tasks/ACs remain in the active increment(s), returns `{ decision: 'block', reason: <actionable continue message naming the increment + remaining counts + userGoal> }`.
- [x] **AC-US2-02**: When all tasks are complete AND all ACs satisfied, it returns `{ decision: 'block', reason: ...'all_complete_needs_closure'... }` (the trigger the skill consumes for `sw:done --auto`).
- [x] **AC-US2-03**: It NEVER blocks when auto-mode.json is absent/`active:false`/stale → `{ decision: 'approve' }` (ordinary sessions are never trapped).
- [x] **AC-US2-04**: A turn counter (`state/.stop-auto-turns`) is incremented per block and, beyond `config.auto.maxTurns` (default 20), the handler safety-stops (returns approve + clears the counter) so the loop can never run away. The counter resets when not auto-active / on closure.
- [x] **AC-US2-05**: The handler never throws (any error → approve). Routed tests (`hookRouter('stop-auto', …)`) cover: not-active→approve; pending→block-continue (+counter increments); all-complete→block-closure; maxTurns→approve. Prefer existing parsers (`parseTasksWithUSLinks`, `calculateProgressFromTasksFile`) for accurate task/AC counts.

### US-003: Parity guard reaches empty + ships (P1)
**Acceptance Criteria**:
- [x] **AC-US3-01**: After all 6 are registered, `KNOWN_UNROUTED` is empty and `hook-wiring-parity.test.ts` still passes (invoked ⊆ registered).
- [x] **AC-US3-02**: `npx vitest run src/core/hooks` is fully green; no regression to the live 4 hooks or 0868/0869 tests.
- [x] **AC-US3-03**: Version bumped (patch) so a republish ships the restored handlers; installed-cache drift noted (needs `refresh-plugins`).

## Out of Scope

- Fleshing out real reflection logic beyond the restored stub (`stop-reflect`) and real external-sync calls inside `stop-sync` beyond queue dedup/clear (those remain skill/command-driven). Tracked as future enhancements.

## Success Criteria

- All 6 events registered; `KNOWN_UNROUTED` empty; routed tests per hook green; `/sw:auto` smoke: with an active `auto-mode.json` + pending tasks, `node bin/specweave.js hook stop-auto` returns `decision:block`; with all complete, blocks with `all_complete_needs_closure`; with no auto-mode, approves.

## Dependencies

- `/tmp/dead-hooks/*.ts` (recovered handlers), `hook-router.ts`, `plugins/specweave/skills/auto/SKILL.md` (contract), `parseTasksWithUSLinks`, `calculateProgressFromTasksFile`, `hook-wiring-parity.test.ts`.
