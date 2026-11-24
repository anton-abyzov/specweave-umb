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

## Follow-ups

Found by the closing review (GPT-6.1 Sol on Copilot Enterprise, November 19, 2026) on app `f08a5830b`; Anton chose to close 1185 (T-02 dropped, AC-01 test skipped), so these are recorded, not fixed here.

- Gap in AC 01, budget: `ProjectLink.readContent` (`apps/server/src/project/ProjectLink.ts:461-468`) calls `readWorkspace` and then `readMemoryFiles`, so it issues 2 project reads and 2 memory queries, and a digest cache miss 3 and 3. Constant in the note count (the per-note loop is gone), but not the one-and-one the AC names.
- Gap in AC 02, race (medium): `contentDigest` (`ProjectLink.ts:490-500`) keys the cache on one `readWorkspace` snapshot and hashes a second one from `readContent`. A goal or instructions edit that is reverted between the two reads stores a digest under a signature it does not match, and it stays until the next signature change or a restart. Fix: hash and key one snapshot.
- Later regression (medium): `readWorkspace` now awaits `specweaveFactsOf` (`ProjectWorkspaceService.ts:342-346`, from `ce517249a`) with no timeout, so a slow setup-file write for one project delays digest reads for every linked project.
- Low: the revision-keyed hash caches in `LinkedMemorySync.ts` and `ProjectLink.ts` never drop deleted notes or projects; they grow with names seen since start.

## Tasks

### T-01 Batch linked memory reads
- AC: AC-01, AC-02, AC-03 | Files: [apps/server/src/project/ProjectWorkspaceService.ts, repositories/anton-abyzov/specwithcode/apps/server/src/project/ProjectLink.ts, repositories/anton-abyzov/specwithcode/apps/server/src/project/LinkedMemorySync.ts] | Test: pnpm exec vitest run apps/server/src/project

### T-02 Bound confirmed polling and sweep load
- AC: AC-04 | Files: [apps/server/src/orchestration-v2/ThreadSettlementService.ts, repositories/anton-abyzov/specwithcode/apps/server/src/mods/SpecweaveProgress.ts, repositories/anton-abyzov/specwithcode/apps/web/src/studio/fleet.ts] | Test: pnpm exec vitest run on the changed files

### T-03 Ship through required checks
- AC: AC-05 | Files: [none] | Test: gh pr checks --required

### T-04 Verify and close 1185
- AC: AC-05 | Files: [none] | Test: specweave verify 1185
