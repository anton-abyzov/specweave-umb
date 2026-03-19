---
increment: 0615-init-multi-repo-patterns-loop
title: 'Init: Multi-repo patterns and add-more loop'
type: feature
priority: P1
status: completed
created: 2026-03-19T00:00:00.000Z
structure: user-stories
test_mode: TDD
coverage_target: 90
---

# Feature: Init Multi-Repo Patterns and Add-More Loop

## Overview

Wire the `specweave get` command's bulk/pattern infrastructure into the `specweave init` flow. Add support for glob patterns (e.g., `org/*`, `org/prefix-*`) during init repo connection, and add a "Do you want to add more repositories?" loop so users can clone from multiple organizations in one session. Clone operations run in background.

## User Stories

### US-001: Pattern-Based Repo Connection During Init (P1)
**Project**: specweave

**As a** developer initializing a new SpecWeave workspace
**I want** to enter glob patterns (e.g., `org/*`, `org/service-*`) in the init repo prompt
**So that** I can connect entire organizations or pattern-matched subsets without entering each repo individually

**Acceptance Criteria**:
- [x] **AC-US1-01**: Init repo prompt accepts glob patterns like `org/*` and `org/prefix-*`, resolves them via GitHub API, and launches background clone
- [x] **AC-US1-02**: Individual repo entries (`org/repo`, URLs, SSH) continue to work as before
- [x] **AC-US1-03**: Mixed input (some individual repos, some patterns) in a single prompt is handled correctly — each token is routed to the appropriate path

### US-002: Multi-Organization Add-More Loop (P1)
**Project**: specweave

**As a** developer working with repos across multiple GitHub organizations
**I want** the init flow to ask "Do you want to add more repositories?" after each batch
**So that** I can clone from org-a, then org-b, then personal repos, all in one init session

**Acceptance Criteria**:
- [x] **AC-US2-01**: After each batch of repos is processed, a confirm prompt asks "Do you want to add more repositories?" (default: no)
- [x] **AC-US2-02**: Answering "yes" re-displays the repo prompt for another batch; answering "no" completes the repo connection step
- [x] **AC-US2-03**: All bulk clone operations run in background via `launchCloneJob()` so the user isn't blocked while adding more orgs

### US-003: I18n Support for New Prompts (P2)
**Project**: specweave

**As a** non-English-speaking developer
**I want** the new prompts (pattern hints, add-more, bulk status) to be localized
**So that** the init experience is consistent in my language

**Acceptance Criteria**:
- [x] **AC-US3-01**: New i18n strings added for en, ru, es (matching existing coverage in repo-connect.ts)

## Out of Scope

- Changes to `specweave get` command (already works)
- Interactive org/strategy picker from `github-repo-selector.ts` (Octokit-based, heavier; using lighter `bulk-get.ts` approach)
- Regex pattern support in init (glob is sufficient for init; regex available via `specweave get`)

## Dependencies

- `parseBulkSource()` from `src/cli/helpers/get/bulk-get.ts`
- `buildBulkRepoList()` from `src/cli/helpers/get/bulk-get.ts`
- `getAuthToken()` from `src/cli/helpers/get/bulk-get.ts`
- `launchCloneJob()` from `src/core/background/job-launcher.ts`
