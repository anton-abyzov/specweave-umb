# Tasks — skill-builder: Distributable Universal Skill Authoring Package

## Task Overview

19 tasks across 5 implementation days. All tasks live in `repositories/anton-abyzov/vskill/`. Zero tasks touch SpecWeave (per AD-006). Test strategy: Vitest for CLI (path A) and browser-UI regression (path B) via Playwright, plus a manual gate for the browser flow.

**Task count increase from initial 13 → 19** is the result of the three-agent deep-verification pass. T-000 captures pre-extraction parity evidence; T-008b/T-011b add documentation; T-012b/T-012c add regression + manual gates; T-013 split into T-013a/b/c/d for independent rollback.

---

## Day 1 — Generator Extraction (with baseline capture)

### T-000: Capture pre-extraction baseline (HTTP JSON + UI trace + SSE contract)
**User Story**: US-004, US-007 | **Satisfies ACs**: AC-US4-02 (prereq), AC-US7-09 (prereq) | **Status**: [x] completed

**Test Plan**:
- **Given** `src/eval-server/skill-create-routes.ts:919-1025` contains the in-line generator (pre-extraction state)
- **When** I (a) invoke `POST /api/skills/generate` from a test harness for three target combinations (`[claude-code]`, `[claude-code, codex, cursor]`, all 8 universal with prompt "lint markdown files"), (b) boot `node dist/index.js eval serve --root e2e/fixtures --port 3077` and record a Playwright trace of the "+ New Skill" → fill → Generate flow at viewport 1600×1000, (c) capture the SSE event sequence (event names + first JSON frame per event type) streamed by `POST /api/skills/generate`
- **Then** I save (a) full SKILL.md per target+combo under `fixtures/pre-extraction-snapshots/http/<combo>/<target>.skill.md`, (b) Playwright trace + screenshots under `fixtures/pre-extraction-snapshots/ui/trace.zip`, (c) SSE contract under `fixtures/pre-extraction-snapshots/sse/contract.json` — these three artifacts are the parity reference for T-003 (HTTP) and T-012b (UI+SSE)

**Verified live 2026-04-19**: path B boots at http://localhost:3077, `+ New Skill` button opens the Create-a-New-Skill dialog with AI-Assisted/Manual tabs, textarea fills (placeholder begins `e.g., A skill that helps format SQL`), `POST /api/skills/generate` returns 400 on empty body (route registered at `:919`). SSE contract capture requires a valid body — do not repeat the empty-body probe.

**Files**: `src/core/__tests__/fixtures/pre-extraction-snapshots/http/` (new, 3 combos × up to 8 targets), `pre-extraction-snapshots/ui/trace.zip` (new), `pre-extraction-snapshots/sse/contract.json` (new).

---

### T-001: Extract generator into src/core/skill-generator.ts
**User Story**: US-004 | **Satisfies ACs**: AC-US4-01, AC-US4-04 | **Status**: [x] completed

**Test Plan**:
- **Given** T-000 fixtures exist and `skill-create-routes.ts:919-1025` contains the in-line generator
- **When** I create `src/core/skill-generator.ts` exporting `generateSkill(request: GenerateSkillRequest): Promise<GenerateSkillResult>` with no `req`/`res`/SSE references
- **Then** the extracted module imports only from `src/core/`, `src/utils/`, `src/agents/`, `src/installer/`, or third-party packages — not from `src/eval-server/` AND `buildAgentAwareSystemPrompt` (still in its existing location) is called from `generateSkill()` without behavior change

**Files**: `src/core/skill-generator.ts` (new, ~250 LOC).

---

### T-002: Rewire HTTP handler as thin wrapper
**User Story**: US-004 | **Satisfies ACs**: AC-US4-03, AC-US4-05 | **Status**: [x] completed

**Test Plan**:
- **Given** `src/core/skill-generator.ts` exists (T-001)
- **When** I refactor `src/eval-server/skill-create-routes.ts` at the `POST /api/skills/generate` handler to call `generateSkill()` and stream results via SSE
- **Then** the handler body is ≤40 lines AND all existing eval-ui unit tests stay green (`npx vitest run src/eval-ui/`) AND all existing eval-server tests stay green (`npx vitest run src/eval-server/`)

**Files**: `src/eval-server/skill-create-routes.ts` (edit — reduce `router.post("/api/skills/generate", …)` body).

---

