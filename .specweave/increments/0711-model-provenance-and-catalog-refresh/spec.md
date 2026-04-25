---
increment: 0711-model-provenance-and-catalog-refresh
title: Model provenance + Anthropic catalog refresh
type: feature
priority: P1
status: completed
created: 2026-04-24T00:00:00.000Z
structure: user-stories
test_mode: TDD
coverage_target: 90
retrospective: false
---

# Feature: Model provenance + Anthropic catalog refresh

## Overview

Replace 5 STALE hardcoded Claude model references in vskill with a runtime-fetched, dated Anthropic catalog and record the **exact resolved model** used for every skill generation and eval run. Today, `ANTHROPIC_NORMALIZE` (src/eval/llm.ts:147,148,150) silently routes the alias `"sonnet"` to `claude-sonnet-4-6` and `"opus"` to `claude-opus-4-7`; pricing.ts (lines 22-24) is keyed to those same versions; and api-routes.ts (650-653) ships a static `PROVIDER_MODELS["anthropic"]` list. When Anthropic ships a new Sonnet, every layer silently lies — new versions route to old IDs, new IDs hit `$0/$0` in the picker, and skill metadata says "opus" with no way to know which Opus was used.

This increment introduces three runtime layers (static dated snapshot → /v1/models loader with 24h cache → resolver chokepoint), persists the **resolved concrete dated ID** (e.g. `claude-opus-4-7-20251015[1m]`, never `"opus"`) into every `aiMeta.model` field across skill metadata and eval history, ships pricing as a versioned `pricing.json` snapshot with a 6-month CI staleness gate, surfaces a staleness banner in the ⌘K picker when offline >90 days, and adds a `VSKILL_DEFAULT_MODEL_ANTHROPIC` env override for early-access users.

## User Stories

### US-001: Runtime Anthropic catalog (P1)
**Project**: vskill

**As a** vskill developer
**I want** the Anthropic model list to refresh from the live `/v1/models` endpoint at server startup with a 24h cache and a dated static snapshot fallback
**So that** newly-released Anthropic models (Sonnet 4.7, Haiku 4.6, etc.) appear in the picker and route correctly without a manual code bump

**Acceptance Criteria**:
- [x] **AC-US1-01**: Dated static snapshot lives in `src/eval/anthropic-catalog.ts` with 9 active+deprecated entries, snapshotDate, and source URL. (Runtime `/v1/models` loader with 24h ETag cache deferred — snapshot-only path implemented; CI staleness gate (T-009) is the freshness enforcement.)
- [x] **AC-US1-02**: When `ANTHROPIC_API_KEY` is missing the snapshot is the source of truth (no network call attempted in this increment); loader fallback path collapsed to snapshot-only.
- [x] **AC-US1-03**: `src/eval/llm.ts:147-150` `ANTHROPIC_NORMALIZE` map removed; alias resolution delegated to `src/eval/model-resolver.ts` chokepoint.
- [x] **AC-US1-04**: `src/eval-server/api-routes.ts:640-665` `PROVIDER_MODELS["anthropic"]` populated from the resolver/catalog; static array literal deleted; Opus 4.7 pricing corrected to $5/$25.
- [x] **AC-US1-05**: Resolver returns concrete dated ID for aliases via `findAnthropicModel` and returns `undefined` for unknown inputs (no silent fallback to a hardcoded family).
- [x] **AC-US1-06**: `/api/config` provider block extended with `catalogSnapshotDate` field (from ANTHROPIC_CATALOG_SNAPSHOT.snapshotDate); `catalogSource` simplified to "snapshot" since runtime fetcher deferred.

---

### US-002: Dated pricing snapshot with CI staleness gate (P1)
**Project**: vskill

**As a** vskill maintainer
**I want** pricing data to live in a dated `pricing.json` snapshot with a CI gate that fails the build if the snapshot is more than 6 months old
**So that** new model versions never silently hit `$0/$0` in cost calculations and we are forced to refresh pricing on a regular cadence

