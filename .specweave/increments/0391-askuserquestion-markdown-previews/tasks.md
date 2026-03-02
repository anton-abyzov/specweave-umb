# Tasks: AskUserQuestion Markdown Previews for SpecWeave Skills

## Task Notation

- `[T###]`: Task ID
- `[P]`: Parallelizable
- `[ ]`: Not started
- `[x]`: Completed
- Model hints: haiku (simple), opus (default)

## Phase 1: ASCII Diagram Utility (TDD)

### US-001: ASCII Diagram Utility Functions

#### T-001: TDD Red — Write failing tests for renderBoxDiagram

**User Story**: US-001 | **Satisfies ACs**: AC-US1-01, AC-US1-05 | **Status**: [x] Completed

**Description**: Write comprehensive failing tests for the `renderBoxDiagram` function before any implementation.

**Implementation Details**:
- Create `tests/unit/ascii-diagrams.test.ts`
- Import from `../../src/utils/ascii-diagrams.js` (ESM .js extension)
- Test cases for: single node, two connected nodes, multiple connections, labels, max width truncation, empty input

**Test Plan**:
- **File**: `tests/unit/ascii-diagrams.test.ts`
- **Tests**:
  - **TC-001**: renderBoxDiagram with single node
    - Given a single BoxNode `{id: "a", label: "Service A"}`
    - When `renderBoxDiagram([node], [])` is called
    - Then output contains a box with "Service A" inside Unicode borders
  - **TC-002**: renderBoxDiagram with two connected nodes
    - Given nodes A and B with connection A→B
    - When `renderBoxDiagram(nodes, connections)` is called
    - Then output shows two boxes with an arrow between them
  - **TC-003**: renderBoxDiagram with sublabels
    - Given a node with `sublabel: "(Workers)"`
    - When rendered
    - Then box contains both label and sublabel on separate lines
  - **TC-004**: renderBoxDiagram with empty input
    - Given empty arrays
    - When `renderBoxDiagram([], [])` is called
    - Then returns empty string
  - **TC-005**: renderBoxDiagram respects 80-char width
    - Given nodes with long labels
    - When rendered
    - Then no line exceeds 80 characters

**Dependencies**: None

---

#### T-002: TDD Red — Write failing tests for renderDAG

**User Story**: US-001 | **Satisfies ACs**: AC-US1-02, AC-US1-05 | **Status**: [x] Completed

**Description**: Write failing tests for the `renderDAG` function.

**Implementation Details**:
- Add to `tests/unit/ascii-diagrams.test.ts`
- Test cases for: linear chain, parallel tasks, diamond dependency, single task, empty input

**Test Plan**:
- **File**: `tests/unit/ascii-diagrams.test.ts`
- **Tests**:
  - **TC-006**: renderDAG with linear chain
    - Given tasks T-001→T-002→T-003
    - When `renderDAG(tasks, deps)` is called
    - Then output shows sequential flow with arrows
  - **TC-007**: renderDAG with parallel tasks
    - Given T-001→T-003, T-002→T-003 (T-001 and T-002 parallel)
    - When rendered
    - Then output shows two lanes merging into T-003
  - **TC-008**: renderDAG with single task
    - Given one task, no deps
    - When rendered
    - Then shows single task node
  - **TC-009**: renderDAG with empty input
    - Given empty arrays
    - When `renderDAG([], [])` is called
    - Then returns empty string
  - **TC-010**: renderDAG annotates critical path
    - Given a DAG with known critical path
    - When rendered
    - Then output includes "Critical path:" annotation

**Dependencies**: None

---

#### T-003: TDD Red — Write failing tests for renderTable

**User Story**: US-001 | **Satisfies ACs**: AC-US1-03, AC-US1-05 | **Status**: [x] Completed

**Description**: Write failing tests for the `renderTable` function.

**Implementation Details**:
- Add to `tests/unit/ascii-diagrams.test.ts`
- Test cases for: basic table, header separator, column alignment, truncation, empty input

**Test Plan**:
- **File**: `tests/unit/ascii-diagrams.test.ts`
- **Tests**:
  - **TC-011**: renderTable with headers and rows
    - Given headers ["Column", "Type", "Notes"] and 2 rows
    - When `renderTable(headers, rows)` is called
    - Then output has aligned columns with consistent spacing
  - **TC-012**: renderTable with header separator
    - Given `options: { headerSeparator: true }`
    - When rendered
    - Then a `─` separator line appears after the header row
  - **TC-013**: renderTable truncates long values
    - Given a cell value exceeding maxColWidth
    - When rendered with `maxColWidth: 20`
    - Then cell is truncated with "…"
  - **TC-014**: renderTable with empty input
    - Given empty headers and rows
    - When `renderTable([], [])` is called
    - Then returns empty string
  - **TC-015**: renderTable respects 80-char total width
    - Given many columns with long content
    - When rendered
    - Then no line exceeds 80 characters