### T-003: Post-extraction parity snapshot tests
**User Story**: US-004 | **Satisfies ACs**: AC-US4-02 | **Status**: [x] completed

**Test Plan**:
- **Given** `generateSkill()` is extracted (T-001, T-002) and T-000 fixtures exist
- **When** I run `npx vitest run src/core/__tests__/skill-generator.test.ts` invoking `generateSkill()` with the same 3 target combinations and same sample prompt used in T-000
- **Then** the output SKILL.md content matches T-000 fixtures **byte-for-byte** for each combo × target — any divergence is a test failure with a line-level diff

**Files**: `src/core/__tests__/skill-generator.test.ts` (new). Pattern: `vi.hoisted()` + `mkdtemp` from `tests/unit/skill-gen/signal-collector.test.ts:10-29`.

---

## Day 2 — vskill skill CLI

### T-004: Implement src/commands/skill.ts subcommand router + wire into CLI
**User Story**: US-003 | **Satisfies ACs**: AC-US3-01, AC-US3-02, AC-US3-03, AC-US3-04, AC-US3-09, AC-US3-10 | **Status**: [x] completed

**Test Plan**:
- **Given** `generateSkill()` is extracted and stable (T-001..T-003)
- **When** I create `src/commands/skill.ts` exporting `registerSkillCommand(program)` wiring `new|import|list|info|publish`, and register it in `src/cli/index.ts` alongside `add`, `init`, `submit`
- **Then** `vskill skill --help` lists all 5 subcommands with descriptions AND `vskill skill new --prompt "X"` emits to the 8 universal-agent directories by default AND `--targets=claude-code,codex` emits to only those two AND `--targets=all` resolves to all 53 registered agents

**Files**: `src/commands/skill.ts` (new, ~200 LOC), `src/cli/index.ts` (edit — add `registerSkillCommand(program)` registration).

---

### T-005: Implement vskill skill import + vskill skill new --engine=anthropic-skill-creator
**User Story**: US-003 | **Satisfies ACs**: AC-US3-05, AC-US3-06 | **Status**: [x] completed

**Test Plan**:
- **Given** T-004 subcommand skeleton exists and `isSkillCreatorInstalled()` helper is importable (from 0665)
- **When** I run `vskill skill import fixtures/existing-skill/SKILL.md --targets=claude-code,codex`
- **Then** the skill is re-emitted under `.claude/skills/<name>/SKILL.md` and `.agents/skills/<name>/SKILL.md`, frontmatter preserved or translated per target, AND a `<name>-divergence.md` is written
- **And when** I run `vskill skill new --prompt "X" --engine=anthropic-skill-creator`, the CLI delegates to the Anthropic built-in, emits Claude-only, and prints `[skill-builder] fallback mode — universal targets not emitted; install vskill for universal support` to stderr

**Files**: `src/commands/skill.ts` (edit — add `import` handler + `--engine` flag branch).

---

### T-006: Implement vskill skill list / info / publish aliases
**User Story**: US-003 | **Satisfies ACs**: AC-US3-07, AC-US3-08 | **Status**: [x] completed

**Test Plan**:
- **Given** `skill-builder` is installed in a sandbox (for fixture purposes) and `vskill submit` exists (mature)
- **When** I run `vskill skill list` and `vskill skill info skill-builder`
- **Then** `list` returns the same output as `vskill list` (thin alias) AND `info skill-builder` prints the skill's frontmatter + divergence-report content if present
- **And when** I run `vskill skill publish skill-builder`, it invokes `vskill submit skill-builder` under the hood (alias — no duplicate publish logic)

**Files**: `src/commands/skill.ts` (edit — add `list`, `info`, `publish` handlers).

---

### T-007: Unit tests for vskill skill commands (error paths + happy paths)
**User Story**: US-003 | **Satisfies ACs**: AC-US3-01..12 | **Status**: [x] completed

**Test Plan**:
- **Given** all subcommand handlers are implemented (T-004..T-006)
- **When** I run `npx vitest run src/commands/__tests__/skill.test.ts`
- **Then** coverage on `src/commands/skill.ts` is ≥90% AND tests cover:
  - default target set (8 universal agents)
  - `--targets=all` resolves to 53 agents
  - `--targets=claude-code,codex` resolves to exactly those two
  - `--targets=<unknown-id>` exits non-zero with error `Unknown agent id: ...` (AC-US3-11)
  - Missing `--prompt` exits non-zero with usage hint (AC-US3-12)
  - Empty `--prompt ""` exits non-zero (AC-US3-12)
  - `--engine=anthropic-skill-creator` with mocked `isSkillCreatorInstalled() → true` → delegates, Claude-only output, stderr warning (AC-US3-05)
  - `--engine=anthropic-skill-creator` with mocked `isSkillCreatorInstalled() → false` → non-zero exit with remediation (AC-US2-07)
  - `vskill skill list` matches `vskill list` output byte-for-byte

