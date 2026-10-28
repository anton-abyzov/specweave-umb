# Simplify handoff mode settings

## Problem

Settings > Machines > Handoff mode was audited end to end on 2026-10-28 (seven code traces, each defect adversarially verified; live M4 snapshot over RPC). Findings:
- "Continue automatically when a machine stops answering" is saved but never read: no automatic takeover exists (only reference handoffState.ts applyConfigPatch).
- The per-project list lists automated and archived projects, edits only the primary machine's local project ids, and reads as per-project. Nobody uses it: the M4 has no handoff-mode.json at all (0 threads, 0 overrides).
- "Push checkpoints to origin" is on by default, pushes uncommitted and untracked files to GitHub, runs inside the thread lock (up to 60 s per checkpoint, delaying Move and sleep), and is never read by any move. A thread with no replicas showed "Ready to move" because of it.
- "Keep new threads ready to move" also applies to existing threads.
- The sleep target list hides offline machines' state, and the row does not say only ready-to-move threads move.

## Scope

In: the settings section, a project-level row, the origin-push default and lock, the badge, project-id validation. Out: implementing auto-takeover, the self-fence, grant enforcement on takeover, and note generation (reported as follow-ups).

## Acceptance Criteria

- [ ] AC-01: Settings > Machines shows one machine default ("Keep threads ready to move", worded for existing threads too), the sleep target with offline machines marked, and More options; no project list, no automated or archived groups, no auto-continue row. Stored project overrides show as a short list with "Use default".
- [ ] AC-02: Settings > Project has "Keep this project's threads ready to move" (Default/On/Off, Mixed when copies disagree), written to every machine that has a copy.
- [ ] AC-03: The origin backup is off by default, runs outside the thread lock, is skipped for moves and sleep, and no longer makes a thread read "Ready to move"; setProjectMode refuses a project that is not on the machine.

## Approach

Keep effectiveHandoffMode and the stored projectModes unchanged, so nothing migrates. The project row calls setProjectMode once per member machine with that machine's own project id. useHandoffModeSnapshots polls several machines at once. The push is forked with Effect.forkDetach after the checkpoint is saved and marks pushedToOrigin when it lands.

## Decisions

### Defaulted
- D-01 Hide the auto-continue row until a takeover loop exists → default
- D-02 Origin backup default off → default (it pushes uncommitted files and nothing reads it)

## Tasks

### T-01 Machine settings without the project list
- AC: AC-01 | Files: repositories/anton-abyzov/specweave-studio/apps/web/src/components/settings/HandoffModeSettings.tsx, repositories/anton-abyzov/specweave-studio/apps/web/src/components/settings/HandoffModeSettings.test.tsx, repositories/anton-abyzov/specweave-studio/apps/web/tests/handoff-mode/verify.mjs | Test: cd ~/.specwithcode/m4/worktrees/specweave-studio/handoff-settings/apps/web && PATH=$HOME/.nvm/versions/node/v22.20.0/bin:$PATH node ../../node_modules/vite-plus/bin/vp test run --project unit src/components/settings/HandoffModeSettings.test.tsx

### T-02 Project-level ready-to-move row
- AC: AC-02 | Files: repositories/anton-abyzov/specweave-studio/apps/web/src/components/settings/ProjectHandoffModeSettings.tsx, repositories/anton-abyzov/specweave-studio/apps/web/src/components/settings/ProjectSettingsPanel.tsx, repositories/anton-abyzov/specweave-studio/apps/web/src/studio/handoffMode.ts | Test: cd ~/.specwithcode/m4/worktrees/specweave-studio/handoff-settings/apps/web && PATH=$HOME/.nvm/versions/node/v22.20.0/bin:$PATH node ../../node_modules/vite-plus/bin/vp test run --project unit src/components/settings/ProjectHandoffModeSettings.test.tsx src/components/settings/ProjectSettingsPanel.test.tsx

### T-03 Safe origin backup and honest badge
- AC: AC-03 | Files: repositories/anton-abyzov/specweave-studio/apps/server/src/handoff/HandoffMode.ts, repositories/anton-abyzov/specweave-studio/apps/server/src/handoff/handoffState.ts, repositories/anton-abyzov/specweave-studio/packages/contracts/src/handoffMode.ts | Test: cd ~/.specwithcode/m4/worktrees/specweave-studio/handoff-settings/apps/server && PATH=$HOME/.nvm/versions/node/v22.20.0/bin:$PATH node ../../node_modules/vite-plus/bin/vp test run src/handoff

### T-04 Verify and close 1121
- AC: AC-01, AC-02, AC-03 | Files: none | Test: cd ~/.specwithcode/m4/worktrees/specweave-studio/handoff-settings && PATH=$HOME/.nvm/versions/node/v22.20.0/bin:$PATH node node_modules/vite-plus/bin/vp run @specweave-studio/web#typecheck
