---
id: FS-526
title: "Test JIRA ADO Sync Hierarchy"
status: active
priority: P2
project: specweave-umb
---

# FS-0526: Test JIRA ADO Sync Hierarchy

## Overview

Minimal test increment to verify that user stories appear as child work items under their parent feature/epic in JIRA and ADO after the v1.0.453 sync fixes.

## User Stories

### US-001: Verify sync hierarchy

**Project**: specweave-umb

**As a** SpecWeave user
**I want** user stories to appear as child work items under their parent feature
**So that** JIRA and ADO show proper hierarchy (Epic → Story / Feature → User Story)

#### Acceptance Criteria

- [ ] **AC-US1-01**: Given a feature synced to JIRA, when sync runs, then a Story appears as a child of the Epic in JIRA
- [ ] **AC-US1-02**: Given a feature synced to ADO, when sync runs, then a User Story appears as a child of the Feature in ADO
