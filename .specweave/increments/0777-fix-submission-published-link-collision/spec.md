---
increment: 0777-fix-submission-published-link-collision
title: Fix submission published-skill link collision
type: bug
priority: P1
status: completed
created: 2026-04-26T00:00:00.000Z
structure: user-stories
test_mode: TDD
coverage_target: 90
---

# Feature: Fix submission published-skill link collision

## Overview

The "View published skill" link on `verified-skill.com/submit/[id]` navigates to a completely unrelated skill page when legacy slugs collide. Production reproduction: submission `sub_8f8f75d7-67b6-4357-9dd1-1d46d87bacf0` (skill `greet-anton-abyzov`) routes to `/skills/mbt1909432/lightweight-agent/hello-skill` — a totally unrelated repo.

**Root cause:** the submission detail page builds the link from the submission's flat `skillName` via `skillUrl()`, which falls through to the legacy-redirect path `/skills/<flat>`. The legacy-redirect handler does `findFirst` on `legacySlug`, a non-unique column. When two skills share a legacy slug, `findFirst` returns whichever Prisma orders first — landing on the wrong skill. Meanwhile, `publish.ts` already correctly links the submission row to its published Skill via `skillId`; the read path just throws that link away.

**Fix:** two layers of defense.
1. Use the linked Skill's hierarchical `name` directly (eliminate the legacy redirect for published submissions).
2. Refuse ambiguous legacy matches (`findMany` + `take: 2`; 404 if more than one match).

## User Stories

### US-001: Canonical link from submission detail page (P1)
**Project**: vskill-platform

**As a** user viewing a published submission detail page,
**I want** the "View published skill" link to navigate to the exact skill I just published,
**So that** I land on my own skill — never an unrelated repo's skill that happens to share a legacy slug.

**Acceptance Criteria**:
- [x] **AC-US1-01**: `getSubmissionFull(id)` in `src/lib/data.ts` joins the linked `Skill` via `submission.skillId` and returns `publishedSkillName: string | null` (the hierarchical 3-segment `Skill.name`, e.g. `anton-abyzov/greet-anton/greet-anton-abyzov`). Returns `null` when `skillId` is null.
- [x] **AC-US1-02**: `GET /api/v1/submissions/[id]` (`src/app/api/v1/submissions/[id]/route.ts`) includes `publishedSkillName` in its JSON response.
- [x] **AC-US1-03**: `src/app/submit/[id]/page.tsx` (the "View published skill" anchor) prefers `publishedSkillName` when present; only falls back to `skillUrl(data.skillName)` when `publishedSkillName` is null. The rendered `href` for a published submission with a hierarchical name is `/skills/<owner>/<repo>/<skill>` — never `/skills/<flat>`.
- [x] **AC-US1-04**: A published submission whose linked Skill has a non-hierarchical legacy `name` (e.g. one-segment) still renders some valid link — falls back to `skillUrl(name)` so legacy data is not broken.

---

### US-002: Refuse ambiguous legacy redirects (P1)
**Project**: vskill-platform

**As a** user clicking any legacy `/skills/<flat>` URL,
**I want** the redirect to refuse rather than guess when the flat slug matches multiple skills,
**So that** an ambiguous slug never silently lands me on a random unrelated skill.

**Acceptance Criteria**:
- [x] **AC-US2-01**: `GET /api/v1/legacy-redirect/[slug]` (`src/app/api/v1/legacy-redirect/[slug]/route.ts`) replaces `findFirst` with `findMany({ where: { legacySlug, isDeprecated: false }, take: 2, select: { ownerSlug, repoSlug, skillSlug, name } })`. When `length === 1`, behaviour matches today (301 redirect to canonical). When `length === 0`, returns 404 (matches today). When `length >= 2`, returns 404 with a clear `X-Legacy-Ambiguous: true` response header (do NOT pick one).
- [x] **AC-US2-02**: The handler's catch path (DB unavailable) still returns 503 — unchanged.

---

### US-003: Test coverage (P1)
**Project**: vskill-platform

**As a** maintainer,
**I want** vitest assertions for both layers of the fix,
**So that** future refactors cannot silently re-introduce the bug.

**Acceptance Criteria**:
- [x] **AC-US3-01**: vitest covers `getSubmissionFull` returning `publishedSkillName` = hierarchical name when `skillId` set, and `null` when not. The DB call is mocked.
- [x] **AC-US3-02**: vitest asserts `GET /api/v1/submissions/[id]` JSON response shape includes `publishedSkillName`.
- [x] **AC-US3-03**: vitest covers the legacy-redirect handler's three branches: 0 matches → 404, 1 match → 301 to canonical, 2+ matches → 404 with `X-Legacy-Ambiguous` header.

## Functional Requirements

### FR-001: Read-side only
Changes are confined to the read path (data fetch + render + redirect). The write path (`publish.ts`, the submission create flow, `Skill` upsert) is unchanged.

### FR-002: No DB migration
This increment does NOT add a unique constraint on `legacySlug`. Adding `@@unique` requires a data dedup migration on production (multiple rows currently share legacy slugs) and is deferred to a future increment.

## Success Criteria

- A new submission published end-to-end renders the "View published skill" link as a 3-segment canonical URL.
- Manual repro of `sub_8f8f75d7-67b6-4357-9dd1-1d46d87bacf0` lands on the correct skill page (or 404 if the data is somehow still inconsistent — never an unrelated skill).
- All new vitest cases pass; existing tests for these files continue to pass.

## Out of Scope

- Adding `@@unique` migration on `legacySlug` (separate increment, requires dedup).
- Deprecating legacy flat URLs entirely.
- Changing `publish.ts` (already correct — submission.skillId is set).
- The Save-button auto-bump-patch behaviour discussed earlier in the conversation (separate concern; tracked elsewhere).

## Dependencies

None. The Submission Prisma model already has the `skill` relation via `skillId`.
