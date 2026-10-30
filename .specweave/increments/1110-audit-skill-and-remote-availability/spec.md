# Audit skill and remote availability

## Problem
Settings > Connections displays On and Skills on from configuration. Those labels do not establish that instructions were loaded, tools registered, accounts authorized, or the same capability exists on a remote machine. Anton reports skills that do not work.

## Scope
In: read-only audit of filesystem skills, native plugins, account connectors, configured MCP servers, provider dispatch, OS-bound tools and per-machine propagation; representative failures and installed evidence; focused repair of verified misreporting within Connections.
Out: duplicate 1091/1093 work, migration changes, remote execution, installs, credentials, grants, live-session restart, external writes, release.

## Acceptance Criteria
- [ ] AC-01: A source-backed local/remote matrix separates declared configuration, discovered instructions, runtime tools, authentication, machine grants and OS support, with unknown states explicit.
- [ ] AC-02: Representative failures are traced through current invocation paths and reconciled with existing fixes and installed evidence.
- [ ] AC-03: Verified Connections misreporting is corrected with focused tests, or existing fixes and a precise remaining limitation are documented.
- [ ] AC-04: Focused validation and a fresh-context review support the report; verify and complete are attempted with exact gate outcomes recorded.

## Approach
Read current owners and 0978/1091/1093 history first. Inspect NativeConnectionDiscovery, ConnectionMatrix, provider skill discovery and dispatch, managed runtime homes and fleet boundaries. Use existing read-only fleet metadata and current tool inventory without starting provider turns. Preserve the dirty shared app checkout. If repair is needed, use an isolated registered worktree under the configured app worktree root. Deliver reports in this increment, then review in a fresh context.

## Decisions
### Asked
- None. The user requested the audit and narrow verified fixes.
### Defaulted
- D-01: No broad capability platform rebuild. Prefer truthful configuration labels and explicit unverified runtime state.
- D-02: Remote inventories without an allowed read-only probe remain unknown.
### Open
- None.

## Tasks
### T-01 Audit declarations, dispatch and representative failures
- AC: AC-01, AC-02 | Files: reports/audit.md | Test: source citations and read-only receipt review

### T-02 Repair verified misreporting and validate
- AC: AC-03 | Files: specweave-studio/apps/web/src/components/connections/ConnectionMatrix.tsx, specweave-studio/apps/web/src/components/connections/ConnectionMatrix.test.tsx, specweave-studio/apps/web/tests/connections-library/mocks.tsx, reports/validation.md | Test: focused ConnectionMatrix tests and production web build

### T-03 Verify and close 1110
- AC: AC-04 | Files: reports/review.md, reports/validation.md | Test: specweave verify 1110; fresh-context review; specweave complete 1110
