# Agents ask before changing a project's model, and a model switch keeps effort and Ultracode

## Problem

Anton (November 18, 2026): "I think it was reset somehow. I used to have it as Fable, but with UltraCode, for some reason, it got reset. Check, maybe when we update the application, it gets reset. Fix it."

His screenshot of Project settings > General for the specweave project showed the coordinator model and the model for threads both on Claude Opus 5.5 (High, 1M, Thinking on) and Ultracode "Not set". He had saved Fable 5.2 with Ultracode on.

What the state database shows for project `1332065e-795b-4f98-91c4-f114917e53f6` (read with `specweave-studio db query` from `orchestration_events`, times in UTC):

- No update, migration, startup pass or sync from another machine changed a model anyone had chosen. The startup pass `project-coordinator-options:v1` only adds Medium effort and Thinking to a coordinator model that has no options.
- Model for threads: Fable 5.2, 1M, High, Ultracode on, Thinking on from November 11, 14:53:45 (rev 41), saved again November 15, 00:01:44 (rev 45).
- November 17, 11:58:52 (sequence 4598245, command `mcp:d27cce69-dd85-4169-b969-fdde63a50b9e`): the worker thread "Rethink model tracks and usage" called `studio_project_update` with Opus 5.5, High, Thinking. The coordinator had told it to, reading Anton's message "main is still opus 5.5!". The write dropped Ultracode and the 1M context window. Nothing showed Anton that a saved setting had changed.
- The same kind of write happened before: sequence 1400486 on October 22, 12:44:11, and 24 agent writes to project models across projects since October 20.
- November 18, 08:21:58 (rev 47): Anton saved Fable 5.2, 1M, Medium, Ultracode on, Thinking on from the settings dialog. Effort came out Medium, not the High he had before.

Two causes in code:

1. `studio_project_update` (`apps/server/src/mcp/toolkits/project/handlers.ts`) lets any agent replace the model the person saved for new threads (`defaultModelSelection`) or for the coordinator (`workspaceSettings.coordinatorModelSelection`). The same handler already refuses project instructions, pause, archive, folders and repositories as the user's to change.
2. The project model pickers start a newly picked model with no options: `createModelSelection(id, model)` in `apps/web/src/components/studio/ProjectModels.tsx`, `apps/web/src/components/studio/shell/ProjectModelsPopover.tsx` and `apps/web/src/components/studio/shell/CoordinatorModelPicker.tsx`. Picking another model silently drops effort, Ultracode, context window and Fast mode. On November 10, 23:30:13 (rev 35 to 36) switching the threads model from Opus 5.5 to Fable 5.2 dropped Ultracode this way. Settings > Defaults already keeps them with `carryModelOptions` (`packages/shared/src/modelOptionCarry.ts`).

## Scope

In:

- An agent can no longer replace a saved project model through `studio_project_update`. It asks with `studio_project_request` action `change_model`, and the user approves a card that names the current and the new model with their options.
- The project pickers for the threads model and the coordinator model keep effort, Ultracode, context window, Thinking and Fast mode across a model change where the new model offers them, and say what was left off.

Out:

- Changing the specweave project's saved models. They are Anton's.
- `apps/web/src/hooks/useProjectCoordinatorHandoff.ts`: continuing a thread on another machine saves that continuation's model as the destination project's coordinator model. Reported, not changed here.
- Which model is the project's main one (project memory `decision_model_tracks.md` says Opus 5.5; Anton just saved Fable 5.2). His call.
- Thread-level model switches (`studio_thread_configure`), model lanes, tracks and fallback.

## Acceptance Criteria

- [ ] AC-01: `studio_project_update` refuses a `defaultModelSelection` that differs from a saved one, and a `workspaceSettings.coordinatorModelSelection` that differs from a saved one, including clearing either. The refusal names `studio_project_request` with action `change_model`, and nothing is written.
- [ ] AC-02: `studio_project_update` still sets either model when none is saved, accepts a value identical to the saved one, and still applies other fields (goal, icon, title).
- [ ] AC-03: `studio_project_request` with action `change_model`, a `role` (`threads` or `coordinator`) and a `modelSelection` shows an approval card that names the project, the role, the current model and the new model, each with its options (effort, Ultracode, context window, Thinking, Fast mode), and lists the options the new choice leaves off.
- [ ] AC-04: Approving the card saves exactly the selection the card named; declining changes nothing. If the saved model changed after the card was shown, approval changes nothing and says so.
- [ ] AC-05: A `change_model` request is refused before any card when the selection equals the saved one, or names a provider or model this machine does not list.
- [ ] AC-06: Picking another model in the project's threads-model picker (Project settings and the Models popover) and in the coordinator picker keeps the options the new model offers (Ultracode on, effort, 1M context, Thinking, Fast mode) and reports the ones it does not.
- [ ] AC-07: The tool descriptions for `studio_project_update` and `studio_project_request`, and the owner table in `docs/internals/agent-instructions.md`, say that a project's saved models are the user's to change and how an agent asks.
- [ ] AC-08: An adversarial review by `muse-wonder-full-1.0` at xhigh effort in full-access mode ends in SHIP, or every blocker is fixed and rechecked; then the PR merges on green CI and a release is requested through `request-release.sh`.

## Approach

