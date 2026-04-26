# Implementation Plan: 0732 follow-up — outbox-time slug derivation + name shape validation

## Overview

Move skillSlug derivation from the publish endpoint (post-DB lookup with silent-failure path) UPSTREAM to `writeSkillVersionWithOutbox` (transactional write time). The outbox-row's frozen payload now carries `skillSlug` from creation. The reconciler forwards the cached payload verbatim. The publish endpoint becomes a pure forwarder; `augmentWithSlug` and its silent failure mode are deleted. A single canonical helper `validateAndDeriveSlug` enforces the shape regex and is the only code that templates `sk_published_<name>`.

## Design

### Components touched

| Component | File | Change |
|---|---|---|
| **NEW** Slug validator | `src/lib/skill-update/skill-name.ts` | Export `CANONICAL_NAME_RE`, `SLUG_PREFIX`, `validateAndDeriveSlug(name)` |
| Outbox writer | `src/lib/skill-update/outbox-writer.ts` (lines 89–97) | Call `validateAndDeriveSlug(skill.name)` during payload construction; set `skillSlug` on payload when valid; warn-log when malformed |
| Publish endpoint | `src/app/api/v1/internal/skills/publish/route.ts` | Delete `augmentWithSlug` + `getDb` import; route forwards verbatim |
| Outbox writer tests | `src/lib/skill-update/__tests__/outbox-writer.test.ts` | +2 new cases (valid → slug present, malformed → slug absent + warn); ≤5 assertion updates in existing 9 cases |
| Publish route tests | `src/app/api/v1/internal/skills/publish/__tests__/route.test.ts` | Revert "forwards payload verbatim" to `toEqual(body)`; remove db.skill mock; add "forwards skillSlug from upstream" case |
| **NEW** Slug validator tests | `src/lib/skill-update/__tests__/skill-name.test.ts` | 6 unit cases for `validateAndDeriveSlug` |

### Data flow (after change)

```
Scanner / Submission → writeSkillVersionWithOutbox (inside db.$transaction):
  ┌──────────────────────────────────────────────────────────┐
  │ skill.name (in scope via SkillRef)                       │
  │       │                                                  │
  │       ▼                                                  │
  │ validateAndDeriveSlug(skill.name) → "sk_published_..."   │
  │       │                                                  │
  │       ▼                                                  │
  │ payload = { skillId, skillSlug, version, gitSha, ... }   │
  │       │                                                  │
  │       ▼                                                  │
  │ INSERT SkillVersion + UpdateEvent (frozen payload)       │
  └──────────────────────────────────────────────────────────┘
                         │
                         ▼
              outbox-reconciler reads UpdateEvent.payload (cached, with slug)
                         │
                         ▼
              POST /api/v1/internal/skills/publish (forwards verbatim — no DB!)
                         │
                         ▼
              UpdateHub DO matches filter against skillId OR skillSlug (0732 dual-format)
                         │
                         ▼
              SSE: event: skill.updated  data: { ..., skillSlug }
```

### Helper signature (FR-001)

```ts
// src/lib/skill-update/skill-name.ts
export const CANONICAL_NAME_RE = /^[a-zA-Z0-9_-]+\/[a-zA-Z0-9_-]+\/[a-zA-Z0-9_-]+$/;
export const SLUG_PREFIX = "sk_published_";

export function validateAndDeriveSlug(name: string | null | undefined): string | null {
  if (typeof name !== "string" || name.length === 0) return null;
  if (!CANONICAL_NAME_RE.test(name)) return null;
  return `${SLUG_PREFIX}${name}`;
}
```

### Outbox-writer integration (FR-002)

```ts
// src/lib/skill-update/outbox-writer.ts (around lines 89-97)
const slug = validateAndDeriveSlug(skill.name);
if (!slug && skill.name !== undefined && skill.name !== null) {
  const segments = (skill.name as string).split("/").length;
  const length = (skill.name as string).length;
  console.warn(
    "[outbox-writer] skipped slug derivation: invalid skill name shape",
    { segments, length },
  );
}
const payload: SkillUpdateEvent = {
  type: "skill.updated",
  eventId,
  skillId: skill.id,
  ...(slug ? { skillSlug: slug } : {}),
  version: input.version,
  gitSha: input.gitSha,
  diffSummary: input.diffSummary ?? undefined,
  publishedAt: now.toISOString(),
};
```

### Publish endpoint cleanup (FR-003)

Before:
```ts
const event = parseEvent(raw);
const augmented = await augmentWithSlug(event); // DB lookup, silent failure
await stub.fetch(/* ... body: JSON.stringify(augmented) */);
```

After:
```ts
const event = parseEvent(raw);
await stub.fetch(/* ... body: JSON.stringify(event) */);
```

Removed: `augmentWithSlug`, `getDb` import. Net effect: publish endpoint hot path is now zero DB queries.

## Rationale

### ADR-0735-01: Slug derivation belongs at outbox-write time

