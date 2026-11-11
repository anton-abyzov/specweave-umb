# Thread plan follows its increment outside the project folder and on other machines

## Problem

Anton, November 11, 2026, with a screenshot of the thread "Build SpecOS on Linux" (project specos, running on the Minisforum, shown as linux-mini): "I don't see a plan, though it seems like it should be available." The agent reports "12 of 26 tasks are done and committed in spec-os" while the plan card says "No plan. No SpecWeave increment and no checklist from the agent yet."

What happened, from the two transcripts (read only):

- The coordinator launched the thread with `increment: "new"` and told it to work in `~/live/spec-os`. Nothing was lost at launch: "new" names no increment, so there was nothing to seed.
- The agent ran `git init` and `specweave init` in `/home/anton/live/spec-os`, then `specweave create-increment`, which made `0001-specos-browser-desktop-for-ai-agent-work` there. The project's folder on that machine is `/home/anton/Projects/github/specos`; the thread has no worktree.
- `specweave task done T-01` and the later ledger writes ran in the thread's turns, so SpecWeave wrote the thread's claim file with root `/home/anton/live/spec-os`.
- The plan reader (`claimedBinding` in `apps/server/src/project/ThreadIncrementProgress.ts`) accepts a claim only when its root is inside the project folder or the thread's worktree, is the umbrella above them, or is another checkout Git registered for the same repository. A new repository elsewhere is none of these, so the claim is dropped, the project folder has no `.specweave`, and the read returns nothing.

Three more gaps on the same path:

- **Link increment** cannot fix it by hand: the picker lists only the increments of the thread's checkout (none here) and the link is refused for a folder outside the project.
- An increment the agent creates mid-run is invisible until its first ledger write, and never appears for providers that do not get the thread id (Cursor, OpenCode 2), because binding needs the claim file.
- The project's Threads pane reads increment progress only for threads of its own machine, so a thread on another machine shows at most the agent's checklist there.

Not a cause: the read already runs on the thread's own machine with that machine's ids, and tasks finished by a background Workflow's agents are ordinary ledger lines, read on the next poll once the thread is bound.

## Scope

In: the server reader and service (`ThreadIncrementProgress.ts`, `ThreadIncrementProgressService.ts`), the Threads pane, the plan-progress doc and changelog. Out: a new binding literal or any contract change (a newer server must stay readable by an older app on another machine); showing Workflow progress as plan steps; the SpecWeave CLI; the SpecOS thread itself (it picks the fix up when the Minisforum updates).

## Acceptance Criteria

- [ ] AC-01: A thread whose claim file names a root outside its project shows that increment, bound as "claim", when the thread's own recorded file changes lie inside that root.
- [ ] AC-02: A claim file naming a root where the thread changed nothing stays refused, so another thread or a forged file cannot aim a plan card at a foreign folder.
- [ ] AC-03: A thread that wrote `<root>/.specweave/increments/<id>/spec.md` itself is bound to that increment without a claim file, the newest such spec first, when nothing else names an increment; a hand-made link, a claim file, a branch, a checkpoint and a name binding outrank it.
- [ ] AC-04: Link increment lists the increments of the folders the thread worked in and accepts a link to one of them; a link to an increment in a folder the thread never touched is still refused.
- [ ] AC-05: The evidence comes from the server's own projection, incrementally: after the first read of a thread, a poll reads only turn items newer than the last one seen.
- [ ] AC-06: The Threads pane shows increment progress for threads on other machines, each read from its own machine.
- [ ] AC-07: The reply uses only existing binding values and fields, so an older client decodes a newer server's answer.
- [ ] AC-08: `docs/studio/plan-progress.md` and the changelog describe the new binding rules.

## Approach

1. `ThreadIncrementProgress.ts`: `ThreadIncrementSource` gains optional `evidence` (`workedIn(roots)`, `writtenSpecs()`), supplied by the service. `claimedBinding` accepts a root the old rules refuse when `workedIn` says the thread changed files there. With no manual, claim or branch binding, the newest spec the thread wrote whose increment folder exists binds it (reported as "claim", task null). `linkedIncrementRoot` and the increment list also look in the thread's evidenced roots.
2. `ThreadIncrementProgressService.ts`: evidence from `orchestration_v2_projection_turn_items` (`file_change` items of the thread and its provider-native subagents, runs not rolled back). Spec paths are found with a text prefilter and kept per thread with an ordinal watermark, the first scan bounded to the newest 1,000 file changes; `workedIn` is asked only for a claim the old rules refuse and its yes is kept.
3. Web: the Threads pane reads other machines' threads through the per-machine loader the sidebar already uses.
4. Docs and changelog.

Why evidence from the projection: the claim file sits in the user's home and any process can write it, so the old root rule is what kept a card inside its project. A thread's own turn items cannot be written by another thread, and its agent could already read whatever folder it edits, so the card shows nothing the thread could not.

Rejected: a new "authored" binding literal (an older app on another machine fails to decode the whole reply); binding in the CLI at `create-increment` (needs a CLI release and still misses Cursor and OpenCode 2); trusting any claim root (cross-project read).

Risk: a thread that edits one increment's spec in passing binds to it until a claim, branch or link says otherwise.

## Decisions

