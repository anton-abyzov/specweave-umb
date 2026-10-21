# Reusable routines in the personal assistant

## Problem

The user wants repeating personal work to live in the personal assistant (Aide) as reusable threads, not as a fresh chat every time (October 20, 2026). Examples: monthly tax preparation, a monthly profit and loss report, a research brief, and email triage with draft replies. SpecWithCode already has routines (scheduled tasks): a title, a prompt, an interval, fixed-time or webhook trigger, an optional bound thread and Run now. What they lack for this:

- a "when I ask" cadence and a monthly one;
- a thread of their own that later runs continue;
- a saved brief with inputs, the output location and a prepare-only rule;
- ready-made templates.

Routines without a bound thread wake the coordinator, so every run starts over. The Routines pane is labelled "Scheduled", even though manual routines have no schedule.

## Scope

In: the SpecWithCode app repository (`anton-abyzov/specwithcode-dev`), covering the contracts, the scheduled task service and storage, shared templates, the personal-assistant instructions, the web Routines pane and the settings editor, plus a headless demonstration with fictional fixtures.

Out:
- iOS edits (the iOS owner `mcp:2c7d2701-3df2-4e93-b3b9-41460a03eaa4` is working on Aide scrolling and links);
- filing or paying taxes, sending email, reading accounts the user did not list;
- enabling any schedule as an example;
- new spend;
- promotion copy, which goes to the promotion lead with evidence after release.

## Acceptance Criteria

