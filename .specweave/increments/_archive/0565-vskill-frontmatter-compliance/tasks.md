# Tasks: Fix vskill SKILL.md frontmatter for Agent Skills standard compliance

## Task Notation

- `[T###]`: Task ID
- `[P]`: Parallelizable
- `[ ]`: Not started
- `[x]`: Completed
- Model hints: haiku (simple), sonnet (default)

---

## US-001: Frontmatter injection during skill installation

### T-001: Write failing unit tests for `ensureFrontmatter` and `validateSkillNameStrict`
**User Story**: US-001, US-003 | **Satisfies ACs**: AC-US1-01, AC-US1-02, AC-US1-03, AC-US1-04, AC-US1-05, AC-US3-01, AC-US3-02, AC-US3-03, AC-US3-04, AC-US3-05
**Status**: [x] Completed

**TDD Phase**: RED — write tests first, all must fail before implementation.

**File**: `repositories/anton-abyzov/vskill/src/installer/frontmatter.test.ts`

**Test**:

- TC-001 (AC-US1-01): Given a SKILL.md string with no frontmatter block → When `ensureFrontmatter(content, "my-skill")` is called → Then the returned string starts with `---\n` and contains `name: my-skill` inside the frontmatter block
- TC-002 (AC-US1-02): Given a SKILL.md string with `---\ndescription: A skill\n---\n# Body` → When `ensureFrontmatter(content, "my-skill")` is called → Then the returned frontmatter block contains `name: my-skill` and the original `description` field is preserved
- TC-003 (AC-US1-03): Given a SKILL.md string with `---\nname: my-skill\n---\n# Heading\n\nFirst paragraph text` → When `ensureFrontmatter(content, "my-skill")` is called → Then the returned frontmatter block contains `description: First paragraph text`
- TC-004 (AC-US1-04): Given a SKILL.md string with `---\nname: my-skill\ndescription: Already set\n---\n# Body` → When `ensureFrontmatter(content, "my-skill")` is called → Then the returned string equals the input (no change)
- TC-005 (AC-US1-05): Given a SKILL.md string with `---\nname: author-chosen-name\n---\n# Body` → When `ensureFrontmatter(content, "different-name")` is called → Then the returned frontmatter contains `name: author-chosen-name` (author value preserved)
- TC-006 (Edge case — empty body): Given a SKILL.md string with no frontmatter and empty body → When `ensureFrontmatter(content, "my-skill")` is called → Then `description` is set to `my skill` (humanized skill name)
- TC-007 (Edge case — CRLF): Given a SKILL.md string using `\r\n` line endings → When `ensureFrontmatter(content, "my-skill")` is called → Then no `\r` characters appear in the frontmatter block and body is not corrupted
- TC-008 (Edge case — malformed frontmatter): Given a SKILL.md string starting with `---\nbroken: [unclosed` (no closing `---`) → When `ensureFrontmatter(content, "my-skill")` is called → Then a new frontmatter block with `name` and `description` is prepended (treated as no-frontmatter)
- TC-009 (NFR — extra fields preserved): Given a SKILL.md string with `---\nauthor: Alice\nversion: 1.0\n---\n# Body` → When `ensureFrontmatter(content, "my-skill")` is called → Then `author: Alice` and `version: 1.0` are still present in the returned frontmatter
- TC-010 (AC-US3-01): Given valid names `["a", "my-skill", "abc123", "a1b2c3", "a-b-c"]` → When `validateSkillNameStrict(name)` is called for each → Then all return `true`
- TC-011 (AC-US3-02): Given names with uppercase `["MySkill", "MY-SKILL", "Abc"]` → When `validateSkillNameStrict(name)` is called for each → Then all return `false`
- TC-012 (AC-US3-03): Given names with underscores or spaces `["my_skill", "my skill", "my-skill_v2"]` → When `validateSkillNameStrict(name)` is called for each → Then all return `false`
- TC-013 (AC-US3-04): Given empty string and a 65-character string of `a` chars → When `validateSkillNameStrict(name)` is called → Then both return `false`
- TC-014 (AC-US3-05): Given names `["-my-skill", "my-skill-", "-"]` → When `validateSkillNameStrict(name)` is called for each → Then all return `false`
- TC-015 (AC-US1-03 — description extraction): Given body with heading then paragraph `"# Title\n\nThis is the description. More text."` → When `extractDescription(body, "my-skill")` is called → Then it returns `"This is the description. More text."`
- TC-016 (AC-US1-03 — description skips headings): Given body starting with only headings `"# Title\n## Subtitle\n"` → When `extractDescription(body, "my-skill")` is called → Then it returns `"my skill"` (humanized fallback)
- TC-017 (Edge case — description truncation): Given a body paragraph exceeding 200 characters → When `extractDescription(body, "my-skill")` is called → Then the returned description is at most 200 characters

