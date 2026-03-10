---
increment: 0472-activation-auto-classify
generated_by: sw:test-aware-planner
tdd_mode: true
coverage_target: 90
by_user_story:
  US-001: [T-001, T-002]
  US-002: [T-003]
  US-003: [T-004]
  US-004: [T-005, T-006]
  US-005: [T-007]
---

# Tasks: Auto-classify Activation Test Expectations

## User Story: US-001 - Two-Phase Activation Evaluation

**Linked ACs**: AC-US1-01, AC-US1-02, AC-US1-03, AC-US1-04
**Tasks**: 2 total, 0 completed

---

### T-001: Add SkillMeta type and classifyExpectation function to activation-tester.ts

**User Story**: US-001
**Satisfies ACs**: AC-US1-01, AC-US1-03, AC-US1-04
**Status**: [ ] pending

**Test Plan**:
- **Given** a `SkillMeta` with name and tags and an LLM client that returns `{"related": true}`
- **When** `classifyExpectation` is called with a prompt
- **Then** it returns `"should_activate"`

**Test Cases**:
1. **Unit**: `src/eval/__tests__/activation-tester.test.ts`
   - `classifyExpectation returns should_activate when LLM says related true`
   - `classifyExpectation returns should_not_activate when LLM says related false`
   - `classifyExpectation returns should_activate fallback on LLM error`
   - **Coverage Target**: 95%

**Implementation**:
1. Add `SkillMeta` interface: `{ name: string; tags: string[] }` to `src/eval/activation-tester.ts`
2. Extend `ActivationPrompt.expected` union to include `"auto"`
3. Add `autoClassified?: boolean` to `ActivationResult`
4. Add `CLASSIFICATION_SYSTEM_PROMPT` constant (requests minimal JSON `{"related": true/false}`, uses only name + tags)
5. Export `classifyExpectation(prompt: string, skillMeta: SkillMeta, client: LlmClient): Promise<"should_activate" | "should_not_activate">`
   - System prompt instructs: respond with ONLY `{"related": true/false}`
   - User prompt: `Skill: {name}\nTags: {tags.join(', ')}\nUser prompt: {prompt}\nIs this prompt related to this skill?`
   - Parse response JSON, extract `related` boolean
   - Return `"should_activate"` if related, `"should_not_activate"` if not
   - On any error or invalid JSON: return `"should_activate"` (backward compat)
6. Run: `cd repositories/anton-abyzov/vskill && npx vitest run src/eval/__tests__/activation-tester.test.ts`

---

### T-002: Implement two-phase flow in testActivation

**User Story**: US-001
**Satisfies ACs**: AC-US1-01, AC-US1-02, AC-US1-03, AC-US1-04
**Status**: [ ] pending

**Test Plan**:
- **Given** prompts with mixed prefixes (`"auto"`, `"should_activate"`, `"should_not_activate"`) and a `SkillMeta`
- **When** `testActivation` is called
- **Then** Phase 1 classifies all `"auto"` prompts first, Phase 2 evaluates all prompts, and `autoClassified` is set only on Phase-1 prompts

**Test Cases**:
1. **Unit**: `src/eval/__tests__/activation-tester.test.ts`
   - `testActivation with skillMeta only classifies auto prompts in phase 1`
   - `testActivation without skillMeta defaults auto prompts to should_activate`
   - `testActivation sets autoClassified true only on auto-resolved prompts`
   - **Coverage Target**: 90%

**Implementation**:
1. Update `testActivation` signature: add optional `skillMeta?: SkillMeta` parameter before `onResult?`
2. Phase 1: filter prompts where `expected === "auto"`, call `classifyExpectation` for each if `skillMeta?.name` exists; otherwise default to `"should_activate"`; store resolved expectations in a local map keyed by prompt index
3. Phase 2: existing evaluation loop unchanged; for `"auto"` prompts use resolved expected from map; set `autoClassified: true` on those results
4. Preserve all existing `onResult?` callback and error-handling behavior
5. Run: `cd repositories/anton-abyzov/vskill && npx vitest run src/eval/__tests__/activation-tester.test.ts`

---

## User Story: US-002 - Classification Prompt and Cross-Model Compatibility

**Linked ACs**: AC-US2-01, AC-US2-02, AC-US2-03
**Tasks**: 1 total, 0 completed

