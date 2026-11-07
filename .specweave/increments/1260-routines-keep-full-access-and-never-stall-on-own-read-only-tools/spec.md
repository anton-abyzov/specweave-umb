# Routines keep full access and never stall on own read-only tools

## Problem

On November 7, 2026 the Aide "Proactive briefing" routine on the M4 waited 4h 39m on a command approval card for `mcp__studio_code__studio_google_status`, and nothing told Anton. Three defects combined:

1. The routine row (`scheduled-task:assistant-setup:4c5387ce…`) was written on October 10, 2026 by an older Aide setup with `runtime_mode = approval-required`. Anton's app default is `full-access`, the Aide project has no override, and all 40 other routines are `full-access`. Each run launches or reuses the routine's own thread with the stored mode (`ScheduledTaskService.ts` `launchOwnThreadUnchecked` passes `active.runtimeMode`), so the stale value never heals. `routineFirstRunMode` describes the intended rule (a person's routine takes the project's mode) but is only used for the team-rules check and ignores the app-wide default.
2. Today's run fell back from Claude Sonnet 5.5 to Muse Code. In approval mode Muse prompts on every tool its name heuristic (`MuseItems.ts` `toolKind`) does not class as read or search. `studio_google_status` and `task_status` land as `other` and ask. Claude pre-allows all `mcp__studio-code__*` tools, so the same routine never asked under Claude. ACP agents (Copilot, Gemini, Grok) and Muse share `AcpClientPolicy`, which has no notion of SpecWithCode's own tools.
3. The run was recorded `succeeded` at dispatch. Approval notifications only come from an open client that owns notifications, a paired phone or Telegram, all generic ("Waiting for your approval"). A routine waiting on approval gives no clear, routine-specific signal and its status reads as success.

## Scope

In: a routine's own thread follows the routine's saved mode; a one-time replacement of the early setup briefing; SpecWithCode's own read-only tools auto-approved for ACP-based providers (Muse, Copilot, Gemini, Grok, registry agents) in every mode, from one list checked against the toolkit annotations; a request that needs the person shows even while the app is focused on another thread with in-app news off.

Out: changing `DEFAULT_RUNTIME_MODE`; Claude's existing `mcp__studio-code__*` wildcard; Codex and OpenCode v1 approval paths; Gmail, Drive and Calendar content reads (stay gated in approval mode); tool names in notifications (the pending-request summary carries none); approval timeouts.

## Acceptance Criteria

- [x] AC-01: Before a routine posts to its own thread, the thread is set to the routine's saved mode when they differ (applied on the next turn), and team rules judge that mode.
- [x] AC-02: Aide setup replaces a `scheduled-task:assistant-setup:*` briefing stored as `approval-required` with the `aide-briefing:` routine in full access (clamped by team rules), keeping its thread, schedule and model, and deletes the early row; other rows and an existing `aide-briefing:` routine are untouched.
- [x] AC-03: For ACP-based providers, a SpecWithCode read-only tool (for example `mcp__studio_code__studio_google_status`, `task_status`) is allowed without a card in any mode and over a provider's own rule; writes, Gmail reads, other servers, bare names and execute requests keep their normal rule.
- [x] AC-04: Every name in the read-only list is a real toolkit tool that is not destructive and is annotated read-only, except `task_status`, which only reads this thread's own delegated tasks; tools that return other threads' content (`studio_thread_read`, thread waits, thread search, queue and pending-request reads) and Google content are excluded; Google contributes only `studio_google_status`.
- [x] AC-05: With input-needed alerts on and in-app notifications off, a thread waiting on the person shows one toast while the app is focused on another thread; with both off the app stays quiet.

## Approach

1. `ScheduledTaskService.ts`: `syncOwnThreadMode` before `sendTo` posts; the team-rules check uses the routine's mode for an own thread.
2. `project/AideBriefingSetup.ts` `earlyBriefingReplacement`, run first in `runOnce`. A migration was tried and dropped: fleet update proofs require every migration declared, and a row rewrite is not additive.
3. `mcp/studioReadOnlyTools.ts` plus `acpRequestDisposition` in `AcpClientPolicy.ts`, called from `AcpAdapterV2.ts` in place of the flavor rule.
4. `ThreadNotificationCoordinator.tsx`: toast when `inAppNotificationsEnabled || needsUser`.

Rejected: answering approvals inside `watchMuseRequests` (bypasses policy); re-applying the project default to person-made routines at launch (would override a mode the person chose); flipping the contracts default.

## Decisions

### Asked
- none
### Defaulted (change any before sw-do)
- D-01 Gmail, Drive and Calendar content reads stay gated in approval mode.
- D-02 Only `assistant-setup:` rows are repaired; a routine a person set to approval mode keeps it.
- D-03 The routine's saved mode wins over a manual change to its own thread's mode.
### Open
- none

## Tasks

### T-01 Own thread follows the routine's mode, repair early setup rows
- AC: AC-01, AC-02 | Files: apps/server/src/scheduledTasks/ScheduledTaskService.ts, apps/server/src/project/AideBriefingSetup.ts | Test: cd apps/server && vp test run src/scheduledTasks src/project/AideBriefingSetup.test.ts

### T-02 Auto-approve SpecWithCode read-only tools for ACP providers
- AC: AC-03, AC-04 | Files: apps/server/src/provider/acp/AcpClientPolicy.ts, apps/server/src/mcp/studioReadOnlyTools.ts | Test: cd apps/server && vp test run src/provider/acp/AcpClientPolicy.test.ts src/mcp/studioReadOnlyTools.test.ts

### T-03 A waiting request shows while focused on another thread
- AC: AC-05 | Files: apps/web/src/components/ThreadNotificationCoordinator.tsx | Test: cd apps/web && vp test run src/components/ThreadNotificationCoordinator.test.tsx

### T-04 PR, CI, squash merge, hand to release dispatcher
- AC: AC-01, AC-03, AC-05 | Files: none | Test: gh pr checks 53 -R anton-abyzov/specwithcode

### T-05 Verify and close 1260
- AC: AC-01, AC-02, AC-03, AC-04, AC-05 | Files: none | Test: specweave verify 1260
