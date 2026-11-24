# Thread plan cards read umbrella increments

## Problem

The SpecWeave project in SpecWithCode is a member repository (`specweave-umb/repositories/anton-abyzov/specweave`) with no `.specweave` of its own. The CLI walks up and writes increments and thread bindings to the umbrella (`specweave-umb`), but the app's reader only accepted roots inside the project folder or worktree. Live receipt on October 20, 2026: 0 of 21 umbrella-rooted thread bindings resolved and the Link increment picker listed 0 increments, so every thread in the project showed no plan card.

## Scope

In: increment root resolution in `apps/server/src/project/ThreadIncrementProgress.ts` (claim acceptance, branch/name fallback, Link picker), regression tests, design doc. Out: thread report folders in `ThreadReports.ts` (workspace-relative paths; widening them changes file-viewer access), the CLI rebinding a thread on `note` events.

## Acceptance Criteria

- [ ] AC-01: A thread in a member repository binds to an increment its claim file records in the umbrella root, with tasks and ACs folded from the umbrella ledger
- [ ] AC-02: A claim naming a sibling repository's `.specweave` under the same umbrella is refused
- [ ] AC-03: Branch binding and the Link picker read the umbrella's increments, also from a worktree outside the umbrella
- [ ] AC-04: An ancestor `.specweave` without `config.json` is not used
- [ ] AC-05: Against the real binding files, the fixed reader resolves the umbrella bindings the old one dropped

## Approach

`planningRootAbove(folder)` walks up to the nearest ancestor with `.specweave/config.json` and `.specweave/increments`, mirroring the CLI's `findProjectRoot`. `incrementRootFor` tries worktree, project, then that planning root. `claimedBinding` also accepts a root that equals (not merely lies under) the planning root. PR anton-abyzov/specwithcode-dev branch `fix/increment-umbrella-root`.

## Decisions

### Asked
- none
### Defaulted (change any before sw-do)
- D-01 Accept only the exact planning root, not any folder under the umbrella (narrowest change that fixes the bug)
### Open
- none

## Tasks

### T-01 Resolve the umbrella planning root in the reader
- AC: AC-01, AC-02, AC-03, AC-04 | Files: apps/server/src/project/ThreadIncrementProgress.ts, apps/server/src/project/ThreadIncrementProgress.test.ts, docs/studio/plan-progress.md | Test: node node_modules/vite-plus/bin/vp test run apps/server/src/project/ThreadIncrementProgress.test.ts

### T-02 Live before/after receipt against real bindings
- AC: AC-05 | Files: ~/Projects/github/studio-research-notes/increment-links-2026-10-20/live-before.json, live-after.json | Test: node --experimental-strip-types /tmp/iur-live.mts <reader>
