# Review: 1316 first-run agent install

Reviewer: three fresh-context reviewers (web state, server probe, callers), each finding re-checked by a separate verifier, on app PR 299 before merge (2026-11-12).

## Findings (all fixed in PR 299 before merge)

- apps/web/src/components/onboarding/AgentsStep.tsx closePanel: closing the log of a failed install left the row with no button. Fixed: the row gets "Install and sign in" back.
- apps/web/src/components/onboarding/AgentsStep.tsx install/installEnded: the "sign in after install" flag outlived a failed or closed install, so a later Claude row could start a sign-in unasked. Fixed: cleared on failure and close, set again on Retry.
- apps/web/src/components/onboarding/AgentsStep.tsx footer: Back and Continue stayed on while an install ran, and leaving stopped it midway. Fixed: both are off with a note until it ends or its log is closed.
- apps/server/src/provider/providerDiscovery.ts probeGit: `xcode-select -p` exit 0 was taken as proof of Git; a macOS upgrade can leave a stale path. Fixed: the printed folder must hold `usr/bin/git`.
- Refuted: the Git row stuck in "requested" after the poll limit (it keeps an "Ask again" button).

## After the fixes

Web unit tests 2,345 pass, server discovery tests 38 pass, PR CI 29 checks green. Released in 1.0.273; the released server passed the headless check with a real Claude Code install (reports/results.json, reports/01-agents-step.png).

Verdict: ship
