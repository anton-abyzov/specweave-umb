# Implementation Plan: Hotfix — OpenRouter pricing units canonicalization

## Overview

Two-edit hotfix that canonicalizes `pricing.{prompt,completion}` to **USD per 1M tokens** on the wire from `/api/openrouter/models`, plus a redundant `× 1_000_000` removal in one downstream consumer. Plus three documentation comments to prevent regression.

**No new endpoints. No schema migration. No state changes. Pass-through hooks (`useAgentCatalog`) remain correct after the change.**

## Architecture

### Components touched

| Component | Path | Change |
|---|---|---|
| OpenRouter ingestion adapter | `repositories/anton-abyzov/vskill/src/eval-server/api-routes.ts:1038-1046` | Multiply `parseFloat` by `1_000_000` for both `prompt` and `completion` |
| OpenRouter cache type | `repositories/anton-abyzov/vskill/src/eval-server/api-routes.ts:708-711` | JSDoc comment naming canonical unit |
| Wire/UI type | `repositories/anton-abyzov/vskill/src/eval-ui/src/types.ts:713` | JSDoc comment naming canonical unit |
| ModelSearchDropdown | `repositories/anton-abyzov/vskill/src/eval-ui/src/components/ModelSearchDropdown.tsx:56-62` | Drop `* 1_000_000` from `formatPricing`; replace with comment naming canonical unit |

### Data flow (unchanged shape, unit-normalized)

```
OpenRouter /v1/models
  ↓ pricing.prompt = "0.000003"   ← USD per token (upstream contract, fixed)
api-routes.ts:1042-1045 (THIS FIX)
  ↓ parseFloat × 1_000_000        ← canonicalize to per-1M
OPENROUTER_CACHE (10-min TTL, per-key)
  ↓ pricing.prompt = 3            ← USD per 1M tokens (canonical wire unit)
GET /api/openrouter/models response
  ↓ pricing.prompt = 3
useAgentCatalog.hydrateOpenRouter (pass-through)
  ↓ pricing.prompt = 3
ModelList.formatMetadata          → "$3.00 / $15.00 per 1M tokens"   ✓
ModelSearchDropdown.formatPricing  (THIS FIX, drop ×1M)
  → "$3.00/1M"                                                       ✓
```

### Why server-side normalization (not "fix `ModelList` to multiply")

- **Preserves 0701's contract.** `api-routes.0701.test.ts:188,195,202` and `ModelList.0701.test.tsx:45,106` already lock per-1M as the Anthropic wire contract. Reverting to per-token would require updating `PROVIDER_MODELS["anthropic"]` (`api-routes.ts:648-651`) from `{ prompt: 3, completion: 15 }` to fractional values like `{ prompt: 0.000003, completion: 0.000015 }` — breaking 0701 tests and reintroducing magic numbers everywhere.
- **One conversion site.** Every future consumer (a sparkline tooltip, a budget calculator, an A/B picker) gets per-1M for free. Per-token would force every consumer to remember `× 1_000_000`.
- **Cache becomes self-describing.** `OPENROUTER_CACHE` stores already-normalized values; debug dumps from a running server are immediately legible.
- **Survives upstream format drift.** If OpenRouter ever switches to per-1k or per-1M strings, only the ingestion adapter changes — every downstream consumer is invariant.

## Architecture Decisions

**ADR-0710-01: `pricing.{prompt,completion}` is canonically USD per 1M tokens on the wire.**
- *Why*: 0701 already shipped this contract for Anthropic; consumers are easier to reason about with one unit; only one adapter needs to convert.
- *Alternatives considered*:
  - "Per-token everywhere" — rejected: breaks 0701 tests and Anthropic hardcoded fixtures.
  - "Add a `pricingUnit` enum field" — rejected: overengineering for two providers; doc-comments + tests are sufficient enforcement.
- *Enforcement*: doc-comments at `OpenRouterCacheEntry` and `ModelEntry.pricing`; tests asserting per-1M values for both Anthropic and OpenRouter paths.

## Technology Stack

