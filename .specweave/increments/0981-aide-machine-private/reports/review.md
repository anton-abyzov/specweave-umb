# 0981 closure review

Reviewed October 24, 2026. Verdict: PASS for T-06 installed acceptance and the scoped implementation. No new blocking findings. T-07 still requires a passing SpecWeave verification report and completion command.

Inspected the spec, ledger, installed 1.0.76 receipt and notes, acceptance harness, saved screenshot, earlier two-machine UI receipt, and source commit `4f9abaf56807cdc12d3cdabcb3825beea15a79cf`. The 19 final API checks exercise the installed artifact in a private fixture. Repeated personal creation returns the same ID; concurrent requests preserve the singleton; kind mutation is rejected. Full-access remote grant calls are rejected with the personal-assistant privacy reason for creation, project/thread reads, send, interrupt and wait. This avoids the earlier permission-mode false positive. The local caller retains access.

The source repair rejects remote personal creation before either creation path reaches the service. Its regression covers both grant clients and inherited remote worker threads. The installed screenshot shows the personal assistant surface and the fictional private thread, with no exposed handoff controls. The earlier two-machine fixture retains the stronger menu, nickname and duplicate-label coverage. Installed API checks are not physical two-Mac acceptance, and neither the report nor closure should claim that.

The harness uses an already-seeded Example Code project from the initial fixture pass; the notes disclose the fixture corrections. It is an acceptance receipt for this isolated test home, not a standalone one-command fresh-home setup script. This does not invalidate its final assertions.

D-05 brokered-phone access remains the explicit out-of-scope phone-owner follow-up. The Aide project-chat separation successor remains separate. No assertion is made that either scope is resolved by 0981. No new tests, browser runs, provider calls or database access were performed for this review.
