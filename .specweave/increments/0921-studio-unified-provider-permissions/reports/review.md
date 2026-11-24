# Review: 0921 Studio unified provider permissions
Verdict: ship · risk: low · 0 surviving findings
Reviewer context: fresh subagent; read-only implementation review against HEAD, followed by re-review of the resume fix.

## Resolved finding
The initial medium finding concerned same-session resume bypassing permission synchronization. The revised `AcpAdapterV2.ts` installs the explicit incoming policy (or latest policy when omitted) before activation and calls `synchronizeAcpPermissions` unconditionally before resume returns. This resolves the AC-02 gap. `AcpPermissions.lifecycle.test.ts` exercises the real adapter through initial enable, same-session downgrade, idle provider drift with omitted policy, and re-enable. Test execution was still pending at final source re-review; the implementing agent must retain its result before completion.

## Evidence and limits
Read retained evidence: 52 focused tests pass across four files; server/web production build logs and headless composer browser.json report success. `git diff --check` passes after the fix. Reviewed boolean/select mapping, saved permission override filtering, acknowledgment validation, configuration extraction, cached composer descriptor filtering, creation/activation/model switching, pre-prompt and resume call sites. No further verified correctness/security findings. Production builds are not evidence of a full TypeScript check; no repository-wide tests/typecheck were run by this reviewer. No real provider turn was executed. Final changed-source tests/builds and manual UI acceptance remain required before closure.

## Implementer final evidence
After fresh source re-review, the lifecycle test passed. Final focused suite: 53/53; retained adapter configuration regressions: 3/3; server rebuild passed; web build and headless UI evidence match unchanged source hashes. SpecWeave verify PASS. Targeted permission-module coverage: 100% lines, 91.66% branches. Manual UI acceptance remains pending; increment remains open.
