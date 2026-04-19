# Tasks — skill-builder: Distributable Universal Skill Authoring Package

## Task Overview

13 tasks across 5 implementation days. All tasks live in `repositories/anton-abyzov/vskill/`. Zero tasks touch SpecWeave (per AD-006).

---

## Day 1 — Generator Extraction

### T-001: Extract generator into src/core/skill-generator.ts
**User Story**: US-004 | **Satisfies ACs**: AC-US4-01, AC-US4-04 | **Status**: [ ] pending

**Test Plan**:
- **Given** `src/eval-server/skill-create-routes.ts:919-1100` contains the in-line generator body
- **When** I create `src/core/skill-generator.ts` exporting `generateSkill(request): Promise<GenerateSkillResult>` with no `req`/`res`/SSE references
- **Then** the extracted module imports only from `src/core/`, `src/utils/`, or third-party packages — not from `src/eval-server/`

**Files**: `src/core/skill-generator.ts` (new).

---

### T-002: Rewire HTTP handler as thin wrapper
**User Story**: US-004 | **Satisfies ACs**: AC-US4-03, AC-US4-05 | **Status**: [ ] pending

**Test Plan**:
- **Given** `src/core/skill-generator.ts` exists (T-001)
- **When** I refactor `src/eval-server/skill-create-routes.ts` at the `POST /api/skills/generate` handler to call `generateSkill()` and stream results
- **Then** the handler body is ≤40 lines AND all existing eval-ui unit tests stay green (`npx vitest run src/eval-ui/`)

**Files**: `src/eval-server/skill-create-routes.ts` (edit — reduce `router.post("/api/skills/generate", …)` body).

---

### T-003: Snapshot tests for extracted generator
**User Story**: US-004 | **Satisfies ACs**: AC-US4-02 | **Status**: [ ] pending

**Test Plan**:
- **Given** `generateSkill()` is extracted (T-001, T-002)
- **When** I run `npx vitest run src/core/__tests__/skill-generator.test.ts` with 3 target combinations (`[claude-code]`, `[claude-code, codex, cursor]`, all 7 universal)
- **Then** the output SKILL.md files match the pre-extraction snapshot byte-for-byte for each combination

**Files**: `src/core/__tests__/skill-generator.test.ts` (new). Pattern: `vi.hoisted()` + `mkdtemp` from `tests/unit/skill-gen/signal-collector.test.ts`.

---

## Day 2 — vskill skill CLI

### T-004: Implement src/commands/skill.ts subcommand router
**User Story**: US-003 | **Satisfies ACs**: AC-US3-01, AC-US3-02, AC-US3-03, AC-US3-04, AC-US3-09, AC-US3-10 | **Status**: [ ] pending

**Test Plan**:
- **Given** `generateSkill()` is extracted and stable (T-001..T-003)
- **When** I create `src/commands/skill.ts` exporting `registerSkillCommand(program)` and wire it into `src/cli/index.ts`
- **Then** `vskill skill --help` lists all subcommands (new, import, list, info, publish) AND `vskill skill new --prompt "X"` emits to 7 universal-agent directories by default AND `--targets=claude-code,codex` emits to only those two AND `--targets=all` emits to all 49

**Files**: `src/commands/skill.ts` (new, ~200 LOC), `src/cli/index.ts` (edit — add `registerSkillCommand(program)`).

---

### T-005: Implement vskill skill import
**User Story**: US-003 | **Satisfies ACs**: AC-US3-06 | **Status**: [ ] pending

**Test Plan**:
- **Given** an existing SKILL.md at `fixtures/existing-skill/SKILL.md`
- **When** I run `vskill skill import fixtures/existing-skill/SKILL.md --targets=claude-code,codex`
- **Then** the skill is re-emitted under `.claude/skills/<name>/SKILL.md` and `.agents/skills/<name>/SKILL.md`, frontmatter fields are preserved or translated per target, AND a `<name>-divergence.md` is written

**Files**: `src/commands/skill.ts` (edit — add `import` handler).

---

