# Tasks: Hotfix — OpenRouter pricing units canonicalization

## Notation

- `[T###]`: Task ID
- `[P]`: Parallelizable
- `[ ]`: Not started · `[x]`: Completed

All work is in `repositories/anton-abyzov/vskill/`. Strict TDD: every code task has a failing test that lands first.

---

## Phase 1: RED — failing tests

### T-001: Server test — OpenRouter ingestion converts per-token to per-1M
**User Story**: US-001 | **AC**: AC-US1-01, AC-US1-02, AC-US1-03 | **Status**: [x] completed

**File**: `src/eval-server/__tests__/api-routes.openrouter-pricing.test.ts` (NEW)

**Implementation**:
- Mock `global.fetch` (using `vi.hoisted()` + `vi.mock()` pattern from `openrouter-cache.test.ts`) to return a synthetic OpenRouter `/v1/models` body.
- Stand up the express router via `createApiRouter({...})` the same way `openrouter-cache.test.ts` does (or import the express handler directly if exposed).
- Provide a configured `OPENROUTER_API_KEY` env so the route doesn't 400.
- Reset `OPENROUTER_CACHE` between tests.

**Test Plan** (Given/When/Then):
- **TC-001**: Per-1M conversion (Sonnet-class rate)
  - **Given** OpenRouter returns `{ data: [{ id: "anthropic/claude-sonnet-4", name: "Sonnet", context_length: 200000, pricing: { prompt: "0.000003", completion: "0.000015" } }] }`
  - **When** `GET /api/openrouter/models` is called with a valid OpenRouter API key
  - **Then** response `models[0].pricing` deep-equals `{ prompt: 3, completion: 15 }`
- **TC-002**: Free models stay free
  - **Given** OpenRouter returns a model with `pricing: { prompt: "0", completion: "0" }`
  - **When** `GET /api/openrouter/models`
  - **Then** response model `.pricing` equals `{ prompt: 0, completion: 0 }` (not NaN, not negative, not Infinity)
- **TC-003**: Missing pricing field defaults to zero
  - **Given** OpenRouter returns a model with no `pricing` key
  - **When** `GET /api/openrouter/models`
  - **Then** response model `.pricing` equals `{ prompt: 0, completion: 0 }` (preserves current null-safety)

---

### T-002: UI test — ModelSearchDropdown formats per-1M without re-multiplying
**User Story**: US-002 | **AC**: AC-US2-01, AC-US2-02 | **Status**: [x] completed

**File**: `src/eval-ui/src/components/__tests__/ModelSearchDropdown.pricing.test.tsx` (NEW)

**Implementation**:
- Use `@testing-library/react` `render` (pattern from `ModelList.0701.test.tsx`).
- Stub the model search dropdown's `models` prop with controlled fixtures.

**Test Plan** (Given/When/Then):
- **TC-004**: Per-1M wire format renders correctly
  - **Given** a model with `pricing: { prompt: 3, completion: 15 }` (per-1M)
  - **When** ModelSearchDropdown is opened and the model is visible
  - **Then** the rendered text contains `"$3.00/1M"` and does NOT contain `"$3,000,000.00/1M"`
- **TC-005**: Free guard preserved
  - **Given** a model with `pricing: { prompt: 0, completion: 0 }`
  - **When** ModelSearchDropdown renders that row
  - **Then** the rendered text contains `"Free"`

---

### T-003: UI test — ModelList renders OpenRouter rows with per-1M values
**User Story**: US-001 | **AC**: AC-US1-04 | **Status**: [x] completed

**File**: `src/eval-ui/src/components/__tests__/ModelList.0701.test.tsx` (EXTEND)

**Implementation**:
- Add a new test case alongside existing 0701 cases, using the same `render(<ModelList ... />)` pattern.

**Test Plan** (Given/When/Then):
- **TC-006**: OpenRouter row metadata
  - **Given** an `agent` with `id: "openrouter"`, `available: true`, and a model `{ pricing: { prompt: 1.25, completion: 5 }, contextWindow: 200000, displayName: "OR Test", billingMode: "per-token" }`
  - **When** ModelList is rendered with that agent
  - **Then** the rendered row metadata text matches `/200k ctx · \$1\.25 \/ \$5\.00 per 1M tokens/`

