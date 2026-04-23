---
increment: 0678-skill-gen-source-model-picker
title: Skill-Gen Source Model Picker — Tasks
scope: Server validation + UI dropdown + preferences persistence + CLI flags
target_days: 1
status: planned
---

# Tasks: Skill-Gen Source Model Picker

> Target codebase: `repositories/anton-abyzov/vskill/`
> Stack: Node 20 + TypeScript 5.7 + Vitest 3 + Vite 6 + React 19
> TDD: tests first, then implementation.

---

### T-001: Write server unit tests for provider/model validation in `skill-create-routes.ts`
**User Story**: US-002 | **Satisfies ACs**: AC-US2-01, AC-US2-02, AC-US2-03, AC-US2-04, AC-US2-05 | **Status**: [ ] pending
**Estimated**: 1h | **Test Level**: unit
**Test Plan**:
  Given `src/eval-server/__tests__/skill-create-routes.test.ts` with `detectAvailableProviders()` mocked to return `[{ id: "claude-cli", models: ["sonnet"] }, { id: "ollama", models: ["qwen2.5-coder:7b"] }]`
  When the endpoint is called with — (a) `{ provider: "ollama", model: "qwen2.5-coder:7b" }`, (b) `{ provider: "unknown-x" }`, (c) `{ provider: "ollama", model: "not-loaded" }`, (d) `{}`, (e) `{ provider: "claude-cli" }`
  Then (a) is accepted with the full `{ provider, model }` passed to dispatch; (b) returns 400 `{ error: "unknown_provider", validProviders: ["claude-cli", "ollama"] }`; (c) returns 400 `{ error: "unknown_model", validModels: ["qwen2.5-coder:7b"] }`; (d) is accepted with `{ provider: "claude-cli", model: "sonnet" }`; (e) is accepted with `{ provider: "claude-cli", model: "sonnet" }` (model default filled)
**Files**:
  - `repositories/anton-abyzov/vskill/src/eval-server/__tests__/skill-create-routes.test.ts`
**Dependencies**: none

---

### T-002: Implement server validation + default handling in `skill-create-routes.ts`
**User Story**: US-002 | **Satisfies ACs**: AC-US2-01, AC-US2-02, AC-US2-03, AC-US2-04, AC-US2-05 | **Status**: [ ] pending
**Estimated**: 1h | **Test Level**: unit
**Test Plan**:
  Given the failing tests from T-001 and the existing handler at `src/eval-server/skill-create-routes.ts:940`
  When the handler is updated to — (1) read both `body.provider` and `body.model`, (2) call `detectAvailableProviders()` and validate the pair, (3) return 400 with structured error on mismatch, (4) fall back to `{ provider: "claude-cli", model: "sonnet" }` only when both are absent, (5) pass the validated pair to the generation dispatch in `src/eval/llm.ts`
  Then all T-001 tests pass, `npx tsc --noEmit` is clean, and legacy callers (no `provider`, no `model`) see identical behavior to before the change
**Files**:
  - `repositories/anton-abyzov/vskill/src/eval-server/skill-create-routes.ts`
**Dependencies**: T-001

---

### T-003: Extend `useStudioPreferences` with `skillGenModel` field + unit tests
**User Story**: US-003 | **Satisfies ACs**: AC-US3-01, AC-US3-02, AC-US3-03 | **Status**: [ ] pending
**Estimated**: 1h | **Test Level**: unit
**Test Plan**:
  Given `src/eval-ui/src/hooks/useStudioPreferences.ts` (shipped in 0674) and a new test file `src/eval-ui/src/__tests__/studio-preferences-skill-gen-model.test.ts`
  When `skillGenModel?: { provider: string; model: string }` is added to the type and getter/setter follow the existing pattern, then tests covering — (a) round-trip set/get, (b) cross-tab propagation via simulated `storage` event, (c) malformed localStorage recovery (JSON parse error resets to undefined, single console.warn in dev)
  Then all three tests pass; existing 0674 preferences tests remain unchanged; storage key remains `vskill-studio-preferences` (no new key)
**Files**:
  - `repositories/anton-abyzov/vskill/src/eval-ui/src/hooks/useStudioPreferences.ts`
  - `repositories/anton-abyzov/vskill/src/eval-ui/src/__tests__/studio-preferences-skill-gen-model.test.ts`
**Dependencies**: none (can run parallel to T-001/T-002)

---