---

### T-003: Harden classifyExpectation prompt and fallback behavior

**User Story**: US-002
**Satisfies ACs**: AC-US2-01, AC-US2-02, AC-US2-03
**Status**: [ ] pending

**Test Plan**:
- **Given** an LLM that returns malformed JSON or throws a network error
- **When** `classifyExpectation` is called
- **Then** it falls back to `"should_activate"` without propagating the error

**Test Cases**:
1. **Unit**: `src/eval/__tests__/activation-tester.test.ts`
   - `classifyExpectation falls back on invalid JSON response`
   - `classifyExpectation falls back on LLM network error`
   - `testActivation skips phase 1 entirely when skillMeta has no name`
   - **Coverage Target**: 90%

**Implementation**:
1. Verify `CLASSIFICATION_SYSTEM_PROMPT` (from T-001) requests `{"related": true/false}` using only name + tags — no full description — per AC-US2-01
2. Wrap JSON parsing in try/catch in `classifyExpectation`; return `"should_activate"` on any failure — per AC-US2-02
3. In `testActivation` Phase 1: guard with `if (!skillMeta || !skillMeta.name)` → skip classification, default all `"auto"` to `"should_activate"` — per AC-US2-03
4. Run: `cd repositories/anton-abyzov/vskill && npx vitest run src/eval/__tests__/activation-tester.test.ts`

---

## User Story: US-003 - Server-Side Metadata Extraction

**Linked ACs**: AC-US3-01, AC-US3-02
**Tasks**: 1 total, 0 completed

---

### T-004: Extract SkillMeta from SKILL.md frontmatter in api-routes.ts

**User Story**: US-003
**Satisfies ACs**: AC-US3-01, AC-US3-02
**Status**: [ ] pending

**Test Plan**:
- **Given** a SKILL.md with frontmatter containing `name: "Slack messaging"` and `metadata.tags: ["slack", "messaging"]`
- **When** the `/activation-test` endpoint processes the request
- **Then** a `SkillMeta` with name `"Slack messaging"` and tags `["slack", "messaging"]` is passed to `testActivation`

**Test Cases**:
1. **Unit**: `src/eval-server/__tests__/api-routes.test.ts` (create if missing)
   - `extractSkillMeta returns name and tags from valid frontmatter with metadata.tags`
   - `extractSkillMeta returns empty tags array when tags field is missing`
   - `extractSkillMeta returns undefined when frontmatter has no name`
   - **Coverage Target**: 85%

**Implementation**:
1. Open `src/eval-server/api-routes.ts`, locate `/activation-test` route handler
2. After reading SKILL.md content, extract frontmatter block via regex (consistent with existing frontmatter extraction pattern in the file)
3. Parse `name:` value and `tags:` array (check both top-level `tags:` and `metadata.tags:`)
4. Build `SkillMeta | undefined` — `undefined` if no name found, `tags: []` if tags missing
5. Pass as new optional parameter to `testActivation(description, prompts, client, skillMeta, onResult)`
6. Run: `cd repositories/anton-abyzov/vskill && npx vitest run`

---

## User Story: US-004 - Client Prefix Handling and UI Updates

**Linked ACs**: AC-US4-01, AC-US4-02, AC-US4-03, AC-US4-04
**Tasks**: 2 total, 0 completed

---

### T-005: Update WorkspaceContext to send "auto" for unprefixed prompts and handle "+" prefix

**User Story**: US-004
**Satisfies ACs**: AC-US4-01, AC-US4-02
**Status**: [ ] pending

**Test Plan**:
- **Given** a textarea with lines: `"send a message"`, `"+ send slack msg"`, `"! what is weather"`
- **When** `runActivationTest` parses the prompts
- **Then** it produces `expected: "auto"`, `expected: "should_activate"` (stripped), and `expected: "should_not_activate"` (stripped) respectively

**Test Cases**:
1. **Unit**: `src/eval-ui/src/__tests__/WorkspaceContext.test.ts` (create if missing)
   - `runActivationTest sends auto for unprefixed prompts`
   - `runActivationTest strips + prefix and sends should_activate`
   - `runActivationTest preserves ! prefix behavior as should_not_activate`
   - **Coverage Target**: 85%

