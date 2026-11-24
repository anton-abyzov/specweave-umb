# Verify joined-machine resources and one-way project and chat privacy

## Problem
A newly joined machine may expose private project and chat metadata in the reverse direction. Its identity and actual grant directions must be established before claiming access or privacy.

## Scope
Read-only live topology investigation and isolated regression verification. Consolidate with 1422 wording, 1428 one-way access, 1388 controlled family machine, 1390 sync/add/handoff and the device approval owner. No access grants, auth mutations, real project/chat copies or remote work for testing. Implementation of overlapping access changes remains with its owning lane.

## Acceptance Criteria
- [ ] AC-01: Establish new machine identity and join time, plus m4 and M5 grant directions, distinguishing unavailable evidence from denial.
- [ ] AC-02: Verify resource discovery and execution authorization with read-only probes and synthetic isolated fixtures without executing real remote work.
- [ ] AC-03: Verify denied reverse access hides project names, gray rows, chat titles and content in discovery, caches and direct reads, including revocation.
- [ ] AC-04: Route reproduced defects to existing owners with exact evidence; record tests, release and installed acceptance separately.

## Approach
First inspect fleet and active owners. Obtain sanitized topology and installed versions through authorized owners. Trace discovery and session authorization separately from project copies and worker grants. Reuse owner tests and independent verifier; add synthetic regressions in owning lane once boundaries are reconciled. Browser checks require explicit headless true, PWDEBUG=0, PLAYWRIGHT_HTML_OPEN=never and reports open never. Full suites use checks copy/run. Verify and close 1431 only after evidence and owner acceptance.

## Decisions
### Asked
None. Existing one-way access decisions govern.
### Defaulted
Missing grant does not authorize a connection, and absent project copy does not prove privacy. No changes to auth pending existing owner reconciliation.
### Open
Actual newly connected identity/time, M5 direction and reverse device access remain unverified.

## Tasks
### T-01 Establish topology and ownership
- AC: AC-01 | Files: .specweave/increments/1431-verify-joined-machine-resources-and-one-way-project-and-chat-privacy/reports/investigation.md | Test: sanitized studio_machine_list and owning-lane receipts
### T-02 Verify authorization and privacy
- AC: AC-02, AC-03 | Files: .specweave/increments/1431-verify-joined-machine-resources-and-one-way-project-and-chat-privacy/reports/investigation.md | Test: owning-lane synthetic discovery, direct-read, cache and revocation regression checks
### T-03 Consolidate fixes and delivery
- AC: AC-04 | Files: .specweave/increments/1431-verify-joined-machine-resources-and-one-way-project-and-chat-privacy/reports/investigation.md | Test: independent verifier receipts and specweave verify 1431
