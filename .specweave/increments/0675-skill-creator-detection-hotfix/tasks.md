# Tasks — 0675 Skill-Creator Detection Hotfix

## Task Overview

5 tasks, strict TDD order. All files under `repositories/anton-abyzov/vskill/`.

---

### T-001: RED — Write failing tests for all six detection branches
**User Story**: US-004 | **Satisfies ACs**: AC-US4-01, AC-US4-02, AC-US4-03, AC-US4-04, AC-US4-05 | **Status**: [x] completed

**Test Plan**:
- **Given** the current `isSkillCreatorInstalled()` misses project-local agent-native installs and marketplace-synced plugins
- **When** I create `src/utils/__tests__/skill-creator-detection.test.ts` with 13 test cases (one per AC: AC-US1-01..04, 06; AC-US2-03..04; AC-US3-01..05) plus schema assertions for AC-US1-05, AC-US2-01, AC-US2-02, AC-US2-05 — using `mkdtempSync` sandboxes with `beforeEach/afterEach` cleanup and `vi.hoisted` + `vi.mock("node:os", ...)` for `homedir()` mocking (patterns from `src/lockfile/project-root.test.ts:1-61` and `src/core/__tests__/baseline.test.ts:33-88`)
- **Then** running `npx vitest run src/utils/__tests__/skill-creator-detection.test.ts` reports AT LEAST AC-US1-01, AC-US1-02, AC-US1-03, AC-US2-03 FAILING (RED gate satisfied) AND all existing vitest suites stay green when run via `npx vitest run` (no accidental import of unmocked modules bleeds into neighbor tests)

**Files**: `src/utils/__tests__/skill-creator-detection.test.ts` (new, ~250 LOC).

---

### T-002: GREEN — Add `pluginMarketplaceDir` field to AgentDefinition + populate claude-code entry
**User Story**: US-002 | **Satisfies ACs**: AC-US2-01, AC-US2-02, AC-US2-05 | **Status**: [x] completed

**Test Plan**:
- **Given** T-001's schema tests fail because `AgentDefinition` has no `pluginMarketplaceDir` and `claude-code` has no value set
- **When** I add `pluginMarketplaceDir?: string` with JSDoc to the `AgentDefinition` interface in `src/agents/agents-registry.ts` and populate `pluginMarketplaceDir: '~/.claude/plugins/marketplaces'` on the `claude-code` entry at line 164 (leave all other agent entries untouched — the field is undefined for them by virtue of being optional)
- **Then** the schema-shape test cases in T-001 pass AND `npx tsc --noEmit` is clean AND no other agent entry has `pluginMarketplaceDir` set (grep-asserted by test)

**Files**: `src/agents/agents-registry.ts` (edit — interface + claude-code entry).

---

### T-003: GREEN — Extend `isSkillCreatorInstalled()` with branches 2b (localSkillsDir) and 4b (pluginMarketplaceDir)
**User Story**: US-001, US-002, US-003 | **Satisfies ACs**: AC-US1-01, AC-US1-02, AC-US1-03, AC-US1-04, AC-US1-05, AC-US2-03, AC-US2-04, AC-US3-01, AC-US3-02, AC-US3-03, AC-US3-04, AC-US3-05 | **Status**: [x] completed

**Test Plan**:
- **Given** T-001 tests are RED for the project-local and marketplace branches, and T-002 has added the `pluginMarketplaceDir` field
- **When** I extend `src/utils/skill-creator-detection.ts::isSkillCreatorInstalled()` with (2b) a `if (projectRoot)` guarded loop over `AGENTS_REGISTRY` checking `join(projectRoot, agent.localSkillsDir, 'skill-creator')` and (4b) inside the existing agent loop, for agents with `pluginMarketplaceDir`, a walker that scans `{dir}/{marketplace}/plugins/*skill-creator*/` using the same try/catch + substring-match pattern as the existing cache walker. Both branches short-circuit on first match
- **Then** all 13 runtime test cases in T-001 pass (ACs US1-01..04, US2-03..04, US3-01..05) AND the regression cases (US3-01..04) still return true AND empty-sandbox case (US3-05) returns false AND null-projectRoot case (US1-04) returns false

**Files**: `src/utils/skill-creator-detection.ts` (edit — add two branches, preserve existing four branches).

---

### T-004: GREEN — Fix `checkSkillCreator()` caller in serve.ts to pass projectRoot
**User Story**: US-001 | **Satisfies ACs**: AC-US1-06 | **Status**: [x] completed

**Test Plan**:
- **Given** `src/commands/eval/serve.ts:28` currently calls `isSkillCreatorInstalled()` with no arguments, defeating the new branch 2b when the CLI boots inside a project with a project-local install
- **When** I change line 28 from `if (!isSkillCreatorInstalled()) {` to `if (!isSkillCreatorInstalled(root)) {` — `root` is already resolved earlier in the same function via `resolve(opts.root || process.cwd())` and in lexical scope
- **Then** booting `node dist/index.js eval serve --root /path/to/specweave-umb` no longer prints the "Skill-Creator not detected" warning when the project has `.claude/skills/skill-creator/` installed AND `npx vitest run` full suite stays green (no test depends on the pre-fix behavior)

**Files**: `src/commands/eval/serve.ts` (edit — one-line arg pass).

---

### T-005: REFACTOR + Verify — Run full regression suite + tsc + manual smoke on Studio
**User Story**: US-001, US-002, US-003, US-004 | **Satisfies ACs**: AC-US4-05, AC-US4-06 | **Status**: [x] completed

**Test Plan**:
- **Given** T-001..T-004 complete
- **When** I run `npx vitest run` (full suite), `npx tsc --noEmit`, and a manual smoke test (boot Studio from `/Users/antonabyzov/Projects/github/specweave-umb/`, hit `http://localhost:{PORT}/api/skill-creator-status`, observe response)
- **Then** full vitest suite reports green (no regressions), tsc reports 0 errors, API returns `{"installed": true}`, Studio left panel shows the green "Skill Creator installed" banner. If any gate fails, drop into REFACTOR cycle and address root cause rather than patching symptoms

**Files**: none (verification only).

---

## Execution Order

Strict sequence: T-001 (RED) → T-002 (GREEN: schema) → T-003 (GREEN: detection) → T-004 (GREEN: caller) → T-005 (verify). No parallelism — each step gates the next.
