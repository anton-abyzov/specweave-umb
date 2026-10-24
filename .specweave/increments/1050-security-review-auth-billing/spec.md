# Security and simplification review: auth and billing

## Problem

Anton asked (October 24, 2026) that once the current feature work is done, the SpecWithCode app gets a comprehensive security and code review using the code review skill. The focus is authentication and payments. Verified gaps are to be fixed and duplicated code simplified. His words: "We have a lot of properties that might be duplicates of the compliant one in Korea. Think about improvements. Maybe leverage the Fable 5.1 model and make sure everything is completely implemented."

The app has no payment processor (no Stripe or invoice code on `origin/main` `f55a7507e3`). In this repository, "payments" means the code that decides who gets billed: subscription vs API billing, paid fallback guards, usage-limit identity and API-credit accounts. Authentication covers `apps/server/src/auth/`, `apps/server/src/cloud/`, relay, fleet, desktop IPC, mobile pairing, the browser extension and MCP OAuth.

The 1039 adversarial review covered settings, handoff, fallback, Aide, navigation, reports and notifications. It did not cover authentication or billing.

## Scope

In:

- Review authentication and billing surfaces with the Claude Code `code-review` skill, using Fable 5.1 subagents for review lenses.
- Verify each finding independently with a reproduction or a cited failing state.
- Fix verified high and medium gaps in routed scratch worktrees.
- Make bounded, behavior-preserving simplifications of duplicated code in the reviewed surfaces.
- Write a duplicate-property inventory, routed to the 1031 settings owner where it touches settings.

Out:

- Repo-wide or indiscriminate refactoring.
- Settings duplicates owned by 1031 ("Find duplicate and overlapping settings").
- Live charges, credential or permission changes, destructive migrations and service restarts.
- Merge, release and installed acceptance.
- Direct access to `statev2.sqlite*` or credential files.
- Paid fallback providers (Devin, Gemini, Vertex).

## Acceptance Criteria

- [ ] AC-01: The feature gate is recorded before the review starts. The record covers 1041, 1042, 1046, 1047, 1048, 1049 and 1031 status, the app `origin/main` SHA, the reviewer provider, model and effort (Fable 5.1 availability proven from `orchestrator_capabilities`, otherwise Opus 5.5 with the reason), and the retained owners.
- [ ] AC-02: The authentication review covers session, pairing, DPoP and replay markers, RPC authorization, cookie and origin policy, device sign-in, MCP OAuth, CLI tokens, cloud link and relay, fleet peers, desktop IPC, mobile pairing and the browser extension. Every surviving finding cites an absolute path and line, a concrete failing state, and a reproduction or an explicit plausible label.
- [ ] AC-03: The billing review covers subscription vs API billing choice, paid fallback guards, API-credit accounts, usage-limit identity scoping (with 1047) and secret handling in logs and handoffs. No path adopts API billing or a paid provider without an explicit choice, and every surviving finding is evidenced as in AC-02.
- [ ] AC-04: The duplicate-code and duplicate-property inventory lists each candidate with its canonical definition, its copies and a keep/merge/delete recommendation. Settings items go to the 1031 owner, and bounded merges inside reviewed surfaces are implemented with tests.
- [ ] AC-05: Each verified high or medium finding has a repair with a regression test at an exact source head, an independent fresh-context review, and routed delivery to the integration owner, coordinated with the three-platform release owner's schedule. Low findings are recorded with a decision.
- [ ] AC-06: A report at `reports/review.md` covers findings, repairs, checks run and remaining gates (CI, merge, release, installed acceptance), with evidence under `/Users/antonabyzov/.specwithcode/m4/evidence/security-review-1050/`.

## Approach

