---
increment: 0710-openrouter-pricing-units-hotfix
title: 'Hotfix: OpenRouter pricing shows $0.00 in Skill Studio'
type: hotfix
priority: P1
status: completed
created: 2026-04-24T00:00:00.000Z
structure: user-stories
test_mode: TDD
coverage_target: 90
---

# Hotfix: OpenRouter pricing units canonicalization

## Overview

Skill Studio's AgentModelPicker (vskill `eval-ui`) renders every OpenRouter model with `$0.00 / $0.00 per 1M tokens`, making cost comparison impossible. Reported via screenshot at `localhost:3162/?panel=tests#/skills/frontend/frontend-design` on 2026-04-24. Same display surface as 0701 US-002 (Anthropic pricing) but a different ingestion code path that 0701 didn't touch.

## Problem

Two pricing unit conventions collide through one shared `pricing.{prompt,completion}` shape:

| Source | Path | Unit |
|---|---|---|
| Anthropic hardcoded `PROVIDER_MODELS` | `api-routes.ts:648-651` | USD per 1M tokens (`3`, `15`, `75`) |
| OpenRouter ingestion `/api/openrouter/models` | `api-routes.ts:1042-1045` | USD **per token** (raw `parseFloat("0.000003")`) |

Two UI consumers each lock in a different assumption:

| Consumer | Path | Assumption |
|---|---|---|
| `ModelList.formatMetadata` (the row in the screenshot) | `eval-ui/src/components/ModelList.tsx:41-43` | per-1M (`$${p.toFixed(2)}`) → renders OpenRouter as `$0.00` |
| `ModelSearchDropdown.formatPricing` | `eval-ui/src/components/ModelSearchDropdown.tsx:56-62` | per-token (multiplies by `1_000_000`) → only correct for raw OpenRouter input |

0701 already shipped Anthropic per-1M as the wire contract (asserted by `api-routes.0701.test.ts:188,195,202`). The fix must preserve that contract.

## Goal

Make `pricing.{prompt,completion}` mean **USD per 1M tokens everywhere on the wire** — one unit, one place to convert (server-side at the OpenRouter ingestion adapter).

## User Stories

### US-001: Real OpenRouter prices in the picker
**Project**: vskill

**As a** vskill user with an OpenRouter API key configured
**I want** the AgentModelPicker to show accurate per-1M-token input/output prices for every OpenRouter model
**So that** I can pick a model based on cost without leaving the picker or doing mental math

**Acceptance Criteria**:
- [x] **AC-US1-01**: `/api/openrouter/models` response returns `pricing.prompt` and `pricing.completion` in USD per 1M tokens (raw OpenRouter `parseFloat` × `1_000_000`). For OpenRouter input `pricing: { prompt: "0.000003", completion: "0.000015" }`, the response carries `pricing: { prompt: 3, completion: 15 }`.
- [x] **AC-US1-02**: Free models (OpenRouter `prompt: "0"`) round-trip as `pricing: { prompt: 0, completion: 0 }` — no NaN, no infinity, no negative drift.
- [x] **AC-US1-03**: Models missing the `pricing` field on the upstream OpenRouter response default to `pricing: { prompt: 0, completion: 0 }` (preserves current null-safety behavior).
- [x] **AC-US1-04**: `ModelList.formatMetadata` renders OpenRouter rows as `${ctx} ctx · $X.XX / $Y.YY per 1M tokens` with the same code path that already formats Anthropic — no `ModelList` source change, parity proven by a new test fixture.

### US-002: ModelSearchDropdown matches the new wire contract
**Project**: vskill

**As a** vskill developer maintaining `eval-ui`
**I want** every consumer of `model.pricing` to assume the same unit (per-1M)
**So that** future providers added to the picker don't have to remember a hidden ×1,000,000

**Acceptance Criteria**:
- [x] **AC-US2-01**: `ModelSearchDropdown.formatPricing` no longer multiplies `pricing.prompt` by `1_000_000`. For input `pricing: { prompt: 3, completion: 15 }` the popover label reads `"$3.00/1M"` (not `"$3,000,000.00/1M"`).
- [x] **AC-US2-02**: Zero-priced (free) models still render as `"Free"` (existing `=== 0` guard preserved).
- [x] **AC-US2-03**: A doc-comment on `ModelEntry.pricing` (`eval-ui/src/types.ts:713`) and on `OpenRouterCacheEntry` (`api-routes.ts:708-711`) names the canonical unit ("USD per 1M tokens") so future maintainers can't accidentally reintroduce the mismatch.

## Out of Scope

- Cache read/write pricing display (per 0701 — same reasoning).
- Live Anthropic pricing via API (no public endpoint).
- Other providers' pricing (Cursor, Codex, Gemini CLI) — separate increments.
- Migrating `OPENROUTER_CACHE` schema — same shape, only unit semantics change. Existing cached entries on a running server become stale-correct on the next 10-min TTL refresh.

## Dependencies

- 0701-studio-provider-pricing-and-model-identity (closed) — established per-1M as the Anthropic wire contract this hotfix preserves.
- OpenRouter `/v1/models` API — pricing strings remain in USD per token (verified 2026-04-24).