**Implementation**:
1. Open `src/eval-ui/src/pages/workspace/WorkspaceContext.tsx`
2. In `runActivationTest`, update prompt parsing:
   - Lines starting with `+`: `expected: "should_activate"`, strip the `+` and trim
   - Lines starting with `!`: `expected: "should_not_activate"`, strip the `!` and trim (existing behavior)
   - All other lines: `expected: "auto"` (was `"should_activate"`)
3. Update the client-side `ActivationPrompt` type import (or local type) to allow `"auto"` in the `expected` field
4. Run: `cd repositories/anton-abyzov/vskill/src/eval-ui && npx vitest run`

---

### T-006: Add Auto badge in ActivationPanel result rows and update help text

**User Story**: US-004
**Satisfies ACs**: AC-US4-03, AC-US4-04
**Status**: [ ] pending

**Test Plan**:
- **Given** an activation result with `autoClassified: true`
- **When** the result row is rendered in the Activation Panel
- **Then** an "Auto" badge appears next to the classification pill

**Test Cases**:
1. **Unit**: `src/eval-ui/src/__tests__/ActivationPanel.test.tsx` (create if missing)
   - `ResultRow shows Auto badge when autoClassified is true`
   - `ResultRow does not show Auto badge when autoClassified is false or undefined`
   - `help text section documents no-prefix (auto), + (activate), ! (not activate) conventions`
   - **Coverage Target**: 80%

**Implementation**:
1. Open `src/eval-ui/src/types.ts`, add `autoClassified?: boolean` to `ActivationResult`
2. Open `src/eval-ui/src/pages/workspace/ActivationPanel.tsx`
3. In `ResultRow` (or equivalent result rendering component), add conditional "Auto" pill/badge rendered when `result.autoClassified === true`, positioned next to the classification pill
4. Update help text below the prompt textarea to document all three conventions:
   - No prefix: auto-classified by LLM
   - `+`: force expect activation
   - `!`: force expect no activation
5. Run: `cd repositories/anton-abyzov/vskill/src/eval-ui && npx vitest run`

---

## User Story: US-005 - Unit Tests for Classification Logic

**Linked ACs**: AC-US5-01, AC-US5-02, AC-US5-03, AC-US5-04
**Tasks**: 1 total, 0 completed

---

### T-007: Write comprehensive unit tests for classifyExpectation and two-phase testActivation

**User Story**: US-005
**Satisfies ACs**: AC-US5-01, AC-US5-02, AC-US5-03, AC-US5-04
**Status**: [ ] pending

**Test Plan**:
- **Given** the full classification and two-phase flow is implemented (T-001 through T-003)
- **When** the full test suite runs
- **Then** all four AC-US5 scenarios pass and coverage reaches 90%+

**Test Cases**:
1. **Unit**: `src/eval/__tests__/activation-tester.test.ts`
   - `classifyExpectation returns should_activate for {"related": true}` — AC-US5-01
   - `classifyExpectation returns should_not_activate for {"related": false}` — AC-US5-02
   - `classifyExpectation returns should_activate fallback on LLM throw` — AC-US5-03
   - `testActivation with mixed prefixes: LLM called only for auto prompts` — AC-US5-04
   - **Coverage Target**: 90%

**Implementation**:
1. Open `src/eval/__tests__/activation-tester.test.ts`
2. Add `import { classifyExpectation } from "../activation-tester.js"` to imports
3. Add `describe("classifyExpectation", ...)` block:
   - Mock LLM returning `'{"related": true}'` → assert returns `"should_activate"` (AC-US5-01)
   - Mock LLM returning `'{"related": false}'` → assert returns `"should_not_activate"` (AC-US5-02)
   - Mock LLM throwing `new Error("timeout")` → assert returns `"should_activate"` (AC-US5-03)
4. Add test for AC-US5-04 in the existing `describe("testActivation", ...)` block:
   - Create 3 prompts: `expected: "auto"`, `expected: "should_activate"`, `expected: "should_not_activate"`
   - Pass `skillMeta: { name: "Test skill", tags: ["test"] }`
   - Assert classification client mock called exactly once (only for the `"auto"` prompt)
5. Run full suite with coverage: `cd repositories/anton-abyzov/vskill && npx vitest run --coverage`
