---
increment: 0711-model-provenance-and-catalog-refresh
status: ready_for_review
---

# Tasks: Model provenance + Anthropic catalog refresh

## Phase 1 — Foundation (catalog snapshot + resolver)

### T-001: Create dated Anthropic catalog snapshot
**User Story**: US-001 | **AC**: AC-US1-01, AC-US1-02 | **Status**: [x] completed
**File**: src/eval/anthropic-catalog.ts
**Test Plan**: Given the snapshot file → When loaded → Then exposes 9 active+deprecated models with full pricing, snapshotDate, and source URL.
**Test**: src/eval/__tests__/anthropic-catalog.test.ts ("ANTHROPIC_CATALOG_SNAPSHOT — integrity")
**Ship**: PR #122 squash-merged into main (commit c58151f), released as vskill@0.5.105

### T-002: Define ModelEntry and CatalogSnapshot types
**User Story**: US-001 | **AC**: AC-US1-01, AC-US1-02 | **Status**: [x] completed
**File**: src/eval/anthropic-catalog.ts:1-40
**Test Plan**: Given the type definitions → When imported → Then TypeScript compiles clean with no `any` on catalog fields.
**Test**: src/eval/__tests__/anthropic-catalog.test.ts (shape assertions on every entry)
**Ship**: PR #122 squash-merged into main (commit c58151f), released as vskill@0.5.105

### T-003: Catalog integrity test — 9 models, pricing, aliases
**User Story**: US-001 | **AC**: AC-US1-02, AC-US1-05 | **Status**: [x] completed
**File**: src/eval/__tests__/anthropic-catalog.test.ts
**Test Plan**: Given the snapshot → When iterated → Then every entry has id, aliases (non-empty), pricing (non-zero), status; aliases are unique across entries; snapshotDate is valid ISO.
**Test**: src/eval/__tests__/anthropic-catalog.test.ts (14 tests including uniqueness + ISO date)
**Ship**: PR #122 squash-merged into main (commit c58151f), released as vskill@0.5.105

### T-004: Implement findAnthropicModel lookup helper
**User Story**: US-001 | **AC**: AC-US1-05 | **Status**: [x] completed
**File**: src/eval/anthropic-catalog.ts (findAnthropicModel export)
**Test Plan**: Given the catalog → When called with "sonnet" alias → Then returns the current Sonnet entry; when called with unknown input → Then returns undefined.
**Test**: src/eval/__tests__/anthropic-catalog.test.ts ("findAnthropicModel — alias hit", "findAnthropicModel — unknown alias")
**Ship**: PR #122 squash-merged into main (commit c58151f), released as vskill@0.5.105

### T-005: Implement model-resolver.ts with ENV→catalog→passthrough precedence
**User Story**: US-001, US-005 | **AC**: AC-US1-03, AC-US1-05, AC-US5-01, AC-US5-02, AC-US5-04 | **Status**: [x] completed
**File**: src/eval/model-resolver.ts (144 lines)
**Test Plan**: Given resolver → When called with alias "opus" and VSKILL_DEFAULT_MODEL_ANTHROPIC set → Then returns env value; when env absent → Then returns catalog default; when input is concrete ID → Then passthrough wins.
**Test**: src/eval/__tests__/model-resolver.test.ts (11 tests covering all precedence branches)
**Ship**: PR #122 squash-merged into main (commit c58151f), released as vskill@0.5.105

### T-006: Wire resolver into llm.ts — remove ANTHROPIC_NORMALIZE
**User Story**: US-001 | **AC**: AC-US1-03 | **Status**: [x] completed
**File**: src/eval/llm.ts:145-160
**Test Plan**: Given llm.ts → When resolving "sonnet" or "opus" → Then delegates to resolveModelId, never reads inline ANTHROPIC_NORMALIZE map.
**Test**: src/eval/__tests__/model-resolver.test.ts ("resolveModelId — ANTHROPIC_NORMALIZE removed" regression check)
**Ship**: PR #122 squash-merged into main (commit c58151f), released as vskill@0.5.105

---

## Phase 2 — Pricing wire

