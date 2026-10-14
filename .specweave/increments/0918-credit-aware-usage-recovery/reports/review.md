# Review: 0918 Credit-aware usage recovery

Verdict: ship · risk: low · 0 unresolved findings
Reviewer context: fresh delegated session; read-only product review against 4d6e30488. Installed and registry SpecWeave both 3.0.15. No pickup, claims, provider turns, browser sessions, release or installation performed.

## Resolved [high] apps/web/src/components/ChatView.tsx:8900 Revalidate credit intent after settings persistence

The new recovery callback consumes an offer and enters onResume, which awaits persistThreadSettingsForNextTurn at line 8880 before submitting paid work. It never re-reads the current UI route or current credit context after that await. Navigating to another chat while persistence is pending still submits the credit-bearing turn to the old chat. The existing onSend path deliberately checks currentRouteThreadKeyRef, currentCreditRouteRef, live provider data and explicitCreditSendStillMatches across asynchronous boundaries; the new recovery path bypasses those checks. Backend account/model checks cannot establish the current UI route. Reverified by extracting and executing the actual onResume AST under Node 22.20 with deferred settings persistence: after changing currentRouteThreadKeyRef to different-thread, startThreadTurn still received threadId old-thread and manualCodexCreditIntent. Add a bound recovery-context check immediately before dispatch, covering route/permissions/provider/model/freshness changes, and callback regression tests.

## Resolved [medium] apps/web/src/components/chat/usageWarningResolution.ts:8 A recovered historical warning reactivates after interruption or a later failure

The predicate requires a later run's current status to be running or completed. A subsequent run can execute successfully for several minutes, then be interrupted or fail for an unrelated reason: the old usage warning changes back from resolved to active despite the chat having continued. Waiting for approval/input similarly ceases to count. This contradicts AC-02's later-started-run rule. Reverified by transpiling and executing the actual helper with the same later started run transitioning running → interrupted/failed: outputs true → false/false. Preserve evidence that execution started (using provider-start/work evidence if startedAt also covers pre-provider admission); continue excluding queued and genuinely pre-start refusals. Update the test that currently asserts every interrupted run is unresolved.

## Re-review evidence

The implementation now captures and revalidates the credit recovery context, live provider data and composer selection before persistence, after persistence and immediately before dispatch. Seven added tests execute the actual onResume callback: a stable request preserves original text/attachments and sends a foreground credit intent without manualContinuationOfRunId; route, model, account, denial, permission and freshness changes during deferred persistence all prevent dispatch.

Historical resolution now uses completed runs or real answer/reasoning/provider-tool evidence, which survives later interruption, waiting or failure while excluding bare admission and workspace preparation commands. An intermediate raw/projected turn-item mismatch was identified and fixed before approval. Regression fixtures now use the actual typed raw OrchestrationV2TurnItem shape with no never cast.

Independently reran explicitCreditSend.test.ts and usageWarningResolution.test.ts under Node 22.20: **95/95 tests passed**. This includes the actual callback race reproductions and typed history integration. Reviewer changes were limited to the two explicitly authorized test files and this report; implementation fixes remained with the parent.

## Verification boundary

No canonical reports/verify.md existed when review began. Parent's broader focused tests and production/headless checks are separate evidence, not independently rerun here. Review approves the corrected credit continuation and historical-warning integration; it does not establish release/deployment or manual UI acceptance.
