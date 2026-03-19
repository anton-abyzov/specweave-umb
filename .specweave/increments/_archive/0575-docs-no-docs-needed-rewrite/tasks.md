# Tasks: Rework no-docs-needed page to lead with SpecWeave value

## Task Notation

- `[T###]`: Task ID
- `[P]`: Parallelizable
- `[ ]`: Not started
- `[x]`: Completed

## Tasks

### T-001: Rewrite no-docs-needed.md
**User Story**: US-001, US-002, US-003, US-004, US-005 | **Satisfies ACs**: AC-US1-01, AC-US1-02, AC-US1-03, AC-US1-04, AC-US2-01, AC-US2-02, AC-US2-03, AC-US3-01, AC-US3-02, AC-US3-03, AC-US4-01, AC-US4-02, AC-US4-03, AC-US5-01, AC-US5-02, AC-US5-03 | **Status**: [ ] Not Started

**Description**: Full content rewrite of `repositories/anton-abyzov/specweave/docs-site/docs/overview/no-docs-needed.md` following the structure in plan.md: new title "Start Building in Minutes", capabilities table (SpecWeave features not Claude Code concepts), before/after comparison (vibe coding vs spec-driven), 3-command workflow, and "Go Deeper" section. Preserve `sidebar_position: 3`. Claude Code mentions capped at 3, never in section titles.

**Test Plan**:
- **TC-001**: Title is "Start Building in Minutes"
  - Given the rewritten file
  - When frontmatter title is read
  - Then it equals "Start Building in Minutes"
- **TC-002**: Claude Code is not the organizing principle
  - Given the rewritten file
  - When section headings are inspected
  - Then no heading references Claude Code
- **TC-003**: Capabilities table is SpecWeave-centric
  - Given the capabilities table
  - When column headers are read
  - Then they describe SpecWeave capabilities, not Claude Code concepts
- **TC-004**: Before/After uses vibe coding framing
  - Given the before/after section
  - When "Without SpecWeave" content is read
  - Then it describes vibe coding problems (lost context, no specs, manual testing)
- **TC-005**: Tool-agnostic positioning present
  - Given the full page
  - When scanned for AI tool references
  - Then Cursor, Copilot, or equivalent tools are mentioned alongside Claude Code
- **TC-006**: sidebar_position preserved
  - Given the frontmatter
  - When sidebar_position is read
  - Then it equals 3

**Dependencies**: None
**Status**: [x] Completed

---

### T-002: Update sidebar label in sidebars.ts
**User Story**: US-005 | **Satisfies ACs**: AC-US5-01 | **Status**: [x] Completed

**Description**: In `repositories/anton-abyzov/specweave/docs-site/sidebars.ts` line ~21, update the sidebar label from `"You Don't Need Claude Code Docs"` to `"Zero Learning Curve"`.

**Test Plan**:
- **TC-001**: Sidebar label updated
  - Given sidebars.ts
  - When the label for the no-docs-needed entry is read
  - Then it reads "Zero Learning Curve"

**Dependencies**: T-001
**Status**: [x] Completed

---

### T-003: Update inbound link teaser text in why-specweave.md
**User Story**: US-003, US-004 | **Satisfies ACs**: AC-US3-03, AC-US4-01 | **Status**: [x] Completed

**Description**: In `repositories/anton-abyzov/specweave/docs-site/docs/overview/why-specweave.md` line ~148, update the teaser text from the Claude Code abstraction framing to: `"SpecWeave's skills encode expertise so you don't need to learn it yourself. Describe your feature, skills handle the rest."` Link target `./no-docs-needed` remains unchanged.

**Test Plan**:
- **TC-001**: Teaser text no longer references Claude Code abstraction
  - Given why-specweave.md
  - When the link teaser around line 148 is read
  - Then it does not contain "abstracts Claude Code" or similar wrapper framing

**Dependencies**: T-001
**Status**: [x] Completed