### T-007: Derive PRICING.anthropic from catalog in pricing.ts
**User Story**: US-002 | **AC**: AC-US2-01, AC-US2-05 | **Status**: [x] completed
**File**: src/eval/pricing.ts:17-78
**Test Plan**: Given pricing.ts → When PRICING.anthropic["claude-opus-4-7"] read → Then value matches catalog entry pricing, not a hardcoded literal.
**Test**: src/eval/__tests__/pricing.test.ts:26-32 (Haiku price correction $0.80→$1.00)
**Ship**: PR #122 squash-merged into main (commit c58151f), released as vskill@0.5.105

### T-008: Rebuild MODEL_ALIASES.anthropic from catalog
**User Story**: US-002 | **AC**: AC-US2-01, AC-US2-02 | **Status**: [x] completed
**File**: src/eval/pricing.ts:17-78 (MODEL_ALIASES.anthropic block)
**Test Plan**: Given pricing.ts → When MODEL_ALIASES.anthropic iterated → Then every alias key resolves to a concrete ID present in the catalog; no stale literal IDs.
**Test**: src/eval/__tests__/pricing.test.ts:77-82 (alias round-trip assertions)
**Ship**: PR #122 squash-merged into main (commit c58151f), released as vskill@0.5.105

### T-009: 6-month CI staleness gate test for pricing snapshot
**User Story**: US-002 | **AC**: AC-US2-03 | **Status**: [x] completed
**File**: src/eval/__tests__/anthropic-catalog.test.ts (6-month CI gate assertion)
**Test Plan**: Given snapshotDate in catalog → When today's date is within 6 months → Then test passes; if snapshot is >180 days old → Then test exits non-zero (CI hard fail per ADR 0711-04).
**Test**: src/eval/__tests__/anthropic-catalog.test.ts ("snapshotDate — within 6-month CI gate")
**Ship**: PR #122 squash-merged into main (commit c58151f), released as vskill@0.5.105

### T-010: Correct Haiku pricing $0.80→$1.00 in catalog + pricing tests
**User Story**: US-002 | **AC**: AC-US2-02 | **Status**: [x] completed
**File**: src/eval/__tests__/pricing.test.ts:26-32, 77-82
**Test Plan**: Given Haiku entry → When pricing.test.ts runs → Then $1.00/1M prompt is asserted (not $0.80); existing 0701 Sonnet wire contract ($3/$15) remains green.
**Test**: src/eval/__tests__/pricing.test.ts:26-32, 77-82
**Ship**: PR #122 squash-merged into main (commit c58151f), released as vskill@0.5.105

---

## Phase 3 — Server wiring + provenance SSE

### T-011: Derive PROVIDER_MODELS["anthropic"] from catalog in api-routes.ts
**User Story**: US-001 | **AC**: AC-US1-04, AC-US1-06 | **Status**: [x] completed
**File**: src/eval-server/api-routes.ts:640-665
**Test Plan**: Given api-routes.ts → When PROVIDER_MODELS["anthropic"] built → Then array contains catalog IDs; static array literal is deleted; Opus 4.7 pricing reads $5/$25 (corrected from $15/$75 typo).
**Test**: src/eval-server/__tests__/api-routes.0701.test.ts:191-205 (Opus $5/$25 assertion)
**Ship**: PR #122 squash-merged into main (commit c58151f), released as vskill@0.5.105

### T-012: Correct Opus 4.7 pricing in api-routes test ($15/$75→$5/$25)
**User Story**: US-002 | **AC**: AC-US2-02 | **Status**: [x] completed
**File**: src/eval-server/__tests__/api-routes.0701.test.ts:191-205
**Test Plan**: Given the 0701 pricing test → When Opus 4.7 pricing asserted → Then $5/$25 per-1M values pass (prior test had incorrect $15/$75 sourced from stale hardcode).
**Test**: src/eval-server/__tests__/api-routes.0701.test.ts:191-205
**Ship**: PR #122 squash-merged into main (commit c58151f), released as vskill@0.5.105

### T-013: Emit provenance SSE event in skill-create-routes.ts
**User Story**: US-003 | **AC**: AC-US3-01, AC-US3-02, AC-US3-03 | **Status**: [x] completed
**File**: src/eval-server/skill-create-routes.ts:1295-1313
**Test Plan**: Given a skill generation request → When SSE stream emitted → Then a "provenance" event fires containing resolvedModelId (concrete dated ID), snapshotDate, and resolverSource before the final "done" event.
**Test**: src/eval-server/__tests__/api-routes.0701.test.ts (provenance event shape assertions)
**Ship**: PR #122 squash-merged into main (commit c58151f), released as vskill@0.5.105

---

