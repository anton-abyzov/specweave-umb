# Plan timeline, forecasts and required increments

## Problem

Feature requests given to agents in SpecWithCode often never become increments, so the plan card stays empty and nobody can see what is in progress. Evidence from October 21-22, 2026:

- Of 180 top-level SpecWithCode threads, 32 were bound to an increment, 46 worked one without a link and 81 changed code with no increment at all (`thread-increment-binding-gaps.md`).
- The CLI binds a thread only when it appends to a ledger. `create-increment`, `verify` and `complete` never bind, so a thread that plans and closes an increment without claiming tasks shows "No plan".
- Nothing asks an agent to plan first. The loop text says "Small fixes need no increment", and no hook checks it, so agents skip the step for feature work too.
- The installed CLI on M4 is 3.1.4 while npm has 3.1.5; the umbrella's `AGENTS.md` sections are from template 3.0.23.
- `specweave dashboard` already has a Kanban "Work board", but it has no timeline, no forecast, no activity feed and only a text search. Every card says "Model unknown" because ledger events carry no model.

## Scope

In: binding on create, verify and complete; per-session work markers; the model on ledger events; an opt-in `planning.requireIncrement` policy (`off`, `remind`, `enforce`) with a PreToolUse guard, `specweave small-fix` as the explicit exemption and `specweave require-increment` to switch it; a Timeline page in `specweave dashboard` with filters, a Gantt chart with forecasts, throughput and an activity feed; filters on the Work board.

Out: SpecWithCode app changes (exporting `SPECWEAVE_STUDIO_THREAD_ID` from ACP, Grok, Cursor, OpenCode and Pi adapters; an increment field on `delegate_task`; coordinator classification). Those live in `anton-abyzov/specwithcode-dev`. No network calls, no model calls.

## Acceptance Criteria

- [ ] AC-01: `specweave create-increment`, `specweave verify` and `specweave complete` run inside a SpecWithCode thread write the thread binding for that increment, and every one of them (plus any ledger append) writes a session marker when the tool exposes a session id.
- [ ] AC-02: Ledger events written by an agent carry `model` when the environment names one (`SPECWEAVE_MODEL`, or `ANTHROPIC_MODEL` under Claude Code), and the Work board shows that model instead of "Model unknown".
- [ ] AC-03: With `planning.requireIncrement` set to `enforce`, an Edit or Write outside `.specweave/` in a session with no increment and no small-fix marker is denied with the two commands that unblock it; `remind` warns once per session; `off` (the default) changes nothing.
- [ ] AC-04: `specweave small-fix "<why>"` exempts the current session and logs the exemption to `.specweave/state/small-fixes.jsonl`; `specweave require-increment <off|remind|enforce>` updates config and installs or removes the project-level PreToolUse hook.
- [ ] AC-05: `GET /api/plan` returns one row per increment with actual start and end from the ledger, a remaining-work forecast for open increments (p50 and p80 hours and finish dates, assuming uninterrupted work), per-tool and per-model task rates, daily throughput and the latest ledger activity.
- [ ] AC-06: The dashboard's Timeline page shows a Gantt chart with forecast bars and a today line, KPI tiles for the forecast, a throughput chart and an activity feed; filters for status, agent tool, time window and text narrow every view; each increment row links to its detail page.
- [ ] AC-07: The Work board can be filtered by agent tool and hides completed work older than the chosen window.

## Approach

Binding: generalize `studio-thread-binding.ts` so callers that have an increment folder, not a ledger line, can bind. Add `work-session.ts` with `recordWorkSession` and `readWorkSession` for `~/.specweave/sessions/<id>.json`. `appendEvent` writes both; `create-increment`, `verify` and `complete` call both.

Policy: the guard lives in `pre-tool-use.ts` beside the status guard, reads `planning.requireIncrement` from `.specweave/config.json` and passes when the session has a marker or a Studio binding. It stays fail-open and offline. The hook is registered in the project's `.claude/settings.json` the same way the Jev Bash guard is (reusing `jev-helpers.ts`), so projects that leave the policy off pay nothing. Other tools read the rule from `AGENTS.md`.

Forecast: per completed task, active time is the gap from the later of its claim and the same agent's previous done in that increment, capped at 4 hours. Task weight is `1 + 0.5 x (files - 1) + 0.25 x (ACs - 1)`, clamped to 0.5-4. The rate is the median (p50) and 80th percentile (p80) of time per weight unit, keyed by model when known, else by tool, else overall. Open increments project remaining weight x rate from now; the overall finish date divides the work across lanes, the median number of agents finishing tasks per active day over the last week. The guard reaches edits through the hook launcher only under a `.specweave/state/require-increment.enabled` marker, and session markers count only for this project and an open increment. The Gantt is plain SVG and CSS, no chart library.

Rejected: a hosted dashboard or a separate static HTML report (the dashboard already serves live local data); a model call to estimate complexity (offline rule); blocking edits by default (would change behaviour for every user on upgrade).

## Decisions

### Asked
- D-01 Should an increment be mandatory? → The user asked for it; shipped as `enforce`-capable policy with the `small-fix` escape.
### Defaulted (change any before sw-do)
- D-02 Default for new projects → `off`; turn on per project with `specweave require-increment enforce`.
- D-03 Forecast assumes uninterrupted work and active-time caps of 4 hours per task.
### Open
- none

## Tasks

### T-01 Bind threads and sessions on create, verify and complete; model on events
- AC: AC-01, AC-02 | Files: src/core/tasks/studio-thread-binding.ts, src/core/tasks/work-session.ts, src/core/tasks/ledger.ts, src/cli/commands/create-increment.ts, src/cli/commands/verify.ts, src/cli/commands/complete.ts, src/dashboard/server/data/work-projection.ts, tests/unit/core/tasks/work-binding.test.ts | Test: npx vitest run tests/unit/core/tasks/work-binding.test.ts

### T-02 Required-increment policy, small-fix and require-increment commands
- AC: AC-03, AC-04 | Files: src/core/hooks/handlers/pre-tool-use.ts, src/core/hooks/handlers/require-increment.ts, src/cli/commands/small-fix.ts, src/cli/commands/require-increment.ts, bin/specweave.js, src/core/config/types.ts, src/templates/AGENTS.md.template, tests/unit/core/hooks/require-increment.test.ts | Test: npx vitest run tests/unit/core/hooks/require-increment.test.ts

### T-03 Plan timeline and forecast API
- AC: AC-05 | Files: src/dashboard/server/data/plan-timeline.ts, src/dashboard/server/routes/plan-routes.ts, src/dashboard/server/dashboard-server.ts, src/dashboard/work-types.ts, tests/unit/dashboard/plan-timeline.test.ts | Test: npx vitest run tests/unit/dashboard/plan-timeline.test.ts

### T-04 Timeline page and Work board filters
- AC: AC-06, AC-07 | Files: src/dashboard/client/src/pages/TimelinePage.tsx, src/dashboard/client/src/pages/timeline.css, src/dashboard/client/src/pages/WorkPage.tsx, src/dashboard/client/src/App.tsx, src/dashboard/client/src/components/layout/Sidebar.tsx | Test: node scripts/dashboard/plan-timeline-check.mjs

### T-05 Verify and close 0996
- AC: AC-01, AC-02, AC-03, AC-04, AC-05, AC-06, AC-07 | Files: none | Test: specweave verify 0996