1. T-01 records the gate and the owners (read-only, can run now).
2. After the feature gate opens, export a scratch worktree from app `origin/main`, outside owner worktrees.
3. Run the `code-review` skill in three disjoint Fable 5.1 lenses: authentication, billing, duplicates. Each lens returns findings with path:line evidence.
4. The primary reviewer re-opens cited lines and runs bounded reproductions. Findings that do not survive are dropped and listed.
5. Repairs go on one branch per surface, each with a test. A fresh-context reviewer checks the diff, and delivery is routed to the integration owner.
6. Closure: `specweave verify`, a fresh review, `specweave complete`.

Risks: the reviewed code moves while features land, so the review pins a SHA and re-checks cited lines at repair time. Auth fixes can lock out paired devices, so each fix keeps existing grants valid or names the migration.

## Tasks

### T-01 Record feature gate, owners and reviewer model
- AC: AC-01 | Files: .specweave/increments/1050-security-review-auth-billing/reports/gate.md | Test: test -s .specweave/increments/1050-security-review-auth-billing/reports/gate.md

### T-02 Authentication review lens
- AC: AC-02 | Files: .specweave/increments/1050-security-review-auth-billing/reports/auth-findings.md | Test: test -s .specweave/increments/1050-security-review-auth-billing/reports/auth-findings.md

### T-03 Billing and paid-fallback review lens
- AC: AC-03 | Files: .specweave/increments/1050-security-review-auth-billing/reports/billing-findings.md | Test: test -s .specweave/increments/1050-security-review-auth-billing/reports/billing-findings.md

### T-04 Duplicate code and property inventory
- AC: AC-04 | Files: .specweave/increments/1050-security-review-auth-billing/reports/duplicates.md | Test: test -s .specweave/increments/1050-security-review-auth-billing/reports/duplicates.md

### T-05 Independent verification of findings
- AC: AC-02, AC-03, AC-04 | Files: .specweave/increments/1050-security-review-auth-billing/reports/verified.md | Test: test -s .specweave/increments/1050-security-review-auth-billing/reports/verified.md

### T-06 Repairs and bounded simplifications with tests
- AC: AC-04, AC-05 | Files: apps/server/src/auth/, apps/server/src/cloud/, apps/server/src/provider/ (app repo, scratch worktree) | Test: npx vp test run apps/server/src/auth apps/server/src/cloud

### T-07 Fresh review and routed delivery
- AC: AC-05, AC-06 | Files: .specweave/increments/1050-security-review-auth-billing/reports/review.md | Test: test -s .specweave/increments/1050-security-review-auth-billing/reports/review.md

### T-08 Verify and close 1050

## Decisions

### Asked
- D-01: Anton asked for a code-review-skill security review focused on authentication and payments, with verified fixes and simplification, and suggested Fable 5.1.

### Defaulted
- D-02: "Payments" maps to billing-mode and paid-fallback code, because the app has no payment processor. If Anton means a specific payment flow (for example the marketing site or App Store purchases), it is added as a lens.
- D-03: "Duplicates of the compliant one in Korea" stays ambiguous (likely speech-to-text; candidate readings: "the component one in core", meaning canonical definitions in `packages/contracts` / `packages/shared`, or the 1031 settings duplicates). T-04 inventories duplicates against canonical definitions under every reading. Clarification is requested only if a concrete merge depends on the reading.
- D-04: Fable 5.1 runs on the `claudeAgent` subscription instance (listed by `orchestrator_capabilities` on October 24, 2026). Devin-hosted Fable variants are paid and excluded. Stricter lane requirements win (1031 UltraCode, 0972/0975 Opus high).
- D-05: The review starts once 1041, 1042, 1046, 1047, 1048 and 1049 have delivered or named their remaining gate. T-01 can run earlier.

- D-06: The read-only review lenses start before the feature gate opens, on `origin/main` `f55a7507e3`, because the open feature PRs do not touch authentication. Repairs wait for the gate (see `reports/gate.md`).

- D-07: Anton approved one-time re-approval on October 24, 2026 ("YES, I allow you to sign in"). Root cause 1 (F-01, F-02) carries a server-established principal. Existing paired devices and sessions whose identity rests only on a client label must be approved once more. Sessions with a server-established principal keep working.

### Open
- None.
