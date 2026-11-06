# Service request path stays responsive under load

## Problem

On M4 (service 1.0.152, November 2, 2026) the app showed "9 requests waiting longer than 15s" and "Attention unavailable". A 45s CPU profile of the service showed its single event loop only 5.6% idle: 32% synchronous SQLite, 16% child process spawn.

Over 6 minutes of traces the largest SQL traffic was linked memory sync. `projectLink.digest` and `projectLink.memoryExport` ran 63 times and issued 11,229 of 12,908 per-note reads plus 11,292 of 16,263 project reads, because `ProjectLink.readContent` and `LinkedMemorySync.readLocal` read each note separately (556 and 812 notes) and each read re-fetches the project. The settlement sweep added 2,086 project reads.

Machine load was also high (load average 293, a MatchCam GPU bench, tsc, ffmpeg), which slows every spawn but does not explain the SQL traffic.

Evidence: `/Users/antonabyzov/Projects/github/specweave-umb/repositories/anton-abyzov/specweave/.specweave/hang-evidence-20261102-175829`.

## Scope

In: linked memory sync reads, repeat hashing, per-thread project reads in sweeps, and hot polling found by the request-path review. Out: moving SQLite off the main thread, shrinking the 21 GB database, MatchCam workloads.

## Acceptance Criteria

- [ ] AC-01: Reading a project's linked memory content issues one memory query and one project read, whatever the note count; a test with many notes asserts the statement count.
- [ ] AC-02: A digest for unchanged notes returns the same value as a full recomputation and changes when a note, goal or instructions change.
- [ ] AC-03: Exports stay byte-identical in content, hash, paging and tombstones to the previous behaviour; existing linked memory tests pass.
- [ ] AC-04: Hot polling and sweep findings confirmed by the review are bounded, each with a test.
- [ ] AC-05: Typecheck, lint and affected server and web tests pass, and required CI checks are green before merge.

## Approach

`ProjectWorkspaceService` gains a batch read of all memory content for one project. `ProjectLink.readContent` and `LinkedMemorySync.readLocal` use it. Hashes are remembered by project, name and revision, since every write bumps the revision. Other fixes follow the review reports.

Rejected: moving SQLite to a worker (too large for an urgent fix), slowing the sync interval alone (leaves the cost per pass).

## Decisions

### Asked
- none
### Defaulted (change any before sw-do)
- D-01 Restart only if evidence shows wedged state rather than sustained load → default (reversible).
### Open
- none

## Tasks

### T-01 Batch linked memory reads
- AC: AC-01, AC-02, AC-03 | Files: [apps/server/src/project/ProjectWorkspaceService.ts, repositories/anton-abyzov/specwithcode-dev/apps/server/src/project/ProjectLink.ts, repositories/anton-abyzov/specwithcode-dev/apps/server/src/project/LinkedMemorySync.ts] | Test: pnpm exec vitest run apps/server/src/project

### T-02 Bound confirmed polling and sweep load
- AC: AC-04 | Files: [apps/server/src/orchestration-v2/ThreadSettlementService.ts, repositories/anton-abyzov/specwithcode-dev/apps/server/src/mods/SpecweaveProgress.ts, repositories/anton-abyzov/specwithcode-dev/apps/web/src/studio/fleet.ts] | Test: pnpm exec vitest run on the changed files

### T-03 Ship through required checks
- AC: AC-05 | Files: [none] | Test: gh pr checks --required

### T-04 Verify and close 1185
- AC: AC-05 | Files: [none] | Test: specweave verify 1185
