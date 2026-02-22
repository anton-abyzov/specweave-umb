# Tasks: vskill install UX improvements

## Task Notation

- `[T###]`: Task ID
- `[P]`: Parallelizable
- `[ ]`: Not started
- `[x]`: Completed
- Model hints: haiku (simple), opus (default)

## Phase 1: Prompt System Enhancements

### US-002: Handle Arrow Key Escape Sequences (P1)

#### T-001: Add escape sequence filtering to promptCheckboxList
**User Story**: US-002 | **Satisfies ACs**: AC-US2-01, AC-US2-03 | **Status**: [x] completed
**File**: `repositories/anton-abyzov/vskill/src/utils/prompts.ts`

**Description**: Add an `isEscapeSequence(line: string): boolean` helper that detects ANSI escape codes (lines starting with `\x1b[` or containing only escape sequences). Integrate it into the `promptCheckboxList` while-loop to skip such lines silently.

**Implementation Details**:
- Add `isEscapeSequence()` function that checks for `\x1b[` prefix and common CSI patterns
- In `promptCheckboxList`, after `const line = await ask("> ")`, add early continue if `isEscapeSequence(line)`
- Cover arrow keys (A/B/C/D), home, end, delete sequences

**Test Plan**:
- **File**: `repositories/anton-abyzov/vskill/src/utils/prompts.test.ts`
- **Tests**:
  - **TC-001**: isEscapeSequence returns true for arrow key sequences
    - Given input "\x1b[A" (up arrow)
    - When isEscapeSequence is called
    - Then returns true
  - **TC-002**: isEscapeSequence returns false for normal input
    - Given input "1"
    - When isEscapeSequence is called
    - Then returns false
  - **TC-003**: promptCheckboxList ignores arrow key input
    - Given a checkbox list with 3 items
    - When user sends "\x1b[A" then "1" then ""
    - Then item 1 is toggled and arrow key is ignored

**Dependencies**: None

---

#### T-002: Add escape sequence filtering to promptChoice
**User Story**: US-002 | **Satisfies ACs**: AC-US2-02, AC-US2-03 | **Status**: [x] completed
**File**: `repositories/anton-abyzov/vskill/src/utils/prompts.ts`

**Description**: Integrate the same `isEscapeSequence()` check into the `promptChoice` while-loop to skip arrow key inputs.

**Implementation Details**:
- In `promptChoice`, after `const line = await ask("> ")`, add early continue if `isEscapeSequence(line)`

**Test Plan**:
- **File**: `repositories/anton-abyzov/vskill/src/utils/prompts.test.ts`
- **Tests**:
  - **TC-004**: promptChoice ignores arrow key input
    - Given a choice prompt with 2 options
    - When user sends "\x1b[B" then "1"
    - Then returns index 0 (arrow key ignored, "1" accepted)

**Dependencies**: T-001 (reuses isEscapeSequence)

---

### US-004: Range and Comma Toggle Syntax (P1)

#### T-003: Implement parseToggleInput utility
**User Story**: US-004 | **Satisfies ACs**: AC-US4-01, AC-US4-02, AC-US4-03, AC-US4-04 | **Status**: [x] completed
**File**: `repositories/anton-abyzov/vskill/src/utils/prompts.ts`

**Description**: Add `parseToggleInput(input: string, maxIndex: number): number[]` that parses range/comma syntax and returns valid 0-based indices.

**Implementation Details**:
- Split input on commas
- For each token, check if it contains `-` (range) or is a plain number
- For ranges like "1-3", generate all numbers from 1 to 3
- Convert 1-based user input to 0-based indices
- Filter out invalid indices (< 0 or >= maxIndex)
- Return deduplicated, sorted array

**Test Plan**:
- **File**: `repositories/anton-abyzov/vskill/src/utils/prompts.test.ts`
- **Tests**:
  - **TC-005**: Single number "2" returns [1]
    - Given input "2" and maxIndex 5
    - When parseToggleInput is called
    - Then returns [1]
  - **TC-006**: Range "1-3" returns [0, 1, 2]
    - Given input "1-3" and maxIndex 5
    - When parseToggleInput is called
    - Then returns [0, 1, 2]
  - **TC-007**: Comma-separated "1,3,5" returns [0, 2, 4]
    - Given input "1,3,5" and maxIndex 5
    - When parseToggleInput is called
    - Then returns [0, 2, 4]
  - **TC-008**: Mixed "1-3,5,7-9" returns [0, 1, 2, 4, 6, 7, 8]
    - Given input "1-3,5,7-9" and maxIndex 10
    - When parseToggleInput is called
    - Then returns [0, 1, 2, 4, 6, 7, 8]
  - **TC-009**: Invalid range "5-2" returns empty
    - Given input "5-2" and maxIndex 5
    - When parseToggleInput is called
    - Then returns []
  - **TC-010**: Out of bounds "0,999" returns empty
    - Given input "0,999" and maxIndex 5
    - When parseToggleInput is called
    - Then returns []
  - **TC-011**: Deduplication "1,1,2" returns [0, 1]
    - Given input "1,1,2" and maxIndex 5
    - When parseToggleInput is called
    - Then returns [0, 1]

