---
increment: 0852-external-sync-architecture-audit
title: "External Sync Architecture Audit and Hardening"
type: refactor
priority: P1
status: active
created: 2026-05-25
structure: user-stories
test_mode: TDD
coverage_target: 90
---

# Feature: External Sync Architecture Audit and Hardening

## Overview

Audit SpecWeave analytics, credential handling, and external tool sync paths for GitHub, Jira, and Azure DevOps. Fix confirmed routing or credential defects in the `specweave` child repo, run local verification, and write a redacted architecture report under this increment.

## User Stories

### US-001: External Sync Architecture Reviewed (P1)
**Project**: specweave

**As a** SpecWeave maintainer
**I want** the GitHub/Jira/ADO sync architecture reviewed against ADRs and runtime code
**So that** the implementation matches the intended umbrella and per-project routing model.

**Acceptance Criteria**:
- [x] **AC-US1-01**: The report maps current runtime entry points for analytics, sync-progress, sync-health, issue creation, AC progress, and reconciliation.
- [x] **AC-US1-02**: The report identifies architecture gaps between accepted ADRs and shipping code, especially duplicated old/new sync paths.
- [x] **AC-US1-03**: Confirmed defects are either fixed or explicitly recorded with reason, risk, and next action.

---

### US-002: Secret and Credential Handling Audited (P1)
**Project**: specweave

**As a** SpecWeave maintainer
**I want** repository and Obsidian credential surfaces audited without exposing values
**So that** reports and tests stay secret-safe while credential gaps are visible.

**Acceptance Criteria**:
- [x] **AC-US2-01**: Repository and relevant Obsidian credential paths are scanned for token-like patterns, with values redacted from all output.
- [x] **AC-US2-02**: External tool commands accept the documented environment variable names for GitHub, Jira, and ADO credentials.
- [x] **AC-US2-03**: The final report contains no secret values and names only variables, files, and pass/fail status.

---

### US-003: Local Verification and Release Readiness (P1)
**Project**: specweave

**As a** release owner
**I want** the audited fixes verified locally before any release or deploy action
**So that** external sync changes do not ship untested.

**Acceptance Criteria**:
- [x] **AC-US3-01**: Focused unit tests cover every code fix.
- [x] **AC-US3-02**: Local build, unit tests, integration tests, e2e tests, and coverage are run or blockers are documented.
- [x] **AC-US3-03**: Release, push, and deploy status is reported truthfully, including any blockers from dirty worktrees, missing credentials, or failed gates.

## Functional Requirements

### FR-001: Routing Source of Truth
External sync routing must prefer per-user-story `**Project**:` fields and metadata project values over removed top-level frontmatter `project`.

### FR-002: Credential Alias Consistency
Health checks and sync commands must support the same credential variable names used by the provider adapters.

### FR-003: Redacted Reporting
Reports may include file paths, variable names, and status, but never credential values.

## Success Criteria

- Confirmed code defects are fixed with focused tests.
- Architecture report is saved under `reports/`.
- Test results and release/deploy blockers are explicit.
- No secret value is printed, committed, or written to a report.

## Out of Scope

- Rewriting the full sync engine in this increment.
- Publishing packages without passing local gates and having required credentials.
- Modifying unrelated dirty files in root, `vskill`, or `vskill-platform`.

## Dependencies

- `repositories/anton-abyzov/specweave`
- ADR-0211, ADR-0234, ADR-0235, ADR-0242, ADR-0246, ADR-0247
- Local `.env*` files and Obsidian credential notes, scanned only with redaction