**Dependencies**: None

---

### T-002: Implement `src/installer/frontmatter.ts`
**User Story**: US-001, US-003 | **Satisfies ACs**: AC-US1-01, AC-US1-02, AC-US1-03, AC-US1-04, AC-US1-05, AC-US3-01, AC-US3-02, AC-US3-03, AC-US3-04, AC-US3-05
**Status**: [x] Completed

**TDD Phase**: GREEN — implement until all T-001 tests pass.

**File**: `repositories/anton-abyzov/vskill/src/installer/frontmatter.ts`

**Implementation Details**:
- Export `ensureFrontmatter(content: string, skillName: string): string` — pure function
- Export `validateSkillNameStrict(name: string): boolean` — regex `/^[a-z0-9]([a-z0-9-]{0,62}[a-z0-9])?$/` plus single-char `/^[a-z0-9]$/`
- Export `extractDescription(body: string, skillName: string): string` — scan lines, skip `#` headings and blank lines, truncate to 200 chars, fallback to `skillName.replace(/-/g, " ")`
- Frontmatter detection: regex match `^---\n([\s\S]*?)\n---` (no YAML lib, no new dependencies)
- Use `.js` import extensions in any imports (NodeNext module resolution)

**Test**:
Given all T-001 tests are written and failing → When `frontmatter.ts` is implemented → Then all 17 T-001 test cases pass with zero skips

**Dependencies**: T-001

---

### T-003: REFACTOR — clean up `frontmatter.ts` after green
**User Story**: US-001 | **Satisfies ACs**: AC-US1-01, AC-US1-02, AC-US1-03, AC-US1-04, AC-US1-05
**Status**: [x] Completed

**TDD Phase**: REFACTOR — no behavior change, only structural improvements.

**Implementation Details**:
- Extract regex constants to named module-level variables
- Ensure every exported function has a JSDoc comment
- Verify no code duplication between `ensureFrontmatter` and `extractDescription`
- Run `npx vitest run src/installer/frontmatter.test.ts` — must stay green

**Test**:
Given the green T-001 test suite → When refactoring is complete → Then `npx vitest run src/installer/frontmatter.test.ts` passes with the same count and no regressions

**Dependencies**: T-002

---

## US-002: Write-site integration across install and update paths

### T-004: Write failing integration tests for canonical.ts write sites
**User Story**: US-002 | **Satisfies ACs**: AC-US2-01, AC-US2-02, AC-US2-03, AC-US2-04
**Status**: [x] Completed

**TDD Phase**: RED — extend `canonical.test.ts` with new tests that fail before integration changes.

**File**: `repositories/anton-abyzov/vskill/src/installer/canonical.test.ts`

**Test**:

- TC-101 (AC-US2-01): Given content `"# My Skill\nThis does things."` with no frontmatter → When `installSymlink("my-skill", content, agents, opts)` is called → Then the canonical SKILL.md at `.agents/skills/my-skill/SKILL.md` contains `name: my-skill` in its frontmatter
- TC-102 (AC-US2-02): Given content with no frontmatter and a `claude-code` agent in the agent list → When `installSymlink("my-skill", content, agents, opts)` is called → Then the copy-fallback SKILL.md at `.claude/skills/my-skill/SKILL.md` contains `name: my-skill` in its frontmatter
- TC-103 (AC-US2-03): Given content with no frontmatter and a symlink-failure scenario (non-existent canonical target) → When `installSymlink` falls back to direct copy → Then the fallback SKILL.md contains `name: my-skill` in its frontmatter
- TC-104 (AC-US2-04): Given content `"# My Skill\nThis does things."` with no frontmatter → When `installCopy("my-skill", content, agents, opts)` is called → Then every agent's SKILL.md contains `name: my-skill` in its frontmatter
- TC-105 (regression — existing frontmatter preserved): Given content `"---\nname: custom-name\ndescription: Custom desc\n---\n# Body"` → When `installSymlink("my-skill", content, agents, opts)` is called → Then the written SKILL.md contains `name: custom-name` (not `my-skill`)

**Dependencies**: T-003

---

### T-005: Integrate `ensureFrontmatter` into `canonical.ts`
**User Story**: US-002 | **Satisfies ACs**: AC-US2-01, AC-US2-02, AC-US2-03, AC-US2-04
**Status**: [x] Completed

**TDD Phase**: GREEN — make T-004 tests pass.

**File**: `repositories/anton-abyzov/vskill/src/installer/canonical.ts`

