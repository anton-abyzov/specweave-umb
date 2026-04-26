# Tasks: Port ## Test Cases parser to vskill (+writer)

## Phase 1: TDD RED — write failing tests first

### T-001: RED test — parseTestCases parses 3-pair fixture

**References**: AC-US1-01, AC-US1-03

**Test Plan**:
- **File**: `src/eval/__tests__/test-case-parser.test.ts`
- **Given**: SKILL.md content with `## Test Cases` block containing 3 pairs (one each: should activate / should not activate / auto)
- **When**: `parseTestCases(content)` runs
- **Then**: returns `[{prompt, expected: "should_activate"}, {prompt, expected: "should_not_activate"}, {prompt, expected: "auto"}]`

**Status**: [x] completed

### T-002: RED test — parseTestCases returns [] when no section

**References**: AC-US1-01

**Test Plan**:
- **Given**: SKILL.md without `## Test Cases`
- **When**: `parseTestCases(content)` runs
- **Then**: returns `[]`

**Status**: [x] completed

### T-003: RED test — parseTestCases handles malformed pairs

**References**: AC-US1-01

**Test Plan**:
- **Given**: `## Test Cases` heading present but body has prose, no `- Prompt: ... Expected: ...` pairs
- **When**: `parseTestCases(content)` runs
- **Then**: returns `[]` (no throw)

**Status**: [x] completed

### T-004: RED test — section regex stops at next ##

**References**: AC-US1-02

**Test Plan**:
- **Given**: `## Test Cases` block followed by `## Notes` containing `- Prompt: "x" Expected: "should activate"` pair
- **When**: `parseTestCases(content)` runs
- **Then**: only pairs from the `## Test Cases` block are returned (not the ones in `## Notes`)

**Status**: [x] completed

### T-005: RED test — serializeTestCases emits parseable block

**References**: AC-US2-01, AC-US2-05

**Test Plan**:
- **Given**: `[{prompt: "a", expected: "should_activate"}, {prompt: "b", expected: "should_not_activate"}, {prompt: "c", expected: "auto"}]`
- **When**: `serializeTestCases(prompts)` runs
- **Then**: result starts with `## Test Cases\n\n`, contains 3 `- Prompt: "..."\n  Expected: "..."` pairs

**Status**: [x] completed

### T-006: RED test — round-trip parse/serialize idempotent

**References**: AC-US2-05

**Test Plan**:
- **Given**: a `ParsedTestCase[]` array of mixed types
- **When**: `parseTestCases(serializeTestCases(prompts))` runs
- **Then**: result equals the input prompts (deep-equal on prompt+expected)

**Status**: [x] completed

### T-007: RED test — upsertTestCasesIntoSkillMd appends when no block

**References**: AC-US2-02

**Test Plan**:
- **Given**: SKILL.md with frontmatter + body sections (`## Workflow`, `## Examples`), NO `## Test Cases`
- **When**: `upsertTestCasesIntoSkillMd(content, prompts)` runs
- **Then**: result preserves frontmatter and original sections verbatim, appends `## Test Cases` at the end

**Status**: [x] completed

### T-008: RED test — upsertTestCasesIntoSkillMd replaces existing block

**References**: AC-US2-02

**Test Plan**:
- **Given**: SKILL.md with frontmatter + `## Workflow` + `## Test Cases` (old) + `## Examples`
- **When**: `upsertTestCasesIntoSkillMd(content, newPrompts)` runs
- **Then**: result has frontmatter unchanged, `## Workflow` unchanged, `## Test Cases` block CONTENT replaced with the serialized newPrompts, `## Examples` unchanged

**Status**: [x] completed

### T-009: RED test — GET /test-cases returns parsed prompts

**References**: AC-US1-04

**Test Plan**:
- **File**: `src/eval-server/__tests__/test-cases-routes.test.ts`
- **Given**: temp skillDir with SKILL.md containing a 2-pair `## Test Cases` block
- **When**: GET handler runs against that skillDir
- **Then**: response body is `{prompts: [...], source: "skill-md"}`, length=2

**Status**: [x] completed

### T-010: RED test — GET /test-cases returns empty when no section

**References**: AC-US1-04

**Test Plan**:
- **Given**: temp skillDir with SKILL.md but NO `## Test Cases`
- **When**: GET handler runs
- **Then**: `{prompts: [], source: null}`

**Status**: [x] completed

### T-011: RED test — PUT /test-cases writes upserted SKILL.md

**References**: AC-US2-03, AC-US2-05

**Test Plan**:
- **Given**: temp skillDir with SKILL.md (no test-cases block)
- **When**: PUT with `{prompts: [{...}, {...}]}` runs
- **Then**: response is `{ok: true, count: 2}`, on-disk SKILL.md round-trips via `parseTestCases` to the same prompts

**Status**: [x] completed

### T-012: RED test — PUT preserves frontmatter and other sections

**References**: AC-US2-02, AC-US2-03

**Test Plan**:
- **Given**: temp skillDir with SKILL.md containing frontmatter + `## Workflow` + `## Examples`
- **When**: PUT with `{prompts: [...]}` runs
- **Then**: on-disk SKILL.md has frontmatter byte-equal to original, `## Workflow` body byte-equal, `## Examples` body byte-equal, `## Test Cases` newly appended

**Status**: [x] completed

## Phase 2: TDD GREEN — implement parser module

### T-013: Implement parseTestCases, serializeTestCases, upsertTestCasesIntoSkillMd