**Dependencies**: None

---

#### T-004: Integrate parseToggleInput into promptCheckboxList
**User Story**: US-004 | **Satisfies ACs**: AC-US4-01, AC-US4-02, AC-US4-03, AC-US4-05 | **Status**: [x] completed
**File**: `repositories/anton-abyzov/vskill/src/utils/prompts.ts`

**Description**: Replace the single-number parsing in `promptCheckboxList` with `parseToggleInput` to support ranges and commas.

**Implementation Details**:
- Replace the existing `parseInt(line, 10)` block with a call to `parseToggleInput(line, items.length)`
- For each returned index, toggle `checked[idx]`
- Re-render checkbox after toggling

**Test Plan**:
- **File**: `repositories/anton-abyzov/vskill/src/utils/prompts.test.ts`
- **Tests**:
  - **TC-012**: Checkbox list toggles range input
    - Given 5 items all unchecked
    - When user enters "1-3" then ""
    - Then items 0, 1, 2 are selected (returned indices [0, 1, 2])

**Dependencies**: T-003

---

## Phase 2: Wizard Simplification

### US-001: Fix Misleading Prompt Text (P1)

#### T-005: Update checkbox list instructions text
**User Story**: US-001 | **Satisfies ACs**: AC-US1-01 | **Status**: [x] completed
**File**: `repositories/anton-abyzov/vskill/src/utils/prompts.ts`

**Description**: Update the `renderCheckbox` function to show range/comma syntax instructions instead of "space to toggle".

**Implementation Details**:
- After rendering items and "a) Toggle all", add a line:
  `writeLine(dim("  Toggle: number, range (1-3), list (1,3,5). a=all. Enter=done"));`
- This replaces the title text that previously said "space to toggle"

**Test Plan**:
- **File**: `repositories/anton-abyzov/vskill/src/utils/prompts.test.ts`
- **Tests**:
  - **TC-013**: Render output includes range syntax instructions
    - Given a checkbox list with options
    - When renderCheckbox is called
    - Then output contains "range" and "Enter=done"

**Dependencies**: T-003, T-004

---

#### T-006: Fix scope and method prompt labels
**User Story**: US-001 | **Satisfies ACs**: AC-US1-02, AC-US1-03 | **Status**: [x] completed
**File**: `repositories/anton-abyzov/vskill/src/commands/add.ts`

**Description**: This task is absorbed into T-007 since the scope and method prompts are being removed. The labels will only appear if a future `--interactive` flag is added. No separate work needed -- mark as N/A and close when T-007 completes.

**Dependencies**: T-007

---

### US-003: Reduce Prompts with Smart Defaults (P1)

#### T-007: Remove scope and method prompts, use defaults
**User Story**: US-003 | **Satisfies ACs**: AC-US3-01, AC-US3-02, AC-US3-03 | **Status**: [x] completed
**File**: `repositories/anton-abyzov/vskill/src/commands/add.ts`

**Description**: Remove prompt steps 3 (scope) and 4 (method) from the interactive wizard. Default to project scope and symlink method. Update the summary to show these defaults.

**Implementation Details**:
- Remove the `prompter3` (scope selection) block entirely
- Remove the `prompter4` (method selection) block entirely
- `method` defaults to `"symlink"` (already the case), `useGlobal` defaults to `false`
- Summary still displays scope and method (as defaults) before confirmation
- Wizard flow becomes: skills -> agents (if multiple) -> confirm

**Test Plan**:
- **File**: `repositories/anton-abyzov/vskill/src/commands/add-wizard.test.ts`
- **Tests**:
  - **TC-014**: Wizard shows only 2 prompts (skills + confirm) for single-agent
    - Given 2 discovered skills and 1 agent
    - When interactive wizard runs
    - Then promptChoice is not called (no scope/method prompts)
    - And promptCheckboxList is called once (skills)
    - And promptConfirm is called once
  - **TC-015**: Wizard shows 3 prompts (skills + agents + confirm) for multi-agent
    - Given 2 skills and 2 agents
    - When interactive wizard runs
    - Then promptCheckboxList is called twice (skills + agents)
    - And promptConfirm is called once
    - And promptChoice is not called

