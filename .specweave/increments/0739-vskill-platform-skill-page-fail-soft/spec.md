---
increment: 0739-vskill-platform-skill-page-fail-soft
title: >-
  vskill-platform: skill page must always render — defensive fail-soft on
  blocklist/rejected fallback queries
type: bug
priority: P1
status: completed
created: 2026-04-26T00:00:00.000Z
structure: user-stories
test_mode: TDD
coverage_target: 90
---

# Feature: vskill-platform — skill page must always render

## Overview

The canonical skill detail route `/skills/{owner}/{repo}/{skill}` rendered by `src/app/skills/[owner]/[repo]/[skill]/page.tsx` (line 152-163) crashes with a Cloudflare Workers digest UI ("This page could not be loaded… digest: 4225981758") when a transient Prisma/D1 hiccup hits one of the **fallback** queries:

```ts
const skill = await getSkillByNameCached(decoded);
if (!skill) {
  const blocked  = await getBlocklistEntryBySkillName(decoded);   // throws on DB error
  if (blocked) return <BlockedSkillView entry={blocked} />;
  const rejected = await getRejectedSubmissionBySkillName(decoded); // throws on DB error
  if (rejected) return <RejectedSkillView entry={rejected} />;
  notFound();
}
```

Both fallbacks rethrow caught DB errors (`src/lib/data.ts:296-301` and `:352-357`). The peer function `getSkillByLegacySlug` (`src/lib/data.ts:242-257`) already uses the correct fail-soft pattern — warn + return null. This increment aligns the two outliers with the established pattern so that any non-existent skill (404 case) ALWAYS renders the soft-404 view instead of the digest error UI when an underlying DB query hiccups.

Originally tagged out-of-scope for 0737 (`spec.md:138`).

## User Stories

### US-001: Skill detail page never crashes on a non-existent skill (P1)
**Project**: vskill-platform

**As a** visitor browsing verified-skill.com
**I want** the skill detail page to always render — either the real skill, the blocked view, the rejected view, or a clean 404
**So that** I never see a generic Cloudflare Workers error digest for a routine "skill not found" lookup, even during transient database hiccups

**Acceptance Criteria**:
- [x] **AC-US1-01**: When `getSkillByName(name)` returns `null` AND `getBlocklistEntryBySkillName(name)` rejects with a DB error, the page renders the Next.js `notFound()` view — not the `error.tsx` boundary. (Verified by Vitest unit test on `getBlocklistEntryBySkillName` returning `null` on simulated Prisma rejection.)
- [x] **AC-US1-02**: When `getSkillByName(name)` returns `null` AND `getBlocklistEntryBySkillName` returns `null` AND `getRejectedSubmissionBySkillName(name)` rejects with a DB error, the page renders the Next.js `notFound()` view. (Verified by Vitest unit test on `getRejectedSubmissionBySkillName` returning `null` on simulated Prisma rejection.)
- [x] **AC-US1-03**: Existing happy paths are unchanged: a real skill renders the detail page, a real blocklisted skill renders `<BlockedSkillView>`, a real rejected submission renders `<RejectedSkillView>`. (Verified by Vitest tests asserting non-error returns are passed through unchanged.)
- [x] **AC-US1-04**: Both fail-soft handlers log the DB error via `console.warn` using the existing prefix shape `[<functionName>] DB error: <message>` so Cloudflare Workers tail logs continue to surface these. (Verified by Vitest spy on `console.warn`.)
- [x] **AC-US1-05**: A Playwright smoke test against a non-existent skill (`/skills/no-such-publisher-9999/no-such-repo/no-such-skill`) returns HTTP 200 with the page `<title>` matching `/Skill Not Found/` (set by `generateMetadata`) AND the body containing the visible 404 marker `404 — Not found`, and NEVER the strings `could not be loaded`, `digest:`, or `Application error`. (Verified by `tests/e2e/skill-not-found.spec.ts`.)

### US-002: Operators can monitor fail-soft events (P2)
**Project**: vskill-platform

