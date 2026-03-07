---
increment: 0444-filter-framework-plugin-skills
title: "Filter Framework Plugin Skills from Marketplace"
type: bug
priority: P0
status: active
created: 2026-03-07
structure: user-stories
test_mode: TDD
coverage_target: 90
---

# Feature: Filter Framework Plugin Skills from Marketplace

## Problem Statement

The vskill-platform scanner discovers SKILL.md files from `anton-abyzov/specweave` and publishes 40+ framework-bundled skills (e.g., brainstorm, pm, architect) as community marketplace entries. These live under `plugins/specweave*/skills/` paths and are part of the SpecWeave framework itself -- they should never appear in the community marketplace.

Root cause: `isAgentConfigPath()` in `skill-path-validation.ts` only filters agent/IDE config directories (`.claude/`, `.cursor/`, etc.). No filter exists for `plugins/specweave*/skills/` framework plugin paths.

## Goals

- Prevent framework-bundled skills from being indexed or published to the marketplace
- Clean up the 40+ misclassified entries already in the database
- Maintain defense-in-depth by filtering at all ingestion points (TS platform + JS crawl-worker)

## User Stories

### US-001: Framework Plugin Path Filter (P0)
**Project**: vskill-platform

**As a** marketplace maintainer
**I want** SKILL.md files under `plugins/specweave*/skills/` to be rejected by the path validation layer
**So that** framework-bundled skills never enter the community marketplace

**Acceptance Criteria**:
- [ ] **AC-US1-01**: Given a path matching `^plugins/specweave[^/]*/skills/`, when `isFrameworkPluginPath()` is called, then it returns `true`
- [ ] **AC-US1-02**: Given a path like `plugins/community-tool/skills/foo/SKILL.md` (not specweave-prefixed), when `isFrameworkPluginPath()` is called, then it returns `false`
- [ ] **AC-US1-03**: Given edge-case inputs (empty string, backslashes, leading slashes), when `isFrameworkPluginPath()` is called, then it normalizes and handles them without error
- [ ] **AC-US1-04**: Given a framework plugin path, when `frameworkPluginRejectionReason()` is called, then it returns a human-readable reason string

---

### US-002: Unified Rejection Wrapper (P0)
**Project**: vskill-platform

**As a** platform developer
**I want** a single `shouldRejectSkillPath()` function that combines agent-config and framework-plugin checks
**So that** call sites use one function for all path rejection logic

**Acceptance Criteria**:
- [ ] **AC-US2-01**: Given a path inside `.claude/skills/`, when `shouldRejectSkillPath()` is called, then it returns `true` (agent-config rejection still works)
- [ ] **AC-US2-02**: Given a path inside `plugins/specweave/skills/`, when `shouldRejectSkillPath()` is called, then it returns `true` (framework-plugin rejection works)
- [ ] **AC-US2-03**: Given a legitimate skill path like `skills/frontend/SKILL.md`, when `shouldRejectSkillPath()` is called, then it returns `false`
- [ ] **AC-US2-04**: `isAgentConfigPath()` remains exported for backward compatibility; `shouldRejectSkillPath()` is the recommended entrypoint

---

### US-003: Migrate TypeScript Call Sites (P0)
**Project**: vskill-platform

**As a** platform developer
**I want** all 8 TypeScript call sites to use `shouldRejectSkillPath()` instead of `isAgentConfigPath()`
**So that** framework plugin paths are filtered at every ingestion point in the platform

**Acceptance Criteria**:
- [ ] **AC-US3-01**: Given `src/lib/scanner.ts` (2 call sites), when the scanner encounters a framework plugin path, then it is rejected
- [ ] **AC-US3-02**: Given `src/app/api/v1/submissions/route.ts` (2 call sites), when a submission has a framework plugin path, then it is rejected with a reason
- [ ] **AC-US3-03**: Given `src/app/api/v1/submissions/bulk/route.ts` (1 call site), when a bulk submission contains framework plugin paths, then those entries are rejected
- [ ] **AC-US3-04**: Given `src/lib/crawler/github-discovery.ts` (2 call sites), when discovery finds a framework plugin SKILL.md, then it is skipped
- [ ] **AC-US3-05**: Given `src/lib/crawler/vendor-org-discovery.ts` (1 call site), when vendor org scan finds a framework plugin path, then it is skipped