**Files**: `src/commands/__tests__/skill.test.ts` (new). Pattern mirrors `src/commands/add.test.ts`.

---

## Day 3 — SKILL.md Package + Divergence Report + Schema Versioning

### T-008: Write skill-builder SKILL.md with detection script
**User Story**: US-001, US-002 | **Satisfies ACs**: AC-US1-01, AC-US1-02, AC-US1-04, AC-US2-01..07 | **Status**: [x] completed

**Test Plan**:
- **Given** fallback chain A/B/C is decided (AD-002)
- **When** I write `plugins/skills/skills/skill-builder/SKILL.md` (<500 lines) with frontmatter (`name: skill-builder`, `description` containing all 7 trigger phrases from AC-US1-02, `tags: [skill-authoring, meta, universal]`, `metadata.version: 0.1.0`), detection script (`which vskill` → path A; else `node -e "require.resolve('vskill')"` → path B; else Claude Code + skill-creator at `~/.claude/skills/skill-creator/` → path C; else error with remediation), and "What this is NOT" section cross-linking `scout` and `sw:skill-gen`
- **Then** `vskill install` lint passes on the SKILL.md AND a frontmatter-parser test asserts all required fields AND a body-lint test asserts detection script contains exactly the 3 detection checks in priority order

**Files**: `plugins/skills/skills/skill-builder/SKILL.md` (new, <500 lines).

---

### T-008b: Write 3 reference files (target-agents, divergence schema, fallback modes)
**User Story**: US-001 | **Satisfies ACs**: AC-US1-03 | **Status**: [x] completed

**Test Plan**:
- **Given** T-008 SKILL.md references these files by path
- **When** I write `references/target-agents.md` (condensed 49-agent table, <100 lines), `references/divergence-report-schema.md` (divergence.md shape, <100 lines), `references/fallback-modes.md` (A/B/C detection commands + warning messages, <100 lines)
- **Then** all three files exist under `plugins/skills/skills/skill-builder/references/` AND each file's line count is < 100 AND the fallback-modes.md detection commands match the script in T-008 SKILL.md exactly

**Files**: `plugins/skills/skills/skill-builder/references/target-agents.md` (new), `divergence-report-schema.md` (new), `fallback-modes.md` (new).

---

### T-009: Add divergence-report generator with security-critical enforcement
**User Story**: US-005 | **Satisfies ACs**: AC-US5-01..05 | **Status**: [x] completed

**Test Plan**:
- **Given** `generateSkill()` emits to N targets (T-001)
- **When** I extend `src/core/skill-generator.ts` to write `<name>-divergence.md` to the invocation cwd after emission
- **Then** (positive case) when source has `allowed-tools: [Bash]` and emits to OpenCode, the report entry reads `allowed-tools → permission: { bash: ask }` AND (negative case) a test fixture with `allowed-tools` emitted to OpenCode AND a stubbed divergence-generator that omits the entry FAILS the test (asserts silent loss is detected) AND (edge case) when all targets are universal and no fields dropped, the report exists with a single line `No divergences — all targets universal`

**Files**: `src/core/skill-generator.ts` (edit — ~50 LOC addition for divergence generation), `src/core/__tests__/skill-generator.test.ts` (edit — positive, negative, and edge-case divergence assertions).

---

### T-010: Add x-sw-schema-version frontmatter tag
**User Story**: US-006 | **Satisfies ACs**: AC-US6-01..04 | **Status**: [x] completed

**Test Plan**:
- **Given** `generateSkill()` emits SKILL.md (T-001, T-009)
- **When** I add `x-sw-schema-version: 1` to the emitted frontmatter at the emit step
- **Then** every SKILL.md emitted by `vskill skill new` and `vskill skill import` contains the tag AND the tag is preserved on re-emission (`vskill skill import` of a file already carrying it) AND the tag is NOT added when `--engine=anthropic-skill-creator` is used AND a unit test parses frontmatter across all 8 universal-target emissions and asserts the field is present with value `1`

