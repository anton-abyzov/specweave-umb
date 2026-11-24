# Source thread links in coordinator replies

## Problem

Coordinator replies following worker messages appear detached from their source. The supplied screenshot shows a collapsed worker trigger followed by a reply without a visible source link. The current CoordinatorConversation renders a source action inside RelayedMessage but does not consistently associate the resulting assistant reply with the triggering source.

## Scope

In: durable trigger provenance, visible reply source links, worker messages, task results and PR watch events, web and desktop shared rendering, native mobile rendering, accessible navigation and headless verification. Out: provider behavior changes, automatically restoring archived threads, remote permission changes and app releases.

## Acceptance Criteria

- [ ] AC-01: A reply triggered by a worker message or task result displays a compact clickable source label above its text, including while streaming and after reload.
- [ ] AC-02: Multiple triggers consumed by one turn produce distinct source links deduplicated by environment and thread, without attributing unrelated earlier or later messages to the turn.
- [ ] AC-03: Source links open the correct worker through existing environment-aware navigation; archived threads remain archived, and unavailable or unauthorized remote sources show an honest unavailable state without navigating to a same-ID local thread.
- [ ] AC-04: A PR event links to a real originating thread only when that requester is retained; watches without requester provenance show a validated PR link or plain event label, never the receiving thread as an invented source.
- [ ] AC-05: Web, desktop and native mobile use the same provenance semantics and compact source-label pattern; narrow layouts wrap labels without obscuring reply text, with accessible names and keyboard activation on web.
- [ ] AC-06: Ordinary user-triggered turns have no invented source; existing historical messages without structured provenance remain readable, and untrusted message text cannot supply navigation targets.

## Approach

Trace event ingestion and run association before extending the shared contract. Persist structured source references with the trigger and retain the references consumed by a run, rather than infer ownership from adjacent transcript text. Reuse existing thread navigation and MessageThreadLink semantics in apps/web/src/components/studio/CoordinatorConversation.tsx; desktop wraps this renderer. Add the corresponding source row in apps/mobile/src/features/threads/ThreadFeed.tsx through its existing navigation callback. Review packages/contracts and server orchestration trigger paths during T-01 and narrow the file list before claiming implementation. Keep source identity scoped by environment. Render compact `re: <thread title>` labels adjacent to the reply header. Use a wrapped list for several sources. Preserve existing disclosure behavior.

## Decisions

### Asked

- None. The user authorized implementation and the existing PR, CI and merge flow.

### Defaulted (change any before sw-do)

- Put source labels on the reply so provenance remains visible when trigger rows collapse.
- Retain structured title snapshots as fallback labels; resolve current titles through existing navigation state when available.
- Do not backfill historical provenance by parsing prose or nearest-message inference.

### Open

- None. User released the clean checkout; implementation uses feat/1244-source-thread-links from fresh origin/main including #1436.

## Tasks

### T-01 Retain structured trigger provenance and shared derivation
- AC: AC-01, AC-02, AC-03, AC-04, AC-06 | Files: packages/contracts/src/orchestrationV2.ts, packages/shared/package.json, packages/shared/src/coordinatorReplySources.ts, packages/shared/src/coordinatorReplySources.test.ts, apps/server/src/project/**, apps/server/src/orchestration-v2/**, apps/server/src/studio/Capacity.test.ts, apps/server/src/fleet/remoteWorkerMatching.ts, apps/server/src/fleet/remoteWorkerMatching.test.ts, apps/server/src/fleet/RemoteWorkerFollower.ts, apps/server/src/fleet/RemoteWorkerFollower.test.ts | Test: focused provenance behavior suites and relevant server build

### T-02 Web and desktop source links
- AC: AC-01, AC-02, AC-03, AC-04, AC-05, AC-06 | Files: apps/web/src/**, apps/web/tests/coordinator-source-links/** | Test: focused coordinator behavior tests, production web build and headless screenshots/navigation checks

### T-03 Native mobile source links
- AC: AC-01, AC-02, AC-03, AC-04, AC-05, AC-06 | Files: apps/mobile/src/** | Test: focused mobile behavior tests and scoped mobile validation

### T-04 Verify and close 1244
- AC: AC-01, AC-02, AC-03, AC-04, AC-05, AC-06 | Files: reports/ | Test: specweave verify 1244; fresh-context review; required PR checks; specweave complete 1244