**Dependencies**: None

---

#### T-008: Add --copy CLI flag
**User Story**: US-003 | **Satisfies ACs**: AC-US3-04 | **Status**: [x] completed
**File**: `repositories/anton-abyzov/vskill/src/index.ts`, `repositories/anton-abyzov/vskill/src/commands/add.ts`

**Description**: Add a `--copy` flag to the `install` command that forces copy method instead of default symlink.

**Implementation Details**:
- In `index.ts`, add `.option("--copy", "Install copies instead of symlinks")` to the install command
- In `add.ts`, add `copy?: boolean` to `AddOptions`
- In the wizard logic, if `opts.copy` is true, set `method = "copy"`
- The `--copy` and `--global` flags can coexist

**Test Plan**:
- **File**: `repositories/anton-abyzov/vskill/src/commands/add-wizard.test.ts`
- **Tests**:
  - **TC-016**: --copy flag sets method to copy
    - Given --copy flag is provided
    - When wizard completes
    - Then method is "copy" (not "symlink")

**Dependencies**: T-007

---

## Phase 3: Skill Descriptions

### US-005: Skill Descriptions in Wizard (P2)

#### T-009: Add description field to DiscoveredSkill and extract from SKILL.md
**User Story**: US-005 | **Satisfies ACs**: AC-US5-01, AC-US5-02, AC-US5-04 | **Status**: [x] completed
**File**: `repositories/anton-abyzov/vskill/src/discovery/github-tree.ts`

**Description**: Add optional `description` field to `DiscoveredSkill`. Add `extractDescription(content: string): string | undefined` helper. After discovering skills, fetch content for each and extract descriptions in parallel.

**Implementation Details**:
- Add `description?: string` to `DiscoveredSkill` interface
- Add `extractDescription()`: skip lines that are empty, start with `#`, or are `---`. Take first remaining line, truncate to 80 chars
- After building the skills array, use `Promise.allSettled` to fetch each `rawUrl` with a 3s timeout via `AbortController`
- For each successful fetch, extract description and set on the skill object
- Failed fetches leave description as undefined

**Test Plan**:
- **File**: `repositories/anton-abyzov/vskill/src/discovery/github-tree.test.ts`
- **Tests**:
  - **TC-017**: extractDescription returns first content line
    - Given "# Title\n\nThis skill does X\n\nMore content"
    - When extractDescription is called
    - Then returns "This skill does X"
  - **TC-018**: extractDescription truncates at 80 chars
    - Given content with a 120-char first line
    - When extractDescription is called
    - Then returns string of length 80 ending with "..."
  - **TC-019**: extractDescription skips frontmatter
    - Given "---\ntitle: foo\n---\n# Title\nDescription here"
    - When extractDescription is called
    - Then returns "Description here"
  - **TC-020**: extractDescription returns undefined for heading-only content
    - Given "# Title\n## Section\n### Subsection"
    - When extractDescription is called
    - Then returns undefined
  - **TC-021**: discoverSkills populates descriptions from fetched content
    - Given a repo with 2 SKILL.md files
    - When discoverSkills is called and fetch returns content
    - Then each DiscoveredSkill has a description field

**Dependencies**: None

---

#### T-010: Pass descriptions to wizard checkbox items
**User Story**: US-005 | **Satisfies ACs**: AC-US5-03 | **Status**: [x] completed
**File**: `repositories/anton-abyzov/vskill/src/commands/add.ts`

**Description**: When building checkbox items for skill selection, pass `skill.description` as the `description` field on `CheckboxItem`.

**Implementation Details**:
- In the wizard skill selection step, change:
  `discovered.map((s) => ({ label: s.name, checked: true }))`
  to:
  `discovered.map((s) => ({ label: s.name, description: s.description, checked: true }))`
- The existing `renderCheckbox` in `prompts.ts` already renders `description` as ` - ${desc}`

**Test Plan**:
- **File**: `repositories/anton-abyzov/vskill/src/commands/add-wizard.test.ts`
- **Tests**:
  - **TC-022**: Skill descriptions passed to checkbox items
    - Given discovered skills with descriptions
    - When promptCheckboxList is called
    - Then items include description field

**Dependencies**: T-009

---

## Phase 4: Verification

#### T-011: Run full test suite and verify all ACs
**User Story**: All | **Satisfies ACs**: All | **Status**: [x] completed

**Description**: Run `npm test` in the vskill repo to verify all existing tests pass and new tests pass.

**Test Plan**:
- Run `cd repositories/anton-abyzov/vskill && npm test`
- Verify 0 test failures
- Verify coverage >= 80%

**Dependencies**: T-001 through T-010