1. `apps/server/src/project/ProjectActionRequests.ts`: add `change_model` to `ProjectAction`; the input and the stored params carry `role`, `modelSelection` and the model saved when the card was shown. `describe` builds the card text from a pure helper; `apply` re-reads the project, refuses when the saved model no longer equals the one the card named, then writes through `projects.update` (the coordinator write is revision-checked).
2. New `apps/server/src/project/projectModelChange.ts`: pure helpers `sameModelSelection`, `describeModelSelection` (model name and option labels from the provider catalog when listed, ids otherwise) and `modelChangeCardText`. No services, so they are unit tested directly.
3. `apps/server/src/mcp/toolkits/project/handlers.ts`: `studio_project_update` reads the project and refuses a differing saved model for both fields; `requestProjectAction` passes `role` and `modelSelection` and checks the selection against the provider registry and the caller's work grant. `tools.ts`: parameters and descriptions.
4. Web: one helper `carriedProjectModelSelection` (new `apps/web/src/components/studio/projectModelCarry.ts`) wraps `carryModelOptions` with the provider catalog; `ProjectModels.tsx`, `ProjectModelsPopover.tsx` and `CoordinatorModelPicker.tsx` call it in place of the bare `createModelSelection(id, model)`, and show the "left off" sentence from `describeCarriedOptions` as a toast.
5. Docs: `docs/internals/agent-instructions.md` owner table.

Rejected:

- Keeping the direct write and only carrying the person's options into the agent's selection: the model would still change with nothing shown.
- A notice after the fact in project settings: it needs a new stored field and UI, and the change has already happened.
- A startup check that restores the last model the person saved: an approved agent change is legitimate, so the event log cannot tell which to restore without the card.

Risks:

- Coordinators set project models on the user's spoken request today (24 writes). They now need one Approve click. The refusal text tells the agent exactly what to call.
- The card appears in the asking thread; a worker's card is surfaced by the existing "needs your input" count.

## Decisions

### Asked
- none

### Defaulted (change any before sw-do)
- D-01 Agent changes to a saved project model need the user's approval card, not a silent write → yes. It matches instructions, folders and archive, which the same tool already refuses.
- D-02 Setting a model where none is saved stays direct → yes. Project creation by an agent depends on it, and nothing of the person's is replaced.
- D-03 Clearing a saved model is the user's, in project settings; `change_model` always names a model → yes.
- D-04 The coordinator picker carries options too, replacing "Effort and other traits belong to the model they were chosen for" → yes. The run-time cap at High still applies.

### Open
- D-05 Which model is the specweave project's main one: Opus 5.5 (memory `decision_model_tracks.md`, Anton on November 17) or Fable 5.2 with Ultracode (Anton's save on November 18). Asked in the final report; does not block the code.

## Tasks

### T-01 Card text and comparison helpers for a model change
- AC: AC-03 | Files: repositories/anton-abyzov/specwithcode/apps/server/src/project/projectModelChange.ts, repositories/anton-abyzov/specwithcode/apps/server/src/project/projectModelChange.test.ts | Test: cd repositories/anton-abyzov/specwithcode/apps/server && node ../../node_modules/vite-plus/bin/vp test run src/project/projectModelChange.test.ts

### T-02 change_model approval request
- AC: AC-03, AC-04, AC-05 | Files: repositories/anton-abyzov/specwithcode/apps/server/src/project/ProjectActionRequests.ts, repositories/anton-abyzov/specwithcode/apps/server/src/project/ProjectActionRequests.test.ts | Test: cd repositories/anton-abyzov/specwithcode/apps/server && node ../../node_modules/vite-plus/bin/vp test run src/project/ProjectActionRequests.test.ts

### T-03 studio_project_update refuses replacing a saved model
- AC: AC-01, AC-02, AC-05, AC-07 | Files: repositories/anton-abyzov/specwithcode/apps/server/src/mcp/toolkits/project/handlers.ts, repositories/anton-abyzov/specwithcode/apps/server/src/mcp/toolkits/project/tools.ts, repositories/anton-abyzov/specwithcode/apps/server/src/mcp/toolkits/project/handlers.projectModels.test.ts, repositories/anton-abyzov/specwithcode/docs/internals/agent-instructions.md | Test: cd repositories/anton-abyzov/specwithcode/apps/server && node ../../node_modules/vite-plus/bin/vp test run src/mcp/toolkits/project/handlers.projectModels.test.ts

### T-04 Project pickers keep options across a model change
- AC: AC-06 | Files: repositories/anton-abyzov/specwithcode/apps/web/src/components/studio/projectModelCarry.ts, repositories/anton-abyzov/specwithcode/apps/web/src/components/studio/projectModelCarry.test.ts, repositories/anton-abyzov/specwithcode/apps/web/src/components/studio/ProjectModels.tsx, repositories/anton-abyzov/specwithcode/apps/web/src/components/studio/shell/ProjectModelsPopover.tsx, repositories/anton-abyzov/specwithcode/apps/web/src/components/studio/shell/CoordinatorModelPicker.tsx | Test: cd repositories/anton-abyzov/specwithcode/apps/web && node ../../node_modules/vite-plus/bin/vp test run --project unit src/components/studio/projectModelCarry.test.ts src/components/studio/shell/CoordinatorModelPicker.test.tsx src/components/studio/shell/ProjectModelsPopover.test.tsx

### T-05 Review, merge, release, verify and close
- AC: AC-08 | Files: .specweave/increments/1405-agents-ask-before-changing-a-projects-model-and-a-model-switch-keeps-effort-and-ultracode/reports/ | Test: gh pr view --repo anton-abyzov/specwithcode --json state,mergedAt
