---
status: completed
project: vskill-platform
---
# 0381 — Fix SKILL.md Validation Gap in Submission Pipeline

## Problem

Repos without a `SKILL.md` file are entering the skills database. Two bypass paths exist:

1. **Batch submissions from `discoverFromRepoSearch` skip SKILL.md validation.** The `discoverFromRepoSearch()` function (github-discovery.ts:275) finds repos by GitHub topics/keywords (`topic:claude-code-skill`, `"SKILL.md" in:readme`, etc.) and hardcodes `skillPath: "SKILL.md"` (line 315) without verifying the file exists. These candidates are submitted as a batch (`skills: [...]` array) to `POST /api/v1/submissions`. The batch path at route.ts:441 trusts the array directly and creates submissions without any SKILL.md check, despite the comment claiming "Discovery endpoint already confirmed these SKILL.md files exist."

2. **Internal single-skill fallback bypasses validation.** When `discoverSkillsEnhanced()` returns zero validated skills for an internal request, the fallback at route.ts:481 resets `skillsToSubmit` to the raw body params — no SKILL.md verification applied.

Both paths eventually reach `processSubmission`, which rejects missing SKILL.md, but by then: submission records are created, resources are wasted, and the gap between creation and rejection creates noise in the admin queue.

**Evidence:** `team-mirai-volunteer/action-board` (a Japanese politics app with no SKILL.md, no relevant topics) was found in the production KV listing with `certTier: "SCANNED"`.

## Solution

Close both bypass paths with defense-in-depth SKILL.md validation:

1. Add GraphQL batch verification to `discoverFromRepoSearch` (matching the pattern used by `github-events.js` and `github-graphql-check.js`)
2. Add SKILL.md validation to the batch submission path in the route
3. Restrict the internal fallback to only apply when the external check already passed

## User Stories

### US-001: Repo search discovery verifies SKILL.md before submission
As the system, repos found by topic/keyword search must have their SKILL.md verified before being submitted, so that only genuine skills enter the pipeline.

**Acceptance Criteria:**
- [x] AC-US1-01: `discoverFromRepoSearch` batch-verifies SKILL.md via GitHub GraphQL API before returning candidates
- [x] AC-US1-02: Repos without SKILL.md are excluded from the returned candidates array
- [x] AC-US1-03: GraphQL rate limiting is handled with backoff (matching github-events.js pattern)

### US-002: Batch submission path validates SKILL.md existence
As the system, batch submissions to the submissions route must validate that SKILL.md exists for each skill, so that no unverified skills enter the queue.

**Acceptance Criteria:**
- [x] AC-US2-01: Batch path in POST /api/v1/submissions runs parallel `checkSkillMdExists` for each skill before creating submissions
- [x] AC-US2-02: Skills failing validation are filtered out and logged
- [x] AC-US2-03: If all skills in a batch fail validation, the route returns 422

### US-003: Internal fallback does not bypass SKILL.md validation
As the system, the fallback path for internal requests with zero discovery results must not create submissions for unverified repos.

**Acceptance Criteria:**
- [x] AC-US3-01: The body-params fallback at route.ts:481 only applies to non-internal requests (which already passed `checkSkillMdExists` at line 425)
- [x] AC-US3-02: Internal requests with zero discovery results return 200 with empty `submissions` array (no error, just nothing to submit)

### US-004: npm discovery verifies SKILL.md before submission
As the system, repos found via npm registry should have SKILL.md verified before submission.

**Acceptance Criteria:**
- [x] AC-US4-01: `discoverFromNpm` batch-verifies SKILL.md via GitHub GraphQL API before returning candidates
- [x] AC-US4-02: Repos without SKILL.md are excluded from the returned candidates array

## Non-Goals

- Retroactively cleaning up existing invalid entries (separate task)
- Changing the `checkSkillMdExists` function itself
- Modifying the `/api/v1/submissions/bulk` route (already validates SKILL.md in Phase 1.5)
- Adding validation to `discoverFromCodeSearch` (already finds SKILL.md files by definition)
- Adding validation to crawl-worker sources (github-events.js and github-graphql-check.js already verify via GraphQL)
