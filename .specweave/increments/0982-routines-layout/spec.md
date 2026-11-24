# Routines layout in the project pane and manager

## Problem

The user (October 21, 2026): "You must improve the layout of routines and the way we display in the manager because this is completely off." Their screenshot of a project's Routines tab shows:

- tall gaps between routines;
- "Goes to the coordinator" repeated on every row;
- Run now, Pause and Enable as unstyled floating text, because the button styles only apply inside the project settings dialog;
- next runs as long numeric dates ("10/21/2026, 12:19:31 AM").

Settings > Scheduled tasks (the manager) shows a two-line prompt on every row, raw "failed"/"succeeded" badges, "Next run in 3h" with no date, and hides Run now in a menu. The pane links to "Manage routines" but lands on a page called "Scheduled tasks".

## Scope

In: the SpecWithCode app repository (`anton-abyzov/specwithcode-dev`), web only: the project Routines pane (`ProjectRoutines`, also shown in Project settings > Routines), Settings > Routines rows, the shared presentation helpers and the headless fixtures.

Out:
- routine semantics, schedules, triggers, storage, contracts and the server (owned by 0980/0981);
- running, enabling, pausing or deleting any real routine while testing;
- iOS and mobile.

## Acceptance Criteria

- [ ] AC-01: Each routine in the project pane is one compact row in a single bordered list: a state dot and word (Active, Paused, On request, Listening, Running, Last run failed), the title (long names wrap), then one line with cadence, next run (only when it will run), last run (only when there is no next run) and destination. Where the row has room for two columns (container 520 px or wider, such as Project settings > Routines at 1280 px), a row with a one-line title, no brief and no error is at most 84 px tall; in the narrower side pane (about 428 px at a 1440 px window) the actions sit below and such a row is at most 100 px.
- [ ] AC-02: Run now and Pause/Enable are bordered buttons with icons, lined up on the right of the row when there is room and below it when narrow, at least 40 px tall on touch screens, with a visible focus ring. Their accessible names stay "Run now", "Pause" and "Enable", described by the routine title.
- [ ] AC-03: Run times read as short local dates with the time zone: "Today 3:23 AM EDT", "Tomorrow 9:00 AM EDT", "Tue, Nov 3, 9:00 AM EST", the year only when it differs. No numeric dates remain.
- [ ] AC-04: The pane header reads "Routines" with the machine and counts ("On Development Mac · 1 active · 3 paused · 1 on request") and offers "New routine" and "Manage routines". "New routine" opens the Settings editor with the project already chosen. The empty state says "No routines yet" and offers "New routine"; loading and errors are readable.
- [ ] AC-05: Settings > Routines rows lead with the title (which opens the editor) and a state badge, then cadence · next run with how soon · last run · project (when the list spans projects) · destination, then a one-line prompt and any error. Run is a visible button beside the switch (none for webhook routines). The page, its nav entry, its New button and the editor say "Routine".
- [ ] AC-06: Behavior is unchanged: Run now keeps its retry identity and the unknown-outcome confirmation; paused or archived projects still block runs and enabling but allow pausing; read-only clients can do nothing. Existing unit tests pass.
- [ ] AC-07: Headless evidence (fictional fixtures only) at 1440, 900 and 390 px for the pane and 1280, 760 and 390 px for the manager, light and dark, before and after, with no sideways scrolling.

## Approach

- `apps/web/src/studio/routinePresentation.ts`: `routineState`, `routineRunTimeLabel`, `routineDestinationLabel`, `routineCountsLabel`, shared by both surfaces.
- `ProjectRoutines.tsx`: header, list and `RoutineRow`; styles in `shell/panes.css` under `.sws-routines` so they apply in the pane and the settings dialog, with a container query for the two-column row.
- `ScheduledTaskRow.tsx`: the manager row and the webhook deliveries dialog move out of `ScheduledTasksSettings.tsx` (1,498 lines) and get the new layout.
- `template=new` in the settings route opens a blank editor for the linked project.
- Fixtures: `?routines=coordinator` and `?routines=none` in the project-workspace fixture, `?routines` in the settings-presentation fixture.

## Decisions

### Asked
- none
### Defaulted (change any before sw-do)
- D-01: Times show in the reader's zone with its abbreviation. The server does not expose the host's zone, and cadences ("Daily at 09:00") stay in host time as before.
- D-02: The machine is named once in the header, not per row: every routine in a project's pane runs on that project's machine.
- D-03: Rename the manager to "Routines" to match the pane and the "Manage routines" link.
- D-05 (October 21, at close review): AC-01 first said 84 px "at 1440 px", but the 1440 px side pane is about 428 px wide, below the 520 px two-column threshold, so the actions stack (AC-02 "below it when narrow") and rows measure 97-98 px. The check only ever enforced 100 px there. The AC now states both measured limits, and PR #575 adds the 84 px assertion for the two-column dialog (plain rows measured 61-62 px; the error row is 84 px and the long-title row 80 px, both outside the assertion). PR #575 also fixes the dark captures, which were unreadable because the inline startup background stayed light.
- D-04: Fix `useHandoffModeSnapshot` (from #536) in the same PR: its subscribe function changed every render, so each snapshot resubscribed and refetched. That hung every project-workspace fixture and caused a refetch loop for a lone subscriber in the app.

## Tasks

### T-01 Presentation helpers and the project pane layout
- AC: AC-01, AC-02, AC-03, AC-04, AC-06 | Files: apps/web/src/studio/routinePresentation.ts, apps/web/src/studio/routinePresentation.test.ts, apps/web/src/components/studio/ProjectRoutines.tsx, apps/web/src/components/studio/shell/ScheduledPane.tsx, apps/web/src/components/studio/shell/panes.css, apps/web/src/components/studio/ProjectWorkspaceSurface.tsx | Test: vp test run apps/web/src/studio/routinePresentation.test.ts apps/web/src/components/studio/ProjectRoutines.test.tsx

### T-02 Manager rows, Routines naming and the new-routine link
- AC: AC-04, AC-05, AC-06 | Files: apps/web/src/components/settings/ScheduledTaskRow.tsx, apps/web/src/components/settings/ScheduledTasksSettings.tsx, apps/web/src/components/settings/scheduledTasksSettings.logic.ts, apps/web/src/components/settings/settingsSearch.ts | Test: vp test run apps/web/src/components/settings

### T-03 Headless before and after evidence
- AC: AC-07 | Files: apps/web/tests/project-workspace/, apps/web/tests/settings-presentation/, apps/web/src/studio/handoffMode.ts | Test: node apps/web/tests/project-workspace/routines-layout-check.mjs and node apps/web/tests/settings-presentation/routines-check.mjs (headless)

### T-04 PR, merge and release
- AC: AC-01, AC-02, AC-03, AC-04, AC-05, AC-06, AC-07 | Files: none | Test: CI green on the PR; release state recorded

### T-05 Verify and close 0982