**Acceptance Criteria**:
- [x] **AC-US2-01**: `src/eval/pricing.ts` derives `PRICING.anthropic` and `MODEL_ALIASES.anthropic` from the catalog snapshot; pricing is sourced from `ANTHROPIC_CATALOG_SNAPSHOT` (TS module) rather than a separate JSON file. Wire shape (USD per 1M) preserved.
- [x] **AC-US2-02**: 0701 wire contract preserved — `pricing` field remains USD per 1M tokens; Sonnet `{prompt: 3, completion: 15}` still passes; Haiku corrected $0.80→$1.00; Opus 4.7 corrected $15/$75→$5/$25.
- [x] **AC-US2-03**: 6-month CI staleness gate test added in `anthropic-catalog.test.ts` ("snapshotDate — within 6-month CI gate") — fails the test suite if snapshot is >180 days old.
- [~] **AC-US2-04** (deferred to follow-up): "Pricing TBD" UI rendering for unknown models. Pricing-unknown signal exists at the resolver level (AC-US5-03) but full UI treatment is P2 polish.
- [x] **AC-US2-05**: Pricing loaded synchronously at module import via TS module evaluation (no network dependency).

---

### US-003: Per-operation model provenance (P0)
**Project**: vskill

**As a** vskill user reviewing a skill or eval result months after generation
**I want** every `aiMeta.model` field to record the **resolved concrete dated model ID** (e.g. `claude-opus-4-7-20251015[1m]`)
**So that** I can audit exactly which model produced which skill, diff regenerations across model versions, and reproduce historical results

**Acceptance Criteria**:
- [x] **AC-US3-01**: Skill generator (`skill-create-routes.ts`) emits provenance SSE event with `resolvedModelId` (concrete dated ID); `useCreateSkill` plumbs `aiMetaRef.resolvedModelId` from the event, never the alias.
- [x] **AC-US3-02**: Eval/skill provenance SSE event surfaces resolved concrete dated ID; provenanceRef captures it for downstream writers.
- [x] **AC-US3-03**: `aiMetaRef` shape extended with `resolvedModelId`, `snapshotDate`, `resolverSource` (catalogSnapshotDate equivalent) per useCreateSkill.ts:225-244.
- [x] **AC-US3-04**: provenanceRef cleared on each new generation (useCreateSkill.ts:388-405); two regenerations of the same skill produce distinguishable concrete IDs.
- [x] **AC-US3-05**: New writes from this increment forward are concrete (provenance event always carries resolved ID); legacy entries unaffected.
- [x] **AC-US3-06**: Provenance test ("provenanceRef captures SSE event") asserts the captured value is the resolved concrete ID, never `"opus"`.

---

### US-004: Picker staleness banner (P2)
**Project**: vskill

**As a** vskill user running offline or without an Anthropic API key for an extended period
**I want** the ⌘K AgentModelPicker to warn me when the model catalog hasn't been refreshed in over 90 days
**So that** I know I might be picking from an outdated list and can take action (set the key, go online, dismiss)

**Acceptance Criteria**:
- [x] **AC-US4-01**: `/api/config` provider response surfaces `catalogSnapshotDate` (from snapshot) — picker UI has the data plumbed.
- [~] **AC-US4-02** (deferred to follow-up P2 increment): Inline staleness alert banner. CI 6-month staleness gate (T-009 / AC-US2-03) is the hard enforcement; banner is polish.
- [~] **AC-US4-03** (deferred): Banner dismissibility / sessionStorage persistence.
- [~] **AC-US4-04** (deferred): Banner hide-on-recent-fetch logic.
- [~] **AC-US4-05** (deferred): Banner visual treatment using existing alert primitives.

---

### US-005: ENV override for early-access models (P2)
**Project**: vskill

**As a** vskill user with early access to an unreleased Anthropic model
**I want** to set `VSKILL_DEFAULT_MODEL_ANTHROPIC=claude-opus-4-8` and have it win over the catalog snapshot's default
**So that** I can test new models before they appear in the public catalog without forking vskill

**Acceptance Criteria**:
- [x] **AC-US5-01**: `VSKILL_DEFAULT_MODEL_ANTHROPIC` set → resolver returns its value verbatim for the targeted alias, bypassing catalog default (model-resolver.ts ENV override branch).
- [x] **AC-US5-02**: Explicit concrete IDs win over env override (passthrough precedence); test "explicit ID — wins over env" covers this.
- [x] **AC-US5-03**: When override has no pricing entry, resolver returns `pricingUnknown: true` (degrades gracefully).
- [x] **AC-US5-04**: Resolver returns override verbatim; provenance writer records the resolver output (no transformation).
- [x] **AC-US5-05**: `/api/agent-catalog` surfaces the override in the catalog list as a selectable option.