## Phase 4 — UI provenance wiring

### T-014: Extend aiMetaRef shape with provenance fields
**User Story**: US-003 | **AC**: AC-US3-01, AC-US3-03, AC-US3-06 | **Status**: [x] completed
**File**: src/eval-ui/src/hooks/useCreateSkill.ts:225-244
**Test Plan**: Given useCreateSkill → When aiMetaRef inspected after init → Then shape includes resolvedModelId, snapshotDate, resolverSource fields (undefined until resolved).
**Test**: src/eval-ui/src/hooks/__tests__/useCreateSkill.provenance.test.ts
**Ship**: PR #122 squash-merged into main (commit c58151f), released as vskill@0.5.105

### T-015: Wire provenanceRef — capture SSE provenance event
**User Story**: US-003 | **AC**: AC-US3-04, AC-US3-05 | **Status**: [x] completed
**File**: src/eval-ui/src/hooks/useCreateSkill.ts:348 (provenanceRef assignment)
**Test Plan**: Given a mocked SSE stream with provenance event → When useCreateSkill processes it → Then provenanceRef.current holds the resolved concrete ID (never the alias "opus").
**Test**: src/eval-ui/src/hooks/__tests__/useCreateSkill.provenance.test.ts ("provenanceRef captures SSE event")
**Ship**: PR #122 squash-merged into main (commit c58151f), released as vskill@0.5.105

### T-016: Reset provenance fields on new generation
**User Story**: US-003 | **AC**: AC-US3-04 | **Status**: [x] completed
**File**: src/eval-ui/src/hooks/useCreateSkill.ts:388-405 (reset block)
**Test Plan**: Given a second generation triggered → When reset runs → Then provenanceRef cleared; new provenance event writes fresh concrete ID distinguishable from prior run.
**Test**: src/eval-ui/src/hooks/__tests__/useCreateSkill.provenance.test.ts ("reset clears provenance on re-generate")
**Ship**: PR #122 squash-merged into main (commit c58151f), released as vskill@0.5.105

---

## Phase 5 — Staleness banner (US-004, deferred UI; CI gate shipped)

### T-017: snapshotDate prop on AgentEntry — catalog source plumbing
**User Story**: US-004 | **AC**: AC-US4-01 | **Status**: [x] completed
**File**: src/eval-server/api-routes.ts:640-665 (catalogSnapshotDate field on provider block)
**Test Plan**: Given /api/config response → When provider "anthropic" parsed → Then catalogSnapshotDate field is present and matches ANTHROPIC_CATALOG_SNAPSHOT.snapshotDate.
**Test**: src/eval-server/__tests__/api-routes.0701.test.ts (catalogSnapshotDate assertion)
**Ship**: PR #122 squash-merged into main (commit c58151f), released as vskill@0.5.105

**Note**: Full staleness banner UX (AC-US4-02 through AC-US4-05) deferred per architect's plan — CI gate (T-009) is the hard enforcement; banner is a P2 polish item for a follow-on increment.

---

## Phase 6 — ENV override (US-005)

### T-018: VSKILL_DEFAULT_MODEL_ANTHROPIC plumbed in resolver
**User Story**: US-005 | **AC**: AC-US5-01, AC-US5-02, AC-US5-03, AC-US5-04, AC-US5-05 | **Status**: [x] completed
**File**: src/eval/model-resolver.ts (ENV override branch, lines ~1-50)
**Test Plan**: Given VSKILL_DEFAULT_MODEL_ANTHROPIC="claude-opus-4-8" set → When resolver called with "opus" → Then returns "claude-opus-4-8" verbatim; when explicit CLI ID supplied → Then CLI ID wins over env; when override has no pricing entry → Then pricingUnknown: true returned.
**Test**: src/eval/__tests__/model-resolver.test.ts ("ENV override — wins over snapshot", "explicit ID — wins over env", "ENV override — unknown pricing degrades gracefully")
**Ship**: PR #122 squash-merged into main (commit c58151f), released as vskill@0.5.105

---

## Completion Gate

- [x] All 25 new tests green under `npx vitest run`
- [x] PROVIDER_MODELS["anthropic"] pricing matches catalog (verified by 0701 test with corrected $5/$25)
- [x] `npx tsc --noEmit` clean
- [x] vskill@0.5.105 published to npm + GitHub release tagged
- [x] No new regressions vs origin/main (4 pre-existing failures unchanged)
