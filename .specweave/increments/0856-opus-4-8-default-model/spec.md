# 0856 — Add Claude Opus 4.8 and make it the opus/best default

## Context

Anthropic shipped **Claude Opus 4.8**. The vskill Anthropic model catalog
(`src/eval/anthropic-catalog.ts`) already carries Opus 4.7 and binds the bare
`opus` / `best` aliases (plus the `[1m]` context-window suffix) to it. Anton
decided Opus 4.8 should become the new default: it must appear in the catalog
**and** take over the `opus` / `best` / `opus[1m]` aliases, demoting 4.7 to a
canonical-id-only entry that is still resolvable but no longer the default.

Official Opus 4.8 pricing is **not yet published**. We ship a PLACEHOLDER price
mirroring Opus 4.7 ($5 / $25 per 1M, $0.5 cache-read, $6.25 cache-write). This
satisfies the catalog integrity invariant (opus prompt price > Sonnet's $3) and
must be refreshed once Anthropic publishes the real numbers.

## User Stories

### US-001 — Select Opus 4.8 to run a skill
As a vskill user, I want Claude Opus 4.8 available as a selectable Anthropic
model so I can run a skill against the newest Opus.

**Acceptance Criteria**
- AC-US1-01: `claude-opus-4-8` exists in `ANTHROPIC_CATALOG_SNAPSHOT.models`
  with a complete, positive pricing block and `status: "active"`.
- AC-US1-02: `claude-opus-4-8` surfaces in `PROVIDER_MODELS["anthropic"]`
  (derived from the catalog) with pricing `{ prompt: 5, completion: 25 }`.
- AC-US1-03: `resolveAnthropicModel("claude-opus-4-8")` resolves from the
  snapshot (`source: "snapshot"`, non-null pricing), NOT passthrough.
- AC-US1-04: The full id `claude-opus-4-8` round-trips to the CLI `opus` alias
  via `CLAUDE_CLI_NORMALIZE` in `src/eval/llm.ts`.

### US-002 — Opus 4.8 is the new opus/best default
As a vskill user, when I ask for `opus` / `best` (or `opus[1m]`) I want Opus 4.8,
because it is now the default Opus tier.

**Acceptance Criteria**
- AC-US2-01: `findAnthropicModel("opus")`, `findAnthropicModel("best")`, and
  `findAnthropicModel("opus[1m]")` all resolve to `claude-opus-4-8`.
- AC-US2-02: `resolveAnthropicModel("opus")` and `resolveAnthropicModel("best")`
  resolve to `claude-opus-4-8` with `source: "snapshot"`.
- AC-US2-03: Opus 4.7 keeps `aliases: ["claude-opus-4-7[1m]"]` and is still
  resolvable by its canonical id `claude-opus-4-7` (regression guarantee:
  create -> install -> use a non-default model still works for 4.7).
- AC-US2-04: `snapshotDate` bumped to `2026-05-30` so the 6-month staleness CI
  gate stays green.

## Out of scope / Notes
- Pricing for Opus 4.8 is a PLACEHOLDER until Anthropic publishes official rates.
- No UI/component changes; catalog + resolver + normalize map only.