**As an** operator watching `wrangler tail` for verified-skill.com
**I want** every fail-soft fallback to emit a single recognisable warn line
**So that** I can see how often DB hiccups silently downgrade to 404 without crashing the page

**Acceptance Criteria**:
- [x] **AC-US2-01**: A simulated DB rejection in `getBlocklistEntryBySkillName` emits exactly one `console.warn` call whose first argument starts with `[getBlocklistEntryBySkillName] DB error:` (Verified by `data-failsoft.test.ts` TC-001 — `expect(warnSpy).toHaveBeenCalledTimes(1)` + regex match on first arg.)
- [x] **AC-US2-02**: A simulated DB rejection in `getRejectedSubmissionBySkillName` emits exactly one `console.warn` call whose first argument starts with `[getRejectedSubmissionBySkillName] DB error:` (Verified by `data-failsoft.test.ts` TC-003 — `expect(warnSpy).toHaveBeenCalledTimes(1)` + regex match.)

## Functional Requirements

### FR-001: Fail-soft contract for fallback lookups
On a thrown error inside `getBlocklistEntryBySkillName` or `getRejectedSubmissionBySkillName`, the function MUST:
1. Call `console.warn("[<fn-name>] DB error:", err instanceof Error ? err.message : err)` (matching `getSkillByLegacySlug` line 252).
2. Return `null`.
3. NOT rethrow.

### FR-002: Server-only side effect
The `console.warn` is gated by `typeof window === "undefined"` only when the original code already does so (`getSkillByLegacySlug` does NOT gate; the two outliers DO gate at lines 297 and 353 — keep that gating to preserve current behaviour). The `return null` happens unconditionally on caught errors.

### FR-003: No change to schema or external contract
No Prisma schema change. No public API contract change (`/api/v1/skills/[owner]/[repo]/[skill]` still returns the skill JSON for live skills and 404 for missing — the page-level fix is below the API surface).

## Success Criteria

- **SC-001**: Vitest unit tests in `src/lib/__tests__/data.test.ts` (or a new `data-failsoft.test.ts`) cover all five AC scenarios — primary-null + blocklist-throws → null, primary-null + rejected-throws → null, real-blocklisted-entry → unchanged object, real-rejected-entry → unchanged object, warn-spy assertion.
- **SC-002**: Playwright e2e test in `tests/e2e/` opens `https://verified-skill.com/skills/no-such-publisher-9999/no-such-repo/no-such-skill` (or local preview) and asserts HTTP 200 + body contains `Skill Not Found`, body does NOT contain `digest:` or `could not be loaded`.
- **SC-003**: After deploy, `wrangler tail --format pretty` for the next 24h shows zero `digest:` strings on the canonical `/skills/<o>/<r>/<s>` route, and any `[getBlocklistEntryBySkillName] DB error:` / `[getRejectedSubmissionBySkillName] DB error:` lines are accompanied by a 200 response (verified manually by sampling a single tail log session).

## Out of Scope

- Changing `getSkillByName` itself. A primary-lookup DB error legitimately surfaces as the "could not be loaded" error boundary — that is correct UX for "the system is broken right now," distinct from "this skill does not exist."
- Sub-route 404 propagation for `/skills/<o>/<r>/<s>/evals|/security|/versions`. The investigation surfaced that those child routes render empty-state UI for non-existent parent skills instead of 404'ing — that is a separate UX bug, not a crash.
- Auth refresh 401 race on `/api/v1/auth/user/refresh` — handled by increment 0738.
- The Cloudflare RUM beacon CORS noise (`cloudflareinsights.com/cdn-cgi/rum`) — cosmetic console error unrelated to rendering.

## Dependencies

- No new dependencies. Uses existing Prisma client (`getDb`), existing `console.warn` plumbing, existing `notFound()` from `next/navigation`.
- Vitest already configured for vskill-platform (`vitest.config.ts`).
- Playwright already configured (`playwright.config.ts`).