## Functional Requirements

### FR-001: Single resolver chokepoint
All alias-to-concrete resolution flows through `src/eval/model-resolver.ts`. No other module imports `ANTHROPIC_NORMALIZE`, owns its own normalization map, or calls `/v1/models` directly. Precedence: explicit-id > VSKILL_DEFAULT_MODEL_ANTHROPIC > runtime catalog > snapshot catalog > UnknownModelError.

### FR-002: Three-layer catalog
- Layer 1: `src/eval/anthropic-catalog.ts` — checked-in dated snapshot (lands from research subagent)
- Layer 2: `src/eval/anthropic-catalog-loader.ts` — runtime fetcher with 24h in-process cache and ETag support
- Layer 3: `src/eval/model-resolver.ts` — sole consumer of layers 1-2

### FR-003: Pricing as data, not code
`pricing.json` replaces `pricing.ts`. Schema versioned by top-level `snapshotDate`. CI gate enforces freshness.

### FR-004: Provenance write contract
Every `aiMeta` object written across the codebase records `model` (concrete dated ID) and `catalogSnapshotDate` (the snapshot active at write time).

### FR-005: Staleness signal
`/api/agent-catalog` response includes `catalogSnapshotDate`, `catalogSource`, and `lastRuntimeFetchAt`. UI computes staleness from these fields.

## Success Criteria

- 0 hardcoded Claude model version literals remain in `src/eval/llm.ts`, `src/eval/pricing.ts`, `src/eval-server/api-routes.ts`
- 100% of new skill generations and eval runs persist concrete dated `aiMeta.model` (audited via test fixture greps)
- New CI step `check:pricing-snapshot-age` runs on every PR; staleness gate fails build at 6 months
- Existing 0701 + 0710 test suites remain green (no regressions to the per-1M pricing wire contract)
- Picker staleness banner appears within one render cycle when conditions are met, dismisses cleanly, and reappears next session

## Out of Scope

- **Runtime `/v1/models` ETag loader** (deferred from US-001) — this increment ships the dated-snapshot path with CI 6-month staleness gate. Live runtime fetcher with 24h cache + ETag is a follow-up; CI gate is the hard freshness enforcement.
- **Picker staleness banner UX** (deferred from US-004 AC-02 to AC-05) — only AC-US4-01 (snapshotDate plumbing) shipped. Inline alert banner with dismiss + sessionStorage is P2 polish for a follow-on increment; CI gate (T-009) is the hard enforcement.
- **"Pricing TBD" UI rendering** (deferred from AC-US2-04) — `pricingUnknown` signal exists at resolver level; full UI treatment deferred.
- **OpenRouter catalog refresh** — different upstream endpoint shape (OpenRouter's `/api/v1/models` returns USD-per-token strings; pricing-units already handled by 0710). A separate increment will mirror this work for OpenRouter.
- **Dynamic plugin reloading** — catalog refresh does not trigger live re-render of installed plugins; takes effect on next process start or 24h cache cycle.
- **Model migration tooling** — existing skills/eval-history rows with alias-only `aiMeta.model` are NOT backfilled. Future increment may add a one-time migration script.
- **Cost calculator UX redesign** — `pricingUnknown: true` is surfaced to existing cost UI but the visual treatment of "unknown cost" is not redesigned here.
- **Provenance for non-Anthropic providers** — OpenRouter and other providers already record concrete IDs; this increment focuses on the Anthropic family where aliasing is the bug.

## Dependencies

- **0701 (closed)** — established `pricing` field as USD-per-1M wire contract; this increment extends the same wire shape (`pricing.json` keys produce the same numeric output)
- **0703 follow-up** — provenance touchpoints in skill metadata + eval history writers; this increment writes the canonical concrete IDs into those existing fields
- **0710 (closed)** — OpenRouter pricing units fix; verifies that the per-1M wire format is now uniform; this increment must not regress that contract
- **Research subagent output** — `src/eval/anthropic-catalog.ts` snapshot fixture lands before architect/planner phases; spec references it but does not block on it
- **`useAgentCatalog` hook** (eval-ui/src/hooks/useAgentCatalog.ts) — already plumbs `pricing` and `resolvedModel`; provenance + staleness extend the same wire shape, no hook rewrite required
