---
increment: 0643-init-repo-clone-flow
title: Fix init repo cloning prompt flow
type: bug
priority: P1
status: completed
created: 2026-03-23T00:00:00.000Z
structure: user-stories
test_mode: TDD
coverage_target: 90
---

# Bug Fix: init repo cloning prompt flow

## Overview

`specweave init` has three interconnected bugs that prevent users from cloning child repositories during initialization in brownfield directories. The repo cloning infrastructure (`promptProjectSetup` + `promptRepoUrlsLoop`) exists and works, but control flow gaps in `init.ts` mean it's never reached.

## User Stories

### US-001: Clone from GitHub sub-choice must trigger cloning (P1)
**Project**: specweave

**As a** developer initializing a SpecWeave workspace in a non-empty folder
**I want** the "Clone from GitHub" migration sub-choice to actually clone repositories
**So that** I can add child repos during init without running `specweave get` separately

**Acceptance Criteria**:
- [x] **AC-US1-01**: Selecting "Clone from GitHub" in the start-empty sub-menu calls `promptRepoUrlsLoop` to accept repo URLs/patterns
- [x] **AC-US1-02**: After cloning via sub-menu, the post-scaffold prompt does NOT re-ask about repos
- [x] **AC-US1-03**: The "Copy local" sub-choice also prevents the post-scaffold re-ask

---

### US-002: Brownfield directories with .git must show repo prompt (P1)
**Project**: specweave

**As a** developer running `specweave init` in an existing git repository with no child repos
**I want** to be asked about cloning repositories regardless of `.git` existence
**So that** I can set up my workspace with repos during init

**Acceptance Criteria**:
- [x] **AC-US2-01**: Post-scaffold repo prompt fires when `repositories/` is empty, even if `.git` exists
- [x] **AC-US2-02**: Post-scaffold repo prompt is skipped when `repositories/` already has child repos
- [x] **AC-US2-03**: Greenfield directories (no `.git`) continue to show the prompt as before

---

### US-003: Umbrella "No" must not block child repo prompt (P1)
**Project**: specweave

**As a** developer who declines connecting the workspace root to GitHub
**I want** to still be asked about cloning child repositories
**So that** the umbrella connection question and child repo question are independent

**Acceptance Criteria**:
- [x] **AC-US3-01**: Answering "No" to "Connect workspace root to GitHub?" does not prevent the child repo cloning prompt from appearing

## Out of Scope

- Smart org discovery (auto-detecting GitHub org from remote URL and offering repo picker)
- Wiring in the unused `prompt-flow.ts` redesign
- Changes to `repo-connect.ts`, `workspace-setup.ts`, or `root-repo-detection.ts`

## Dependencies

- `promptRepoUrlsLoop` from `repo-connect.ts` (already exists, no changes needed)
- `promptProjectSetup` from `repo-connect.ts` (already exists, no changes needed)
