---
increment: 0429-centralized-sync-test
title: Centralized Sync Verification
status: completed
priority: P2
type: experiment
created: 2026-03-05T00:00:00.000Z
---

# Centralized Sync Verification

## Problem Statement

Verify that centralized sync (umbrella.enabled=false) routes all external items to global targets.

## Goals

- Verify GitHub issues go to global repo (anton-abyzov/specweave)
- Verify JIRA ticket goes to global project (SWE2E)
- Verify ADO work item goes to global project (SpecWeaveSync)

## User Stories

### US-001: Centralized GitHub Sync
**Project**: specweave

**As a** developer
**I want** centralized sync to route to the global GitHub repo
**So that** all issues land in the global targets

**Acceptance Criteria**:
- [ ] **AC-US1-01**: GitHub issue created in anton-abyzov/specweave (global config)
- [ ] **AC-US1-02**: JIRA ticket created in SWE2E project (global config)
- [ ] **AC-US1-03**: ADO work item created in SpecWeaveSync project (global config)

## Technical Notes

This test temporarily sets umbrella.enabled=false to verify the centralized fallback path.
