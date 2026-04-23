# Implementation Plan — skill-builder: Distributable Universal Skill Authoring Package

## Source of Truth

This plan is derived from the approved user-facing plan at `/Users/antonabyzov/.claude/plans/lazy-swinging-wren.md`, refined after a three-agent deep-verification pass (infrastructure claims, Playwright applicability, spec grill). This file distills the corrected architecture and implementation sequence for closure gates.

## Architecture Summary

```
 Host AI agent (49 platforms)
        │
        │ natural-language trigger
        ▼
 skill-builder SKILL.md            ← NEW (this increment)
        │
        │ detection script → path A | B | C
        ▼
 ┌────────────────────────────────────────────────────┐
 │ Path A (preferred): vskill skill new|import|...   │ ← NEW CLI (this increment)
 │ Path B (fallback): vskill eval serve → Skill      │ ← EXISTING React UI (0465)
 │                     Studio browser workspace      │
 │ Path C (last resort, Claude-only):                │
 │           Anthropic skill-creator built-in         │ ← EXISTING (Anthropic ships)
 └────────────────────────────────────────────────────┘
        │
        ▼
 src/core/skill-generator.ts       ← EXTRACTED from skill-create-routes.ts:919-1025 (this increment)
        │
        │ uses (existing infra from 0665)
        ▼
  • agents-registry.ts (49 agents)
  • buildAgentAwareSystemPrompt (skill-create-routes.ts:523-573)
  • installer/canonical.ts (target-agents routing)
  • installer/frontmatter.ts (target-agents field parser)
  • isSkillCreatorInstalled() (detection helper)
```

**Key correction from initial plan**: 0465 shipped a **React UI workspace** at `src/eval-ui/src/pages/workspace/`, NOT a CLI workspace. This increment does not "wrap 0465 workspace as a CLI"; it adds an entirely new CLI (path A) and positions the existing React UI as path B fallback.

**Key correction on skill-creator**: it is an **Anthropic built-in skill** shipped with Claude Code, detected at `~/.claude/skills/skill-creator/`. It is NOT a SpecWeave plugin. `isSkillCreatorInstalled()` (already in 0665 infra) is the detection helper.

## Key Architectural Decisions

### AD-001: Skill lives in vskill, not SpecWeave
**Decision**: Canonical location is `repositories/anton-abyzov/vskill/plugins/skills/skills/skill-builder/SKILL.md`, alongside the existing `scout` meta-skill.
**Rationale**: User explicit requirement — must be tool-agnostic, distributable via verified-skill.com, installable from any AI agent without requiring SpecWeave. Matches the pattern established in 0331 (75 skills migrated from SpecWeave to vskill to shed framework lock-in).

### AD-002: Fallback chain is A → B → C (strict priority, not parallel)
**Decision**: The SKILL.md body specifies CLI → browser UI → Anthropic built-in as a strict priority chain. The detection script (implemented as a small shell snippet in SKILL.md) picks the highest available path and invokes it once.
**Rationale**: Predictable output. Parallel attempts would double token cost and produce inconsistent results. User's "Anthropic is fallback" mandate is satisfied by making path C the last resort AND requiring it only when the host is Claude Code AND skill-creator is actually installed. Referenced by AC-US2-01..07.

### AD-003: Generator extraction, no duplication
**Decision**: Extract the in-HTTP-handler generator at `skill-create-routes.ts:919-1025` into `src/core/skill-generator.ts` as a pure async function. Rewire both the HTTP handler and the new CLI to call it. **Capture pre-extraction snapshots first** (T-000) so post-extraction behavior parity is provable byte-for-byte.
**Rationale**: The HTTP handler and the CLI need the exact same generation behavior. Copy-paste would drift; a shared pure module keeps parity. The HTTP handler shrinks to ≤40 lines of transport concerns (SSE, request parsing). Referenced by AC-US4-01..05.

