---
increment: 0327-submit-page-discovery-fix
title: "Fix submit page skill discovery bug + remove selection step"
type: feature
priority: P1
status: in-progress
created: 2026-02-22
structure: user-stories
test_mode: test-after
coverage_target: 80
---

# Feature: Fix submit page skill discovery bug + remove selection step

## Overview

Fix the submit page at verified-skill.com/submit where discovery errors (GitHub rate limits, auth failures) surface as the misleading "No SKILL.md files found" message, and simplify the submit flow by removing the skill selection/confirmation step -- always submit ALL discovered skills automatically.

### Root Cause Analysis

1. **Discovery error masking**: `discoverSkillsEnhanced()` can fail due to GitHub API errors (rate limit 403, auth 401). The discover route catches all errors and returns 500, but the **real problem** is that API failures within the function return an empty `skills: []` result (not an error), causing the client to display "No SKILL.md files found" when the actual issue is an upstream API failure.

2. **Submit path mismatch**: `page.tsx` calls `/api/v1/submissions/bulk` which requires `X-Internal-Key` (internal-only). The client gets 401, and only 404 triggers the legacy fallback. The submit flow silently fails for most users.

3. **Unnecessary complexity**: The "select" phase adds ~165 lines of UI code plus ~80 lines of supporting functions/state for a feature no one uses -- users always want to submit all skills.

## User Stories

### US-001: Surface discovery errors with specific messages (P1)
**Project**: vskill-platform

**As a** skill author submitting a repo
**I want** to see a specific error message when GitHub API limits or auth issues prevent discovery
**So that** I understand the problem is temporary and not that my repo has no skills

**Acceptance Criteria**:
- [x] **AC-US1-01**: `DiscoveryResult` type gains an optional `error` field: `error?: { code: "rate_limited" | "auth_failed" | "api_error"; message: string }`
- [x] **AC-US1-02**: When GitHub API returns 403 (rate limit), `discoverSkillsEnhanced` returns `{ skills: [], error: { code: "rate_limited", message: "GitHub API rate limit exceeded. Please try again in a few minutes." }, ... }` instead of throwing or returning empty
- [x] **AC-US1-03**: When GitHub API returns 401, `discoverSkillsEnhanced` returns `{ skills: [], error: { code: "auth_failed", message: "GitHub authentication issue. Please try again later." }, ... }`
- [x] **AC-US1-04**: For other non-success GitHub responses, `discoverSkillsEnhanced` returns `{ skills: [], error: { code: "api_error", message: "<descriptive message>" }, ... }`
- [x] **AC-US1-05**: When `GITHUB_TOKEN` is missing, the discover route logs a server-side warning (`console.warn`) but proceeds with unauthenticated calls (existing behavior, now explicit)
- [x] **AC-US1-06**: The discover route (`/api/v1/submissions/discover`) inspects the `error` field and returns HTTP 502 with the user-friendly error message when present
- [x] **AC-US1-07**: Discovery with 0 skills and no error field still returns HTTP 200 (backward compatible)
- [x] **AC-US1-08**: The submit page displays the specific error message from the 502 response (not the generic "No SKILL.md files found")

---

### US-002: Remove selection step and auto-submit all skills (P1)
**Project**: vskill-platform

**As a** skill author
**I want** discovery to immediately submit all found skills
**So that** the submit flow is faster and requires fewer clicks

**Acceptance Criteria**:
- [x] **AC-US2-01**: The `Phase` type changes from `"input" | "discovering" | "select" | "submitting" | "done"` to `"input" | "discovering" | "submitting" | "done"` (no "select" phase)
- [x] **AC-US2-02**: After successful discovery (skills.length > 0), the page transitions directly from "discovering" to "submitting" -- no user interaction required
- [x] **AC-US2-03**: All discovered skills are submitted (no client-side filtering by status). Already-verified and already-pending skills are submitted and the bulk endpoint's dedup logic handles them.
- [x] **AC-US2-04**: The following state variables are removed: `selected`, `collapsed`
- [x] **AC-US2-05**: The following functions are removed: `toggleSkill`, `toggleAll`, `togglePlugin`, `toggleCollapse`
- [x] **AC-US2-06**: The `StatusBadge` component is removed
- [x] **AC-US2-07**: The `btnSmall` style constant is removed
- [x] **AC-US2-08**: The entire "select" rendering block (previously lines 351-516 in page.tsx) is removed
- [x] **AC-US2-09**: The `reset()` function no longer references `selected`, `collapsed`, or other removed state
- [x] **AC-US2-10**: After cleanup, page.tsx is under 500 lines