---

### US-004: Update Crawl-Worker JS Copies (P0)
**Project**: vskill-platform

**As a** platform developer
**I want** all 4 crawl-worker JavaScript files to include framework plugin filtering
**So that** the crawl workers (running on Hetzner VMs) also reject framework plugin paths

**Acceptance Criteria**:
- [ ] **AC-US4-01**: Given `crawl-worker/lib/repo-files.js`, when updated, then it exports `isFrameworkPluginPath()` and `shouldRejectSkillPath()` alongside existing exports
- [ ] **AC-US4-02**: Given `crawl-worker/lib/skill-discovery.js`, when updated, then it imports and uses `shouldRejectSkillPath` from `repo-files.js`
- [ ] **AC-US4-03**: Given `crawl-worker/sources/queue-processor.js`, when updated, then it has an inline `isFrameworkPluginPath()` and combined check (does not import from repo-files)
- [ ] **AC-US4-04**: Given `crawl-worker/sources/vendor-org-discovery.js`, when updated, then it has an inline framework plugin regex and combined check (does not import from repo-files)

---

### US-005: Clean Up Existing Misclassified DB Entries (P1)
**Project**: vskill-platform

**As a** marketplace maintainer
**I want** existing framework plugin entries removed from the marketplace
**So that** users only see legitimate community skills

**Acceptance Criteria**:
- [ ] **AC-US5-01**: Given submissions with `skillPath` matching `plugins/specweave*/skills/`, when the cleanup script runs, then their state is set to REJECTED with reason `framework_plugin`
- [ ] **AC-US5-02**: Given published Skill rows linked to those submissions, when the cleanup script runs, then the Skill rows are hard-deleted from the database
- [ ] **AC-US5-03**: The cleanup script logs how many submissions were rejected and how many Skill rows were deleted
- [ ] **AC-US5-04**: The cleanup script is idempotent -- running it twice produces no additional changes

---

### US-006: Update Existing Tests (P1)
**Project**: vskill-platform

**As a** platform developer
**I want** the test suite updated to cover framework plugin filtering and to fix tests using `plugins/specweave/` as legitimate test data
**So that** tests validate the new behavior and do not produce false passes

**Acceptance Criteria**:
- [ ] **AC-US6-01**: Given `skill-path-validation.test.ts`, when run, then it includes tests for `isFrameworkPluginPath()`, `shouldRejectSkillPath()`, and `frameworkPluginRejectionReason()`
- [ ] **AC-US6-02**: Given the existing test case `accepts plugins/*/skills/*/SKILL.md` that asserts `isAgentConfigPath("plugins/specweave/skills/do/SKILL.md")` returns `false`, when updated, then it reflects the new expected behavior (rejected by `shouldRejectSkillPath`)
- [ ] **AC-US6-03**: Given `multi-skill-expand.test.ts` which uses `plugins/specweave/skills/` paths as test data, when updated, then test data uses non-specweave paths or the test accounts for rejection

## Out of Scope

- Broader pattern matching for non-SpecWeave framework plugins (`plugins/*/skills/` generalized)
- KV cleanup (skills are not stored in KV)
- Filtering `plugins/specweave*/commands/` paths (scanner only indexes SKILL.md, not found under commands/)
- UI changes to the marketplace frontend

## Technical Notes

### Dependencies
- `src/lib/skill-path-validation.ts` -- primary filter module
- Prisma DB (Submission and Skill tables) for cleanup script
- 4 crawl-worker JS files deployed to 3 Hetzner VMs

### Constraints
- Regex must be SpecWeave-specific: `^plugins/specweave[^/]*/skills/` -- no broad patterns
- `isAgentConfigPath()` must remain exported (backward compat)
- Crawl-worker `queue-processor.js` and `vendor-org-discovery.js` use inline copies, not imports

### Architecture Decisions
- Two-function design: `isFrameworkPluginPath()` (new) + `isAgentConfigPath()` (existing) composed by `shouldRejectSkillPath()`
- Cleanup uses soft-reject for submissions (audit trail) but hard-delete for Skill rows (should not exist)

## Success Metrics

- 0 framework plugin skills visible in marketplace after cleanup
- 0 new framework plugin submissions accepted after filter deployment
- All 12 call sites (8 TS + 4 JS) using the new combined filter
