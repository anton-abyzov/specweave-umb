# Forced update closes and reopens questions

## Problem

An automatic install waited 5h10m on "1 open request" on 2026-10-21 (0985 reports/timeline.md): a thread waiting on a question never quiets, and only an Update now press cleared it. Update now's drain already dismisses and cancels pending questions and approvals (ServiceUpdatePreparation clearLeftovers), but it does so silently: the confirm dialog does not say questions will be closed, nothing records what was closed, and after the update the person has to find those threads and ask again. The owner approved D-03 (2026-10-21, "yes"): a forced Update now may close unanswered questions so they cannot block it, as long as they are named first and reopened after the update.

## Scope

In: the confirm dialog naming the questions a forced press closes; a durable record of each closed question or approval, written before it is cancelled; reopening each recorded thread once after the updated service starts (Needs you plus a note quoting the closed question, and the continuation prompt asks the agent to ask again where the project continues threads after restarts); the sidebar of a blocked automatic install naming the waiting questions with Update now. Out: automatic installs closing questions (they keep waiting), the run record (0988), the launcher.

## Acceptance Criteria

- [x] AC-01: Before a forced Update now, the confirm dialog says how many questions and approvals will be closed and reopened after the update, and names their threads.
- [x] AC-02: The forced drain records every question and approval it closes (thread, request id, kind, the question text, time) in a durable record before cancelling it; an automatic install never closes a question, and the 30-minute stale-approval release it already has (0936 AC-05) records and reopens those approvals the same way.
- [x] AC-03: After the updated service starts, each recorded thread is reopened exactly once: it shows in Needs you with a note quoting the closed question, and where the project continues threads after restarts the continuation asks the agent to ask it again. A rolled-back or cancelled update reopens them too, and a restart never reopens one twice.
- [x] AC-04: A blocked automatic install shows "Update ready: waiting for N questions you haven't answered", naming the threads, with Update now.

## Approach

