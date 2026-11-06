# Source thread links in coordinator replies

## Problem

Coordinator replies following worker messages appear detached from their source. The supplied screenshot shows a collapsed worker trigger followed by a reply without a visible source link. The current CoordinatorConversation renders a source action inside RelayedMessage but does not consistently associate the resulting assistant reply with the triggering source.

## Scope

In: durable trigger provenance, visible reply source links, worker messages, task results and PR watch events, web and desktop shared rendering, native mobile rendering, accessible navigation and headless verification. Out: provider behavior changes, automatically restoring archived threads, remote permission changes and app releases.

## Acceptance Criteria

- [ ] AC-01: A reply triggered by a worker message or task result displays a compact clickable source label above its text, including while streaming and after reload.
- [ ] AC-02: Multiple triggers consumed by one turn produce distinct source links deduplicated by environment and thread, without attributing unrelated earlier or later messages to the turn.
- [ ] AC-03: Source links open the correct worker through existing environment-aware navigation; archived threads remain archived, and unavailable or unauthorized remote sources show an honest unavailable state without navigating to a same-ID local thread.
- [ ] AC-04: A PR event with an originating thread links to it; an event without a thread shows a validated PR link or plain event label and never invents a thread.
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

- Implementation waits for checkout ownership: Use worktrees is off and the shared app checkout remains on fix/1205-incoming-retry-key, with other workers not released. Do not switch it or bypass the project worktree guard.

## Tasks

### T-01 Persist consumed trigger sources

- AC: AC-01, AC-02, AC-04, AC-06 | Files: packages/contracts/src/**, apps/server/src/orchestration/** (narrow after tracing event owners) | Test: focused existing orchestration tests extended for trigger batching, task results, PR-only events and reload persistence

### T-02 Render and navigate source labels across clients

- AC: AC-01, AC-02, AC-03, AC-04, AC-05, AC-06 | Files: apps/web/src/components/studio/CoordinatorConversation.tsx, apps/web/src/components/studio/ProjectWorkspace.test.tsx, apps/mobile/src/features/threads/ThreadFeed.tsx, apps/mobile/src/lib/threadActivity.ts, apps/mobile/src/lib/threadActivity.test.ts | Test: focused coordinator and mobile behavior suites; headless light/dark desktop and narrow viewport fixture with navigation assertions; relevant production builds

### T-03 Verify and close 1244

- AC: AC-01, AC-02, AC-03, AC-04, AC-05, AC-06 | Files: reports/ | Test: specweave verify 1244; fresh-context review; required PR checks; specweave complete 1244