**Status**: Accepted.

**Context**: 0732 augmented events at publish time with a `db.skill.findUnique` lookup. On null/throw, the augmentation silently dropped the slug — slug subscribers missed the event with no observable signal. The lookup also added one Neon round-trip per event on the publish hot path.

**Decision**: Derive the slug inside `writeSkillVersionWithOutbox` where `skill.name` is already in scope via the `SkillRef` parameter, inside the existing `db.$transaction`. Persist the slug on the frozen `UpdateEvent.payload`. The reconciler and publish endpoint forward the cached payload verbatim.

**Alternatives**:
- (b) Keep augment at publish time but add a retry/circuit-breaker. Rejected: still pays one DB hit per event; circuit-breaker adds complexity that obscures observability.
- (c) Move slug derivation client-side (Studio computes it from skill metadata). Rejected: pushes complexity to every consumer; doesn't help non-Studio clients; out of scope.

**Consequence**: Publish endpoint hot path drops to zero DB queries. Reconciler-replayed publishes carry the slug end-to-end without any DB hit. Silent-failure mode eliminated by construction (the DB hit is gone — there's nothing to fail silently). The 0732 dual-format DO filter remains the safety net for any pre-deploy in-flight events that lack `skillSlug`.

### ADR-0735-02: Single canonical helper for slug derivation

**Status**: Accepted.

**Context**: Slug derivation today is a single-line template `\`sk_published_${skill.name}\`` — but it's about to live in multiple places (or could). The shape of `skill.name` is implicit (3 slash-separated segments, GitHub-style chars).

**Decision**: New module `src/lib/skill-update/skill-name.ts` exports `CANONICAL_NAME_RE`, `SLUG_PREFIX`, and `validateAndDeriveSlug`. The outbox-writer is the only caller in v1. Future code that needs to derive a slug from a name MUST import the helper.

**Reasoning**: Single source of truth for the shape regex avoids drift. Folds G-001 (silent failure) and G-003 (no shape validation) into one change. Clean unit-testable surface.

**Consequence**: One new file, ~25 lines. New regex `CANONICAL_NAME_RE` used here and not adopted elsewhere — `discovery/resolver.ts:parseOwnerRepoFromName` keeps its split-based parser because it's permissive by design (handles `{owner}/{repo}` and `{owner}/{repo}/{slug}` and edge cases for tracking-source resolution). No drift risk because the two parsers serve different concerns.

## Implementation phases

### Phase 1: Validator helper (TDD)
- T-001 (RED) → T-002 (GREEN): unit tests + implementation of `validateAndDeriveSlug`.

### Phase 2: Outbox-writer integration (TDD)
- T-003 (RED) → T-004 (GREEN): outbox-writer payload includes `skillSlug` for valid name; omits + warns for malformed.
- T-005 (REFACTOR): update existing outbox-writer test fixtures' assertions.

### Phase 3: Publish endpoint cleanup (TDD)
- T-006 (RED) → T-007 (GREEN): publish/route forwards verbatim; remove `augmentWithSlug`.

### Phase 4: Integration + cross-cutting
- T-008: integration test proving reconciler-replayed publish carries slug end-to-end.
- T-009: full vskill-platform skill-update + publish suite green.
- T-010: vskill eval-ui slug real-SSE E2E still green.

## Testing strategy

- **Unit**: `skill-name.test.ts` (6 cases) + 2 new cases in `outbox-writer.test.ts`.
- **Integration**: 1 case proving slug survives reconciler forward path.
- **E2E (cross-repo)**: existing `useSkillUpdates.real-sse.slug.test.ts` in vskill — unchanged, must still pass.
- **Vitest mocking patterns**: reuse `vi.hoisted` + `vi.mock` from `outbox-writer.test.ts`; reuse `console.warn` spy patterns from `update-hub.test.ts`.

## Technical challenges

### Challenge 1: Some outbox-writer test paths set `SkillRef.name` to a non-canonical value
**Solution**: Update those test fixtures to use a valid `owner/repo/slug` shape (existing tests use `"owner/repo/pdf"` which IS valid — minimal churn expected). New test for the malformed path uses a deliberately-bad fixture like `"not-a-valid-name"`.
**Risk**: Low. Fixture audit confirmed ≤5 assertion updates needed.

### Challenge 2: Pre-deploy in-flight outbox rows lack `skillSlug`
**Solution**: 0732 dual-format DO filter accepts UUID match. Pre-deploy in-flight events still deliver to UUID subscribers; slug subscribers experience a brief drop only during the 30-sec deploy window. SSE replay window (5 min) closes any reconnect gap. Documented as Out of Scope in spec.md.
**Risk**: Low. Acceptable degradation during deploy.

## Out of plan

- Backfilling slugs into stale `UpdateEvent` rows.
- Validating skill.name at upsert time (separate hardening pass).
- Migrating `parseOwnerRepoFromName` to use `validateAndDeriveSlug` (different concern).
