# Tasks: Figma Connect Skill - Combined MCP + CLI

## Task Notation

- `[T###]`: Task ID
- `[P]`: Parallelizable
- `[ ]`: Not started
- `[x]`: Completed
- Model hints: haiku (simple), opus (default)

## Phase 1: Category Scaffold

### T-001: Create frontend plugin category
**User Story**: US-001 | **Satisfies ACs**: AC-US1-01 | **Status**: [x] completed
**Test Plan**:
- Given the vskill plugins directory
- When I create `plugins/frontend/.claude-plugin/plugin.json`
- Then it contains valid JSON with name "frontend", description, version, author, keywords
- And the file validates as proper plugin metadata

**Files**: `plugins/frontend/.claude-plugin/plugin.json`
**Dependencies**: None

## Phase 2: TDD RED - Evals First

### T-002: Create evals.json with 12 test cases
**User Story**: US-005 | **Satisfies ACs**: AC-US5-01, AC-US5-02 | **Status**: [x] completed
**Test Plan**:
- Given no SKILL.md exists yet
- When evals.json is created with 12 cases covering Setup, D2C, Publish, Tokens, Roundtrip, Errors
- Then each case has unique id, descriptive name, realistic prompt, expected_output, and 3-5 boolean assertions
- And running `npx vskill eval run frontend/figma-connect` shows 0/12 pass (all fail = RED)

**Files**: `plugins/frontend/skills/figma-connect/evals/evals.json`
**Dependencies**: T-001

### T-003: Create activation-prompts.json
**User Story**: US-005 | **Satisfies ACs**: AC-US5-03 | **Status**: [x] completed
**Test Plan**:
- Given the skill directory exists
- When activation-prompts.json is created with 20 prompts
- Then it contains exactly 10 should_activate and 10 should_not_activate prompts
- And prompts are natural language covering Figma URLs, code connect, tokens, and boundary cases

**Files**: `plugins/frontend/skills/figma-connect/evals/activation-prompts.json`
**Dependencies**: T-001

## Phase 3: TDD GREEN - SKILL.md (Iterative)

### T-004: Create SKILL.md with frontmatter + Mode 1 (Setup) + Mode 2 (Design-to-Code)
**User Story**: US-001, US-002, US-006 | **Satisfies ACs**: AC-US1-02, AC-US1-03, AC-US2-01, AC-US2-02, AC-US2-03, AC-US2-04, AC-US6-01, AC-US6-02, AC-US6-03 | **Status**: [x] completed
**Test Plan**:
- Given evals.json exists with cases 1 (setup), 2-3 (D2C), 9 (auth error), 11 (branch URL)
- When SKILL.md is created with frontmatter, Prerequisites, Framework Detection, Mode 1, Mode 2
- Then eval cases 1, 2, 3, 9, 11 should pass
- And SKILL.md has valid YAML frontmatter with name "figma-connect"
- And description contains activation trigger keywords

**Files**: `plugins/frontend/skills/figma-connect/SKILL.md`
**Dependencies**: T-002, T-003

### T-005: Add Mode 3 (CC Publish) + Mode 4 (Token Extraction) + Mode 5 (Roundtrip)
**User Story**: US-003, US-004 | **Satisfies ACs**: AC-US3-01, AC-US3-02, AC-US3-03, AC-US3-04, AC-US3-05, AC-US4-01, AC-US4-02, AC-US4-03 | **Status**: [x] completed
**Test Plan**:
- Given SKILL.md exists with Modes 1-2
- When Modes 3 (CC Publish), 4 (Token Extraction), 5 (Roundtrip) are added
- Then eval cases 4, 5, 6, 7, 8 should pass
- And SKILL.md documents the full publish lifecycle (suggest → generate → validate → publish → verify)

**Files**: `plugins/frontend/skills/figma-connect/SKILL.md`
**Dependencies**: T-004

### T-006: Add Decision Tree + Error Handling + Framework Detection table
**User Story**: US-006 | **Satisfies ACs**: AC-US6-01, AC-US6-04 | **Status**: [x] completed
**Test Plan**:
- Given SKILL.md exists with all 5 modes
- When Decision Tree, Error Handling table, and Framework Detection table are added
- Then eval cases 10 (CLI not installed), 12 (Vue detection) should pass
- And all 12 eval cases pass (GREEN complete)
- And SKILL.md is under 500 lines

**Files**: `plugins/frontend/skills/figma-connect/SKILL.md`
**Dependencies**: T-005

## Phase 4: Reference Files

### T-007: Create MCP tools reference
**User Story**: US-001 | **Satisfies ACs**: AC-US1-03 | **Status**: [x] completed
**Test Plan**:
- Given SKILL.md references the references/ directory
- When mcp-tools-reference.md is created
- Then it documents all 16 Figma MCP tools with parameters, return types, and usage notes
- And SKILL.md can point to it for detailed API info

**Files**: `plugins/frontend/skills/figma-connect/references/mcp-tools-reference.md`
**Dependencies**: T-004

### T-008: Create Code Connect CLI reference
**User Story**: US-001 | **Satisfies ACs**: AC-US1-03 | **Status**: [x] completed
**Test Plan**:
- Given SKILL.md references CLI commands
- When code-connect-cli-reference.md is created
- Then it documents all CLI commands (create, publish, parse, unpublish, migrate) with flags
- And includes figma.config.json schema and .figma.tsx template examples
- And includes CI/CD GitHub Actions workflow example

**Files**: `plugins/frontend/skills/figma-connect/references/code-connect-cli-reference.md`
**Dependencies**: T-004

### T-009: Create token format mappings reference
**User Story**: US-004 | **Satisfies ACs**: AC-US4-02 | **Status**: [x] completed
**Test Plan**:
- Given Mode 4 (Token Extraction) references format mappings
- When token-format-mappings.md is created
- Then it maps Figma variable types to CSS custom properties, Tailwind config, and Style Dictionary formats
- And includes examples for each format

**Files**: `plugins/frontend/skills/figma-connect/references/token-format-mappings.md`
**Dependencies**: T-005

## Phase 5: TDD REFACTOR - Benchmark

### T-010: Run benchmark and iterate
**User Story**: US-005 | **Satisfies ACs**: AC-US5-04 | **Status**: [x] completed
**Test Plan**:
- Given all files are created (SKILL.md + evals + references)
- When `npx vskill eval run frontend/figma-connect` is executed
- Then benchmark achieves 83%+ pass rate (10/12 evals)
- And activation testing shows precision 100%, recall 90%+
- And any failing evals are analyzed and SKILL.md is refined

**Files**: All files (iterative refinement)
**Dependencies**: T-006, T-007, T-008, T-009
