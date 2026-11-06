# Allow a machine to run work here with clear file-transfer permissions

## Problem

On M4, Connected to M1 describes app connectivity and Allow workers on M1 grants M4 outgoing access. Neither grants M1 incoming access to M4. Who can run work here only edits existing grants, leaving users unable to initiate the direction they want from the destination. Android signing-secret transfer additionally depends on coordinator ownership, approved folders, full-access self grants and per-file owner approval. No actual failed transfer was supplied.

## Scope

In: source-grounded diagnosis, actionable direction-specific guidance, an explicit incoming-worker setup action for an already connected owned machine using existing authenticated invitation and grant APIs, regression and headless UI checks, PR, merge, owner-coordinated release and acceptance.

Out: automatic live grants, secret reads, transfers without owner approval, broadening worker-to-third-machine delegation, new authentication protocols, unrelated update permission changes. Increment 1201 retains its already shipped connection presentation scope.

## Acceptance Criteria

- [ ] AC-01: The report separates connectivity, incoming/outgoing work permission, coordinator-only file transfer and per-secret approval; gives the exact current M1-to-M4 setup steps and does not invent a transfer failure.
- [ ] AC-02: Who can run work here offers an explicit named-machine action, with direction and access clear before confirmation, using existing authenticated APIs. Missing Manage access, offline state and setup failure explain the next step; no grant is made on render.
- [ ] AC-03: Existing revocation, project/account limits and secret approval remain enforced. Tests cover direction, authorization, failure and partial setup without claiming success.
- [ ] AC-04: Production web build and focused tests pass; headless screenshots are saved; fresh review and required CI pass; the change merges and ships through the existing release owner with acceptance and worktree cleanup recorded.

## Approach

Add incoming setup beside MachineWorkGrants, reusing authenticated per-environment fleet reads, addVisibleMachineToStudioFleet and allowStudioFleetWorkers. Select the coordinator as the remote environment and this machine as the worker destination; never invert those arguments. Existing server-side grants remain authoritative. Use explicit confirmation for setup and retain separate per-file secret approval. Preserve team-rule restrictions and fail closed on unreadable fleet or missing identity. Do not modify the shared checkout.

## Decisions

### Asked
- User requested M1 access to work on M4 and a shipped UI/grant-flow fix. Coordinator confirmed no other active owner of MachineWorkGrants or FleetWorkerGrants.

### Defaulted
- New increment because creating incoming grants is outside 1201's presentation-only scope.
- Reuse existing authenticated APIs rather than create another credential protocol. No live grant changes during verification.
- Preserve existing access defaults and offer the access selector before the user confirms.

### Open
- No actual transfer error or M1 thread was supplied; diagnosis is bounded to source gates and supplied screenshots.

## Tasks

### T-01 Diagnose directional access and plan incoming setup
- AC: AC-01 | Files: reports/diagnosis.md | Test: source-linked explanation and current fleet readback

### T-02 Add incoming-worker setup and permission regression coverage
- AC: AC-02, AC-03 | Files: repositories/anton-abyzov/specwithcode-dev/apps/web/src/components/settings/MachineWorkGrants.tsx, repositories/anton-abyzov/specwithcode-dev/apps/web/src/components/settings/MachineWorkGrants.test.tsx, repositories/anton-abyzov/specwithcode-dev/apps/web/src/components/settings/IncomingWorkerSetup.tsx, repositories/anton-abyzov/specwithcode-dev/apps/web/src/components/settings/IncomingWorkerSetup.test.tsx, repositories/anton-abyzov/specwithcode-dev/docs/studio/incoming-work-access.md | Test: focused settings and incoming setup tests

### T-03 Verify and deliver the UI
- AC: AC-04 | Files: repositories/anton-abyzov/specwithcode-dev/apps/web/tests/incoming-worker-access, reports/verification.md, reports/review.md, reports/delivery.md | Test: focused suites, production web build, headless screenshots, exact-head review, hosted CI and release inclusion

### T-04 Verify and close 1205
- AC: AC-01, AC-02, AC-03, AC-04 | Files: reports/closure.md | Test: specweave verify, fresh-context review, then specweave complete
