# Ultracode on model track rows, so threads started on a track run with it

## Problem

The owner reported (November 23, 2026) that new threads in the specweave project never run with Ultracode, although he had set it for the project. His screenshots show a thread on m4 on Opus 5.5 whose menu reads "Ultracode: Not set: follows the Claude workflow mode", and Project settings with "New threads use: Tracks", where each Daily row has an effort level and nothing for Ultracode.

Traced on `origin/main` at `42dafc536`:

- Ultracode reaches Claude Code in two ways only. The thread's own model selection carries `ultracode: true` (`apps/server/src/claudeModelOptions.ts:213`), or the Claude workflow mode is Automatic (`apps/server/src/orchestration-v2/RuntimePolicy.ts:304`, `apps/server/src/provider/ClaudeWorkflowPolicy.ts:130`). There is no project default for it: increment 1295 planned one (`claudeUltracodeDefault`) and stopped after its first task, so the key is not on main.
- In One model mode the project's model carries the option, set in Project settings or with the Ultracode button in the coordinator's Models popover (`apps/web/src/components/studio/shell/ProjectModelsPopover.tsx:321`).
- On Tracks that model is ignored: `projectThreadModel` and `projectWorkerModel` return null (`packages/shared/src/projectSettings.ts:313` and `:342`), and a new draft takes the first Daily entry (`packages/shared/src/modelTracks.ts:506`).
- A track entry can hold any model option, but the only control on a row is effort (`TrackEffortSelect`, `apps/web/src/components/settings/ModelTracksSettings.tsx:581`). So an entry never has `ultracode`.
- The Models popover still shows "New threads", "Effort for new threads" and the Ultracode button on a Tracks project. They save the project's own model (`apps/web/src/components/studio/ProjectWorkspaceSurface.tsx:937`), which no thread starts on. This is the setting that looks set and does nothing.
- Even with the option on an entry, three launch paths would drop it: a delegated worker is resolved from model and effort only (`routedTarget`, `apps/server/src/project/TaskRouting.ts:272`); and when the track's pick is the model the launch already had, the entry is never read (`packages/shared/src/modelLanes.ts:579`, `apps/server/src/project/TracksLaunch.ts:109`, `apps/server/src/mcp/OrchestratorMcpService.ts:2343`, `apps/server/src/mcp/toolkits/project/handlers.ts:814`). That is the common case here: a coordinator on Opus 5.5 delegating into a Daily track topped by Opus 5.5.

## Scope

In: an Ultracode switch on Daily and Complex track rows whose model offers it, stored in the entry's options beside its effort; every thread started on a track entry takes it (composer draft, unnamed launch, `delegate_task`, `studio_thread_launch`, `create_threads`), also when the entry is the model the launch already had; the Models popover on a Tracks project shows where threads start and no longer edits an unused model; docs; tests; a headless capture of the rows.

Out: the project-wide default of 1295 (on for every thread that never chose, usage pause, one-time notice); Ultracode for providers that have none (Copilot, Cursor, Devin, Codex, Muse); the Review track; routine threads; changing a thread that already exists; the phone apps' settings screens.

## Acceptance Criteria

- [ ] AC-01: In Settings > Models and in Project settings on Tracks, a Daily or Complex row whose own source lists the model with an Ultracode option shows an Ultracode switch beside the effort level. Rows without it (GPT, a Claude model through Copilot, Haiku 4.5) and every Review row show none.
- [ ] AC-02: Turning the switch on saves `ultracode: true` in that entry's options and keeps its effort; turning it off removes the option. On a built-in track the whole built-in list is saved as the person's own, like an effort change, with only that row different.
- [ ] AC-03: A new draft in a Tracks project whose first Daily entry has Ultracode on shows it in the composer ("Medium · Ultracode"), and the thread it starts has `ultracode: true` in its model selection.
- [ ] AC-04: A thread started without a named model on an entry with Ultracode on (`delegate_task`, `studio_thread_launch`, `create_threads`, a draft sent unpicked) starts with `ultracode: true`, both when the track moves it to another model and when the entry is the model it already had.
- [ ] AC-05: A launch that names the option keeps its own value: `ultracode: false` in a target's options, or a model selection that already carries the option, is never overwritten. A launch that names a model is not routed and takes nothing from a row.
- [ ] AC-06: An entry's Ultracode is never applied to a model that does not offer it (the same model on a source of another harness, or a release without it), and such a launch does not fail.
- [ ] AC-07: A routine's own thread started from a track does not take the row's Ultracode.
- [ ] AC-08: On a Tracks project the Models popover's "New threads" row names the first Daily model with its effort, and Ultracode when on, and links to Project settings. It has no model picker, no "Use default", no effort row and no Ultracode button. On One model it is unchanged.
- [ ] AC-09: A headless capture (`headless: true`) shows the rows with the switch on and off.

