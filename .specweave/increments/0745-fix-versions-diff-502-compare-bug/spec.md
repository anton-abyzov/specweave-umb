---
increment: 0745-fix-versions-diff-502-compare-bug
title: Fix Skill Studio Versions tab compare → 502 Bad Gateway
type: bug
priority: P1
status: completed
created: 2026-04-26T00:00:00.000Z
structure: user-stories
test_mode: TDD
coverage_target: 90
---

# Feature: Fix Skill Studio Versions tab compare → 502 Bad Gateway

## Overview

Selecting two versions on the Skill Studio Versions tab is silently broken. The frontend fires `GET /api/skills/{plugin}/{skill}/versions/diff?from=X&to=Y`, the eval-server proxies it to `https://verified-skill.com/api/v1/skills/{owner}/{repo}/{skill}/versions/diff?from=X&to=Y`, and the platform returns 404 because **no Next.js route exists at `versions/diff/`**. The studio proxy maps the upstream failure to `502 platform_unreachable` and the diff viewer renders nothing.

There IS dead-code intent in `vskill-platform/src/app/api/v1/skills/[owner]/[repo]/[skill]/versions/route.ts` lines 27-32 to handle `/diff` inline (`if (url.pathname.endsWith("/diff"))`), but Next.js dir-based routing never delivers `/versions/diff` to the `/versions` handler — so the branch never fires.

The platform already has a working sibling route at `versions/compare/route.ts` with full GitHub-aware diffing and an LCS fallback. The cleanest fix is to expose `versions/diff` as a thin adapter over `versions/compare`, returning the simpler shape the studio's `VersionDiff` type expects, and delete the unreachable inline branch + its helpers.

The website's `/skills/.../versions/compare` page hits `/versions/compare` directly and is not affected — the user's recollection that it was also broken does not match the code.

## User Stories

### US-001: Studio compare-versions returns a usable diff (P1)
**Project**: vskill-platform + vskill (no client changes)

**As a** Skill Studio user
**I want** picking two versions on the Versions tab to render a unified diff
**So that** I can review what changed between releases of a skill

**Acceptance Criteria**:
- [x] **AC-US1-01**: `GET /api/v1/skills/{owner}/{repo}/{skill}/versions/diff?from=X&to=Y` returns `200` with body shape `{ from, to, diffSummary, contentDiff }` when both versions exist.
- [x] **AC-US1-02**: `contentDiff` is the unified-patch string for the SKILL.md file (preferred) or the first file in the compare result; empty string when no files changed.
- [x] **AC-US1-03**: `diffSummary` is the `SkillVersion.diffSummary` of the `to` row (string), or empty string when null. Never null/undefined in the response body.
- [x] **AC-US1-04**: Missing `from` or `to` → `400 { error }` (matches existing `/compare` contract).
- [x] **AC-US1-05**: `from` or `to` not matching semver-or-SHA shape → `400 { error }` (matches existing `/compare` contract — DB lookup is skipped on bad input).
- [x] **AC-US1-06**: Skill not found → `404 { error: "Skill not found" }`.
- [x] **AC-US1-07**: Either version not found → `400 { error: "Version 'X' not found" }`.

### US-002: Dead code removed; one source of truth for diff logic (P2)
**Project**: vskill-platform

**As a** maintainer
**I want** the unreachable `/diff` interceptor inside `versions/route.ts` removed
**So that** the next reader doesn't waste time tracing a code path that Next.js never takes

**Acceptance Criteria**:
- [x] **AC-US2-01**: `versions/route.ts` no longer references `/diff`, `handleDiff`, `computeSimpleDiff`, or `positionalDiff`.
- [x] **AC-US2-02**: `versions/route.ts` only handles its own list endpoint; the file's exported logic is unchanged for `GET /versions` callers.

### US-003: TDD coverage gates the fix (P1)
**Project**: vskill-platform

**As a** maintainer
**I want** every behavior change preceded by a failing test
**So that** the bug stays fixed

**Acceptance Criteria**:
- [x] **AC-US3-01**: New test file `versions/diff/__tests__/route.test.ts` covers AC-US1-01, AC-US1-02, AC-US1-04, AC-US1-06, AC-US1-07. Tests fail before the route file is added (RED) and pass after (GREEN).
- [x] **AC-US3-02**: Existing `versions/compare/__tests__/route.test.ts` continues to pass unchanged — diff route MUST NOT regress compare behavior.
- [x] **AC-US3-03**: Existing studio tests at `vskill/src/eval-server/__tests__/version-routes.test.ts` (which mock the platform fetch) continue to pass — the studio's proxy URL stays at `/versions/diff`.

## Functional Requirements

### FR-001: Diff route is a thin adapter over compare
`versions/diff/route.ts` MUST delegate the heavy lifting (auth/validation/DB lookup/GitHub fetch/LCS fallback) to the existing compare logic, then collapse the `files[]` array down to a single `contentDiff` string. No duplicated diff computation.

### FR-002: Studio API contract preserved
The studio's `VersionDiff` TypeScript type and the `api.getVersionDiff()` URL stay untouched. This is a backend-only fix.

### FR-003: Dead code is deleted, not commented
The unreachable `if (url.pathname.endsWith("/diff"))` branch and its helpers are removed entirely from `versions/route.ts`. No `// removed` comments left behind.
