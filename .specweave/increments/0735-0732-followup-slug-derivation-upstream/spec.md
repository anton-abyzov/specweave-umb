---
increment: 0735-0732-followup-slug-derivation-upstream
title: '0732 follow-up: outbox-time slug derivation + name shape validation'
type: feature
priority: P2
status: completed
created: 2026-04-26T00:00:00.000Z
structure: user-stories
test_mode: TDD
coverage_target: 90
---

# Feature: 0732 follow-up — outbox-time slug derivation + name shape validation

## Overview

Increment 0732 shipped server-side `skillSlug` augmentation in the publish endpoint so SSE subscribers using the public slug ID format (`sk_published_<owner>/<repo>/<slug>`) receive events alongside subscribers using DB UUIDs. The grill flagged a residual correctness gap and a defense-in-depth gap:

- **G-001 (HIGH)**: `augmentWithSlug` (`src/app/api/v1/internal/skills/publish/route.ts:92–106`) does a `db.skill.findUnique` on every publish. On null result OR thrown error, it silently returns the event UUID-only — slug subscribers miss the event with no signal. Under transient Neon errors / replica lag, this is silent data loss.
- **G-003 (MED)**: `sk_published_${skill.name}` templating has zero shape validation on `skill.name`. Today values are clean, but no defense-in-depth.

This increment moves slug derivation **upstream** to `writeSkillVersionWithOutbox` (`src/lib/skill-update/outbox-writer.ts:89–97`). At that point we are already inside `db.$transaction` and `skill.name` is in scope via the `SkillRef` parameter — zero new DB round-trips, zero new failure modes. The frozen outbox payload now carries `skillSlug` from creation; the reconciler forwards it verbatim; the publish endpoint becomes a pure forwarder; `augmentWithSlug` is deleted along with its silent-failure path. A single canonical helper `validateAndDeriveSlug(name)` enforces the shape regex.

## Personas

- **Slug-ID SSE subscriber** — Studio client that learned from the public discovery API and subscribes to `?skills=sk_published_owner/repo/slug`. Today they can silently miss events. After this increment, every event they should receive is delivered.
- **Platform operator** — runs Cloudflare Workers + Neon. Today the publish hot path does an extra DB round-trip per event. After this increment, the publish endpoint has zero DB queries.

## User Stories

### US-001: Slug derived at outbox-write time (P2)
**Project**: vskill-platform

**As a** slug-ID SSE subscriber
**I want** every published skill update to carry its slug from creation time
**So that** I never silently miss events due to transient DB lookup failures or replica lag in the publish endpoint

**Acceptance Criteria**:
- [x] **AC-US1-01**: `writeSkillVersionWithOutbox` produces a `SkillUpdateEvent` payload containing `skillSlug: "sk_published_<name>"` when the input `SkillRef.name` matches the canonical shape (3 segments of `[a-zA-Z0-9_-]+` separated by `/`).
- [x] **AC-US1-02**: When `SkillRef.name` is malformed (not 3 segments OR contains disallowed chars OR empty OR undefined), the payload omits `skillSlug` entirely AND a structured warning is logged with segment count + total length only (never the raw name) AND the write still commits successfully.
- [x] **AC-US1-03**: A new `validateAndDeriveSlug(name)` helper at `src/lib/skill-update/skill-name.ts` exposes a single canonical regex (`CANONICAL_NAME_RE`) and a single prefix constant (`SLUG_PREFIX = "sk_published_"`). Returns `null` for invalid input, `"sk_published_<name>"` for valid input.
- [x] **AC-US1-04**: `publish/route.ts` no longer performs any DB lookup or slug augmentation. The forwarded body to the UpdateHub DO is byte-equal to the parsed input event (assuming valid auth + payload). The previous `augmentWithSlug` function is deleted, along with the `getDb` import on the publish hot path.
- [x] **AC-US1-05**: A reconciler-replayed publish (cached payload from `UpdateEvent` row) carries `skillSlug` end-to-end without any DB hit on the publish hot path. Verified by an integration test that loads a stored payload via the reconciler's forward path with mocks and asserts `skillSlug` survives the round-trip.

## Functional Requirements