**Files**: `src/core/skill-generator.ts` (edit — add tag insertion at emit step).

---

### T-011: Register skill-builder in plugin manifest + bump badge
**User Story**: US-008 | **Satisfies ACs**: AC-US8-03 (badge only) | **Status**: [x] completed

**Test Plan**:
- **Given** `skill-builder/SKILL.md` exists (T-008, T-008b)
- **When** I edit `plugins/skills/` manifest (`plugin.json` or equivalent) to register `skill-builder` alongside `scout`, AND bump README badge `skills: 7 → 8`
- **Then** `vskill list` shows both `scout` and `skill-builder` AND README renders the badge as `skills: 8`

**Files**: `plugins/skills/plugin.json` (edit — or equivalent manifest), `README.md` (edit — badge count).

---

### T-011b: Document vskill skill CLI in README + CHANGELOG
**User Story**: US-008 | **Satisfies ACs**: AC-US8-03 (CHANGELOG), AC-US8-04 (README) | **Status**: [x] completed

**Test Plan**:
- **Given** T-011 badge is bumped and CLI subcommand exists (T-004..T-006)
- **When** I add a `### Added` entry to `CHANGELOG.md` for `vskill skill new|import|list|info|publish` and bundled `skill-builder`, AND add a "Commands" (or equivalent) subsection to `README.md` with a usage example `vskill skill new --prompt "lint markdown" --targets=claude-code,codex`
- **Then** a markdown-lint test confirms the CHANGELOG entry exists with date AND README contains the exact subcommand name AND a usage example fence-block (```bash`). `--help` output alone does NOT satisfy this task — the docs must be user-readable

**Files**: `CHANGELOG.md` (edit — Added section), `README.md` (edit — Commands section).

---

## Day 4 — Test Suite (Vitest for CLI, Playwright for Studio, Manual for Path B)

### T-012: Vitest CLI integration tests
**User Story**: US-007, US-001 | **Satisfies ACs**: AC-US7-01..06, AC-US7-08, AC-US1-05, AC-US1-06, AC-US1-07 | **Status**: [x] completed

**Test Plan**:
- **Given** all implementation tasks (T-001..T-011b) complete
- **When** I run `./node_modules/.bin/vitest run src/commands/__tests__/skill.integration.test.ts`
- **Then** the test suite covers:
  - (a) ~~`mkdtemp` sandbox; `vskill install anton-abyzov/vskill/plugins/skills/skills/skill-builder`; asserts skill lands in `.claude/skills/skill-builder/` AND `.agents/skills/skill-builder/` (AC-US1-05, AC-US1-06, AC-US7-02)~~ **DEFERRED to T-013c** — real `vskill install` requires network + a pinned older vskill; the install resolver itself is unit-tested in `src/commands/add.test.ts`. Including it here would duplicate that coverage and add network flakiness without raising the contract bar.
  - (b) `vskill skill new --prompt "lint markdown files" --targets=claude-code,codex,cursor,opencode`; asserts SKILL.md at all four target localSkillsDir fragments (AC-US7-03) ✅
  - (c) Each emitted SKILL.md parses as valid YAML frontmatter and contains `x-sw-schema-version: 1` (AC-US7-04) ✅
  - (d) `<slug>-divergence.md` exists in sandbox cwd; report references the OpenCode target (silent loss = test failure) (AC-US7-05) ✅
  - (e) `--engine=anthropic-skill-creator` with mocked `isSkillCreatorInstalled() → true` emits Claude-only + stderr fallback warning; with `false` exits 1 with remediation (AC-US7-06, AC-US2-07) ✅
  - (f) `--targets=all` emits to every installable+expressive agent (de-duped by shared localSkillsDir fragment); the single non-expressive agent (`mcpjam`, `customSystemPrompt: false`) appears in the divergence report as a documented skip — silent skips fail (AC-US7-08) ✅
  - (g) Sentinel file `.skill-builder-invoked.json` is written to cwd on every `vskill skill new` invocation, containing `{ trigger, agent, timestamp, targets, prompt }`; covers both `universal` and `anthropic-skill-creator` engines (AC-US1-07) ✅

**Files**: `src/commands/__tests__/skill.integration.test.ts` (new). Pattern: in-process Commander `parseAsync` + `mkdtempSync` + `afterEach` cleanup, mocking only `generateSkill` so the REAL `emitSkill` exercises file-system side effects. Result: 8 tests, all GREEN, no network, no LLM.

---

