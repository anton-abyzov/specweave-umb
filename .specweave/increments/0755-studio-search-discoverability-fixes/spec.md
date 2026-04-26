---
increment: 0755-studio-search-discoverability-fixes
title: "Studio search discoverability: ranking + LIST filter + auto-reindex"
type: bug
priority: P1
status: planned
created: 2026-04-26
structure: user-stories
test_mode: TDD
coverage_target: 90
---

# Feature: Studio search discoverability — ranking + LIST filter + isVendor + KV auto-reindex

## Overview

Follow-up to the 0754 P0 hotfix that restored `/api/v1/studio/search` from 502→200. With the proxy fixed, four discoverability bugs are still preventing the originally-reported user from finding their published skill `anton-abyzov/vskill/skill-builder`.

**Diagnosis was refined during planning** — the original ordering put ranking first, but a deeper probe of production data revealed the actual root cause is the KV index staleness:

- Production probe (2026-04-26 03:55Z) of `/api/v1/skills/search?q=skill-builder&limit=30`: returns 30 results, total=31. ALL 30 results are `certTier: VERIFIED`. The user's `CERTIFIED T4` skill is the missing 31st.
- Direct lookup `/api/v1/skills/anton-abyzov/vskill/skill-builder` returns the row from Postgres with `certTier: CERTIFIED, trustTier: T4` — so the data IS in Postgres.
- The `/api/v1/skills/search` route runs `searchSkillsEdge` first (KV) and skips Postgres if edge already returned `>= limit + 1` rows (`route.ts: edgeResults.length >= limit + 1 → pgSkipped = true`). With edge returning 30 and limit=30, Postgres is **never consulted** — and edge is missing the user's skill.
- The `searchSkillsEdge` sort at `src/lib/search.ts:269-275` already puts `certTier === "CERTIFIED"` first. If the user's skill were in the KV "s" shard, it would rank #1 immediately.

**Conclusion**: the ranking algorithm is fine. The KV index is stale — it was indexed before the user published, and re-indexing is admin-triggered (`POST /api/v1/admin/rebuild-search` requires bearer auth). **Auto-reindex on publish is the actual fix for the user's specific complaint.**

The four discrete fixes in this increment, **re-prioritized**:

1. **(was #4) Auto-rebuild KV search index on publish** — root cause of the user's "can't find my skill" symptom. Promoted to Phase 1.
2. **(was #1) Search ranking up-weight cert tier** — defensive improvement for cases where multiple CERTIFIED skills compete; not the user's specific issue but still a valid quality bug. Demoted to Phase 2 / "if-time-permits".
3. **(unchanged #2) `/api/v1/skills` LIST endpoint silently drops `q=`, `author=`, `source=` filter params.** Independent bug.
4. **(unchanged #3) Submission `isVendor:false` drifts from published Skill row `labels:[vendor,certified]`.** Independent bug.

This increment ships fixes for all four with TDD discipline and live production verification, with phases ordered by user-impact (auto-reindex first).

## User Stories

### US-001: Vendor-tier skills surface near the top of name-relevant searches (P1)
**Project**: vskill-platform

**As a** user who has just published a vendor-tier skill (T4 CERTIFIED) to verified-skill.com
**I want** my skill to appear in the top 10 results when someone searches for its exact name (e.g., `q=skill-builder` for my `anton-abyzov/vskill/skill-builder`)
**So that** newly-published vendor skills are discoverable instead of being buried below older popular community VERIFIED skills

**Acceptance Criteria**:
- [ ] **AC-US1-01**: For `q=skill-builder` against the production registry, the result list includes `anton-abyzov/vskill/skill-builder` within the top 10 of `/api/v1/skills/search?q=skill-builder&limit=30` AND within the top 30 of `/api/v1/studio/search?q=skill-builder` (LIMIT_MAX bound).
- [ ] **AC-US1-02**: A unit test pins the ranking: given a synthetic input of one T4 CERTIFIED vendor skill (githubStars=24, vskillInstalls=0) and 30 T2 VERIFIED community skills with `name` containing `skill-builder` (githubStars range 0-200, downloads=0), the T4 skill scores **higher** than every T2 skill via the production search path's blended rank.
- [ ] **AC-US1-03**: The ranking change does not regress existing exact-name-match behavior — a query that exactly matches a name still ranks that name #1 (the relevance term still dominates for high-confidence matches).
- [ ] **AC-US1-04**: For neutral queries like `q=react`, popularity (stars + downloads) still drives ranking — the change up-weights cert tier without flattening popularity for low-tier-mass queries.

---

### US-002: `/api/v1/skills` LIST endpoint honors filter query params (P1)
**Project**: vskill-platform

**As a** developer or internal tool calling the skills LIST endpoint
**I want** `q=`, `author=`, `source=` filter params to actually narrow results
**So that** I can build paginated views over filtered subsets (e.g., "show all skills authored by anton-abyzov", "show only vendor-source skills", "search for skills containing 'react'")

**Acceptance Criteria**:
- [ ] **AC-US2-01**: `GET /api/v1/skills?author=anton-abyzov&limit=20` returns only skills where `Skill.author === "anton-abyzov"` (or `ownerSlug === "anton-abyzov"` — whichever is the canonical authored-by field on the Skill model).
- [ ] **AC-US2-02**: `GET /api/v1/skills?source=vendor&limit=20` returns only skills with `source === "vendor"` (or labels including `vendor` — TBD in plan based on the actual data model).
- [ ] **AC-US2-03**: `GET /api/v1/skills?q=skill-builder&limit=20` narrows to skills whose `name`, `displayName`, or `description` contains `skill-builder` (case-insensitive). For full-text relevance, callers should still use `/api/v1/skills/search`; LIST `q=` is a coarse contains-filter.
- [ ] **AC-US2-04**: Combining filters uses AND semantics: `?author=anton-abyzov&source=vendor` returns the intersection.
- [ ] **AC-US2-05**: Empty / missing filter values are no-ops — passing `?author=` or omitting the param entirely returns the unfiltered default-sorted list.
- [ ] **AC-US2-06**: Input validation: `q`, `author`, `source` each capped at 200 chars; charset whitelist `[A-Za-z0-9._/-]+` (rejected with 400 if violation). Mirrors `/api/v1/skills/search` sanitization.

---

### US-003: Publish-time isVendor backfill on the submission row (P2)
**Project**: vskill-platform

**As an** internal admin reading `submission.isVendor` to triage vendor publishes
**I want** the submission row's `isVendor` field to match the published Skill row's vendor classification
**So that** queries like "show me all vendor submissions" return correct results without joining through to the Skill table

**Acceptance Criteria**:
- [ ] **AC-US3-01**: When `publish.ts` upserts a Skill with vendor classification (labels include `vendor` OR `certMethod === "VENDOR_AUTO"`), the same code path also writes `submission.isVendor = true` on the source submission row in the same transaction (or, if separate transactions, with explicit error handling that surfaces drift).
- [ ] **AC-US3-02**: For a vendor publish, both `GET /api/v1/submissions/<id>` and `GET /api/v1/skills/<owner>/<repo>/<skill>` return consistent vendor-classification flags (both true / both labeled).
- [ ] **AC-US3-03**: Idempotent: re-publishing an already-vendor submission is a no-op (no extra DB write needed when `submission.isVendor` is already correct).
- [ ] **AC-US3-04**: Out of scope — historical backfill of pre-existing drifted rows. New publishes only.

---

### US-004: Auto-rebuild KV search index on submission publish (P2)
**Project**: vskill-platform

**As a** user who just published a skill
**I want** my skill to appear in `/api/v1/skills/search` results within ~1 minute of publish
**So that** I don't have to wait for an admin to manually trigger `POST /api/v1/admin/rebuild-search` before my skill is discoverable in edge KV results

**Acceptance Criteria**:
- [ ] **AC-US4-01**: When `publish.ts` transitions a submission to PUBLISHED state, it enqueues a partial-index-update message (to a CF Queue or invokes a Durable Object alarm — chosen in plan based on what infra already exists). The publish path stays non-blocking — the enqueue is fire-and-forget.
- [ ] **AC-US4-02**: A consumer worker picks up the message, fetches the new Skill row from Postgres, and writes the corresponding sharded KV entry. Idempotent: replays of the same message produce the same KV state.
- [ ] **AC-US4-03**: Live verification: publish a test submission; within 60 seconds, `searchSkillsEdge` returns the new skill (no manual rebuild required).
- [ ] **AC-US4-04**: Existing `POST /api/v1/admin/rebuild-search` admin endpoint stays as an escape hatch for full rebuilds and recovery from queue failures.
- [ ] **AC-US4-05**: Queue failures fall back gracefully — Postgres is the source of truth; a failed KV update logs a warning but does not roll back the publish.

## Functional Requirements

### FR-001: Ranking algorithm tunability
The blended ranking formula (whatever the production search path uses) MUST be exposed as an exported function with explicit weight constants, so tests can pin specific weights and ranking changes are auditable in diffs.

### FR-002: LIST endpoint backwards compatibility
Default behavior (no filter params) returns the same envelope shape and pagination as today. Adding filter params MUST narrow without changing the envelope.

### FR-003: Publish-path resilience
The KV-reindex enqueue MUST NOT block the publish transaction. A queue-down scenario must let the publish complete with a logged warning, never roll back.

### FR-004: Sanitization parity
LIST endpoint filter inputs use the same sanitization rules as the existing search endpoint — no new validation surface invented per-route.

## Success Criteria

- After deploy, `q=skill-builder` against `/api/v1/studio/search?limit=30` returns `anton-abyzov/vskill/skill-builder` within the visible page.
- `/api/v1/skills?author=anton-abyzov` returns the user's vendor skills.
- A test publish of a new submission produces a discoverable Skill in edge KV search within 60 seconds.
- All new + existing search and LIST tests pass; no regression in `/api/v1/skills/search` or `/api/v1/skills/<owner>/<repo>/<skill>` direct lookup.

## Out of Scope

- Replacing the search engine entirely (e.g., introducing Algolia / Meilisearch). The existing KV+Postgres dual path stays.
- Backfill of historical drifted `submission.isVendor` rows. New publishes only.
- Search UI changes in vskill-platform (`/find`, `/skills/...`) or in the local Skill Studio.
- Personalized ranking ("show me skills similar to ones I've installed").
- Trending score recomputation cadence changes.
- Adding a `verified-skill.com/find/<owner>/<repo>/<skill>` page route (the `/find/...` 404 noted in 0754 investigation — separate cleanup).
- Changes to vskill CLI behavior.

## Dependencies

- `/api/v1/studio/search` proxy works correctly (delivered by 0754 hotfix, deployed 158fae83).
- Existing KV `SEARCH_CACHE_KV` binding (already wired in `wrangler.jsonc`).
- Existing Cloudflare Queue infrastructure for `submission-processing` etc. (a new queue name may be added in plan; TBD).
- Prisma Skill + Submission models (existing fields used; no migrations expected unless the source-field semantics need adjustment).
