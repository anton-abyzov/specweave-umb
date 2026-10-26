# Recover failed turns with Continue and model switch

## Problem

On October 24, 2026 the EasyChamp thread "Verify qualification deployment evidence" (`thread:delegated-task:command%3Amcp%3Ad7cd4891-7700-48ea-b755-1be4becb2890%3Adelegate-task%3Aqualification-deployment-evidence-20261024`) failed runs 7 (7:20 PM EDT) and 8 (7:50 PM) with Codex's "Your access token could not be refreshed because you have since logged out or signed in to another account." The stored failure is `class: provider_error`, `code: unauthorized`. When the user came back, the thread showed two collapsed "Provider error · earlier turn" rows and no recovery action. Nothing moved until another agent sent run 9 at 12:16 AM.

Cause, from source on `origin/main` 5c2e98e616 (same rules as installed 1.0.76):

- `timelineFailureIsHistory` (`packages/shared/src/orchestrationV2ThreadError.ts`) turns a failure into a quiet "earlier turn" note once it is 30 minutes old, even when it is the thread's latest run and the thread is unsettled.
- The only Continue next to an error is in `ThreadErrorBanner`, which `threadErrorIsLive` hides after the same 30 minutes.
- No failure surface offers a model or provider switch. The composer's picker can switch, but nothing points to it.
- Continue on 1.0.76 would have failed again on the stale shared Codex runtime; #689 (merged, unreleased) restarts it on the next open.

## Scope

In: the latest failed run of an unsettled thread stays an actionable timeline row regardless of age, with Continue (when the run can continue) and Switch model (opens the composer's model picker); Switch model on the live banner too; tests and a headless fixture of the real failure. Out: automatic fallback on non-limit failures (no unrequested spend), server changes (#689 already covers the runtime restart), resuming EasyChamp work (its coordinator owns it).

## Acceptance Criteria

- [x] AC-01: A failed latest run on an unsettled thread is not shown as "earlier turn" history because of its age; a superseded run or a settled thread still is.
- [x] AC-02: That row shows Continue when the run is resumable, and pressing it calls the same resume path as the composer's Continue.
- [x] AC-03: That row and the live error banner show Switch model, which opens the composer's model picker; it is shown for non-continuable failures too.
- [x] AC-04: A headless fixture of the Codex auth-change failure (provider_error, code unauthorized, 5 hours old, latest run) shows Continue and Switch model; screenshots saved.

## Approach

`packages/shared/src/orchestrationV2ThreadError.ts`: drop the age rule for the latest run in `timelineFailureIsHistory` (keep superseded and settled). `apps/web/src/components/chat/MessagesTimeline.tsx`: a `failureRecovery` context value (`failureItemId`, `onContinue?`, `continueBusy`, `onSwitchModel?`) in the same shape as `contextLimitRecovery`, rendered by the live failure row. `ChatView.tsx` builds it from `resumableRunId`, `onResume` and `composerRef.current?.openModelPicker()`. `ThreadErrorBanner.tsx` gets `onSwitchModel`. Rejected: lengthening the 30-minute window (still hides recovery later) and auto-switching providers on auth errors (unrequested spend, excluded providers).

## Decisions

### Asked
- none
### Defaulted (change any before sw-do)
- D-01: Manual switch only; no automatic fallback on non-limit failures → avoids paid or excluded providers.
- D-02: The banner's 30-minute window stays; the timeline row carries recovery after it.
### Open
- none

## Tasks

### T-01 Keep the latest failed run actionable
- AC: AC-01 | Files: packages/shared/src/orchestrationV2ThreadError.ts, packages/shared/src/orchestrationV2ThreadError.test.ts | Test: npx vp test run packages/shared/src/orchestrationV2ThreadError.test.ts

### T-02 Continue and Switch model on the failure row and banner
- AC: AC-02, AC-03 | Files: apps/web/src/components/chat/MessagesTimeline.tsx, apps/web/src/components/chat/ThreadErrorBanner.tsx, apps/web/src/components/chat/FailureRecovery.tsx, apps/web/src/components/ChatView.tsx | Test: web unit tests for the row and banner

### T-03 Headless fixture of the real failure
- AC: AC-04 | Files: apps/web/tests/provider-errors/main.tsx | Test: headless Playwright screenshots in ~/.specwithcode/m4/evidence/failed-turn-recovery-20261025/

### T-04 PR, checks and report back
- AC: AC-01, AC-02, AC-03, AC-04 | Files: none | Test: gh pr checks

### T-05 Verify and close 1067
- AC: AC-01, AC-02, AC-03, AC-04 | Files: none | Test: specweave verify 1067-recover-failed-turns-with-continue-and-model-switch