**Dependencies**: None

---

#### T-004: TDD Red — Write failing tests for renderTree

**User Story**: US-001 | **Satisfies ACs**: AC-US1-04, AC-US1-05 | **Status**: [x] Completed

**Description**: Write failing tests for the `renderTree` function.

**Implementation Details**:
- Add to `tests/unit/ascii-diagrams.test.ts`
- Test cases for: flat list, nested tree, deep nesting, single item, empty input

**Test Plan**:
- **File**: `tests/unit/ascii-diagrams.test.ts`
- **Tests**:
  - **TC-016**: renderTree with flat list
    - Given items without children
    - When `renderTree(items)` is called
    - Then output uses `├──` and `└──` branch chars
  - **TC-017**: renderTree with nested items
    - Given a root with 2 levels of children
    - When rendered
    - Then output shows proper indentation with `│   ` for continuation
  - **TC-018**: renderTree with deep nesting
    - Given 4 levels of nesting
    - When rendered
    - Then each level is indented correctly
  - **TC-019**: renderTree with single item
    - Given one item, no children
    - When rendered
    - Then shows just the item name
  - **TC-020**: renderTree with empty input
    - Given empty array
    - When `renderTree([])` is called
    - Then returns empty string

**Dependencies**: None

---

#### T-005: TDD Green — Implement renderBoxDiagram

**User Story**: US-001 | **Satisfies ACs**: AC-US1-01 | **Status**: [x] Completed

**Description**: Implement `renderBoxDiagram` in `src/utils/ascii-diagrams.ts` to make TC-001 through TC-005 pass.

**Implementation Details**:
- Create `src/utils/ascii-diagrams.ts` with TypeScript interfaces and `renderBoxDiagram` export
- Use Unicode box-drawing characters: `─│┌┐└┘`
- Horizontal layout: boxes side by side with `──►` arrows
- Max width 80 chars, truncate box labels with `…` if needed

**Test Plan**:
- Run `npx vitest run tests/unit/ascii-diagrams.test.ts` — TC-001..TC-005 pass

**Dependencies**: T-001

---

#### T-006: TDD Green — Implement renderDAG

**User Story**: US-001 | **Satisfies ACs**: AC-US1-02 | **Status**: [x] Completed

**Description**: Implement `renderDAG` to make TC-006 through TC-010 pass.

**Implementation Details**:
- Topological sort to determine task ordering
- Assign lane numbers based on depth (parallel tasks share same depth)
- Render with `──►` horizontal arrows and `──┐`/`──┘` merge points
- Append "Critical path:" annotation with longest path

**Test Plan**:
- Run `npx vitest run tests/unit/ascii-diagrams.test.ts` — TC-006..TC-010 pass

**Dependencies**: T-002

---

#### T-007: TDD Green — Implement renderTable

**User Story**: US-001 | **Satisfies ACs**: AC-US1-03 | **Status**: [x] Completed

**Description**: Implement `renderTable` to make TC-011 through TC-015 pass.

**Implementation Details**:
- Calculate max width per column from all rows + header
- If total width > 80, proportionally shrink widest columns
- Pad cells with spaces for alignment
- Optional `─` separator after header row
- Truncate cells at `maxColWidth` with `…`

**Test Plan**:
- Run `npx vitest run tests/unit/ascii-diagrams.test.ts` — TC-011..TC-015 pass

**Dependencies**: T-003

---

#### T-008: TDD Green — Implement renderTree

**User Story**: US-001 | **Satisfies ACs**: AC-US1-04 | **Status**: [x] Completed

**Description**: Implement `renderTree` to make TC-016 through TC-020 pass.

**Implementation Details**:
- Recursive rendering with prefix tracking
- `├──` for non-last siblings, `└──` for last sibling
- `│   ` continuation prefix for nested children under non-last siblings
- `    ` (spaces) continuation prefix under last siblings

**Test Plan**:
- Run `npx vitest run tests/unit/ascii-diagrams.test.ts` — TC-016..TC-020 pass

