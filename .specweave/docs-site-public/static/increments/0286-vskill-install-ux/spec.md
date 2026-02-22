---
increment: 0286-vskill-install-ux
title: vskill install UX improvements
type: feature
priority: P1
status: completed
created: 2026-02-21T00:00:00.000Z
structure: user-stories
test_mode: TDD
coverage_target: 80
---

# Feature: vskill install UX improvements

## Overview

The `vskill install` interactive wizard has several UX issues that create friction during multi-skill repo installations. This increment addresses five areas: misleading prompt text, arrow key escape sequence handling, excessive prompt steps, range/comma selection syntax, and skill description display.

## User Stories

### US-001: Fix Misleading Prompt Text (P1)
**Project**: vskill

**As a** CLI user installing skills from a multi-skill repo
**I want** clear, accurate prompt instructions
**So that** I understand what each input does without guessing

**Acceptance Criteria**:
- [x] **AC-US1-01**: Checkbox list prompt shows "Toggle: 1-N, ranges (1-3), comma-separated (1,3,5). a=all. Enter=done" instead of "space to toggle"
- [x] **AC-US1-02**: Scope prompt label reads "Scope" instead of "Installation scope:" (colon removed, more concise)
- [x] **AC-US1-03**: Method prompt label reads "Method" instead of "Installation method:" (colon removed, more concise)

---

### US-002: Handle Arrow Key Escape Sequences (P1)
**Project**: vskill

**As a** CLI user
**I want** arrow key presses to be silently ignored
**So that** pressing up/down/left/right does not produce garbage output or break the prompt

**Acceptance Criteria**:
- [x] **AC-US2-01**: ANSI escape sequences (ESC [ A/B/C/D for arrow keys) are detected and ignored in `promptCheckboxList`
- [x] **AC-US2-02**: ANSI escape sequences are detected and ignored in `promptChoice`
- [x] **AC-US2-03**: Other common escape sequences (home, end, delete) do not produce errors

---

### US-003: Reduce Prompts with Smart Defaults (P1)
**Project**: vskill

**As a** CLI user installing skills
**I want** fewer prompts during the wizard
**So that** the install flow is faster and less tedious

**Acceptance Criteria**:
- [x] **AC-US3-01**: Scope defaults to "Project" and method defaults to "Symlink" without prompting -- wizard skips steps 3 and 4
- [x] **AC-US3-02**: Only skills and agents are prompted (when applicable); scope and method use defaults
- [x] **AC-US3-03**: Summary shows defaults for scope and method before confirmation
- [x] **AC-US3-04**: New `--copy` flag forces copy method without prompt
- [x] **AC-US3-05**: Existing `--global` flag still forces global scope without prompt

---

### US-004: Range and Comma Toggle Syntax (P1)
**Project**: vskill

**As a** CLI user with many discovered skills
**I want** to toggle multiple items using ranges (1-3) and comma-separated lists (1,3,5)
**So that** I can efficiently select/deselect groups without toggling one by one

**Acceptance Criteria**:
- [x] **AC-US4-01**: Input "1-3" toggles items 1, 2, and 3
- [x] **AC-US4-02**: Input "1,3,5" toggles items 1, 3, and 5
- [x] **AC-US4-03**: Input "1-3,5,7-9" toggles items 1, 2, 3, 5, 7, 8, 9 (mixed syntax)
- [x] **AC-US4-04**: Invalid ranges (e.g., "5-2", "0", "999") are silently ignored (no crash)
- [x] **AC-US4-05**: Ranges work in both skill selection and agent selection checkbox lists

---

### US-005: Skill Descriptions in Wizard (P2)
**Project**: vskill

**As a** CLI user choosing skills from a multi-skill repo
**I want** to see a brief description of each skill
**So that** I can make informed decisions about which skills to install

**Acceptance Criteria**:
- [x] **AC-US5-01**: `DiscoveredSkill` interface includes optional `description` field
- [x] **AC-US5-02**: Discovery fetches the first non-empty, non-heading line from each SKILL.md as description (truncated to 80 chars)
- [x] **AC-US5-03**: Wizard checkbox list shows skill name with description as hint text (using existing `description` field on `CheckboxItem`)
- [x] **AC-US5-04**: Missing descriptions (fetch failure or empty content) gracefully fall back to no hint

## Functional Requirements

### FR-001: Escape sequence filtering
The `promptCheckboxList` and `promptChoice` methods must detect lines starting with ESC (0x1b) or containing ANSI CSI patterns (`\x1b[`) and skip them without re-rendering or error.

### FR-002: Range/comma parsing
A new `parseToggleInput(input: string, maxIndex: number): number[]` utility function parses user input and returns a deduplicated, sorted array of valid 0-based indices. Invalid tokens are silently dropped.

### FR-003: Description extraction
A new `extractDescription(content: string): string | undefined` helper extracts a description from SKILL.md content by finding the first non-empty line that is not a heading (`#`) and not a frontmatter delimiter (`---`).

## Success Criteria

- Interactive wizard reduced from 5 prompts to 3 (skills, agents, confirm) for default case
- Arrow keys no longer produce garbled output
- Users can select ranges of skills with "1-3" syntax
- Skill descriptions visible during selection

## Out of Scope

- Rewriting the prompt system to use raw mode / keypress events (would require a new TTY library)
- Adding descriptions to registry-based installs (registry already has descriptions)
- Changing non-interactive (`--yes`) behavior

## Dependencies

- `src/utils/prompts.ts` -- prompt system
- `src/commands/add.ts` -- install wizard flow
- `src/discovery/github-tree.ts` -- skill discovery
