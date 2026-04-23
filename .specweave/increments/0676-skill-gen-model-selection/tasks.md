# 0676 — Tasks

All tasks follow TDD: test file written first (RED), implementation follows (GREEN). Bidirectional linking via `**AC**:` field.

### T-001: Write unit tests for `model-registry.ts` resolver
**User Story**: US-001, US-002 | **AC**: AC-US1-01, AC-US1-03, AC-US2-01, AC-US2-03 | **Status**: [x] completed
**Test Plan**: Given the registry API, When `resolveDefaultModel()` is called with no arg, Then it returns the first `current` Opus (`claude-opus-4-7`). When called with `"opus"`/`"sonnet"`/`"haiku"`, Then it returns the matching current tier. When `resolveModel()` gets an alias, Then it resolves to the tier default; given a full BYO ID, Then it echoes it back unchanged.
**File**: `src/lib/eval/__tests__/model-registry.test.ts` (14 cases)

### T-002: Implement `model-registry.ts` (GREEN)
**User Story**: US-001, US-002 | **AC**: AC-US1-01, AC-US1-03, AC-US2-01, AC-US2-03 | **Status**: [x] completed
**Test Plan**: Given T-001 tests failing (RED), When `model-registry.ts` is created with registry data + `resolveDefaultModel` + `resolveModel` + header comment explaining forward-compat update, Then all 14 T-001 tests pass.
**File**: `src/lib/eval/model-registry.ts`

### T-003: Write unit tests for updated `claude-adapter.ts`
**User Story**: US-001, US-002 | **AC**: AC-US1-02, AC-US2-02 | **Status**: [x] completed
**Test Plan**: Given a source-level assertion, When `claude-adapter.ts` source is read, Then it must not contain the literal `claude-sonnet-4-6`. Given a mocked `@anthropic-ai/sdk`, When `createClaudeAdapter` is called with `ANTHROPIC_BASE_URL` set, Then `new Anthropic()` is invoked with `baseURL`; When unset, `baseURL` is absent from constructor args. Given `SKILL_EVAL_MODEL="sonnet"`, Then `modelId` is `claude-sonnet-4-6`.
**File**: `src/lib/eval/__tests__/claude-adapter.test.ts` (7 cases)

### T-004: Update `claude-adapter.ts` to use resolver + thread baseURL (GREEN)
**User Story**: US-001, US-002 | **AC**: AC-US1-02, AC-US2-02 | **Status**: [x] completed
**Test Plan**: Given T-003 tests failing (RED), When `claude-adapter.ts` imports `resolveModel` and conditionally spreads `baseURL` into the `Anthropic` constructor, Then all 7 T-003 tests pass.
**File**: `src/lib/eval/claude-adapter.ts`

### T-005: Write unit tests for `skill-validator.ts`
**User Story**: US-003 | **AC**: AC-US3-01, AC-US3-02, AC-US3-03, AC-US3-04, AC-US3-05 | **Status**: [x] completed
**Test Plan**: Given a valid SKILL.md fixture, When `validateSkillMarkdown` runs, Then it returns `{ok: true}`. Given missing frontmatter / invalid name regex / short description / missing action verb / missing period / missing ## heading / HTML inside mermaid block, Then each case returns `{ok: false, errors: [...]}` with a descriptive message.
**File**: `src/lib/skills/__tests__/skill-validator.test.ts` (18 cases)

### T-006: Implement `skill-validator.ts` (GREEN)
**User Story**: US-003 | **AC**: AC-US3-01, AC-US3-02, AC-US3-03, AC-US3-04, AC-US3-05 | **Status**: [x] completed
**Test Plan**: Given T-005 tests failing (RED), When `skill-validator.ts` implements a zero-dep frontmatter parser + NAME_REGEX + ACTION_VERBS list + mermaid-block extractor, Then all 18 T-005 tests pass.
**File**: `src/lib/skills/skill-validator.ts`

