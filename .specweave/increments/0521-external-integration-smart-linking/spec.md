---
increment: 0521-external-integration-smart-linking
title: External Integration Health Check & Smart Linking
type: feature
priority: P1
status: completed
created: 2026-03-13T00:00:00.000Z
structure: user-stories
test_mode: TDD
coverage_target: 90
---

# Feature: External Integration Health Check & Smart Linking

## Overview

Enhance SpecWeave's external integration pipeline by wiring health checks into the sync-setup flow, integrating external ticket keys into branch naming, adding a standalone `sync-health` CLI command, and auto-triggering PR-to-ticket linking during PR-based closure. Most building blocks already exist (`integration-health-check.ts`, `resolveExternalBranchPrefix()`, `pr-linker.ts`, `link-pr` command) — this increment connects them into a cohesive, production-ready workflow.

## User Stories

### US-001: Integration Health Check at Setup Time (P1)
**Project**: specweave

**As a** developer setting up external sync
**I want** SpecWeave to automatically run health checks after sync-setup completes
**So that** I catch misconfigurations (wrong credentials, missing permissions, invalid project keys) immediately, not during the first sync attempt

**Acceptance Criteria**:
- [x] **AC-US1-01**: When `specweave sync-setup` completes successfully, integration health checks run automatically for the configured provider(s) and results are displayed
- [x] **AC-US1-02**: Health check results include actionable fix suggestions for each failing check (e.g., "Grant Edit Issues permission in JIRA project settings")
- [x] **AC-US1-03**: A standalone `specweave sync-health` CLI command runs health checks on-demand and returns exit code 0 for healthy, 1 for failures

---

### US-002: Branch Naming with External Ticket Keys (P1)
**Project**: specweave

**As a** developer working with JIRA or ADO
**I want** increment branches to include the external ticket key (e.g., `PROJ-123/sw/0521-smart-linking`)
**So that** JIRA/ADO smart commits and CI integrations can auto-link branches to tickets

**Acceptance Criteria**:
- [x] **AC-US2-01**: When `cicd.git.includeExternalKey` is true and an increment has an external ticket, the branch name includes the ticket key as a prefix (format: `{ticketKey}/{branchPrefix}{incrementId}`)
- [x] **AC-US2-02**: When no external ticket exists or the setting is disabled, branch naming falls back to the existing `{branchPrefix}{incrementId}` format
- [x] **AC-US2-03**: JIRA keys use the format `PROJ-123` and ADO keys use the format `AB#123` in branch names

---

### US-003: Automatic PR-to-Ticket Linking on PR Creation (P1)
**Project**: specweave

**As a** developer using pr-based push strategy
**I want** SpecWeave to automatically add remote links (JIRA) and hyperlinks (ADO) when a PR is created during increment closure
**So that** external tickets are bidirectionally linked to PRs without manual `specweave link-pr` invocation

**Acceptance Criteria**:
- [x] **AC-US3-01**: When pr-based closure creates a PR and the increment has JIRA external refs, `addRemoteLink` is called automatically for each JIRA issue
- [x] **AC-US3-02**: When pr-based closure creates a PR and the increment has ADO external refs, `addHyperlink` is called automatically for each ADO work item
- [x] **AC-US3-03**: Link failures are logged as warnings but do not block PR creation or increment closure

---

### US-004: Standalone Sync Health Command (P2)
**Project**: specweave

**As a** DevOps engineer
**I want** a `specweave sync-health` command that validates all configured integrations
**So that** I can include it in CI pipelines and scheduled checks to detect credential expiration or permission changes

**Acceptance Criteria**:
- [x] **AC-US4-01**: `specweave sync-health` checks all enabled providers (GitHub, JIRA, ADO) and displays results in a structured format
- [x] **AC-US4-02**: The command supports `--json` flag for machine-readable output suitable for CI pipelines
- [x] **AC-US4-03**: Exit code is 0 when all checks pass, 1 when any check fails, 2 when no providers are configured

## Technical Notes

- `integration-health-check.ts` already implements `checkJiraIntegration()`, `checkAdoIntegration()`, `checkGitHubIntegration()` and `formatHealthCheckResults()` — no new health check logic needed
- `pr-linker.ts` already implements `linkPrToExternalTickets()` and `resolveExternalBranchPrefix()` — need to wire into PR creation flow
- `jira-client.ts` has `addRemoteLink()`, `ado-client.ts` has `addHyperlink()` — both fully implemented
- Branch creation happens in the CI/CD module via `GitConfig.branchPrefix` — need to extend with external key integration
- `sync-setup.ts` delegates to `setupIssueTracker()` — health checks should run after successful setup

## Out of Scope

- New health check types beyond what `integration-health-check.ts` already provides
- Automatic retry/healing of failed health checks
- Branch naming for non-PR workflows (direct push)
- GitHub remote links (GitHub already auto-links PRs to issues)

## Dependencies

- `src/sync/integration-health-check.ts` (existing)
- `src/sync/pr-linker.ts` (existing)
- `src/integrations/jira/jira-client.ts` → `addRemoteLink()` (existing)
- `plugins/specweave-ado/lib/ado-client.ts` → `addHyperlink()` (existing)
- `src/core/config/types.ts` → `GitConfig` (existing, needs extension)