**Dependencies**: T-004

---

## Phase 2: SKILL.md Integration

### US-002: Architect Skill Markdown Previews

#### T-009: Add markdown preview guidelines to architect SKILL.md

**User Story**: US-002 | **Satisfies ACs**: AC-US2-01, AC-US2-02, AC-US2-03, AC-US2-04 | **Status**: [x] Completed

**Description**: Add a "Markdown Preview Guidelines" section to the architect SKILL.md with instructions and examples for using `AskUserQuestion` with `markdown` previews.

**Implementation Details**:
- Add section after "Design Approach" in `plugins/specweave/skills/architect/SKILL.md`
- Include trigger condition: "When presenting 2+ architectural approaches"
- Include box diagram example for service architecture decisions
- Include ASCII table example for schema/DB design decisions
- Include complete `AskUserQuestion` call format with all required fields

**Test Plan**:
- **File**: Manual verification
- **Tests**:
  - **TC-021**: SKILL.md contains "Markdown Preview Guidelines" section
    - Given the updated architect SKILL.md
    - When searching for "Markdown Preview"
    - Then the section exists with at least 2 complete AskUserQuestion examples
  - **TC-022**: Examples include box diagrams
    - Given the examples in the section
    - When reviewing markdown field content
    - Then at least one example contains Unicode box-drawing characters
  - **TC-023**: Examples include ASCII tables
    - Given the examples
    - When reviewing
    - Then at least one example shows column-aligned table format

**Dependencies**: T-005, T-007

---

### US-003: Plan Skill Markdown Previews

#### T-010: Add markdown preview guidelines to plan SKILL.md

**User Story**: US-003 | **Satisfies ACs**: AC-US3-01, AC-US3-02, AC-US3-03 | **Status**: [x] Completed

**Description**: Add markdown preview section to plan SKILL.md for DAG previews.

**Implementation Details**:
- Add section in `plugins/specweave/skills/plan/SKILL.md`
- Trigger: "When execution strategy has 2+ viable approaches"
- DAG example showing parallel lanes and critical path
- Complete AskUserQuestion format

**Test Plan**:
- **File**: Manual verification
- **Tests**:
  - **TC-024**: plan SKILL.md contains DAG preview example
    - Given the updated plan SKILL.md
    - When searching for "Markdown Preview"
    - Then section contains at least 1 AskUserQuestion example with DAG in markdown field
  - **TC-025**: DAG example shows task dependencies
    - Given the DAG preview example
    - When reviewing markdown content
    - Then it shows task IDs, arrows, parallel lanes, and "Critical path:" annotation

**Dependencies**: T-006

---

### US-004: Increment Skill Markdown Previews

#### T-011: Add markdown preview guidelines to increment SKILL.md

**User Story**: US-004 | **Satisfies ACs**: AC-US4-01, AC-US4-02, AC-US4-03 | **Status**: [x] Completed

**Description**: Add markdown preview section to increment SKILL.md for tree and table previews.

**Implementation Details**:
- Add section in `plugins/specweave/skills/increment/SKILL.md`
- Trigger: "When scope/structure decisions have 2+ options"
- Tree example for folder structure proposals
- Table example for AC coverage comparison
- Complete AskUserQuestion format

**Test Plan**:
- **File**: Manual verification
- **Tests**:
  - **TC-026**: increment SKILL.md contains tree preview example
    - Given the updated increment SKILL.md
    - When searching for "Markdown Preview"
    - Then section contains tree diagram with `├──` / `└──` characters
  - **TC-027**: increment SKILL.md contains table preview example
    - Given the examples
    - When reviewing
    - Then at least one example shows AC coverage as aligned table

**Dependencies**: T-008

---

## Phase 3: Verification

#### T-012: Run full test suite and verify coverage

**User Story**: US-001 | **Satisfies ACs**: AC-US1-01..05 | **Status**: [x] Completed

**Description**: Run all tests, verify 95%+ coverage on ascii-diagrams.ts, fix any regressions.

**Implementation Details**:
- `cd repositories/anton-abyzov/specweave && npx vitest run tests/unit/ascii-diagrams.test.ts --coverage`
- Verify all 20 test cases pass
- Verify coverage >= 95% for `src/utils/ascii-diagrams.ts`

**Test Plan**:
- All TC-001..TC-020 green
- Coverage report shows >= 95% statements, branches, functions, lines

**Dependencies**: T-005, T-006, T-007, T-008
