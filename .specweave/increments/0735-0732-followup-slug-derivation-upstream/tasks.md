# Tasks: 0732 follow-up — outbox-time slug derivation + name shape validation

## Task notation

- `[T-NNN]`: Task ID — `[ ]` pending, `[x]` completed
- `[P]`: Parallelizable
- TDD strict: every implementation task is preceded by a failing-test task in the same phase
- All tasks run at xhigh effort (Opus 4.7)

---

## Phase 1: Validator helper (US-001 / AC-US1-03)

### T-001: Failing test — `validateAndDeriveSlug` unit cases
**User Story**: US-001 | **Satisfies ACs**: AC-US1-03 | **Status**: [x] completed
**File**: `src/lib/skill-update/__tests__/skill-name.test.ts` (NEW)
**Test Plan (Given/When/Then)** — 6 cases:
- Given a valid `owner/repo/slug` name, When `validateAndDeriveSlug(name)` runs, Then it returns `"sk_published_owner/repo/slug"`.
- Given a 2-segment name `"owner/repo"`, When called, Then returns `null`.
- Given an empty string, When called, Then returns `null`.
- Given `null` or `undefined`, When called, Then returns `null`.
- Given a name with disallowed chars `"owner/repo/slug with spaces"`, When called, Then returns `null`.
- Given a name with leading or trailing slash `"/owner/repo/slug"` or `"owner/repo/slug/"`, When called, Then returns `null`.

Run: `npx vitest run src/lib/skill-update/__tests__/skill-name.test.ts` from vskill-platform — must fail at import (helper does not yet exist).

### T-002: Implement `validateAndDeriveSlug` helper
**User Story**: US-001 | **Satisfies ACs**: AC-US1-03 | **Status**: [x] completed
**File**: `src/lib/skill-update/skill-name.ts` (NEW)
**Test Plan**: T-001 transitions RED → GREEN. Exports must include `CANONICAL_NAME_RE`, `SLUG_PREFIX`, `validateAndDeriveSlug`.

---

## Phase 2: Outbox-writer integration (US-001 / AC-US1-01, AC-US1-02)

### T-003: Failing test — outbox-writer sets `skillSlug` for valid name; omits + warns for malformed
**User Story**: US-001 | **Satisfies ACs**: AC-US1-01, AC-US1-02 | **Status**: [x] completed
**File**: `src/lib/skill-update/__tests__/outbox-writer.test.ts` (extend existing)
**Test Plan**:
- Given a `SkillRef` with `name: "anton-abyzov/vskill/appstore"`, When `writeSkillVersionWithOutbox` constructs the payload, Then `payload.skillSlug === "sk_published_anton-abyzov/vskill/appstore"` AND no `console.warn` is emitted.
- Given a `SkillRef` with `name: "not-a-valid-shape"`, When called, Then `payload.skillSlug` is undefined AND `console.warn` is called with `"[outbox-writer] skipped slug derivation: invalid skill name shape"` and `{ segments, length }` details (raw name NOT in args).

Run: `npx vitest run src/lib/skill-update/__tests__/outbox-writer.test.ts` — both new cases fail.

### T-004: Implement slug derivation in outbox-writer payload construction
**User Story**: US-001 | **Satisfies ACs**: AC-US1-01, AC-US1-02 | **Status**: [x] completed
**File**: `src/lib/skill-update/outbox-writer.ts` (around lines 89–97)
**Test Plan**: T-003 transitions RED → GREEN. `skillSlug` set on payload when valid; absent + warn-logged when malformed.

