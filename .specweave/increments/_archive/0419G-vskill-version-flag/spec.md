---
increment: 0419G-vskill-version-flag
title: Add --version flag to vskill CLI
type: feature
priority: P2
status: completed
created: 2026-03-03T00:00:00.000Z
project: vskill
structure: user-stories
test_mode: TDD
coverage_target: 90
total_stories: 1
total_acs: 2
checked_acs: 2
---

# Feature: Add --version flag to vskill CLI

## Overview

Imported from GitHub: anton-abyzov/vskill#2

The vskill CLI should support a `--version` flag that outputs the current version number from package.json.

## User Stories

### US-001: Version Flag Support (P2)
**Project**: vskill

**As a** vskill CLI user
**I want** to run `vskill --version` to see the current version
**So that** I can verify which version is installed

**Acceptance Criteria**:
- [x] **AC-US1-01**: Running `vskill --version` outputs the version from package.json
- [x] **AC-US1-02**: The version output format is just the version number (e.g., `0.2.20`)