### T-006: Implement vskill skill list/info/publish
**User Story**: US-003 | **Satisfies ACs**: AC-US3-07, AC-US3-08 | **Status**: [ ] pending

**Test Plan**:
- **Given** `skill-builder` is installed in a sandbox
- **When** I run `vskill skill list` and `vskill skill info skill-builder`
- **Then** `list` returns the same output as `vskill list` (thin alias) AND `info skill-builder` prints the skill's frontmatter + divergence-report if present
- **And when** I run `vskill skill publish skill-builder`, it invokes `vskill submit skill-builder` under the hood (alias)

**Files**: `src/commands/skill.ts` (edit — add `list`, `info`, `publish` handlers).

---

### T-007: Unit tests for vskill skill commands
**User Story**: US-003 | **Satisfies ACs**: AC-US3-01..10 | **Status**: [ ] pending

**Test Plan**:
- **Given** all subcommand handlers are implemented (T-004..T-006)
- **When** I run `npx vitest run src/commands/__tests__/skill.test.ts`
- **Then** coverage on `src/commands/skill.ts` is ≥90% AND tests cover: default target set, `--targets=all`, `--targets=<list>`, `--engine=anthropic-skill-creator`, unknown target ID error, missing `--prompt` error

**Files**: `src/commands/__tests__/skill.test.ts` (new). Pattern mirrors `src/commands/__tests__/add.test.ts`.

---

## Day 3 — SKILL.md Package + Divergence Report + Schema Versioning

### T-008: Write skill-builder SKILL.md + 3 references
**User Story**: US-001, US-002 | **Satisfies ACs**: AC-US1-01, AC-US1-02, AC-US1-03, AC-US1-04, AC-US2-01..05 | **Status**: [ ] pending

**Test Plan**:
- **Given** the plan's fallback chain A/B/C is approved
- **When** I write `plugins/skills/skills/skill-builder/SKILL.md` (<500 lines) + 3 reference files (`target-agents.md`, `divergence-report-schema.md`, `fallback-modes.md`, each <100 lines)
- **Then** SKILL.md frontmatter contains `name`, `description` (with all 7 trigger phrases), `tags: [skill-authoring, meta, universal]`, `metadata.version: 0.1.0` AND body includes "What this is NOT" section cross-linking `scout` and `sw:skill-gen`

**Files**: `plugins/skills/skills/skill-builder/SKILL.md` (new), `plugins/skills/skills/skill-builder/references/target-agents.md` (new), `plugins/skills/skills/skill-builder/references/divergence-report-schema.md` (new), `plugins/skills/skills/skill-builder/references/fallback-modes.md` (new).

---

### T-009: Add divergence-report generator to skill-generator.ts
**User Story**: US-005 | **Satisfies ACs**: AC-US5-01..05 | **Status**: [ ] pending

**Test Plan**:
- **Given** `generateSkill()` emits to N targets (T-001)
- **When** I extend `src/core/skill-generator.ts` to write `<name>-divergence.md` as a side-effect after emission
- **Then** the report lists each dropped field with original name, target, and translation (e.g., `allowed-tools: [Bash] → OpenCode permission: { bash: ask }`) AND security-critical fields (`allowed-tools`, `context: fork`, `model`) always appear if dropped AND schema matches `references/divergence-report-schema.md` AND a unit test parses the report back into that schema

**Files**: `src/core/skill-generator.ts` (edit — ~50 LOC addition), `src/core/__tests__/skill-generator.test.ts` (edit — add divergence assertions).

---

### T-010: Add x-sw-schema-version frontmatter tag
**User Story**: US-006 | **Satisfies ACs**: AC-US6-01..04 | **Status**: [ ] pending

**Test Plan**:
- **Given** `generateSkill()` emits SKILL.md (T-001, T-009)
- **When** I add `x-sw-schema-version: 1` to the emitted frontmatter
- **Then** every emitted SKILL.md contains that tag AND tag is preserved on `vskill skill import` re-emission AND tag is NOT added to Anthropic-fallback emissions AND unit test asserts presence across all 7 universal targets

**Files**: `src/core/skill-generator.ts` (edit — add tag to emit step).