### Asked
- none
### Defaulted (change any before sw-do)
- D-01 A spec the thread wrote binds it → yes, as the last fallback: below manual, claim, branch, checkpoint and name (reversible). Moved below checkpoint and name after the round 1 SHIP review: a thread named for one increment that edits another's spec keeps its own.
- D-02 No new binding literal → reuse "claim" (skew-safe).
- D-03 Workflow progress stays out of the plan card → the ledger carries it.
- D-04 Only completed file changes are evidence; failed, cancelled and interrupted edits prove nothing. A rolled-back run's completed edits still count, because the question is whether the thread itself wrote there (round 1 review).
- D-05 Paths are compared as text after resolving `.` and `..`; relative paths, links and other spellings answer no. A relative spec path is taken from the thread's checkout.
- D-06 The Threads pane issues its own query per other machine, like both sidebars; no shared atom.

## Follow-ups

Low findings the round 3 SHIP review left open; none blocks. Details in `reports/ship.md`.

- `writtenSpecIncrements` resolves `..` in a written spec path as text; refuse such paths as `isInsideAny` does.
- Subagents are looked up one level deep; a subagent of a subagent does not count for the root thread.
- `subagentsOf` returns an empty map on a failed lookup instead of the last known one.
- `docs/studio/plan-progress.md` does not mention the first project-wide subagent listing after a server start.

## Closure

Merged as `6aa0ac06` (PR #163). `specweave verify 1303` runs the product gate in `repositories/anton-abyzov/specwithcode-dev`, which must be checked out at main `6aa0ac06` or later and free of another thread's run. On November 11, 2026 that checkout sat at `0e2f3a9034`, before the merge, with another increment's verify running, so T-06 waits for a checkout slot from the coordinator.
### Open
- none

## Tasks

### T-01 Reader: evidenced claim roots, written-spec binding, link and list roots
- AC: AC-01, AC-02, AC-03, AC-04, AC-07 | Files: repositories/anton-abyzov/specwithcode-dev/apps/server/src/project/ThreadIncrementProgress.ts, repositories/anton-abyzov/specwithcode-dev/apps/server/src/project/ThreadIncrementProgress.test.ts | Test: cd "$HOME/.specwithcode/m4/scratch/2026-11-11-plan-binding/tree/apps/server" && node ../../node_modules/vite-plus/bin/vp test run src/project/ThreadIncrementProgress.test.ts

### T-02 Service: evidence from the projection, list and link through it
- AC: AC-01, AC-02, AC-03, AC-04, AC-05 | Files: repositories/anton-abyzov/specwithcode-dev/apps/server/src/project/ThreadIncrementProgressService.ts, repositories/anton-abyzov/specwithcode-dev/apps/server/src/project/ThreadIncrementProgressService.test.ts, repositories/anton-abyzov/specwithcode-dev/apps/server/src/project/ThreadIncrementEvidence.test.ts | Test: cd "$HOME/.specwithcode/m4/scratch/2026-11-11-plan-binding/tree/apps/server" && node ../../node_modules/vite-plus/bin/vp test run src/project/ThreadIncrementProgressService.test.ts src/project/ThreadIncrementEvidence.test.ts

### T-03 Threads pane: increment progress for threads on other machines
- AC: AC-06 | Files: repositories/anton-abyzov/specwithcode-dev/apps/web/src/components/studio/shell/ThreadsPane.tsx, repositories/anton-abyzov/specwithcode-dev/apps/web/tests/thread-row-meta/incrementProgress.ts, repositories/anton-abyzov/specwithcode-dev/apps/web/tests/thread-row-meta/main.tsx, repositories/anton-abyzov/specwithcode-dev/apps/web/tests/thread-row-meta/vite.config.ts, repositories/anton-abyzov/specwithcode-dev/apps/web/tests/thread-row-meta/other-machine-plan.mjs, repositories/anton-abyzov/specwithcode-dev/apps/web/tests/thread-row-meta/README.md | Test: cd "$HOME/.specwithcode/m4/scratch/2026-11-11-plan-binding/tree" && node node_modules/vite-plus/bin/vp build --config apps/web/tests/thread-row-meta/vite.config.ts && STUDIO_PLAYWRIGHT_MODULE="$PWD/node_modules/.pnpm/playwright-core@1.60.0/node_modules/playwright-core/index.mjs" node apps/web/tests/thread-row-meta/other-machine-plan.mjs

### T-04 Docs and changelog
- AC: AC-08 | Files: repositories/anton-abyzov/specwithcode-dev/docs/studio/plan-progress.md, repositories/anton-abyzov/specwithcode-dev/CHANGELOG.md | Test: cd "$HOME/.specwithcode/m4/scratch/2026-11-11-plan-binding/tree" && grep -q "worked in" docs/studio/plan-progress.md && node node_modules/vite-plus/bin/vp fmt --check docs/studio/plan-progress.md CHANGELOG.md

### T-05 Ship: PR, exact-head review, required CI, merge, release request
- AC: AC-01, AC-06 | Files: .specweave/increments/1303-thread-plan-follows-its-increment-outside-the-project-folder-and-on-other-machines/reports/ship.md | Test: test -s .specweave/increments/1303-thread-plan-follows-its-increment-outside-the-project-folder-and-on-other-machines/reports/ship.md

### T-06 Verify and close 1303
- AC: AC-08 | Files: .specweave/increments/1303-thread-plan-follows-its-increment-outside-the-project-folder-and-on-other-machines/spec.md | Test: specweave task list 1303