- **Language**: TypeScript (existing).
- **Test runner**: Vitest with `vi.hoisted()` + `vi.mock()` ESM mocking pattern (existing — see `openrouter-cache.test.ts:11-19`).
- **Test renderer for UI**: `@testing-library/react` (existing — `ModelList.0701.test.tsx`).
- **No new dependencies.**

## Implementation Phases

### Phase RED — failing tests
1. New `src/eval-server/__tests__/api-routes.openrouter-pricing.test.ts` — mock fetch to OpenRouter `/v1/models`, hit `/api/openrouter/models`, assert per-1M values; cover free model + missing-pricing edge cases.
2. New `src/eval-ui/src/components/__tests__/ModelSearchDropdown.pricing.test.tsx` — render with per-1M fixture, assert `"$3.00/1M"` (NOT `"$3,000,000.00/1M"`); assert `"Free"` for `pricing.prompt === 0`.
3. Extend `src/eval-ui/src/components/__tests__/ModelList.0701.test.tsx` — add OpenRouter-shape fixture asserting `"$1.25 / $5.00 per 1M tokens"`.

### Phase GREEN — minimum implementation
1. Edit `api-routes.ts:1042-1045` — multiply both `parseFloat` results by `1_000_000`.
2. Edit `ModelSearchDropdown.tsx:60` — remove `* 1_000_000`, format `prompt` directly.

### Phase REFACTOR — documentation only
1. Add JSDoc comment on `OpenRouterCacheEntry.value.pricing` (`api-routes.ts:708-711`): `"USD per 1M tokens (canonical wire unit)."`
2. Add JSDoc comment on `ModelEntry.pricing` (`types.ts:713`): same wording.
3. Verify no behavior change.

## Testing Strategy

- **Unit (server)**: Vitest with mocked `global.fetch`, hits the express handler in-process; resets `OPENROUTER_CACHE` between tests via `resetOpenRouterCache()`.
- **Unit (UI)**: Vitest + React Testing Library; assert `screen.getByText` matches the formatted price.
- **Regression**: Full vskill suite (`npx vitest run`) must pass — especially `api-routes.0701.test.ts` (Anthropic per-1M) and `ModelList.0701.test.tsx` (Anthropic display).
- **E2E (manual)**: localhost:3162 — open AgentModelPicker → OpenRouter → confirm rows show real prices like `$3.00 / $15.00 per 1M tokens` (not `$0.00`); confirm OpenRouter dropdown popover shows `$3.00/1M` (not `$3,000,000.00/1M`).
- **TypeScript**: `npx tsc --noEmit` — no type changes, only doc comments; should remain green.

## Technical Challenges

### Challenge 1: Stale in-memory cache after deploy
**Issue**: A running dev server with the old code has cached per-token values; first hit after the fix reads stale per-token data, rendering as `$0.00` for up to 10 minutes.
**Solution**: Acceptable on a dev tool. Restart of the eval-server clears `OPENROUTER_CACHE` (it's process-memory only, no persistence). Document in PR description.
**Risk**: Low. No production deploy involved; localhost only.

### Challenge 2: Existing tests must keep asserting per-1M for Anthropic
**Issue**: 0701 tests at `api-routes.0701.test.ts:188,195,202` assert `{ prompt: 3, completion: 15 }` etc. The fix must not touch the Anthropic path.
**Solution**: Anthropic ingestion is via the `PROVIDER_MODELS` constant (`api-routes.ts:648-651`) — physically separate from the OpenRouter `/v1/models` handler at `api-routes.ts:1038-1046`. The fix is scoped to the OpenRouter `data.data.map()` body only.
**Risk**: Low — verified by exploration; the two code paths don't share a function.

### Challenge 3: ModelSearchDropdown is the only other consumer
**Issue**: If a future consumer (yet to be written) assumed per-token, removing the multiplier in ModelSearchDropdown would break it.
**Solution**: Doc-comments on `OpenRouterCacheEntry` and `ModelEntry.pricing` declare the canonical unit. Future consumers read the type and get it right.
**Risk**: Mitigated by tests + comments; no current code matches that pattern.
