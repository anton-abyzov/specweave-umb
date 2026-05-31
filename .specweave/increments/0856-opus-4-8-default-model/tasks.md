# 0856 — Tasks

### T-001: Add claude-opus-4-8 catalog entry as the default
**AC**: AC-US1-01, AC-US1-02, AC-US2-04 | **Status**: [x] completed
**Test**: Given the Anthropic catalog → When `claude-opus-4-8` is inserted as the first active model with full pricing and `snapshotDate` is bumped to 2026-05-30 → Then `ANTHROPIC_CATALOG_SNAPSHOT.models[0].id === "claude-opus-4-8"`, the integrity test passes (opus prompt > Sonnet $3), and `PROVIDER_MODELS["anthropic"]` contains it with `{ prompt: 5, completion: 25 }`.

### T-002: Move opus/best/opus[1m] aliases from 4.7 to 4.8
**AC**: AC-US2-01, AC-US2-02, AC-US2-03 | **Status**: [x] completed
**Test**: Given the catalog with both Opus entries → When `opus`/`best`/`opus[1m]` are looked up → Then `findAnthropicModel(...)` and `resolveAnthropicModel(...)` return `claude-opus-4-8` (source `snapshot`), while `claude-opus-4-7` remains resolvable by its canonical id and keeps `aliases: ["claude-opus-4-7[1m]"]`.

### T-003: Round-trip claude-opus-4-8 to the CLI opus alias
**AC**: AC-US1-04 | **Status**: [x] completed
**Test**: Given `CLAUDE_CLI_NORMALIZE` in `src/eval/llm.ts` → When the full id `claude-opus-4-8` is normalized for the Claude CLI → Then it maps to `opus` (single-line map addition; no other region of llm.ts touched).

### T-004: Update intentionally-pinned tests to the new 4.8 default
**AC**: AC-US1-03, AC-US2-01, AC-US2-02 | **Status**: [x] completed
**Test**: Given the four pinned test files (anthropic-catalog, model-resolver, pricing, api-routes.0701) → When the alias-default assertions are repointed to 4.8 (and the passthrough test repointed to the still-unknown `claude-opus-4-9`) → Then `npx vitest run src/eval` and `npx vitest run src/eval-server/__tests__/api-routes.0701.test.ts` pass for these files with no new catalog/resolver/pricing failures.