## Approach

The option lives where the effort does: in the track entry (`ModelSelection.options`). Storage is unchanged (`modelLanes.routine`, `modelLanes.complex`); an older app ignores an option it has no control for and still passes it to Claude Code, which reads `ultracode` since 1122.

1. `packages/shared/src/modelTracks.ts`: `trackEntryOffersUltracode`, `trackEntryUltracode`, `withTrackUltracode` (set or remove) and `withTrackEntryUltracode(selection, entry, providers)`, which adds `ultracode: true` to a launch selection only when the entry has it, the selection names no `ultracode` of its own and its model offers the option.
2. `packages/shared/src/modelLanes.ts`: when the lane's pick is the baseline model, the decision's selection is the baseline with the entry's Ultracode applied; a moved decision already carries the entry's options.
3. Server launch paths read the decision's selection in both cases: `TracksLaunch.ts`, `OrchestratorMcpService.ts` (`routeWorker`, where a moved worker's resolved target also takes the entry's Ultracode, because target resolution passes only model and effort), `mcp/toolkits/project/handlers.ts`. `routeUnnamedLaunch` gets `rowUltracode: false` for routines.
4. Web: `TrackUltracodeToggle` in `ModelTracksSettings.tsx` rows (icon only below the `sm` width, so a phone-width row keeps the model's name); `ProjectModelsPopover.tsx` gets a read-only Tracks form, fed from `ProjectWorkspaceSurface.tsx`.
5. Docs: `docs/studio/claude-workflows.md`.

Rejected:

- Building 1295's `claudeUltracodeDefault` here. It changes what every Claude thread costs without a choice per model, and brings a usage pause, a notice and a chat-kind rule. The owner asked for a way to set it on Tracks; a row switch is that, and it is opt-in. 1295 stays open for the project-wide default.
- One Ultracode switch per track or per project. Entries of a track are different models, and several cannot run it; a row switch shows exactly where it applies and matches the per-row effort.
- Making the popover's button write the first Daily row. The popover edits one model; on Tracks there are two lists, and a second editor for them would drift from Project settings.

1295 rejected stamping `ultracode: true` into a new thread's selection for a default nobody chose. Here the person chose it for that model on that track, and One model mode already stamps the project's model the same way, so the known costs are the same as today: the option stays on the thread after the row is turned off, and a fallback to a model without Ultracode names it as dropped.

Risks: a worker delegated by a thread that runs Ultracode inherits its parent's options, as today. A thread that falls back along its track keeps its own options and does not take the next row's switch.

## Decisions

### Asked
- none (the task said to decide the scope and record it)

### Defaulted (change any before sw-do)
- D-01 Where the choice lives → per track row, in the entry's options beside its effort, on Daily and Complex. Alternative: one project switch (1295), left to 1295 (reversible).
- D-02 Off means not set → the row stores `ultracode: true` or nothing, never `false`, so a thread from an off row still follows the Claude workflow mode, as every thread did before (reversible).
- D-03 Review track → no switch. A review launch takes only the model and effort from its row, and a review is a read of finished work, not a build (reversible).
- D-04 Routines → a routine's own thread never takes a row's Ultracode: it runs unattended and repeatedly, which 1295 D-02 also kept off. A routine that should run it can pin a model with the option (reversible).
- D-05 Who wins → an `ultracode` value the launch names, or one the launch's selection already carries (inherited from the thread that delegates), beats the row. The row only fills an unset option (reversible).
- D-06 Models popover on Tracks → read-only "New threads" row with a link to Project settings; the saved project model is left as it is and applies again if the project goes back to One model (reversible).
- D-07 Limit fallback → unchanged: a thread that moves down its track keeps its own options (reversible).
- D-08 Unpicked draft → a composer draft nobody picked a model or options for carries the first Daily row's options, so its Ultracode is that row's: when the task is routed to another row of the same model (Complex), that row decides. A trait edit in the composer marks the draft as picked and is kept (review finding, reversible).
- D-09 Fitted entries → an entry that launches on another release or source than the one it was saved for keeps its Ultracode only where that model lists the switch (review finding, reversible).

### Open
- none

## Tasks

### T-01 Shared: the option on a track entry and the launch rule
- AC: AC-02, AC-04, AC-05, AC-06 | Files: repositories/anton-abyzov/specwithcode/packages/shared/src/modelTracks.ts, repositories/anton-abyzov/specwithcode/packages/shared/src/modelTracks.test.ts, repositories/anton-abyzov/specwithcode/packages/shared/src/modelLanes.ts, repositories/anton-abyzov/specwithcode/packages/shared/src/modelLanes.test.ts | Test: cd repositories/anton-abyzov/specwithcode/packages/shared && ../../node_modules/.bin/vp test run src/modelTracks.test.ts src/modelLanes.test.ts

### T-02 Server: every track launch takes the row's Ultracode
- AC: AC-04, AC-05, AC-06, AC-07 | Files: repositories/anton-abyzov/specwithcode/apps/server/src/project/TracksLaunch.ts, repositories/anton-abyzov/specwithcode/apps/server/src/project/TracksLaunch.test.ts, repositories/anton-abyzov/specwithcode/apps/server/src/mcp/OrchestratorMcpService.ts, repositories/anton-abyzov/specwithcode/apps/server/src/mcp/toolkits/project/handlers.ts, repositories/anton-abyzov/specwithcode/apps/server/src/mcp/toolkits/project/remoteLaunchModel.ts, repositories/anton-abyzov/specwithcode/apps/server/src/ws.ts, repositories/anton-abyzov/specwithcode/apps/server/src/scheduledTasks/ScheduledTaskService.ts | Test: cd repositories/anton-abyzov/specwithcode/apps/server && ../../node_modules/.bin/vp test run src/project/TracksLaunch.test.ts src/project/TaskRouting.test.ts src/project/TaskRouting.startEffort.test.ts

### T-03 Web: the switch on track rows
- AC: AC-01, AC-02, AC-03, AC-09 | Files: repositories/anton-abyzov/specwithcode/apps/web/src/components/settings/ModelTracksSettings.tsx, repositories/anton-abyzov/specwithcode/apps/web/src/components/settings/ModelTracksSettings.effort.test.tsx, repositories/anton-abyzov/specwithcode/apps/web/tests/model-tracks/main.tsx, repositories/anton-abyzov/specwithcode/apps/web/tests/model-tracks/verify.mjs | Test: cd repositories/anton-abyzov/specwithcode/apps/web && ../../node_modules/.bin/vp test run src/components/settings/ModelTracksSettings.effort.test.tsx

### T-04 Web: the Models popover on a Tracks project
- AC: AC-08 | Files: repositories/anton-abyzov/specwithcode/apps/web/src/components/studio/shell/ProjectModelsPopover.tsx, repositories/anton-abyzov/specwithcode/apps/web/src/components/studio/shell/ProjectModelsPopover.test.tsx, repositories/anton-abyzov/specwithcode/apps/web/src/components/studio/ProjectWorkspaceSurface.tsx | Test: cd repositories/anton-abyzov/specwithcode/apps/web && ../../node_modules/.bin/vp test run src/components/studio/shell/ProjectModelsPopover.test.tsx

### T-05 Docs
- AC: AC-01 | Files: repositories/anton-abyzov/specwithcode/docs/studio/claude-workflows.md | Test: cd repositories/anton-abyzov/specwithcode && grep -q "track row" docs/studio/claude-workflows.md

### T-06 Review, merge, release and close 1441
- AC: AC-01, AC-02, AC-03, AC-04, AC-05, AC-06, AC-07, AC-08, AC-09 | Files: none | Test: specweave verify 1441-ultracode-on-model-track-rows-so-threads-started-on-a-track-run-with-it