---

### US-003: Fix submit path to use individual submissions endpoint (P1)
**Project**: vskill-platform

**As a** skill author
**I want** skill submission to actually work from the browser
**So that** clicking submit doesn't silently fail

**Acceptance Criteria**:
- [x] **AC-US3-01**: `handleSubmitAll` submits all discovered skills (not just selected) since selection is removed
- [x] **AC-US3-02**: The submission flow uses the legacy individual `POST /api/v1/submissions` endpoint (which accepts user auth cookies) instead of attempting the internal-only `/api/v1/submissions/bulk` endpoint first
- [x] **AC-US3-03**: Each skill submission includes `repoUrl`, `skillName`, and `skillPath` fields
- [x] **AC-US3-04**: The progress bar tracks submission progress across all skills
- [x] **AC-US3-05**: On error during submission, remaining skills still attempt to submit (no early abort)
- [x] **AC-US3-06**: The done phase shows per-skill results: "Already verified" badge, "Already pending" badge, error message, or "Track >>" link

---

### US-004: Done phase displays flat results list (P2)
**Project**: vskill-platform

**As a** skill author
**I want** the done phase to show a simple flat list of results
**So that** I can quickly see the outcome of each skill submission

**Acceptance Criteria**:
- [x] **AC-US4-01**: The done phase displays a flat list of per-skill results (no plugin grouping, no collapsible sections)
- [x] **AC-US4-02**: Each result row shows skill name + status badge or link: "Already verified" (green), "Already pending" (yellow), error message (red), or "Track >>" link
- [x] **AC-US4-03**: The marketplace badge (if present) is shown above the results list
- [x] **AC-US4-04**: Summary line shows counts: "N submitted, N skipped, N failed"

## Functional Requirements

### FR-001: Structured error propagation from GitHub API
When `discoverSkillsEnhanced` encounters a non-success GitHub API response during tree fetching or marketplace.json fetching, it must populate the `error` field on the returned `DiscoveryResult` rather than throwing. This preserves backward compatibility (empty skills array) while adding error visibility.

### FR-002: HTTP status mapping in discover route
The discover route maps the `error` field to HTTP responses:
- `error` present → 502 with `{ error: result.error.message, code: result.error.code }`
- No error, skills > 0 → 200 with full result
- No error, skills === 0 → 200 with empty skills (legitimate empty repo)

### FR-003: Server-side logging for missing token
When `GITHUB_TOKEN` is undefined/empty, `console.warn("GITHUB_TOKEN not configured — using unauthenticated GitHub API calls")` is logged once per request. Discovery proceeds with unauthenticated calls (lower rate limits).

### FR-004: Automatic submission after discovery
After discovery returns skills, the client immediately invokes the submission flow with all skills. No user interaction between discovery and submission.

## Success Criteria

- Submit page no longer shows "No SKILL.md files found" when the actual issue is a GitHub API error
- Submit page correctly shows contextual error messages for rate limits and auth issues
- Submit flow completes in 2 clicks: paste URL + click "Discover Skills" (submission is automatic)
- page.tsx is under 500 lines after cleanup (down from ~675)
- All existing tests pass; new tests cover error propagation paths

## Out of Scope

- Creating a new client-facing bulk submission endpoint (the individual endpoint works fine for client-side use)
- Retry logic for failed individual submissions (user can click "Submit more")
- WebSocket/SSE streaming of submission progress (sequential fetch is sufficient)
- Plugin marketplace detection changes (marketplace.json parsing is unrelated to this bug)

## Dependencies

- `src/lib/scanner.ts` — `DiscoveryResult` and `discoverSkillsEnhanced` types/function
- `src/app/api/v1/submissions/discover/route.ts` — discover route
- `src/app/api/v1/submissions/route.ts` — individual submission endpoint (POST)
- `src/app/submit/page.tsx` — submit page client component
