# 0856 — Plan

## Approach

The Anthropic catalog (`src/eval/anthropic-catalog.ts`) is the single source of
truth. `PROVIDER_MODELS["anthropic"]`, `pricing.ts`, and the model resolver all
derive from it. So the whole change is:

1. Add a `claude-opus-4-8` entry as the **first** element of
   `ANTHROPIC_CATALOG_SNAPSHOT.models`, mirroring the 4.7 entry's shape.
   - First position = it becomes `PROVIDER_MODELS["anthropic"][0]`, the default
     picker entry (`buildAnthropicProviderModels()` filters `status==="active"`
     and maps in array order; `getEffectiveRawModel` returns `models[0]`).
   - Aliases: `["opus", "opus[1m]", "best", "claude-opus-4-8[1m]"]`.
   - Pricing PLACEHOLDER: `promptUsdPer1M 5.0, completionUsdPer1M 25.0,
     cacheReadUsdPer1M 0.5, cacheWriteUsdPer1M 6.25`.
   - `contextWindow 1_000_000`, `maxOutputTokens 128_000`, `status "active"`,
     `releaseDate "2026-05-30"`, `sunsetDate null`, capabilities mirror 4.7.
2. Strip the default aliases from the 4.7 entry → `aliases: ["claude-opus-4-7[1m]"]`.
   4.7 stays resolvable by its canonical id and its own `[1m]` suffix.
3. Bump `snapshotDate` `2026-04-24` → `2026-05-30`.
4. `src/eval/llm.ts` — add `"claude-opus-4-8": "opus"` to `CLAUDE_CLI_NORMALIZE`
   ONLY (single-line edit; the rest of llm.ts is owned by a parallel agent).

## Pinned-test updates (the alias move is intentional; pinned tests reflect it)

- `src/eval/__tests__/anthropic-catalog.test.ts`: `opus`/`best`/`opus[1m]`/`OPUS`
  now resolve to `claude-opus-4-8`; added a positive test that 4.7 is still
  reachable by canonical id and by `findAnthropicModel("claude-opus-4-8")`.
- `src/eval/__tests__/model-resolver.test.ts`: `resolveAnthropicModel("opus")`,
  `"best"`, `"opus[1m]"`, and the whitespace-override `opus` case → 4.8;
  added a snapshot-source test for the full `claude-opus-4-8` id; re-pointed the
  passthrough test from `claude-opus-4-8-20260601` to the still-unknown
  `claude-opus-4-9` so it keeps exercising passthrough.
- `src/eval/__tests__/pricing.test.ts`: renamed the `opus` alias test to 4.8
  (pricing assertion `inputPerMillion === 5` unchanged).
- `src/eval-server/__tests__/api-routes.0701.test.ts`: added a pin that
  `PROVIDER_MODELS["anthropic"]` contains `claude-opus-4-8` with
  `{ prompt: 5, completion: 25 }`.

## Verification

- `npx vitest run src/eval`
- `npx vitest run src/eval-server/__tests__/api-routes.0701.test.ts`

## Risks

- Placeholder pricing must be refreshed when Anthropic publishes Opus 4.8 rates.
- Pre-existing UI test failures (`SkillDetailPanel.test.tsx`, 0845
  InstallTargetsModal `deriveBadge`) are unrelated baseline breakage, not from
  this change — those files are not touched here.
