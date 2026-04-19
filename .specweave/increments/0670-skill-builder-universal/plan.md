# Implementation Plan — skill-builder: Distributable Universal Skill Authoring Package

## Source of Truth

This plan is derived from the approved user-facing plan at `/Users/antonabyzov/.claude/plans/lazy-swinging-wren.md`. That plan is the authoritative design document. This file distills the architecture and implementation sequence for closure gates.

## Architecture Summary

```
 Host AI agent (49 platforms)
        │
        │ natural-language trigger
        ▼
 skill-builder SKILL.md            ← NEW (this increment)
        │
        │ shells out (path A)
        ▼
 vskill skill new|import|list|...  ← NEW CLI subcommand (this increment)
        │
        │ calls
        ▼
 src/core/skill-generator.ts       ← EXTRACTED from skill-create-routes.ts (this increment)
        │
        │ uses
        ▼
 Existing infra (0665 + 0465):
  • agents-registry.ts (49 agents, feature flags)
  • buildAgentAwareSystemPrompt
  • installer/canonical.ts (target-agents routing)
  • isSkillCreatorInstalled() fallback detection
  • eval-ui SkillWorkspace (path B fallback)
  • Anthropic skill-creator plugin (path C fallback)
```

## Key Architectural Decisions

### AD-001: Skill lives in vskill, not SpecWeave
**Decision**: Canonical location is `repositories/anton-abyzov/vskill/plugins/skills/skills/skill-builder/SKILL.md`, alongside the existing `scout` meta-skill.
**Rationale**: User explicit requirement — must be tool-agnostic, distributable via verified-skill.com, installable from any AI agent without requiring SpecWeave. Matches the pattern established in increment 0331 (75 skills migrated from SpecWeave to vskill to shed framework lock-in).

### AD-002: Fallback chain is A → B → C (strict priority, not parallel)
**Decision**: The SKILL.md body specifies CLI → browser UI → Anthropic plugin as a strict priority chain. The agent tries A first, falls through only if A fails.
**Rationale**: Predictable output. Parallel attempts would double token cost and produce inconsistent results. User's "Anthropic is fallback" mandate is satisfied by making path C the last resort.

### AD-003: Generator extraction, no duplication
**Decision**: Extract the in-HTTP-handler generator at `skill-create-routes.ts:919-1100` into `src/core/skill-generator.ts` as a pure async function. Rewire both the HTTP handler and the new CLI to call it.
**Rationale**: The HTTP handler and the CLI need the exact same generation behavior. Copy-paste would drift; a shared pure module keeps parity. The HTTP handler shrinks to ≤40 lines of transport concerns (SSE, request parsing). Referenced by AC-US4-01..05.

### AD-004: Divergence report is the one net-new emission artifact
**Decision**: After emitting SKILL.md to N targets, the generator writes `<name>-divergence.md` to the project root listing every dropped or translated field per target.
**Rationale**: Security-critical fields (`allowed-tools`, `context: fork`, `model`) silently lost in translation are a defect (see 0665 US-007 rationale — "generated skills work correctly on non-Claude agents without hooks/MCP/slash commands"). The divergence report makes silent loss impossible. Referenced by AC-US5-01..05.

### AD-005: Schema versioning on every emission
**Decision**: Generator adds `x-sw-schema-version: 1` to every emitted frontmatter. Not added to Anthropic-fallback output (fallback is not universal-aware).
**Rationale**: Future evolution. When the schema changes, compilers can detect version and apply migrations deterministically. Referenced by AC-US6-01..04.

### AD-006: No SpecWeave changes for MVP
**Decision**: Zero files modified in `repositories/anton-abyzov/specweave/` for this increment. `sw:skill-gen` keeps its current Anthropic-skill-creator delegation unchanged.
**Rationale**: User explicitly pushed back on "make it part of SpecWeave" in the plan-review iteration. Scope hygiene: follow-up increment (tracked separately) will rewire `sw:skill-gen → vskill skill new` when both are stable. Referenced by AC-US9-04, FR-001.

### AD-007: Flat directory + unprefixed name
**Decision**: `plugins/skills/skills/skill-builder/SKILL.md` (flat dir, not nested under a namespace subdir). Frontmatter `name: skill-builder` without `sw/` or other prefix.
**Rationale**: Honors `feedback_skill_naming_flat_dirs.md` — the namespace belongs in the frontmatter, not the directory tree. No `sw:` prefix because this is not a SpecWeave command. Referenced by FR-006.

## ADR References

No new ADRs created in `.specweave/docs/internal/architecture/adr/` for this increment — the architectural decisions above are documented inline in this plan and traceable back to completed increments 0665, 0465, 0331, 0250, 0586 where the broader "universal skills" architecture was established.

## Implementation Sequence