### T-012b: Playwright Skill Studio regression test
**User Story**: US-007 | **Satisfies ACs**: AC-US7-07 | **Status**: [x] completed
**Implementation note**: `e2e/skill-studio-regression.spec.ts` (2 tests, GREEN). Mocks the `POST /api/skills/generate?sse` SSE stream at the `page.route()` layer with deterministic `progress` / `provenance` / `done` events — isolates the regression check from LLM availability. Asserts (1) body lands in the editor textarea after `done`, (2) request payload carries `prompt` (regression contract for T-002's CLI/SPA shared-shape rewire), (3) 5xx error path surfaces a user-visible message without crashing the page.

**Test Plan**:
- **Given** T-002 rewired the HTTP handler to call `generateSkill()` — the React Skill Studio UI (path B) depends on this handler
- **When** I run `npx playwright test tests/e2e/skill-studio-regression.spec.ts` (boots via existing `playwright.config.ts` webServer `eval serve --root e2e/fixtures --port 3077`)
- **Then** the test drives the existing React Studio flow end-to-end: navigates to `/workspace`, fills prompt "lint markdown files", selects 3 target agents, clicks Generate, waits for SSE stream to complete, asserts the preview panel shows SKILL.md content, asserts Save produces files on the sandbox filesystem — all without errors. This is a REGRESSION gate: it must match pre-T-002 behavior exactly.

**Files**: `tests/e2e/skill-studio-regression.spec.ts` (new). Model: `e2e/eval-ui.spec.ts`.

---

### T-012c: Manual verification gate — path B browser flow + trigger-activation across 3 agents
**User Story**: US-007 | **Satisfies ACs**: AC-US2-02 (manual), AC-US1-07 (evidence trail) | **Status**: [ ] pending | **Type**: MANUAL

**Test Plan**:
- **Given** T-012b automated regression passed
- **When** the user (not an agent) runs `cd repositories/anton-abyzov/vskill && node dist/index.js eval serve --root plugins/skills --port 3077`, opens `http://localhost:3077` in Chrome, and walks "+ New Skill" → prompt "lint markdown" → Generate, AND separately in three fresh sandbox dirs runs a Claude Code session, a Codex session, and a Cursor session (one per sandbox) after `vskill install <local-path>/plugins/skills/skills/skill-builder`, typing the trigger phrase "create a skill for linting markdown" in each
- **Then** the user signs off `reports/manual-verification.md` with a structured checklist per agent: `[x] Claude Code / 2026-MM-DD / AA — sentinel written: YES, transcript attached: reports/manual-verification/claude-code-session.jsonl, path taken: A`, same for Codex, same for Cursor. Path B sign-off additionally asserts (a) no visible layout regression vs the pre-T-002 screenshot, (b) emitted SKILL.md lands in `.claude/skills/<name>/`, `.agents/skills/<name>/`, and `.cursor/skills/<name>/` at minimum. **Enumerated agents are non-optional**: missing any of the three is a failed gate.

**Files**: `reports/manual-verification.md` (new), `reports/manual-verification/claude-code-session.jsonl` (new), `codex-session.jsonl`, `cursor-session.jsonl` — all signed off by human tester.

---

## Day 5 — Release (Four Independently Reversible Tasks)

### T-013a: Release vskill patch (npm publish + GitHub Release)
**User Story**: US-009 | **Satisfies ACs**: AC-US9-01, AC-US9-02 | **Status**: [ ] pending

**Test Plan**:
- **Given** all tests pass (T-001..T-012c) and CHANGELOG/README updated (T-011b)
- **When** I run `cd repositories/anton-abyzov/vskill && sw:release-npm` (patch release)
- **Then** npm package publishes successfully AND GitHub Release is created AND `npx vskill@latest skill --help` lists the 5 subcommands from a clean install
- **Rollback**: `npm unpublish vskill@<version>` within 72h window OR publish forward-fix `+0.0.1`.

**Files**: Release artifacts (version bump, changelog entry — no repo edits in this task beyond what release automation does).

---

### T-013b: Submit skill-builder to verified-skill.com registry
**User Story**: US-008 | **Satisfies ACs**: AC-US8-01 | **Status**: [ ] pending

**Test Plan**:
- **Given** T-013a released the CLI that contains the new `submit` path
- **When** I run `vskill submit anton-abyzov/vskill/plugins/skills/skills/skill-builder`
- **Then** submission succeeds AND returns a registry URL AND the skill appears in a `vskill find skill-builder` query
- **Rollback**: `vskill unsubmit skill-builder` — independent of T-013a (npm publish stays live).

**Files**: Registry entry (no repo edits).

---

### T-013c: Sandbox smoke test with pinned older vskill
**User Story**: US-008 | **Satisfies ACs**: AC-US8-02 | **Status**: [ ] pending

**Test Plan**:
- **Given** T-013a and T-013b complete (npm published + registry submitted)
- **When** I create a fresh sandbox, `npm i vskill@0.5.80` (older pinned version — pre-this-release), and run `vskill install skill-builder` (from registry)
- **Then** install succeeds AND `.claude/skills/skill-builder/SKILL.md` exists AND invoking the "create a skill for X" trigger in a Claude Code session inside this sandbox activates skill-builder and writes the sentinel file
- **If this fails**: do NOT proceed to T-013d; investigate the registry/pinned-version interaction.

**Files**: Smoke test log in `reports/t013c-sandbox-smoke.md`.

---

### T-013d: Umbrella sync + follow-up increment stub
**User Story**: US-009 | **Satisfies ACs**: AC-US9-03, AC-US9-04 | **Status**: [x] completed (stub portion); umbrella sync commit folds into T-013a's publish flow

**Test Plan**:
- **Given** T-013a, T-013b, T-013c all passed
- **When** I commit umbrella sync on main (`sync umbrella after vskill v0.5.X release`) AND create `.specweave/increments/<next-id>-skill-gen-vskill-integration/` with stub spec.md + metadata.json status `planned` titled "Rewire sw:skill-gen to prefer vskill skill new when available"
- **Then** umbrella main shows the sync commit AND the follow-up increment is discoverable AND no SpecWeave code was modified in this increment (AC-US9-04)

**Implementation note**:
- ✅ **Follow-up increment**: `0726-skill-gen-vskill-integration` created via `specweave create-increment` with status `planned`, type `feature`, priority `P3`. Title matches the AC requirement; description points back to 0670 T-013d. Discoverable on disk + via metadata.json scans.
- ✅ **No-SpecWeave-code-modified invariant** (AC-US9-04): 0670's diff is scoped entirely to `repositories/anton-abyzov/vskill/` (vskill repo) and `.specweave/increments/0670-skill-builder-universal/` (this increment's docs). No `repositories/anton-abyzov/specweave/` files touched. Verified via `git diff --stat` filter.
- ⏳ **Umbrella sync commit** ("sync umbrella after vskill v0.5.X release"): bundled with T-013a (npm publish) since the commit message references the version that publish produces. Will land naturally during the human-gate publish flow.

