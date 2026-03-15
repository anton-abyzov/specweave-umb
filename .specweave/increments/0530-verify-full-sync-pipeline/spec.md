---
id: FS-530
title: "Verify Full Sync Pipeline — All 3 Platforms + AC Comments"
status: active
priority: P1
project: specweave-umb
---

# FS-530: Verify Full Sync Pipeline — All 3 Platforms + AC Comments

## Overview

End-to-end verification that the full AC sync pipeline works automatically across GitHub, JIRA, and ADO. Specifically verify that:
1. AC completion automatically posts progress comments to all three platforms
2. No excessive API calls to any platform (GitHub, JIRA, ADO)
3. All checkboxes flip correctly when tasks complete

## User Stories

### US-001: AC completion auto-posts comments to all platforms

**Project**: specweave-umb

**As a** SpecWeave user
**I want** AC completion to automatically post progress comments to GitHub, JIRA, and ADO stories
**So that** stakeholders on any platform see real-time AC progress without manual updates

#### Acceptance Criteria

- [x] **AC-US1-01**: Given a task marked complete in tasks.md, when the AC status hook fires, then a progress comment is posted to the linked GitHub issue showing which ACs are done
- [x] **AC-US1-02**: Given a task marked complete in tasks.md, when the AC status hook fires, then a progress comment is posted to the linked JIRA story showing AC completion percentage
- [x] **AC-US1-03**: Given a task marked complete in tasks.md, when the AC status hook fires, then a progress comment is posted to the linked ADO work item showing AC completion percentage

### US-002: Verify no excessive API calls during sync

**Project**: specweave-umb

**As a** SpecWeave user
**I want** sync operations to use minimal API calls
**So that** rate limits are not exhausted by normal operations

#### Acceptance Criteria

- [x] **AC-US2-01**: Given sync-living-docs runs for this increment, when checking rate limit before and after, then fewer than 100 GitHub API calls are used for an update (not creation) cycle
- [x] **AC-US2-02**: Given the AC status hook fires, when checking JIRA API calls, then no more than 4 calls per user story are made (1 fetch + 1 update + 0-1 comment)
