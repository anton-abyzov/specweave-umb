---
increment: 0417J-update-cli-help-umbrella
title: "E2E Test: Update CLI help text for umbrella commands"
type: feature
priority: P2
status: completed
created: 2026-03-03
structure: user-stories
test_mode: TDD
coverage_target: 90
external_ref: "jira#SWE2E#SWE2E-6"
project: specweave
---

# Update CLI Help Text for Umbrella Commands

## Problem Statement

The `migrate-to-umbrella` CLI command's help text does not document the `--consolidate` flag or the distributed/centralized sync strategy modes, making it difficult for users to discover these features.

## User Stories

### US-001: Update migrate-to-umbrella Help Text
**Project**: specweave
**As a** SpecWeave user
**I want** the `migrate-to-umbrella --help` output to document the `--consolidate` flag and sync strategy modes
**So that** I can discover and use these features without consulting external docs

**Acceptance Criteria**:
- [x] **AC-US1-01**: Given `specweave migrate-to-umbrella --help` is run, when the output is displayed, then it includes `--consolidate` with a description of consolidating orphaned increments
- [x] **AC-US1-02**: Given the CLI help is displayed, when a user reads it, then it mentions distributed vs centralized sync strategy modes

## Out of Scope

- Changes to the actual consolidation logic
- Changes to sync routing behavior