---

## Phase 2: GREEN — minimum implementation (failing tests turn green)

### T-004: Server canonicalization — multiply OpenRouter pricing by 1_000_000
**User Story**: US-001 | **AC**: AC-US1-01, AC-US1-02, AC-US1-03 | **Status**: [x] completed

**File**: `src/eval-server/api-routes.ts:1042-1045`

**Change**:
```ts
pricing: {
  prompt: parseFloat(m.pricing?.prompt || "0") * 1_000_000,
  completion: parseFloat(m.pricing?.completion || "0") * 1_000_000,
},
```

**Test Plan**: T-001 turns green.

**Dependencies**: T-001 must exist and be RED first.

---

### T-005: UI canonicalization — drop ×1,000,000 in ModelSearchDropdown
**User Story**: US-002 | **AC**: AC-US2-01, AC-US2-02 | **Status**: [x] completed

**File**: `src/eval-ui/src/components/ModelSearchDropdown.tsx:56-62`

**Change**:
```ts
function formatPricing(model: OpenRouterModel): string {
  const prompt = model.pricing?.prompt;
  if (prompt == null || prompt === 0) return "Free";
  // Wire format is USD per 1M tokens (canonicalized server-side).
  return `$${prompt.toFixed(2)}/1M`;
}
```

**Test Plan**: T-002 turns green.

**Dependencies**: T-002 must exist and be RED first.

---

## Phase 3: REFACTOR — documentation only (no behavior change)

### T-006: Doc comment on OpenRouterCacheEntry
**User Story**: US-002 | **AC**: AC-US2-03 | **Status**: [x] completed

**File**: `src/eval-server/api-routes.ts:708-711`

**Change**: Add JSDoc on the `pricing` field of `OpenRouterCacheEntry.value` member type:
```ts
/** USD per 1M tokens (canonical wire unit; OpenRouter source values are per-token and converted at ingestion). */
pricing: { prompt: number; completion: number };
```

**Test Plan**: No behavior change — full suite still passes.

---

### T-007: Doc comment on ModelEntry.pricing
**User Story**: US-002 | **AC**: AC-US2-03 | **Status**: [x] completed

**File**: `src/eval-ui/src/types.ts:713`

**Change**: Add JSDoc:
```ts
/** USD per 1M tokens (canonical wire unit). */
pricing: { prompt: number; completion: number };
```

**Test Plan**: TypeScript compile clean. No behavior change.

---

## Phase 4: Verification

### T-008: Full vskill vitest suite — no regressions
**Status**: [x] completed

**Command**: `cd repositories/anton-abyzov/vskill && npx vitest run`

**Acceptance**:
- All new tests (T-001, T-002, T-003) pass.
- 0701 suite (`api-routes.0701.test.ts`, `ModelList.0701.test.tsx`) remains green — proves Anthropic per-1M contract preserved.
- No new failures introduced anywhere in the suite.

---

### T-009: TypeScript typecheck clean
**Status**: [x] completed

**Command**: `cd repositories/anton-abyzov/vskill && npx tsc --noEmit`

**Acceptance**: Zero errors. (Doc comments don't affect type structure.)

---

### T-010: Manual smoke at localhost:3162
**Status**: [x] completed

**Steps**:
1. Restart eval-server (clears `OPENROUTER_CACHE` of stale per-token values from prior runs).
2. Open `localhost:3162/?panel=tests#/skills/frontend/frontend-design` (the URL from the bug report).
3. Click the model picker, select **OpenRouter**.
4. **Expected**: rows show real prices like `$3.00 / $15.00 per 1M tokens` (not `$0.00`).
5. Open the OpenRouter search dropdown popover. **Expected**: labels read e.g. `$3.00/1M` (not `$3,000,000.00/1M`).
6. Free models (e.g. Hy3 preview free) **Expected**: still show `Free` in the dropdown.