### T-007: Add `GET /api/v1/models/default` operator self-check endpoint
**User Story**: US-004 | **AC**: AC-US4-01 | **Status**: [x] completed
**Test Plan**: Given the dev server is running, When `GET /api/v1/models/default` is called, Then it returns 200 with JSON `{modelId, tier, defaultOpus, envOverride, baseURLOverride}`; `tier` is `"opus"` when no env override; `defaultOpus` starts with `claude-opus-`.
**File**: `src/app/api/v1/models/default/route.ts`

### T-008: Write Playwright E2E spec (full assertion)
**User Story**: US-004 | **AC**: AC-US4-01, AC-US4-02, AC-US4-03, AC-US4-04 | **Status**: [x] completed
**Test Plan**: Given the dev server, When `GET /api/v1/models/default` is hit, Then the response reports Opus-tier (AC-US4-01). Given the validator + a valid fixture, When run, Then `{ok:true}` (AC-US4-02). Given `resolveModel` + aliases / full BYO IDs / undefined, Then each resolves correctly (AC-US4-03). Given 5 regression fixtures (no frontmatter, invalid name, short description, HTML in mermaid, no heading), When validated, Then each returns `{ok:false}` (AC-US4-04).
**File**: `tests/e2e/skill-creation.spec.ts` (11 cases)

### T-009: Update `sw:skill-gen` SKILL.md with "Model Selection" section
**User Story**: US-004 (ecosystem consistency) | **AC**: (doc-only, covered by ADR) | **Status**: [x] completed
**Test Plan**: Given the existing SKILL.md, When the "Model Selection" section is added after frontmatter, Then `grep "Model Selection\|ANTHROPIC_BASE_URL" SKILL.md` returns matches; `/model opus` and `npx anymodel proxy` patterns are both documented.
**File**: `repositories/anton-abyzov/specweave/plugins/specweave/skills/skill-gen/SKILL.md`

### T-010: Update vendored Anthropic `skill-creator` SKILL.md with "Model Recommendations"
**User Story**: US-004 (ecosystem consistency) | **AC**: (doc-only) | **Status**: [x] completed
**Test Plan**: Given the existing skill-creator SKILL.md, When the "Model Recommendations" section is added before "Communicating with the user", Then `/model opus` and AnyModel proxy pattern are both documented, and a pointer to the ADR is present.
**File**: `.claude/skills/skill-creator/SKILL.md`

### T-011: Create ADR `0676-01-skill-gen-model-selection.md`
**User Story**: US-004 (decision record) | **AC**: (architectural artifact) | **Status**: [x] completed
**Test Plan**: Given the ADR template convention in `.specweave/docs/internal/architecture/adr/`, When the ADR is written with Context / Decision / Alternatives / Consequences / Related, Then it is discoverable via `grep "Skill Generator Model Selection"` and referenced by `sw:skill-gen`, `skill-creator`, and `0670-skill-builder-universal/plan.md`.
**File**: `.specweave/docs/internal/architecture/adr/0676-01-skill-gen-model-selection.md`

### T-012: Seed `0670-skill-builder-universal/plan.md` with cross-increment model-selection note
**User Story**: US-004 (ecosystem consistency) | **AC**: (prevent duplicate resolver) | **Status**: [x] completed
**Test Plan**: Given `0670-skill-builder-universal/plan.md` exists and the new CLI path A will invoke an LLM, When the "Open Design Decisions" section is added with a reference to the 0676 registry pattern, Then `grep "model-registry.ts\|ANTHROPIC_BASE_URL\|AnyModel" plan.md` returns matches in 0670's plan.
**File**: `.specweave/increments/0670-skill-builder-universal/plan.md`

### T-013: Run full test suite — verify no regressions + full green on new code
**User Story**: all | **AC**: all | **Status**: [x] completed
**Test Plan**: Given the 4 new Vitest files and 1 new Playwright spec, When `npx vitest run` is run against them, Then 39/39 pass; When `npx playwright test tests/e2e/skill-creation.spec.ts --project=chromium` runs against a vskill-platform dev server, Then 11/11 pass. Pre-existing unrelated failures in `src/app/api/v1/skills/[owner]/[repo]/[skill]/versions/__tests__/route.test.ts` are out of scope (tracked separately).