- [ ] AC-01: Routines gain two cadences. `manual` runs only on Run now (by the user or an agent's `run_scheduled_task_now`) and never fires on its own. `monthly` runs on a day of the month (1-28) at a local time and follows the fixed-time missed-run rule. Existing routines are unchanged, and a client that cannot read the new cadences skips those routines instead of failing the list.
- [ ] AC-02: A routine set to use its own thread starts one thread, titled after the routine, on its first run and binds it. Later runs continue that thread. A retried run reuses the thread it started, so there is one thread. If the bound thread was deleted or archived, the next run starts a new one and binds it.
- [ ] AC-03: A routine keeps a brief: up to 8 inputs (label and location), an output location and a prepare-only rule. Every run's message opens with a short readable brief header:
  - the routine, the run date and the previous month;
  - the inputs, to be checked for presence and freshness before any work, stopping with a list when one is missing or stale;
  - the output location, to be updated in place on a rerun;
  - with prepare-only, that the run prepares and drafts only and lists the actions the user must take themselves (file, pay, send, post).

  The routine's own prompt follows the header unchanged.
- [ ] AC-04: A personal project offers four templates: Monthly tax prep, Monthly profit and loss, Research brief, and Email triage and draft replies. The existing Morning briefing stays.
  - Each template opens a prefilled, editable form that defaults to "When I ask", own thread and prepare-only.
  - Nothing is saved or scheduled until the user saves.
  - Template prompts route project-owned parts to the owning project and never send, file, pay or read an account the user did not list.
- [ ] AC-05: The project panel tab is labelled "Routines". Each routine shows:
  - its cadence in words ("When you ask", "Monthly on the 1st at 09:00");
  - a link to its thread;
  - its inputs and output;
  - its last run;
  - Run now and Pause controls.

  The pane is readable and operable at 390 px wide.
- [ ] AC-06: The settings editor edits manual and monthly routines without changing their cadence. The brief and own-thread settings survive edits from either editor. The MCP `schedule_task` tool accepts the new cadences and fields.
- [ ] AC-07: The personal assistant's instructions say to:
  - offer a routine from a template for repeating personal work;
  - keep it "When I ask" unless the user asks for a cadence;
  - route project-owned parts;
  - never take an external action itself.
- [ ] AC-08: A headless demonstration uses only fictional fixtures:
  - Routines pane screenshots at desktop width and 390 px;
  - a template form screenshot;
  - a server test that runs the Monthly tax prep routine twice against a fictional receipts folder, giving one thread, two runs and the brief header.

  Evidence files sit under the increment's `evidence/` folder.

## Approach

- **Contracts:** `packages/contracts/src/scheduledTask.ts` adds the `manual` and `monthly` schedules and `ScheduledTaskBrief`. Read and write unions both include them, and `ownThread` is added to the task and upsert models.
- **Schedule math:** `apps/server/src/scheduledTasks/Schedule.ts` handles next run, equality, description and the missed-run rule for monthly.
- **Storage:** `brief` and `ownThread` go into the existing `run_policy_json` column, so no migration is needed.
- **Service:** `ScheduledTaskService.runTask` covers an own-thread routine with no live thread. It launches the thread with the fire's command identity, binds it under the project lock, and prefixes the prompt with `routineBriefHeader` from `packages/shared/src/routineBrief.ts`.
- **Templates and instructions:** templates live in `packages/shared/src/routineTemplates.ts`. Aide's lines go in `ProjectWorkspaceService.projectContextText`.
- **Web:** `ProjectRoutines.tsx` gets template chips for personal projects, readable cards and a compact form component (`RoutineQuickForm.tsx`). The settings editor gains "When I ask" and "Monthly" modes; helpers move to its logic file so it stays under the file limit.
- **Demonstration:** a Playwright fixture under `apps/web/tests/` (headless, `PWDEBUG=0`, `PLAYWRIGHT_HTML_OPEN=never`) plus a server test with a temp fixture folder.

## Decisions

### Asked
- none
### Defaulted (change any before sw-do)
- D-01: Extend routines rather than add a new entity. The user-facing name stays "Routines", and the "Scheduled" tab is renamed to match.
- D-02: Templates default to "When I ask". Only the user turns on a cadence. Agents keep the existing `schedule_task` rules, and the instructions tell Aide not to enable a cadence the user did not ask for.
- D-03: An own-thread routine replaces a deleted or archived thread with a new one instead of failing, because the routine is the durable unit and the thread is its current home.
- D-04: Inputs are labels and locations the user provides (folders, files, URLs). The run checks freshness from what is at those locations. It never searches other accounts or folders.
- D-05: Idempotence comes from existing identities. A scheduled fire is keyed by its due time, Run now by the client's command id, and the own-thread launch by the fire's command id. Output named by period is updated in place.

## Tasks

### T-01 Contracts and schedule math for manual and monthly routines
- AC: AC-01, AC-06 | Files: packages/contracts/src/scheduledTask.ts, apps/server/src/scheduledTasks/Schedule.ts, apps/server/src/scheduledTasks/Schedule.test.ts | Test: vp test run apps/server/src/scheduledTasks/Schedule.test.ts

### T-02 Own thread, brief storage and brief header in runs
- AC: AC-02, AC-03 | Files: packages/shared/src/routineBrief.ts, packages/shared/src/routineBrief.test.ts, apps/server/src/scheduledTasks/ScheduledTaskStorage.ts, apps/server/src/scheduledTasks/ScheduledTaskService.ts, apps/server/src/scheduledTasks/ScheduledTaskService.routines.test.ts | Test: vp test run apps/server/src/scheduledTasks/ScheduledTaskService.routines.test.ts packages/shared/src/routineBrief.test.ts

### T-03 Templates, assistant instructions and MCP descriptions
- AC: AC-04, AC-06, AC-07 | Files: packages/shared/src/routineTemplates.ts, packages/shared/src/routineTemplates.test.ts, apps/server/src/project/ProjectWorkspaceService.ts, apps/server/src/project/ProjectWorkspaceService.test.ts, packages/contracts/src/orchestratorMcp.ts | Test: vp test run packages/shared/src/routineTemplates.test.ts apps/server/src/project/ProjectWorkspaceService.test.ts

### T-04 Routines pane, template form and settings editor modes
- AC: AC-04, AC-05, AC-06 | Files: apps/web/src/components/studio/ProjectRoutines.tsx, apps/web/src/components/studio/RoutineQuickForm.tsx, apps/web/src/components/studio/ProjectRoutines.test.tsx, apps/web/src/components/settings/ScheduledTasksSettings.tsx, apps/web/src/components/settings/scheduledTasksSettings.logic.ts, apps/web/src/components/studio/shell/ProjectPaneBar.tsx | Test: vp test run apps/web/src/components/studio/ProjectRoutines.test.tsx apps/web/src/components/settings

### T-05 Headless demonstration with fictional fixtures
- AC: AC-05, AC-08 | Files: apps/web/tests/routines-demo/ | Test: headless Playwright fixture; evidence in .specweave/increments/0980-aide-reusable-routines/evidence/

### T-06 PR, release and installed runtime check
- AC: AC-01, AC-02, AC-03, AC-04, AC-05, AC-06, AC-07, AC-08 | Files: none | Test: installed version and a manual template routine created and run in a fictional personal project, headless

### T-07 Verify and close 0980