**References**: AC-US1-01, AC-US1-02, AC-US1-03, AC-US2-01, AC-US2-02, AC-US2-05

**Implementation Details**:
- `src/eval/test-case-parser.ts` exports `ParsedTestCase`, `TestCaseExpected`, `parseTestCases`, `serializeTestCases`, `upsertTestCasesIntoSkillMd`.
- Parser regex matches platform's exactly: `/-\s*Prompt:\s*"([^"]+)"\s*\n\s*Expected:\s*"([^"]+)"/gi` inside `/## Test Cases\s*\n([\s\S]*?)(?=\n## |\n---|\n$|$)/i`.
- Serializer emits `- Prompt: "..."\n  Expected: "..."` pairs with `expected_to_text` mapping (`should_activate` → `"should activate"`, etc.).
- Upserter: if `prompts.length === 0` and section exists, REMOVE section. Otherwise replace-or-append.

**Status**: [x] completed

## Phase 3: Server routes

### T-014: Add GET /api/skills/:plugin/:skill/test-cases route

**References**: AC-US1-04

**Implementation Details**:
- In `src/eval-server/api-routes.ts`, after the existing `/activation-test` route block.
- Use `resolveSkillDir(root, plugin, skill)` for the skill path.
- Read SKILL.md if exists, parse via `parseTestCases`, return `{prompts, source: prompts.length ? "skill-md" : null}`.

**Status**: [x] completed

### T-015: Add PUT /api/skills/:plugin/:skill/test-cases route

**References**: AC-US2-03

**Implementation Details**:
- After GET route. Body shape: `{ prompts: ParsedTestCase[] }`.
- Validate each prompt: prompt is non-empty string, expected is one of the three allowed values, prompt does not contain `"` (return 400 with clear error if so).
- Read existing SKILL.md (or empty string), call `upsertTestCasesIntoSkillMd`, write back via `writeFileSync`.
- Return `{ok: true, count: prompts.length}`.

**Status**: [x] completed

## Phase 4: UI wiring

### T-016: Extend WorkspaceContext with activationPromptsSource state

**References**: AC-US3-01, AC-US3-02

**Implementation Details**:
- `workspaceTypes.ts`: add `activationPromptsSource: "skill-md" | "ai-generated" | "user-typed" | null` to `WorkspaceState`. Add `{ type: "SET_PROMPTS_SOURCE", source: ... }` to `WorkspaceAction`.
- `WorkspaceContext.tsx`: handle the new action in the reducer. Initial value: `null`.
- AI-generation success handler: dispatch `SET_PROMPTS_SOURCE` with `"ai-generated"`.

**Status**: [x] completed

### T-017: ActivationPanel — initial load fetch + source badge

**References**: AC-US1-05, AC-US3-03

**Implementation Details**:
- New `useEffect` on mount: fetch `/api/skills/:plugin/:skill/test-cases`. If `prompts.length > 0`, build textarea text with `+`/`!`/no-prefix lines, dispatch `SET_ACTIVATION_PROMPTS` and `SET_PROMPTS_SOURCE: "skill-md"`.
- Render a green "from SKILL.md" pill next to the "Test Prompts" label when source is `"skill-md"`. Purple "AI-generated" pill when source is `"ai-generated"`. Nothing when `"user-typed"` or `null`.

**Status**: [x] completed

### T-018: ActivationPanel — Save as test cases button

**References**: AC-US2-04, AC-US3-04

**Implementation Details**:
- New button next to "Generate Test Prompts", labeled "Save as test cases".
- onClick handler: parse the current textarea (lines, prefix mapping), filter empty, PUT to `/api/skills/:plugin/:skill/test-cases` with `{prompts}`.
- On success: brief inline confirmation `Saved N test cases to SKILL.md`, dispatch `SET_PROMPTS_SOURCE: "skill-md"`.
- On error: inline error message.

**Status**: [x] completed

### T-019: WorkspaceContext — flip source to user-typed on textarea edit

**References**: AC-US3-02

**Implementation Details**:
- The existing `dispatch({type: "SET_ACTIVATION_PROMPTS", prompts: promptsText})` flow in the textarea onChange path should ALSO dispatch `SET_PROMPTS_SOURCE: "user-typed"` when the new prompts text differs from the most recently loaded "canonical" text.
- Track the canonical text as a ref or in state to compare against.

**Status**: [x] completed

## Phase 5: Build + smoke test

### T-020: Build eval-ui bundle

**Implementation Details**: `npm run build:eval-ui` from vskill repo root. Confirm clean build output.

**Status**: [x] completed

### T-021: Studio smoke test on greet-anton

**References**: All US-level ACs

**Test Plan**:
- Add a `## Test Cases` block to `repositories/anton-abyzov/greet-anton/SKILL.md` with 3 prompts (one each: should activate / should not activate / auto).
- Launch studio, navigate to greet-anton → Trigger tab.
- Expected: textarea pre-populated, green "from SKILL.md" badge visible.
- Edit one prompt. Expected: badge flips to nothing (or "user-typed" pill).
- Click "Save as test cases". Expected: inline confirm; SKILL.md updated.
- Reload studio. Expected: new prompts load from SKILL.md, green badge visible again.
- `cat SKILL.md` after save: frontmatter byte-equal to original, body sections preserved, only `## Test Cases` differs.

**Status**: [x] completed

### T-022: Sync living docs

**Implementation Details**: `specweave sync-living-docs 0776-vskill-test-cases-parser`.

**Status**: [x] completed