---

### T-011: Register skill-builder in skills plugin manifest + cross-link scout + bump README badge
**User Story**: US-008 | **Satisfies ACs**: AC-US8-03, AC-US8-04 | **Status**: [ ] pending

**Test Plan**:
- **Given** `skill-builder/SKILL.md` exists (T-008)
- **When** I edit `plugins/skills/` manifest (`plugin.json` or equivalent) to register `skill-builder` alongside `scout`, edit `plugins/skills/skills/scout/SKILL.md` to add a "Related skills" cross-link, AND bump README badge `skills: 7 → 8`
- **Then** `vskill list` shows both `scout` and `skill-builder` AND `scout` SKILL.md mentions `skill-builder` AND README renders the badge as `skills: 8`

**Files**: `plugins/skills/plugin.json` (edit — or equivalent manifest), `plugins/skills/skills/scout/SKILL.md` (edit — add ~10 lines cross-link), `README.md` (edit — badge count).

---

## Day 4 — E2E Tests + Fallback Verification

### T-012: Playwright E2E test skill-builder.spec.ts
**User Story**: US-007, US-001 | **Satisfies ACs**: AC-US7-01..06, AC-US1-05, AC-US1-06, AC-US1-07 | **Status**: [ ] pending

**Test Plan**:
- **Given** all implementation tasks (T-001..T-011) complete
- **When** I run `npx playwright test tests/e2e/skill-builder.spec.ts`
- **Then** the test: (a) creates a sandbox, (b) runs `vskill install anton-abyzov/vskill/plugins/skills/skills/skill-builder`, (c) asserts skill lands in `.claude/skills/skill-builder/` and `.agents/skills/skill-builder/`, (d) runs `vskill skill new --prompt "lint markdown files" --targets=claude-code,codex,cursor,opencode`, (e) asserts files exist at each target's path, (f) asserts `x-sw-schema-version: 1` in each emitted SKILL.md, (g) asserts `lint-markdown-files-divergence.md` exists and lists translations, (h) runs a second case with `--engine=anthropic-skill-creator` and asserts Claude-only emission + fallback warning in stderr

**Files**: `tests/e2e/skill-builder.spec.ts` (new).

---

## Day 5 — Release and Verification

### T-013: Release vskill + submit skill-builder + verify + umbrella sync + follow-up increment stub
**User Story**: US-008, US-009 | **Satisfies ACs**: AC-US8-01, AC-US8-02, AC-US9-01..04 | **Status**: [ ] pending

**Test Plan**:
- **Given** all tests pass (T-001..T-012)
- **When** I run `sw:release-npm` from `repositories/anton-abyzov/vskill/`, then `vskill submit anton-abyzov/vskill/plugins/skills/skills/skill-builder`, then verify in a clean sandbox with a pinned older vskill (e.g., 0.5.80), then check umbrella sync commit lands on main
- **Then** npm package published successfully AND registry URL returned from submit AND sandbox install succeeds with pinned version AND umbrella sync commit matches pattern `sync umbrella after vskill v0.5.X release`
- **And** I create a follow-up SpecWeave increment stub (separate ID) titled "Rewire sw:skill-gen to prefer vskill skill new when available" to track the integration work (not part of this increment)

**Files**: Release artifacts (no repo edits in this task — it's the release operation). Follow-up increment created at `.specweave/increments/<next-id>-skill-gen-vskill-integration/` with stub spec.md + metadata.json status `planned`.

---

## Completion Checklist

- [ ] T-001 through T-013 all marked `[x]`
- [ ] All ACs in spec.md marked `[x]`
- [ ] `npx vitest run` passes with ≥90% coverage on new modules
- [ ] `npx playwright test tests/e2e/skill-builder.spec.ts` passes
- [ ] vskill patch released, npm published, GitHub Release created
- [ ] `skill-builder` submitted to verified-skill.com registry
- [ ] Umbrella sync commit on main
- [ ] Follow-up increment stub created
- [ ] `sw:done` closure gates pass (code-review, simplify, grill, judge-llm, PM gates)
