---
increment: 0711-model-provenance-and-catalog-refresh
title: "Model provenance + Anthropic catalog refresh"
type: feature
priority: P1
status: ready_for_review
created: 2026-04-24
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
- [ ] **AC-US1-01**: `src/eval/anthropic-catalog-loader.ts` fetches `https://api.anthropic.com/v1/models` on first request, caches the response in-process for 24h, and refreshes via ETag on subsequent expirations
- [ ] **AC-US1-02**: When `ANTHROPIC_API_KEY` is missing OR the upstream call fails (network, 5xx, timeout >5s), the loader returns the dated static snapshot from `src/eval/anthropic-catalog.ts` without throwing
- [ ] **AC-US1-03**: `src/eval/llm.ts:147-150` `ANTHROPIC_NORMALIZE` map is removed; alias resolution (`"sonnet"`, `"opus"`, `"haiku"`) is delegated to a single `src/eval/model-resolver.ts` chokepoint that consults the catalog
- [ ] **AC-US1-04**: `src/eval-server/api-routes.ts:650-653` `PROVIDER_MODELS["anthropic"]` is populated from the resolver (runtime catalog when present, snapshot otherwise); the static array literal is deleted
- [ ] **AC-US1-05**: Resolver returns the concrete dated ID for an alias (e.g. `"sonnet"` → `claude-sonnet-4-6-20260101[1m]`) and throws `UnknownModelError` for unrecognized inputs (no silent fallback to a hardcoded family)
- [ ] **AC-US1-06**: `/api/agent-catalog` response shape extends with `catalogSnapshotDate: string` and `catalogSource: "runtime" | "snapshot"`; `useAgentCatalog` plumbs both to UI without breaking existing pricing/resolvedModel fields

---

### US-002: Dated pricing snapshot with CI staleness gate (P1)
**Project**: vskill

**As a** vskill maintainer
**I want** pricing data to live in a dated `pricing.json` snapshot with a CI gate that fails the build if the snapshot is more than 6 months old
**So that** new model versions never silently hit `$0/$0` in cost calculations and we are forced to refresh pricing on a regular cadence

**Acceptance Criteria**:
- [ ] **AC-US2-01**: `src/eval/pricing.ts` is converted to `src/eval/pricing.json` with shape `{ snapshotDate: "YYYY-MM-DD", models: { "<resolvedId>": { promptPer1M: number, completionPer1M: number, currency: "USD" } } }`
- [ ] **AC-US2-02**: Existing 0701 wire contract is preserved — `pricing` field remains USD per 1M tokens; tests `api-routes.0701.test.ts:188,195,202` and `ModelList.0701.test.tsx:45,106` continue to pass with `pricing: { prompt: 3, completion: 15 }` for Sonnet
- [ ] **AC-US2-03**: New script `npm run check:pricing-snapshot-age` reads `snapshotDate` and exits non-zero if it is >6 months older than today; wired into the existing CI test pipeline
- [ ] **AC-US2-04**: Models in the catalog with no entry in `pricing.json` render `"Pricing TBD"` in the UI (not `$0/$0`); cost-calculator returns `null` with `pricingUnknown: true` rather than zero
- [ ] **AC-US2-05**: Loading `pricing.json` is synchronous at module import (JSON parse from disk), no network dependency

---

### US-003: Per-operation model provenance (P0)
**Project**: vskill

**As a** vskill user reviewing a skill or eval result months after generation
**I want** every `aiMeta.model` field to record the **resolved concrete dated model ID** (e.g. `claude-opus-4-7-20251015[1m]`)
**So that** I can audit exactly which model produced which skill, diff regenerations across model versions, and reproduce historical results

**Acceptance Criteria**:
- [ ] **AC-US3-01**: Skill generator (`src/skill-builder/...` write paths) records `aiMeta.model` as the resolved concrete dated ID returned by the resolver, never an alias like `"opus"` or `"sonnet"`
- [ ] **AC-US3-02**: Eval history writer (`src/eval/...` write paths) records `aiMeta.model` as the resolved concrete dated ID for every eval run
- [ ] **AC-US3-03**: `aiMeta` schema gains a `catalogSnapshotDate` field capturing which catalog version was active when the resolution happened (lets future readers reconstruct what `"opus"` meant on that date)
- [ ] **AC-US3-04**: Regenerating a skill on a newer model writes a NEW `aiMeta.model` value; eval history diff view keys runs by their concrete IDs so two regenerations of the same skill across model versions are distinguishable
- [ ] **AC-US3-05**: Legacy entries with alias-only `aiMeta.model` are NOT migrated retroactively (out-of-scope per increment boundary), but every NEW write from this increment forward is concrete
- [ ] **AC-US3-06**: Unit test asserts that calling the resolver with `"opus"` produces a value matching the regex `/^claude-opus-\d+-\d+-\d{8}/` and never the literal string `"opus"`

---

### US-004: Picker staleness banner (P2)
**Project**: vskill

**As a** vskill user running offline or without an Anthropic API key for an extended period
**I want** the ⌘K AgentModelPicker to warn me when the model catalog hasn't been refreshed in over 90 days
**So that** I know I might be picking from an outdated list and can take action (set the key, go online, dismiss)

**Acceptance Criteria**:
- [ ] **AC-US4-01**: AgentModelPicker shows a subtle footer caption with the active snapshot date and last successful runtime fetch time (e.g. `"Catalog: 2026-04-24 · refreshed 3h ago"`)
- [ ] **AC-US4-02**: When `catalogSnapshotDate` is >90 days old AND the last successful runtime fetch is also >24h ago, an inline alert banner appears above the model list: `"Model catalog may be stale — last refreshed N days ago. Set ANTHROPIC_API_KEY for live updates."`
- [ ] **AC-US4-03**: Banner is dismissible via close button; dismissal persists per-session in `sessionStorage` and reappears on next session
- [ ] **AC-US4-04**: Banner is hidden whenever a successful runtime fetch occurred in the last 24h, regardless of snapshot date
- [ ] **AC-US4-05**: Banner uses existing alert component styles (no new visual primitives)

---

### US-005: ENV override for early-access models (P2)
**Project**: vskill

**As a** vskill user with early access to an unreleased Anthropic model
**I want** to set `VSKILL_DEFAULT_MODEL_ANTHROPIC=claude-opus-4-8` and have it win over the catalog snapshot's default
**So that** I can test new models before they appear in the public catalog without forking vskill

**Acceptance Criteria**:
- [ ] **AC-US5-01**: When `VSKILL_DEFAULT_MODEL_ANTHROPIC` is set, the resolver returns its value verbatim for the `"opus"` alias (or whichever family the override targets), bypassing catalog default selection
- [ ] **AC-US5-02**: Explicit user-supplied concrete IDs (CLI flags, API requests) win over the env override (most-specific-wins precedence)
- [x] **AC-US5-03**: When the override value has no entry in `pricing.json`, pricing renders as `"Pricing TBD"` and cost calc returns `pricingUnknown: true` (degrades gracefully, never crashes)
- [ ] **AC-US5-04**: Provenance writer records the literal env-override value into `aiMeta.model` (no transformation)
- [x] **AC-US5-05**: `/api/agent-catalog` response surfaces the override in the catalog list so the picker shows it as a selectable option marked `"(env override)"`

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