### T-005: Update existing outbox-writer test fixtures
**User Story**: US-001 | **Satisfies ACs**: AC-US1-01 | **Status**: [x] completed
**File**: `src/lib/skill-update/__tests__/outbox-writer.test.ts`
**Test Plan**: Walk all 9 existing test cases; where the assertion uses `toEqual(payload)` and the SkillRef has a valid name, update the expected payload to include `skillSlug`. Existing 9 cases stay green. Test count: 9 → 11 (with T-003's 2 additions).

---

## Phase 3: Publish endpoint cleanup (US-001 / AC-US1-04)

### T-006: Failing test — publish/route.ts forwards event verbatim (no augmentation)
**User Story**: US-001 | **Satisfies ACs**: AC-US1-04 | **Status**: [x] completed
**File**: `src/app/api/v1/internal/skills/publish/__tests__/route.test.ts`
**Test Plan**:
- Revert the existing "forwards payload" assertion from `toMatchObject(body)` back to `toEqual(body)` (no skillSlug augmentation appended by the route).
- Remove the `vi.mock("@/lib/db")` block AND the slug-augmentation `describe` (DB lookup is gone).
- Add new case: "forwards an event whose body already contains skillSlug, byte-equal to the DO body" — assert `forwardedBody.skillSlug === "sk_published_x/y/z"` came from the input, not from a route-side augmentation.

Run: `npx vitest run src/app/api/v1/internal/skills/publish/__tests__/route.test.ts` — existing tests fail (route still augments).

### T-007: Delete `augmentWithSlug` and DB lookup from publish/route.ts
**User Story**: US-001 | **Satisfies ACs**: AC-US1-04 | **Status**: [x] completed
**File**: `src/app/api/v1/internal/skills/publish/route.ts`
**Test Plan**: T-006 transitions RED → GREEN. Lines 92–106 (or wherever `augmentWithSlug` lives) deleted. `getDb` import removed if no longer used. `parseEvent(raw)` result forwarded verbatim to `stub.fetch`.

---

## Phase 4: Integration + cross-cutting

### T-008: Integration test — reconciler-replayed publish carries skillSlug end-to-end
**User Story**: US-001 | **Satisfies ACs**: AC-US1-05 | **Status**: [x] completed
**File**: `src/lib/skill-update/__tests__/outbox-writer.test.ts` (extend) OR `src/lib/skill-update/__tests__/outbox-reconciler-slug.test.ts` (new — pick whichever has more reusable mocks)
**Test Plan**:
- Given an `UpdateEvent` row with stored `payload` containing `skillSlug: "sk_published_a/b/c"`, When the reconciler forwards via `publishToUpdateHubWithEventId`, Then the body sent to the DO contains the same `skillSlug` (no DB lookup occurred between cache-read and DO-forward).
- Spy on `db.skill.findUnique` — assert it was NOT called during the reconciler forward path.

### T-009: Run full vskill-platform skill-update + publish suite green
**User Story**: US-001 | **Satisfies SCs**: SC-003 | **Status**: [x] completed
**Test Plan**: `npx vitest run src/lib/skill-update src/app/api/v1/internal/skills/publish` from vskill-platform — must show 0 failures, 0 skips except the existing migration skips, ≥6 net new test cases on top of 0732's baseline.

### T-010: Run vskill eval-ui slug real-SSE E2E green
**User Story**: US-001 | **Satisfies ACs**: AC-US1-04, AC-US1-05 | **Satisfies SCs**: SC-002 | **Status**: [x] completed
**Test Plan**: `npx vitest run src/eval-ui/src/hooks/__tests__/useSkillUpdates.real-sse.slug.test.ts` from vskill repo — must still pass without modification (proves the dual-accept contract is preserved end-to-end).

---

## Phase order summary

1. **Phase 1** (T-001..T-002): validator helper — must land first (T-004 depends on it).
2. **Phase 2** (T-003..T-005): outbox-writer integration — depends on Phase 1.
3. **Phase 3** (T-006..T-007): publish endpoint cleanup — independent of Phase 1/2 in code but benefits from being ordered after so the slug always arrives via outbox.
4. **Phase 4** (T-008..T-010): integration + cross-cutting — runs after Phases 1–3.

Total: 10 tasks, ~7 net new test cases. TDD strict.