**Implementation Details**:
- Add import: `import { ensureFrontmatter } from "./frontmatter.js";`
- In `installSymlink`: add `content = ensureFrontmatter(content, skillName);` as the first statement in the function body (before any `writeFileSync` calls — all three write sites covered by one assignment)
- In `installCopy`: add `content = ensureFrontmatter(content, skillName);` as the first statement in the function body

**Important**: existing canonical.test.ts assertions compare written file content to raw input (e.g., `"# My Skill\nContent here"`). These assertions must be updated to expect frontmatter-prefixed content. Update them in this task.

**Test**:
Given T-004 tests are written and failing → When `canonical.ts` is modified → Then all T-004 tests plus all existing canonical.test.ts tests pass

**Dependencies**: T-004

---

### T-006: Write failing test for update.ts write site
**User Story**: US-002 | **Satisfies ACs**: AC-US2-05
**Status**: [x] Completed

**TDD Phase**: RED — add a test that asserts the update path produces frontmatter.

**File**: `repositories/anton-abyzov/vskill/src/commands/update.test.ts` (create or extend)

**Test**:

- TC-201 (AC-US2-05): Given `update.ts` writes a SKILL.md from a fetched result without frontmatter → When the update command runs for a skill with content `"# Updated Skill\nNew content."` → Then the written SKILL.md at each agent dir contains `name:` in its frontmatter block

**Note**: `update.ts` writes directly via `writeFileSync` bypassing `canonical.ts`. The test must target the write output, not the function boundary. Use a temp dir for agent skill dirs via the real filesystem (matching canonical.test.ts pattern).

**Dependencies**: T-003

---

### T-007: Integrate `ensureFrontmatter` into `update.ts`
**User Story**: US-002 | **Satisfies ACs**: AC-US2-05
**Status**: [x] Completed

**TDD Phase**: GREEN — make T-006 test pass.

**File**: `repositories/anton-abyzov/vskill/src/commands/update.ts`

**Implementation Details**:
- Add import: `import { ensureFrontmatter } from "../installer/frontmatter.js";`
- In the agent write loop (around line 162-178), apply `ensureFrontmatter` before the `writeFileSync` call:
  ```
  const processedContent = ensureFrontmatter(result.content, name);
  writeFileSync(join(skillDir, "SKILL.md"), processedContent, "utf-8");
  ```

**Test**:
Given T-006 test is written and failing → When `update.ts` is modified → Then T-006 test passes and existing update tests show no regressions

**Dependencies**: T-006

---

### T-008: Integrate `ensureFrontmatter` into `add.ts` write sites
**User Story**: US-002 | **Satisfies ACs**: AC-US2-01, AC-US2-04
**Status**: [x] Completed

**TDD Phase**: GREEN — apply `ensureFrontmatter` at the 4 direct write sites in `add.ts`.

**File**: `repositories/anton-abyzov/vskill/src/commands/add.ts`

**Implementation Details**:
- Add import: `import { ensureFrontmatter } from "../installer/frontmatter.js";`
- Lines ~507, ~521: repo plugin install paths — wrap `content` with `ensureFrontmatter(content, skillName)` before `writeFileSync`
- Lines ~1587, ~2241: direct install paths — wrap content variable with `ensureFrontmatter(content, skillName)` before `writeFileSync`
- The skill name variable at each site must be identified from context (may differ in naming: `name`, `skillName`, `skill.name`)

**Test**:
Given add.ts has 4 `writeFileSync(join(skillDir, "SKILL.md"), ...)` calls → When each is updated → Then running `npx vitest run` shows no regressions in existing add.ts tests and each written SKILL.md would include a frontmatter block when content lacks one

**Dependencies**: T-003

---

## Phase 3: Validation

### T-009: Run full test suite and verify coverage
**User Story**: US-001, US-002, US-003 | **Satisfies ACs**: AC-US1-01, AC-US1-02, AC-US1-03, AC-US1-04, AC-US1-05, AC-US2-01, AC-US2-02, AC-US2-03, AC-US2-04, AC-US2-05, AC-US3-01, AC-US3-02, AC-US3-03, AC-US3-04, AC-US3-05
**Status**: [x] Completed

**Implementation Details**:
- Run `npx vitest run` from `repositories/anton-abyzov/vskill/`
- Confirm zero regressions in all pre-existing tests
- Confirm all new tests (T-001, T-004, T-006) pass
- Check coverage target: `npx vitest run --coverage` — frontmatter.ts must reach 90%+ line coverage

**Test**:
Given all implementation tasks T-002 through T-008 are complete → When `npx vitest run` executes → Then exit code is 0, all new tests pass, and no existing tests regress

**Dependencies**: T-005, T-007, T-008
