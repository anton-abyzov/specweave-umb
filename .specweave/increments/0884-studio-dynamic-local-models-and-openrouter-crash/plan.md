# Implementation Plan: Skill Studio: real local model list + OpenRouter hover-crash fix

## Architecture context

Skill Studio is the Tauri v2 desktop app in `repositories/anton-abyzov/vskill`. Model
catalog flow:

```
eval-server/api-routes.ts
  PROVIDER_MODELS (static seeds)  +  probeOllama()/probeLmStudio() (runtime probes, 30s cache)
        │  GET localhost:11434/api/tags   GET localhost:1234/v1/models
        ▼
  GET /api/config  →  eval-ui/hooks/useAgentCatalog.ts  →  AgentModelPicker / AgentList / ModelList
                       hydrateOpenRouter() lazy-fetches /api/openrouter/models on agent focus/hover
```

## Track A — Server: real local model list (US-001)

File: `src/eval-server/api-routes.ts`

1. `PROVIDER_MODELS["ollama"]` → `[]` (it currently holds the four fake Llama-family
   seeds at ~L1172-1177). LM Studio is already `[]` — bring Ollama to parity.
2. `probeOllama()` (~L1277-1300): start `models` from `[]` (not the seed). Only assign the
   mapped list inside the `if (resp.ok)` success branch. On throw/timeout/non-OK, the
   cached result is `{ available: false, models: [] }`. Keep the existing
   `filter(m => typeof m?.name === "string" && m.name.length > 0)` blank-name guard.
3. Raise the timeout in both `probeOllama()` and `probeLmStudio()`:
   `AbortSignal.timeout(500)` → `AbortSignal.timeout(2000)`. Keep the 30s `PROBE_CACHE_TTL`
   so the slower timeout fires at most once per cache window.
4. Reuse the existing `resetDetectionCache()` test hook for deterministic unit tests.

Net: the picker lists exactly what the runtimes report; an offline runtime yields an empty
list + the existing `ctaType: "start-service"` CTA (unchanged) instead of fake models.

## Track B — Frontend: OpenRouter hover-crash hardening (US-002)

Files: `src/eval-ui/src/hooks/useAgentCatalog.ts`, `src/eval-ui/src/components/ModelList.tsx`

1. `hydrateOpenRouter()` (~L306-319): guard `const list = Array.isArray(data.models) ? data.models : []`
   before `.map`; build entries with `displayName: m.name ?? m.id` and drop entries where
   both `m.id` and `m.name` are missing (`.filter(m => m.id || m.name)`).
2. `ModelList.tsx rankFiltered()` (~L55-65): replace every `m.displayName.toLowerCase()` /
   `a.displayName` / `b.displayName` with a `(m.displayName ?? m.id ?? "")` local so a null
   display name can never throw. `formatMetadata` is already null-safe — leave it.

## Files touched

- `src/eval-server/api-routes.ts` (Track A)
- `src/eval-ui/src/hooks/useAgentCatalog.ts` (Track B)
- `src/eval-ui/src/components/ModelList.tsx` (Track B)
- Tests: `src/eval-server/*.test.ts` (probe), `src/eval-ui/src/**/*.test.ts(x)` (hydrate/rankFiltered),
  `e2e/agent-model-picker.spec.ts`, `e2e/lm-studio-smoke.spec.ts`

## Parallelization

Track A (eval-server) and Track B (eval-ui) touch disjoint files → run as two parallel
agents. No shared edits, no merge conflict risk. TDD (RED→GREEN→REFACTOR) within each track.

## Verification

- `npm run build && npm run build:eval-ui` clean.
- `npx vitest run` — new probe + OpenRouter regression tests green.
- `npx playwright test` — picker hover (no crash) + live-Ollama list assertions green.
- Built Tauri app smoke: Ollama shows `qwen3-coder:30b` + `qwen2.5:14b`; OpenRouter hover ok.