Stacked on feat/update-run-record (0988, PR #585). Server: ServiceUpdatePreparation/ServiceUpdateCleanup record before dismiss/cancel; a startup reaction reopens from the record. Web: the confirm dialog and sidebar copy. Branch feat/update-closes-questions in ~/.specwithcode/m4/worktrees/closes-questions.

## Decisions

### Asked
- D-03 (from 0985, answered "yes" 2026-10-21): a forced Update now may close unanswered questions, recorded and reopened after the update.
### Defaulted (change any before sw-do)
- D-01: Only a forced press closes questions; automatic installs keep waiting and say so.
- D-02: Keep 0936's stale-approval release on automatic installs, now recorded and reopened after the install, instead of removing it.
### Open

## Tasks

### T-01 Record closed questions before a forced drain
- AC: AC-02 | Files: repositories/anton-abyzov/specweave-studio/apps/server/src/serviceUpdate/ServiceUpdateClosedQuestions.ts, repositories/anton-abyzov/specweave-studio/apps/server/src/serviceUpdate/ServiceUpdateClosedQuestions.test.ts, repositories/anton-abyzov/specweave-studio/apps/server/src/serviceUpdate/ServiceUpdatePreparation.ts, repositories/anton-abyzov/specweave-studio/apps/server/src/serviceUpdate/ServiceUpdatePreparation.test.ts, repositories/anton-abyzov/specweave-studio/apps/server/src/serviceUpdate/ServiceUpdatePreparation.closedQuestions.test.ts, repositories/anton-abyzov/specweave-studio/apps/server/src/server.ts, repositories/anton-abyzov/specweave-studio/packages/contracts/src/serviceUpdatePreparation.ts | Test: cd ~/.specwithcode/m4/worktrees/closes-questions && export PATH=$HOME/.nvm/versions/node/v22.20.0/bin:$PATH && node node_modules/vite-plus/bin/vp test run apps/server/src/serviceUpdate && node node_modules/vite-plus/bin/vp run @specweave-studio/contracts#typecheck

### T-02 Reopen recorded questions once after the update
- AC: AC-03 | Files: repositories/anton-abyzov/specweave-studio/apps/server/src/serviceUpdate/ServiceUpdateReopenQuestions.ts, repositories/anton-abyzov/specweave-studio/apps/server/src/serviceUpdate/ServiceUpdateReopenQuestions.test.ts, repositories/anton-abyzov/specweave-studio/apps/server/src/orchestration-v2/RestartContinuation.ts, repositories/anton-abyzov/specweave-studio/apps/server/src/orchestration-v2/RestartContinuation.test.ts, repositories/anton-abyzov/specweave-studio/apps/server/src/orchestration-v2/EffectWorker.ts, repositories/anton-abyzov/specweave-studio/apps/server/src/orchestration-v2/runtimeLayer.ts, repositories/anton-abyzov/specweave-studio/apps/server/src/orchestration-v2/UpdateContinuation.integration.test.ts | Test: cd ~/.specwithcode/m4/worktrees/closes-questions && export PATH=$HOME/.nvm/versions/node/v22.20.0/bin:$PATH && node node_modules/vite-plus/bin/vp test run apps/server/src/serviceUpdate/ServiceUpdateReopenQuestions.test.ts apps/server/src/orchestration-v2/RestartContinuation.test.ts apps/server/src/orchestration-v2/UpdateContinuation.integration.test.ts && node node_modules/vite-plus/bin/vp run @specweave-studio/contracts#typecheck

### T-03 Name closed questions in the Update now confirm
- AC: AC-01 | Files: repositories/anton-abyzov/specweave-studio/apps/web/src/components/sidebar/SidebarRestartToUpdate.logic.ts, repositories/anton-abyzov/specweave-studio/apps/web/src/components/sidebar/SidebarRestartToUpdate.logic.test.ts, repositories/anton-abyzov/specweave-studio/apps/web/src/components/serviceUpdateRunView.ts | Test: cd ~/.specwithcode/m4/worktrees/closes-questions && export PATH=$HOME/.nvm/versions/node/v22.20.0/bin:$PATH && node node_modules/vite-plus/bin/vp test run apps/web/src/components/sidebar/SidebarRestartToUpdate.logic.test.ts apps/web/src/components/sidebar/SidebarRestartToUpdate.test.tsx && node node_modules/vite-plus/bin/vp run @specweave-studio/web#typecheck

### T-04 Say what a blocked automatic install waits for
- AC: AC-04 | Files: repositories/anton-abyzov/specweave-studio/apps/web/src/components/serviceUpdateRunView.ts, repositories/anton-abyzov/specweave-studio/apps/web/src/components/serviceUpdateRunView.test.ts, repositories/anton-abyzov/specweave-studio/apps/web/src/components/serviceUpdateCalls.ts, repositories/anton-abyzov/specweave-studio/apps/web/src/components/sidebar/useServiceQuestionBlockers.ts, repositories/anton-abyzov/specweave-studio/apps/web/src/components/sidebar/SidebarRestartToUpdate.tsx, repositories/anton-abyzov/specweave-studio/apps/web/src/components/sidebar/SidebarRestartToUpdate.run.test.tsx | Test: cd ~/.specwithcode/m4/worktrees/closes-questions && export PATH=$HOME/.nvm/versions/node/v22.20.0/bin:$PATH && node node_modules/vite-plus/bin/vp test run apps/web/src/components/serviceUpdateRunView.test.ts apps/web/src/components/sidebar && node node_modules/vite-plus/bin/vp run @specweave-studio/web#typecheck

### T-05 Re-run every task Test with its typechecks on a real install
- AC: AC-01, AC-02, AC-03, AC-04 | Files: repositories/anton-abyzov/specweave-studio/apps/server/src/serviceUpdate/ServiceUpdateClosedQuestions.ts | Test: cd ~/.specwithcode/m4/worktrees/closes-questions && export PATH=$HOME/.nvm/versions/node/v22.20.0/bin:$PATH && node node_modules/vite-plus/bin/vp test run apps/server/src/serviceUpdate apps/server/src/orchestration-v2/RestartContinuation.test.ts apps/server/src/orchestration-v2/UpdateContinuation.integration.test.ts apps/web/src/components/serviceUpdateRunView.test.ts apps/web/src/components/sidebar && node node_modules/vite-plus/bin/vp run @specweave-studio/contracts#typecheck && node node_modules/vite-plus/bin/vp run @specweave-studio/web#typecheck
