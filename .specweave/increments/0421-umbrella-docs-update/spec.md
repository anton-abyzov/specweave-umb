---
increment: 0421-umbrella-docs-update
title: "Update umbrella project documentation"
type: feature
priority: P2
status: completed
created: 2026-03-03
project: specweave-umb
structure: user-stories
test_mode: TDD
coverage_target: 90
total_stories: 1
total_acs: 2
checked_acs: 2
---

# Feature: Update umbrella project documentation

## Overview

Update the umbrella project's README and configuration documentation to reflect the new distributed sync, consolidation, and umbrella-aware project routing features.

## User Stories

### US-001: Update Umbrella Documentation (P2)
**Project**: specweave-umb

**As a** SpecWeave umbrella user
**I want** the umbrella README to document distributed sync and consolidation
**So that** I can understand how multi-repo sync routing works

**Acceptance Criteria**:
- [x] **AC-US1-01**: Given the umbrella README, when a user reads it, then it describes distributed vs centralized sync modes
- [x] **AC-US1-02**: Given the umbrella project config, when umbrella.projectName is set, then living docs route to a distinct umbrella folder

## Out of Scope

- Changes to sync routing logic
- Changes to consolidation engine