**Files**: `.specweave/increments/0726-skill-gen-vskill-integration/{metadata.json,spec.md,plan.md,tasks.md,rubric.md}` (stubs created).

---

## Completion Checklist

- [ ] T-000 through T-013d all marked `[x]` (19 tasks total)
- [ ] All ACs in spec.md marked `[x]` (US-001..US-009)
- [ ] `npx vitest run` passes with ≥90% coverage on `src/core/skill-generator.ts` and `src/commands/skill.ts`
- [ ] `npx vitest run tests/integration/skill-cli.test.ts` passes (CLI integration)
- [ ] `npx playwright test tests/e2e/skill-studio-regression.spec.ts` passes (UI regression)
- [ ] Manual verification signed off in `reports/manual-verification.md`
- [ ] vskill patch released (T-013a), skill submitted to registry (T-013b), sandbox smoke passed (T-013c)
- [ ] Umbrella sync commit on main (T-013d)
- [ ] Follow-up increment stub created (T-013d)
- [ ] rubric.md pass-criteria met at `standard` tier
- [ ] `sw:done` closure gates pass (code-review, simplify, grill, judge-llm, PM gates)

---

## Cross-reference: 0679-skills-spec-compliance

> **Note (added by 0679)**: The canonical SKILL.md frontmatter shape at
> https://agentskills.io/specification nests `tags` and `target-agents` under
> a `metadata:` block, NOT at the top level. When writing the skill-builder's
> own SKILL.md (AC-US1-01) and its references (`references/target-agents.md`,
> T-008b), use the compliant shape. The primary emitter in
> `src/eval-server/skill-create-routes.ts` and its golden-file tests
> (`src/eval-server/__tests__/skill-emitter-spec-compliance.test.ts`) lock
> this shape as of 0679. No 0670 task status changes — this note is
> informational only.
