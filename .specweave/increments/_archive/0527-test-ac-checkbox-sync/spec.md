---
id: FS-527
title: Test AC Checkbox Sync
status: completed
priority: P2
project: specweave-umb
---

# FS-527: Test AC Checkbox Sync

## Overview

Test increment to verify that:
1. JIRA story descriptions now show native checkboxes (ADF taskItem) for each AC
2. Marking an AC complete in spec.md auto-updates the JIRA story description checkbox
3. Epic → Story hierarchy is intact in JIRA, ADO, and GitHub
4. ADO Issue appears as child of the ADO Epic with correct title

## User Stories

### US-001: Verify JIRA native AC checkboxes

**Project**: specweave-umb

**As a** SpecWeave user
**I want** acceptance criteria in JIRA story descriptions to render as native tickable checkboxes
**So that** I can track AC progress directly inside the JIRA issue without leaving the tool

#### Acceptance Criteria

- [x] **AC-US1-01**: Given a feature synced to JIRA, when the story description is viewed, then each AC appears as a native JIRA checkbox (ADF taskItem) not plain bullet text
- [x] **AC-US1-02**: Given an AC is marked [x] in spec.md, when the AC status hook fires, then the corresponding JIRA story description checkbox is flipped to DONE automatically
- [x] **AC-US1-03**: Given the JIRA story description, when Priority and Status fields are rendered, then they appear on separate lines (not fused as "Priority: P1Status: done")

### US-002: Verify full hierarchy across platforms

**Project**: specweave-umb

**As a** SpecWeave user
**I want** the feature hierarchy (Epic → Story in JIRA, Feature → Issue in ADO, Milestone → Issue in GitHub) to be correct
**So that** work items are navigable and properly nested in all three platforms

#### Acceptance Criteria

- [x] **AC-US2-01**: Given a feature synced to JIRA, when the Epic is viewed, then the linked Story appears as a child work item under it
- [x] **AC-US2-02**: Given a feature synced to ADO, when the Epic is viewed, then the linked Issue appears as a child work item under it
- [x] **AC-US2-03**: Given a feature synced to GitHub, when the Milestone is viewed, then the linked Issue is associated with the correct milestone
