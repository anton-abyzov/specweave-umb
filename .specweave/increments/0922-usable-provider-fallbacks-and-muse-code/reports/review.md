# Review: 0922 usable-provider-fallbacks-and-muse-code

Verdict: no remaining high-severity findings in final reviewed fixes. Reviewer context: fresh subagent `/root/review_muse`, sw-review skill, read-only.

The independent reviewer confirmed five concrete corrections: expired exhausted windows no longer become fallback-eligible based on another active window; startup/dispatch control RPCs time out and close their owned host; restored approvals are pulled after opening; unsupported questions are explicitly declined; native approval stages serialize until acknowledgement and terminal outcomes suppress trailing stale updates. Current folded requirements supersede restored state, and expected settlement races stay nonfatal.

Final reviewer result: 82 tests passed across 8 focused files. Actual native Muse sign-in, eligible Wonder Full account access and installed CLI acceptance remain unverified. Background text generation remains explicitly unsupported in this preview. Manual UI/auth acceptance is required before closure; this report is not live deployment evidence.

Product commits: d09180375, 62fe1c185, 263448ff8. Headless UI evidence and final web/typecheck/test logs: `/Users/antonabyzov/Projects/github/studio-muse-fallback/.artifacts/muse-picker/evidence/`. Server build/headless command receipts are in verify.md.