### AD-004: Divergence report is the one net-new emission artifact
**Decision**: After emitting SKILL.md to N targets, the generator writes `<name>-divergence.md` to the invocation cwd (not the target's path) listing every dropped or translated field per target. Security-critical fields (`allowed-tools`, `context: fork`, `model`) always appear if dropped — silent loss is a test failure.
**Rationale**: Security-critical fields silently lost in translation are a defect (see 0665 US-007 rationale — "generated skills work correctly on non-Claude agents without hooks/MCP/slash commands"). The divergence report makes silent loss impossible. Referenced by AC-US5-01..05, AC-US7-05.

### AD-005: Schema versioning on every emission (except Anthropic fallback)
**Decision**: Generator adds `x-sw-schema-version: 1` to every emitted frontmatter. NOT added to Anthropic-fallback output (that path is not universal-aware and would misrepresent the schema).
**Rationale**: Future evolution. When the schema changes, compilers can detect version and apply migrations deterministically. Referenced by AC-US6-01..04.

### AD-006: No SpecWeave changes for MVP
**Decision**: Zero files modified in `repositories/anton-abyzov/specweave/` for this increment. `sw:skill-gen` keeps its current Anthropic-skill-creator delegation unchanged.
**Rationale**: User explicitly pushed back on "make it part of SpecWeave". Scope hygiene: follow-up increment (separate ID) will rewire `sw:skill-gen → vskill skill new` when both are stable. Referenced by AC-US9-04, FR-001.

### AD-007: Flat directory + unprefixed name
**Decision**: `plugins/skills/skills/skill-builder/SKILL.md` (flat dir, not nested). Frontmatter `name: skill-builder` without any `sw/` prefix.
**Rationale**: Honors `feedback_skill_naming_flat_dirs.md`. This is not a SpecWeave command, so no prefix. Referenced by FR-006.

### AD-008: CLI tests with Vitest, Browser tests with Playwright
**Decision**: Playwright is used ONLY for the Skill Studio browser regression (path B). CLI behavior (path A) is tested with Vitest + `execa`/`spawn`. This reverses the initial plan's mistake of forcing Playwright for CLI integration.
**Rationale**: Playwright's value (DOM, network, screenshots) is irrelevant for asserting "the CLI wrote files to `.claude/skills/`". Vitest + `execa` is faster, simpler, and more honest. Playwright IS the right tool for verifying that T-002's HTTP-handler rewire did not break the existing React Studio. Referenced by AC-US7-01..08.

### AD-009: Activation signal is a sentinel file, not subjective observation
**Decision**: The `skill-builder` SKILL.md, on path A, always writes a sentinel `.skill-builder-invoked.json` to cwd containing `{ trigger, agent, timestamp, targets, prompt }`. Tests grep this file to confirm activation. Manual verification gates use this file as evidence too.
**Rationale**: "Verified in Claude Code and Codex" is untestable without a detectable signal. The sentinel file is cheap (one `fs.writeFile`), non-invasive, and lets automated tests and humans agree on the same pass/fail criterion. Referenced by AC-US1-07.

## ADR References

No new ADRs created. Decisions above are traceable to completed increments 0665 (agent-aware generator), 0465 (React UI workspace), 0331 (skill migration to vskill), 0250 (universal skill discovery), 0586 (SKILL.md cleanup).

## Implementation Sequence (Refined)

### Day 1 — Generator Extraction (with baseline capture)

1. **T-000**: Before any code changes, capture pre-extraction snapshot fixtures by hitting `POST /api/skills/generate` from a test harness for three target combinations (`[claude-code]`, `[claude-code, codex, cursor]`, all 8 universal). Save to `src/core/__tests__/fixtures/pre-extraction-snapshots/`.
2. **T-001**: Create `src/core/skill-generator.ts` with the extracted generator body from `skill-create-routes.ts:919-1025`. Pure async function. No `req`/`res`/SSE references.
3. **T-002**: Rewire the HTTP handler to a thin wrapper (≤40 lines) calling `generateSkill()`.
4. **T-003**: Post-extraction snapshot tests — assert byte-for-byte parity with T-000 fixtures.
5. **Regression check**: all existing eval-ui tests stay green.

### Day 2 — vskill skill CLI

6. **T-004**: Create `src/commands/skill.ts` with `registerSkillCommand(program)` wiring `new|import|list|info|publish`. Register in `src/cli/index.ts`.
7. **T-005**: Implement `new` (shells to generator), `import` (reads existing SKILL.md → generator with re-emit flag).
8. **T-006**: Implement `list` (alias), `info` (frontmatter reader), `publish` (alias to `submit`).
9. **T-007**: Unit tests for flag parsing, target resolution, unknown-target error, missing-prompt error, `--engine=anthropic-skill-creator` delegation.

### Day 3 — SKILL.md Package + Divergence Report + Schema Versioning

10. **T-008**: Write `plugins/skills/skills/skill-builder/SKILL.md` (<500 lines) with trigger phrases, detection script for path A/B/C, "What this is NOT" section cross-linking `scout` and `sw:skill-gen`.
11. **T-008b**: Write 3 reference files (`target-agents.md`, `divergence-report-schema.md`, `fallback-modes.md`, each <100 lines).
12. **T-009**: Add divergence-report generator (~50 LOC) to `src/core/skill-generator.ts`. Include security-critical-field enforcement and negative-case test (emitting with `allowed-tools` to OpenCode without a divergence entry is a test failure).
13. **T-010**: Add `x-sw-schema-version: 1` to every emitted frontmatter (not Anthropic-fallback). Unit test across all 8 universal targets.
14. **T-011**: Register `skill-builder` in `plugins/skills/` manifest. Bump README badge `skills: 7 → 8`.
15. **T-011b**: Add CHANGELOG entry and README "Commands" section for `vskill skill new|import|list|info|publish` with a usage example.

### Day 4 — Test Suite (Vitest for CLI, Playwright for Studio)

16. **T-012**: Write `tests/integration/skill-cli.test.ts` (Vitest + `execa`): sandbox install, generate across targets, divergence assertions, schema-version assertions, `--engine=anthropic-skill-creator` with mocked `isSkillCreatorInstalled()`, `--targets=all` (49 agents), unknown-target error, missing-prompt error, sentinel file assertion for AC-US1-07.
17. **T-012b**: Write `tests/e2e/skill-studio-regression.spec.ts` (Playwright): drive the existing Skill Studio browser flow end-to-end post-T-002 rewire. Asserts the React UI still renders, generates, and emits correctly — regression gate for path B.
18. **T-012c**: **Manual verification gate** — run `vskill eval serve` in a sandbox, walk the "Create a new skill" flow in Chrome, confirm the sentinel file is written and emission lands correctly. Documented pass/fail in the manual-verification checklist in `reports/manual-verification.md`.

### Day 5 — Release (Split into Four Independently Reversible Tasks)

19. **T-013a** (npm publish): `cd repositories/anton-abyzov/vskill && sw:release-npm` (patch release). If this fails, rollback is `npm unpublish` within the 72h window OR patch-forward.
20. **T-013b** (registry submit): `vskill submit plugins/skills/skills/skill-builder`. If this fails, `vskill unsubmit` and retry. npm publish (T-013a) is already complete and survives this rollback.
21. **T-013c** (sandbox smoke test): fresh sandbox, pin vskill to `0.5.80` (older version), `vskill install skill-builder` from registry, invoke "create a skill" trigger, assert multi-target output. If this fails, investigate — don't proceed to T-013d.
22. **T-013d** (umbrella sync + follow-up stub): umbrella sync commit `sync umbrella after vskill v0.5.X release`. Create follow-up SpecWeave increment stub (separate ID) titled "Rewire sw:skill-gen to prefer vskill skill new".

## Testing Strategy

### Unit tests (Vitest)
- `src/commands/__tests__/skill.test.ts` — CLI subcommand routing, flag parsing, target resolution, error paths.
- `src/core/__tests__/skill-generator.test.ts` — generator behavior snapshots (pre + post extraction parity), divergence-report content, schema-version tag presence.
- Pattern: `vi.hoisted()` + `vi.mock()` for ESM mocking, `mkdtemp` + cleanup in `afterEach`.
- Coverage target: ≥90% on `src/core/skill-generator.ts` and `src/commands/skill.ts`.

### Integration tests (Vitest + execa)
- `tests/integration/skill-cli.test.ts` — full `vskill skill new/import/list/info/publish` invocations in sandbox dirs, file-existence assertions, stderr assertions, sentinel file assertions.

### Regression tests (Playwright)
- `tests/e2e/skill-studio-regression.spec.ts` — drives the existing React Skill Studio flow. Model template: `e2e/eval-ui.spec.ts`, `e2e/leaderboard.spec.ts`.
- Boots via existing `playwright.config.ts` webServer (`node dist/index.js eval serve --root e2e/fixtures --port 3077`).

### Manual verification
- `reports/manual-verification.md` — signed-off checklist for path B browser flow (T-012c) and Codex re-verification of sentinel activation.

### Regression gates (must stay green)
- All existing eval-ui unit tests (`npx vitest run src/eval-ui/`).
- All existing `skill-create-routes.ts` tests.
- All existing installer tests (`src/installer/` — verifies `target-agents` routing).

## Risks and Mitigations

| Risk | Likelihood | Mitigation |
|---|---|---|
| Generator extraction introduces subtle behavior change | Low | T-000 captures baseline snapshots BEFORE T-001. T-003 asserts byte-for-byte parity post-extraction. |
| T-002 breaks the React Studio UI silently | Medium | T-012b Playwright regression test drives the UI end-to-end post-rewire. T-012c is manual UI re-verification. |
| `--targets=all` silently skips a malformed agent | Medium | AC-US7-08 asserts all 49 directories receive files; any skipped agent is a test failure. |
| Security-critical field silently dropped | Medium | Negative-case test in T-009 — emitting `allowed-tools` to OpenCode without a divergence entry fails the test. |
| CLI installed but not in PATH → path A falsely detected | Medium | Detection script uses `which vskill` AND `node -e "require.resolve('vskill')"` — covered in AC-US2-06. |
| Anthropic skill-creator absent on test CI | Medium | All path-C tests mock `isSkillCreatorInstalled()`. AC-US2-07 covers the "absent" case with a remediation message. |
| T-001/T-002 slips past Day 1.5 | Medium | Explicit slip plan: if extraction is not done by EOD Day 1, move T-008b reference files to a follow-up and compress Day 3. |
| Registry submit (T-013b) fails | Low | Separated from npm publish (T-013a) — npm is already live; submit retry is independent. `vskill unsubmit` rollback available. |
| 5-day estimate aggressive | Medium | Day 5 split into 4 tasks with independent gates so partial completion is useful (npm + registry before sandbox verify). |

## Open Design Decisions (cross-increment)

### Model Selection (seeded from 0676)

When path A (`vskill skill new|import|...`) drives generation through any LLM hot path, follow the model-selection pattern established in increment `0676-skill-gen-model-selection` and ADR `.specweave/docs/internal/architecture/adr/0676-01-skill-gen-model-selection.md`:

- **Default**: resolve the newest current Opus from `vskill-platform/src/lib/eval/model-registry.ts` — do NOT hardcode a model string. If 0670 needs its own resolver (i.e., operating independently of vskill-platform), mirror the registry pattern rather than duplicating the list: one source of truth per repo, priority-ordered, one-line forward-compat updates.
- **Env override**: honor `SKILL_EVAL_MODEL` (alias or full ID) and `ANTHROPIC_BASE_URL` (AnyModel proxy) so users can route BYO models (GPT-5, Gemini 3, OpenRouter, LM Studio, Ollama) without new SDK deps.
- **Path B (React Studio UI)**: already inherits via `claude-adapter.ts` after 0676 — no work here.
- **Path C (Anthropic skill-creator)**: inherits parent Claude Code session model; skill-creator SKILL.md already documents the `/model opus` recommendation after 0676.

Capture this in whichever module wraps the LLM call in path A (likely `src/core/skill-generator.ts` per the architecture above). Do NOT introduce a second, divergent resolver.

## Definition of Done

- All AC items across US-001..US-009 are `[x]` in spec.md.
- Vitest unit + integration tests green. Coverage ≥90% on new modules.
- Playwright studio regression test green.
- Manual verification checklist signed off (`reports/manual-verification.md`).
- Divergence report and schema-version tag verified in integration tests.
- vskill patch released (T-013a), skill submitted to registry (T-013b), sandbox smoke passed (T-013c), umbrella synced + follow-up stub created (T-013d).
- rubric.md pass-criteria met at the `standard` tier (see rubric.md).
- `sw:done` closure gates pass (code-review, simplify, grill, judge-llm, PM gates).
