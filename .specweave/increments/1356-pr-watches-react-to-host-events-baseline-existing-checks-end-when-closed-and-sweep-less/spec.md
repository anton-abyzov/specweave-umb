# PR watches react to host events, baseline existing checks, end when closed, and sweep less

## Problem

Agents here wait on CI with `watch_pull_request`, and merge on green without asking, so every slow or wrong wake costs a turn (triage report of increment 1346, section 4, row F1; Anton approved on November 14, 2026).

- A watched pull request is looked at on a 2-minute pass only (`apps/server/src/orchestration-v2/PullRequestWatchReactor.ts:44`, `:663`). A check that finishes just after a pass waits up to 2 minutes, and nothing reacts to the host saying a check suite completed.
- A watch that starts on a pull request whose checks already failed or passed reports them as news, which wakes the thread for something it already knew (`apps/server/src/orchestration-v2/pullRequestWatch.ts:45`).
- When a pull request is closed and the activity read fails in the same pass, the watch does not end; it keeps counting toward the 8-failure limit.
- One pass can wake a thread more than once, and a wake queued for a head that has since moved is still delivered.
- `apps/server/src/orchestration-v2/ThreadPullRequestService.ts:408` rereads every thread's branch each minute, including branches that have no pull request and hosts that cannot be read. This has burned the GitHub rate limit before.

## Scope

In: the reactor, the pure watch evaluation, the per-minute branch sweep, the GitHub provider's event read, tests, and `UPSTREAM.md`. Our own design: the 2-minute pass stays as the fallback and the existing host fingerprint stays the gate for reads.

Out: `Orchestrator.ts` and `QueuedRunOrder.ts` (owned by increments 1347 to 1349); if a row needs them, ask that thread. Settling rules for watched threads, merge-queue support, hosts other than GitHub for the event path, the subagent watch refusal.

## Acceptance Criteria

- [ ] AC-01: When the host reports a change for a watched pull request (a check suite or run completed, a push, a review or comment), that pull request is read within one event poll, not at the next 2-minute pass. A host or account without the event stream, or a failed event read, falls back to the pass with no error surfaced to the thread.
- [ ] AC-02: The event path adds no request per watched pull request per poll: one conditional request per watched repository, honouring the host's poll interval and rate-limit pause.
- [ ] AC-03: A watch's first look records the checks that already failed or passed as its baseline and does not wake the thread for them; a later change still wakes it.
- [ ] AC-04: A pull request that is closed or merged ends its watch even when the activity read of the same pass fails.
- [ ] AC-05: One pass sends a thread at most one wake per watched pull request, and a queued wake whose head commit is no longer the pull request's head is dropped.
- [ ] AC-06: A branch with no pull request, and a host that could not be read, are rechecked on a backoff (not every minute); a push, a new link or a thread event rechecks at once. Lookups run with a bounded concurrency.
- [ ] AC-07: `reports/red-green.md` records the failing and passing run of each new test, and `reports/measurements.md` records host requests per hour before and after for a fixture of idle threads and watched pull requests.
- [ ] AC-08: The PR has green CI, a ship verdict from `muse-wonder-1.0` at its exact head, is merged, and a release holds it. The public repository names the upstream project only in `UPSTREAM.md`.

## Approach

1. Pure logic first: baseline, one-wake-per-pass and stale-wake rules in `pullRequestWatch.ts` with unit tests.
2. Reactor: end a closed watch from the detail read alone; add an event-driven trigger that marks a group for an immediate read through the existing `readGroup`.
3. GitHub provider: a conditional (ETag) repository events read behind the provider interface; other hosts return "not supported".
4. `ThreadPullRequestService.ts`: backoff map for branches without a pull request and unreadable hosts, bounded lookup concurrency.

Risk: the port thread is merging about 18 PRs; rebase on main before review. Event reads must never raise the request count on a quiet repository.

## Decisions

### Asked
- D-01 Adopt section 4 as recommended → yes (Anton, November 14, 2026).
### Defaulted (change any before sw-do)
- D-02 Event source → GitHub repository events with a conditional request; no webhooks, no new credentials.
- D-03 Merge-queue removal wakes and "a watched PR keeps its thread from settling only while checks run" → out of this increment, because they change `Orchestrator.ts`.
### Open
- none

## Tasks

### T-01 Baseline, one wake per pass, stale wake dropped
- AC: AC-03, AC-05 | Files: repositories/anton-abyzov/specwithcode/apps/server/src/orchestration-v2/pullRequestWatch.ts, repositories/anton-abyzov/specwithcode/apps/server/src/orchestration-v2/pullRequestWatch.test.ts, repositories/anton-abyzov/specwithcode/apps/server/src/orchestration-v2/PullRequestWatchReactor.ts | Test: cd repositories/anton-abyzov/specwithcode && node node_modules/vite-plus/bin/vp test run apps/server/src/orchestration-v2/pullRequestWatch.test.ts

### T-02 Closed watch ends and host events trigger a read
- AC: AC-01, AC-02, AC-04 | Files: repositories/anton-abyzov/specwithcode/apps/server/src/orchestration-v2/PullRequestWatchReactor.ts, repositories/anton-abyzov/specwithcode/apps/server/src/orchestration-v2/PullRequestWatchReactor.test.ts, repositories/anton-abyzov/specwithcode/apps/server/src/pullRequest | Test: cd repositories/anton-abyzov/specwithcode && node node_modules/vite-plus/bin/vp test run apps/server/src/orchestration-v2/PullRequestWatchReactor.test.ts

### T-03 Branch sweep backs off
- AC: AC-06 | Files: repositories/anton-abyzov/specwithcode/apps/server/src/orchestration-v2/ThreadPullRequestService.ts, repositories/anton-abyzov/specwithcode/apps/server/src/orchestration-v2/ThreadPullRequestService.test.ts | Test: cd repositories/anton-abyzov/specwithcode && node node_modules/vite-plus/bin/vp test run apps/server/src/orchestration-v2/ThreadPullRequestService.test.ts

### T-04 Reports and provenance
- AC: AC-07 | Files: .specweave/increments/1356-pr-watches-react-to-host-events-baseline-existing-checks-end-when-closed-and-sweep-less/reports/measurements.md, .specweave/increments/1356-pr-watches-react-to-host-events-baseline-existing-checks-end-when-closed-and-sweep-less/reports/red-green.md, repositories/anton-abyzov/specwithcode/UPSTREAM.md | Test: test -s .specweave/increments/1356-pr-watches-react-to-host-events-baseline-existing-checks-end-when-closed-and-sweep-less/reports/measurements.md && test -s .specweave/increments/1356-pr-watches-react-to-host-events-baseline-existing-checks-end-when-closed-and-sweep-less/reports/red-green.md

### T-05 PR, cross-family review, merge and release
- AC: AC-08 | Files: repositories/anton-abyzov/specwithcode | Test: test -s .specweave/increments/1356-pr-watches-react-to-host-events-baseline-existing-checks-end-when-closed-and-sweep-less/reports/red-green.md