### Day 1 — Generator Extraction
1. Create `src/core/skill-generator.ts` with the extracted generator body from `src/eval-server/skill-create-routes.ts:919-1100`.
2. Rewire the HTTP handler to a thin wrapper that calls `generateSkill()`.
3. Unit tests: snapshot behavior on 3 target combinations (Claude only, 3 universal, all 7 universal).
4. Regression check: all existing eval-ui tests stay green.

### Day 2 — vskill skill CLI
5. Create `src/commands/skill.ts` with `registerSkillCommand(program)` wiring `new|import|list|info|publish`.
6. Register in `src/cli/index.ts`.
7. Implement `new` (shells to generator), `import` (reads existing SKILL.md → generator with re-emit flag), `list` (alias), `info` (frontmatter reader), `publish` (alias to `submit`).
8. Unit tests following `src/commands/add.test.ts` patterns.

### Day 3 — SKILL.md Package + Divergence Report + Schema Versioning
9. Write `plugins/skills/skills/skill-builder/SKILL.md` (~200 lines) with trigger phrases, fallback chain A/B/C, "What this is NOT" section.
10. Write 3 reference files (`target-agents.md`, `divergence-report-schema.md`, `fallback-modes.md`).
11. Add divergence-report generator (~50 LOC side-effect) to `src/core/skill-generator.ts`.
12. Add `x-sw-schema-version: 1` to every emitted frontmatter.
13. Update `plugins/skills/` manifest to register `skill-builder` alongside `scout`.
14. Cross-link `skill-builder` from `plugins/skills/skills/scout/SKILL.md` (~10 lines).
15. Bump README badge `skills: 7 → 8`.

### Day 4 — E2E Tests + Fallback Verification
16. Write `tests/e2e/skill-builder.spec.ts` (Playwright): install in sandbox, invoke from Claude Code, assert multi-target emission + divergence report + schema-version.
17. Second test case: `--engine=anthropic-skill-creator` asserts Claude-only emission + fallback-mode warning in stderr.
18. Verify test runs cleanly on both Claude Code and Codex sandboxes.

### Day 5 — Release and Verification
19. `cd repositories/anton-abyzov/vskill && sw:release-npm` (patch release).
20. `vskill submit plugins/skills/skills/skill-builder` (registry publish).
21. Smoke test from a clean sandbox: `vskill install skill-builder` → "create a skill" trigger → assert multi-target output.
22. Umbrella sync commit.
23. Create follow-up SpecWeave increment stub (separate ID) to track the `sw:skill-gen → vskill skill new` integration.

## Testing Strategy

### Unit tests (Vitest)
- `src/commands/__tests__/skill.test.ts` — CLI subcommand routing, flag parsing, target resolution.
- `src/core/__tests__/skill-generator.test.ts` — generator behavior snapshots; divergence-report content assertions; schema-version tag presence.
- Pattern: `vi.hoisted()` + `vi.mock()` for ESM mocking, `mkdtemp` + cleanup in `afterEach` — matches `src/commands/add.test.ts` and `tests/unit/skill-gen/signal-collector.test.ts:10-29`.
- Coverage target: ≥90% on `src/core/skill-generator.ts` and `src/commands/skill.ts`.

### E2E tests (Playwright)
- `tests/e2e/skill-builder.spec.ts` — install in sandbox, generate across targets, assert divergence report, assert fallback warning.
- Run: `npx playwright test tests/e2e/skill-builder.spec.ts`.

### Regression gates
- All existing eval-ui unit tests green (`npx vitest run src/eval-ui/`).
- All existing `skill-create-routes.ts` tests green.
- All existing installer tests green (`src/installer/` tests verify canonical.ts target-agents routing — must not regress).

## Risks and Mitigations

| Risk | Likelihood | Mitigation |
|---|---|---|
| Generator extraction introduces subtle behavior change | Low | Snapshot test on 3 target combinations pre + post extraction. |
| Divergence report format drift from `references/divergence-report-schema.md` | Medium | Unit test that asserts report parses back into the schema's shape. |
| Fallback chain mis-sequencing in SKILL.md body | Medium | `references/fallback-modes.md` has exact detection commands; SKILL.md body is validated by a lint test that checks the ordering. |
| Registry submission fails | Low | Manual smoke test on staging; rollback is `vskill unsubmit` (existing). |
| Umbrella sync cascade fails | Low | Existing pattern — recent vskill v0.5.x releases all succeed. Monitor post-release. |

## Definition of Done

- All 42 AC items across US-001..US-009 are `[x]` in spec.md.
- Vitest + Playwright tests green.
- Coverage ≥90% on new modules.
- Divergence report and schema-version tag verified in E2E.
- vskill patch released, skill submitted to registry.
- Umbrella sync commit on main.
- Follow-up SpecWeave increment stub created (for the sw:skill-gen rewire).
- `sw:done` closure gates pass (code-review, simplify, grill, judge-llm, PM gates).
