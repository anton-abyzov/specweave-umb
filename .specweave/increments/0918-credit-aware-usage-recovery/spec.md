# 0918 Credit-aware usage recovery

## Problem
Included plan exhaustion appears as total unavailability despite funded credits; old timeline warnings remain active after continuation.

## Scope
Credit balance and explicit one-request continuation, resolved historical warnings, user instructions, focused tests, headless visual checks, builds, and coordinated successor release of completed mainline fixes.

## Acceptance Criteria
- [ ] AC-01: A funded eligible Codex account exposes its balance and explicit Continue using credits action with existing account/model/freshness checks.
- [ ] AC-02: A later started run resolves the earlier usage warning; queued or pre-start failed requests do not.
- [ ] AC-03: Instructions and regression/headless checks cover credits, unavailable permissions, and recovery.
- [ ] AC-04: Reviewed source is released and deployment readback records exact version; manual UI acceptance remains explicit.

## Approach
Isolated product checkout /Users/antonabyzov/Projects/github/studio-credit-recovery at origin/main 4d6e30488. Preserve other owners including pending 1.0.14. New credit continuation is an explicit foreground submission in the same chat; no persistent spend permission. Extract new behavior into small modules rather than adding logic to oversized legacy components. Browser automation is headless with PWDEBUG=0 and PLAYWRIGHT_HTML_OPEN=never. Node22.20 scoped; no shared toolchain changes.

## Tasks
### T-01 Implement and verify credit recovery
- AC: AC-01, AC-02, AC-03 | Files: /Users/antonabyzov/Projects/github/studio-credit-recovery/apps/web/src/components/chat/, /Users/antonabyzov/Projects/github/studio-credit-recovery/apps/web/src/components/ChatView.tsx, /Users/antonabyzov/Projects/github/studio-credit-recovery/apps/web/tests/usage-limit-recovery/, /Users/antonabyzov/Projects/github/studio-credit-recovery/docs/user/usage.md | Test: focused credit, recovery and timeline tests; headless visual fixture; web/server build
### T-02 Review and release completed fixes
- AC: AC-04 | Files: /Users/antonabyzov/Projects/github/studio-credit-recovery/CHANGELOG.md, /Users/antonabyzov/Projects/github/studio-credit-recovery/apps/*/package.json, /Users/antonabyzov/Projects/github/studio-credit-recovery/packages/contracts/package.json, .specweave/increments/0918-credit-aware-usage-recovery/reports/ | Test: release asset and deployed version readback

### T-03 Live funded-account credit continuation and manual acceptance
- AC: AC-01, AC-04 | Files: .specweave/increments/0918-credit-aware-usage-recovery/reports/ | Test: Anton confirms, on an installed release with a funded eligible Codex account, the balance and explicit Continue using credits action, and accepts the recovery UI

Added 2026-10-15 at close-out. Shipped in 1.0.19 (see reports/release-readback.md). The installed M4 account has no funded balance, so no live credits evidence exists yet.
