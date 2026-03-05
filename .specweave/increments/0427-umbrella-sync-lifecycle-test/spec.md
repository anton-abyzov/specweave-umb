---
status: completed
---
# Umbrella Sync Lifecycle Test

**Type**: Feature
**Priority**: P2
**Complexity**: Low

## Overview

End-to-end lifecycle test for umbrella cross-project sync. Tests that creating an increment with cross-project user stories automatically syncs to GitHub, JIRA, and ADO per child repo.

## User Stories

### US-SPE-001: Specweave CLI Version Display
**Project**: specweave

**As a** developer
**I want** to see the specweave version in sync output
**So that** I can verify which version is running

#### Acceptance Criteria
- [x] **AC-SPE-US1-01**: Sync output includes specweave version number
- [x] **AC-SPE-US1-02**: Version matches package.json

### US-VSK-001: VSkill Sync Routing Verification
**Project**: vskill

**As a** developer
**I want** sync to route to vskill repo
**So that** GitHub issues appear in anton-abyzov/vskill

#### Acceptance Criteria
- [x] **AC-VSK-US1-01**: GitHub milestone created in vskill repo
- [x] **AC-VSK-US1-02**: GitHub issue created with [FS-427][US-VSK-001] title

### US-VPL-001: VSkill-Platform Sync Routing Verification
**Project**: vskill-platform

**As a** developer
**I want** sync to route to vskill-platform repo
**So that** GitHub issues appear in anton-abyzov/vskill-platform

#### Acceptance Criteria
- [x] **AC-VPL-US1-01**: GitHub milestone created in vskill-platform repo
- [x] **AC-VPL-US1-02**: GitHub issue created with [FS-427][US-VPL-001] title