- **FR-001 (helper)**: New module `src/lib/skill-update/skill-name.ts` exports `CANONICAL_NAME_RE = /^[a-zA-Z0-9_-]+\/[a-zA-Z0-9_-]+\/[a-zA-Z0-9_-]+$/`, `SLUG_PREFIX = "sk_published_"`, and `validateAndDeriveSlug(name: string | null | undefined): string | null`.
- **FR-002 (outbox-writer integration)**: `writeSkillVersionWithOutbox` calls `validateAndDeriveSlug(skill.name)` during payload construction. When a slug is returned, set it on the payload. When `null`, log `console.warn("[outbox-writer] skipped slug derivation: invalid skill name shape", { segments, length })` (segment count + total length only — never the raw name) and continue without `skillSlug`. Never throw.
- **FR-003 (publish endpoint cleanup)**: Remove `augmentWithSlug`, the DB lookup, and the `getDb` import from `src/app/api/v1/internal/skills/publish/route.ts`. The route forwards the parsed event verbatim to the DO.
- **FR-004 (test parity)**: The Phase 3 dual-format DO filter must continue to deliver to slug subscribers when receiving payloads with `skillSlug` present. The existing real-SSE slug E2E test in vskill (`useSkillUpdates.real-sse.slug.test.ts`) must remain green without modification.

## Non-Functional Requirements

- **NFR-001 (perf)**: Publish endpoint hot path now executes zero DB queries (down from one). Outbox-writer adds at most one regex match per write (sub-microsecond).
- **NFR-002 (compatibility)**: Existing `SkillUpdateEvent.skillSlug?: string` field stays optional. In-flight events without slug still match by UUID per the 0732 dual-format filter. Backwards compatible.
- **NFR-003 (observability)**: Worker logs surface a structured warn line on every malformed-name slug skip — operator can grep for `[outbox-writer] skipped slug derivation` to identify dirty rows. Expected count today: 0 (verified via Prisma query — no rows in production violate the canonical shape).
- **NFR-004 (privacy)**: Warn log NEVER includes the raw `skill.name` value — only its segment count and total length. Avoids leaking author/repo names in worker logs.

## Success Criteria

- **SC-001**: After deploy, the worker logs contain ZERO `[publish] slug augmentation failed` lines (function deleted) AND zero `[outbox-writer] skipped slug derivation` warns over a 24h window for the current Skill table.
- **SC-002**: A trivial commit pushed to `anton-abyzov/vskill@main` produces a `skill.updated` SSE frame containing `skillSlug` within ≤1 cron tick (~10 min) for any subscriber, regardless of which ID format they used to subscribe.
- **SC-003**: Vitest suite for skill-update + publish-route grows by ≥6 new test cases (skill-name 6 + outbox-writer 2-3 + publish-route revisions). All tests green.
- **SC-004**: Median publish-route latency drops measurably (one less Neon round-trip per event); observable via Cloudflare Analytics Engine `publish.duration.ms` if instrumented.

## Out of Scope

- Backfilling `skillSlug` into stale `UpdateEvent` rows already written before this change. Outbox rows are short-lived (reconciler drains within minutes) and the SSE replay window is 5 minutes — pre-deploy in-flight events lack slug but UUID match still delivers them.
- Validating/normalizing `skill.name` shape AT WRITE TIME (the upsert call sites in `rebuild-index/route.ts` and `submission/publish.ts`). Separate hardening pass — production currently has zero malformed names.
- Renaming `SkillUpdateEvent.skillSlug` to a more semantically generic name. Keeping the 0732 contract.
- Backwards-compatibility shim for events without `skillSlug` — already handled by the 0732 dual-format DO filter.
- Migrating the existing `parseOwnerRepoFromName` ad-hoc parser in `discovery/resolver.ts` to the new helper. That parser handles tracking-source resolution (different concern); leave in place.

## Dependencies

- **0708-skill-update-push-pipeline** — closed; this increment depends on the deployed scanner, outbox, DO, and SSE infrastructure.
- **0732-skill-update-tracking-resolution** — closed 2026-04-26; this increment is a direct follow-up addressing residual grill findings G-001 and G-003.

## Risk

- **R-001**: Removing `augmentWithSlug` regresses a publish path that bypasses `writeSkillVersionWithOutbox`. **Mitigation**: Audited via increment 0735 exploration agent — confirmed only 4 publish sites exist (scanner + submission both use writeSkillVersionWithOutbox; reconciler is a pure forwarder of cached payloads; publish endpoint receives those forwarded events). No untraced path. Risk: low.
- **R-002**: Strict regex rejects names that previously worked. **Mitigation**: Verified zero malformed names in current production via `SELECT count(*) FROM "Skill" WHERE name !~ '^[a-zA-Z0-9_-]+/[a-zA-Z0-9_-]+/[a-zA-Z0-9_-]+$'` returning 0. Risk: low.
- **R-003**: Outbox-writer test churn. **Mitigation**: Bounded — exploration confirmed ≤5 assertion updates across the existing 9-case suite. Risk: low.
- **R-004**: Pre-deploy in-flight events lose slugs during the deploy window. **Mitigation**: DO accepts UUID match per 0732 dual-format filter; subscribers don't lose the event, only its slug-form delivery during a 30-second window. SSE replay window is 5 min so reconnects close any gap. Risk: low / acceptable.