### T-004: Write jsdom tests for the CreateSkillPage dropdown
**User Story**: US-001 | **Satisfies ACs**: AC-US1-01, AC-US1-02, AC-US1-03, AC-US1-04, AC-US1-05 | **Status**: [ ] pending
**Estimated**: 1h | **Test Level**: unit
**Test Plan**:
  Given `src/eval-ui/src/__tests__/create-skill-model-picker.test.tsx` renders `CreateSkillPage` with `detectAvailableProviders` mocked and `useStudioPreferences` stubbed under four scenarios — (a) no prior selection + 2 providers detected, (b) prior selection for a currently detected provider, (c) prior selection for a provider NOT currently detected, (d) zero providers detected
  When the dropdown is opened and interacted with
  Then (a) shows all providers and models grouped, preselects `claude-cli/sonnet` with a "Default" caption; (b) preselects the persisted value; (c) falls back to default AND renders a one-time toast with the described copy; (d) renders the dropdown disabled with the exact tooltip copy from AC-US1-04
**Files**:
  - `repositories/anton-abyzov/vskill/src/eval-ui/src/__tests__/create-skill-model-picker.test.tsx`
**Dependencies**: T-003

---

### T-005: Implement the dropdown on CreateSkillPage
**User Story**: US-001 | **Satisfies ACs**: AC-US1-01, AC-US1-02, AC-US1-03, AC-US1-04, AC-US1-05 | **Status**: [ ] pending
**Estimated**: 1.5h | **Test Level**: unit
**Test Plan**:
  Given the failing tests from T-004 and the ComparisonPage selector as a visual reference (not imported — ADR-0678-02 keeps them separate)
  When `CreateSkillPage.tsx` is updated to render a "Source model" dropdown wired to `detectAvailableProviders()` and `useStudioPreferences().skillGenModel`, with the fallback toast for unavailable-persisted selections and the disabled state for zero detected providers
  Then all T-004 tests pass; the dropdown visually matches the ComparisonPage selector (same label position, same grouping); a TODO comment `// TODO(0678): extract <ProviderModelPicker> — shared with ComparisonPage` is added for the future refactor
**Files**:
  - `repositories/anton-abyzov/vskill/src/eval-ui/src/pages/CreateSkillPage.tsx`
**Dependencies**: T-004

---

### T-006: Add `--provider` and `--model` flags to `vskill skill new` + CLI integration tests
**User Story**: US-004 | **Satisfies ACs**: AC-US4-01, AC-US4-02, AC-US4-03, AC-US4-04 | **Status**: [ ] pending
**Estimated**: 1h | **Test Level**: integration
**Test Plan**:
  Given the `vskill skill new` command definition (in `src/cli/skill.ts` or wherever commander options live) and a new test file `src/cli/__tests__/skill-new-flags.test.ts` that spawns the CLI via `execa` with a mock server capturing the HTTP body
  When the CLI is invoked under four scenarios — (a) `--provider ollama --model qwen2.5-coder:7b` with Ollama detected, (b) `--provider unknown-x` with Ollama detected, (c) no flags, (d) only `--provider claude-cli`
  Then (a) exits 0 and the captured request body is `{ provider: "ollama", model: "qwen2.5-coder:7b" }`; (b) exits 2 with stderr "Unknown provider 'unknown-x'. Valid: [...]"; (c) exits 0 with body `{ provider: "claude-cli", model: "sonnet" }`; (d) exits 0 with body `{ provider: "claude-cli", model: "sonnet" }` (model default filled); help text for both flags matches the AC-US4-01 strings
**Files**:
  - `repositories/anton-abyzov/vskill/src/cli/skill.ts` (or whichever file registers the `skill new` command)
  - `repositories/anton-abyzov/vskill/src/cli/__tests__/skill-new-flags.test.ts`
**Dependencies**: T-002

---

### T-007: Documentation + closure gate
**User Story**: US-001, US-002, US-003, US-004 | **Satisfies ACs**: All ACs | **Status**: [ ] pending
**Estimated**: 0.5h | **Test Level**: docs + integration
**Test Plan**:
  Given all preceding tasks are complete
  When the README's "Creating a skill" section is updated to document the new picker, the new CLI flags, and the persistence behavior; then `npx tsc --noEmit`, `npx vitest run`, and `npx playwright test` are executed
  Then the README section renders without markdown-lint warnings; tsc exits 0; Vitest reports ≥ 90% coverage on the touched files; no Playwright regressions; `specweave validate 0678-skill-gen-source-model-picker` passes
**Files**:
  - `repositories/anton-abyzov/vskill/README.md`
**Dependencies**: T-002, T-003, T-005, T-006
