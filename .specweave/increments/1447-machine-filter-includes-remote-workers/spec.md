# Machine filter includes remote workers

## Problem

When an unlinked project on one machine (such as EasyChamp on `m1`) has active remote workers running on another machine (such as `m4`), the Threads pane renders the remote worker cards above the thread groups and shows the machine column on every thread row (`multiMachine` checks `Boolean(props.remoteWorkerCount)`), and `RemoteWorkerCards` already accepts `machineFilter`. However, the by-machine filter bar is hidden because `ThreadsPane` builds `machineOptions` and `threadFacts` exclusively from `allThreads`. Since `allThreads` only contains the local machine's threads, `machineOptions.length` is `1` and `machineRow.length > 1` evaluates to `false`.

## Scope

In:
- Include visible unrepresented remote workers (from `visibleRemoteWorkers(remoteWorkers, representedThreads)`) in `ThreadsPane` machine filter options, open counts, waiting indicators, and empty-state suppression when filtering to a machine that only has remote worker cards.
- Pass the visible unrepresented remote workers from `ProjectWorkspaceSurface` to `ThreadsPane`.
- Unit tests covering machine filter options, counts, waiting indicators, and empty-state suppression with remote workers.
- Headless screenshot verifying the machine filter bar rendered with local threads + remote worker cards.

Out:
- Changing project linking semantics or merging unlinked projects' full thread histories.
- Adding agent or pull-request metadata to remote worker cards.

## Acceptance Criteria

- [ ] AC-01: When a project's `allThreads` belong to one machine and it has active unrepresented remote workers on another machine, the Threads pane displays the machine filter bar listing `All` and every machine (both thread machines and remote worker machines) with accurate open counts.
- [ ] AC-02: Selecting a machine that only has active remote worker cards filters the thread list to that machine (showing only that machine's remote worker cards via `renderNotice`) and does not show the "No thread matches these filters." empty state while at least one remote worker card matches the active machine filter.
- [ ] AC-03: Selecting a different machine while a remote worker on another machine has `waiting` status displays the waiting indicator dot on that remote worker's machine chip, and remote workers already represented in `allThreads` (linked projects) are not double-counted.
- [ ] AC-04: Unit tests in `apps/web/src/components/studio/shell/ThreadsPane.test.tsx` and `apps/web/src/studio/threadMachineFilter.test.ts` pass, typecheck passes, and a headless screenshot of the rendered Threads pane with the machine filter bar is saved under this increment's `reports/` folder.

## Approach

1. `repositories/anton-abyzov/specwithcode/apps/web/src/studio/threadMachineFilter.ts`: Extend or add a helper (or accept additional machine items) so `machineFilterOptions` cleanly merges thread machines and active remote worker machines without duplicating machine entries.
2. `repositories/anton-abyzov/specwithcode/apps/web/src/components/studio/shell/ThreadsPane.tsx`:
   - Accept optional `remoteWorkers?: readonly StudioFleetRemoteWorker[]` prop (keeping `remoteWorkerCount` for backwards compatibility / falling back to `remoteWorkers.length`).
   - Include `remoteWorkers` (deduplicated against `allThreads` by `environmentId` + `remoteThreadId`) when building `machineOptions`, `allFacts` (with `agent: ""`, `openPullRequest: false`, `open: true`), and `machinesWaiting` (for remote workers whose `remoteWorkerCardStatus(worker).tone === "waiting"`).
   - Suppress the "No thread matches these filters." empty state when `!searching && activeMenuFilters === 0` and at least one remote worker matches `machineFilter`.
3. `repositories/anton-abyzov/specwithcode/apps/web/src/components/studio/ProjectWorkspaceSurface.tsx`:
   - Memoize `representedThreads` (`projectAttention.roots.map((root) => root.thread)`) and `unrepresentedRemoteWorkers = visibleRemoteWorkers(remoteWorkers, representedThreads)`.
   - Pass `remoteWorkers={unrepresentedRemoteWorkers}` and `remoteWorkerCount={unrepresentedRemoteWorkers.length}` to `ThreadsPane`.
4. Tests & visual verification:
   - Add unit tests in `apps/web/src/studio/threadMachineFilter.test.ts` and `apps/web/src/components/studio/shell/ThreadsPane.test.tsx`.
   - Capture a headless Playwright/Vitest/HTML screenshot showing the EasyChamp-style Threads pane with `m4` remote workers + `m1` threads and the machine filter bar (`All`, `m4 2`, `m1 6`), saved to `.specweave/increments/1447-machine-filter-includes-remote-workers/reports/machine-filter-remote-workers.png`.

## Decisions

### Asked
- none
### Defaulted (change any before sw-do)
- D-01 Show machine filter for unlinked projects with active remote workers → Yes, include active unrepresented remote workers in the machine filter bar rather than adding an explanatory note, because `ThreadsPane` already shows the machine column and `RemoteWorkerCards` already filters by `machineFilter` (reduces confusion and matches user expectation).
### Open
- none

## Tasks

### T-01 Include remote workers in ThreadsPane machine filter
- AC: AC-01, AC-02, AC-03 | Files: [repositories/anton-abyzov/specwithcode/apps/web/src/studio/threadMachineFilter.ts, repositories/anton-abyzov/specwithcode/apps/web/src/components/studio/shell/ThreadsPane.tsx, repositories/anton-abyzov/specwithcode/apps/web/src/components/studio/ProjectWorkspaceSurface.tsx] | Test: pnpm --dir repositories/anton-abyzov/specwithcode/apps/web test -- src/studio/threadMachineFilter.test.ts src/components/studio/shell/ThreadsPane.test.tsx

### T-02 Add unit tests and visual verification screenshot
- AC: AC-01, AC-02, AC-03, AC-04 | Files: [repositories/anton-abyzov/specwithcode/apps/web/src/studio/threadMachineFilter.test.ts, repositories/anton-abyzov/specwithcode/apps/web/src/components/studio/shell/ThreadsPane.test.tsx, .specweave/increments/1447-machine-filter-includes-remote-workers/reports/machine-filter-remote-workers.png] | Test: pnpm --dir repositories/anton-abyzov/specwithcode/apps/web test -- src/studio/threadMachineFilter.test.ts src/studio/threadPaneFilters.test.ts src/components/studio/shell/ThreadsPane.test.tsx

