# Tasks: Docs Phase 2: UX, Dual Activation, Plugin Accuracy, Team-Lead Section

## Task Notation

- `[T###]`: Task ID
- `[P]`: Parallelizable
- `[ ]`: Not started
- `[x]`: Completed

## Phase 1: Plugin Accuracy

### T-001: Fix plugin counts in skills/fundamentals.md
**User Story**: US-002 | **Satisfies ACs**: AC-US2-01 | **Status**: [x] completed
**Description**: Correct the claim of "22 plugins with 126 skills" to reflect reality: 1 unified sw plugin with 44 skills in specweave, 5 marketplace plugins in vskill.
**Test Plan**: Verify content matches actual marketplace.json files in both repos.
**Dependencies**: None

### T-002: Fix reference/skills.md plugin references
**User Story**: US-002 | **Satisfies ACs**: AC-US2-02, AC-US2-03 | **Status**: [x] completed
**Description**: Remove references to non-existent separate plugins (backend, frontend, testing, infra, k8s, kafka, confluent, payments, cost, docs) from skill table Plugin columns. Note these as community/domain skills. Fix the "Installing Domain Plugins" section to list only actual vskill marketplace plugins.
**Test Plan**: Verify no non-existent plugin names remain in install commands.
**Dependencies**: None

### T-003: Fix vskill install commands in reference/skills.md
**User Story**: US-003 | **Satisfies ACs**: AC-US3-01, AC-US3-02, AC-US3-03 | **Status**: [x] completed
**Description**: Replace all `vskill add specweave --plugin X` with correct `npx vskill install --repo anton-abyzov/specweave --plugin sw`. Remove install commands for non-existent separate plugins (sw-github, sw-jira, sw-ado, sw-diagrams, sw-release).
**Test Plan**: Every vskill command in the file uses valid syntax and references existing plugins.
**Dependencies**: None

## Phase 2: Dual Activation

### T-004: Add dual activation to reference/skills.md core skill sections
**User Story**: US-001 | **Satisfies ACs**: AC-US1-01 | **Status**: [x] completed
**Description**: For each core skill section (increment, do, auto, done, brainstorm, team-lead, grill, code-reviewer), add a natural language alternative alongside the slash command example.
**Test Plan**: Each listed skill has both invocation methods shown.
**Dependencies**: T-002 (skills page should be accurate first)

### T-005: Add dual activation to workflows/overview.md
**User Story**: US-001 | **Satisfies ACs**: AC-US1-02 | **Status**: [x] completed
**Description**: Add natural language alternatives for each workflow phase command in the quick reference table and phase descriptions.
**Test Plan**: Quick reference table has a "Natural Language" column.
**Dependencies**: None

### T-006: Add dual activation to commands/overview.md
**User Story**: US-001 | **Satisfies ACs**: AC-US1-03 | **Status**: [x] completed
**Description**: Add natural language alternatives alongside slash commands in the commands overview page.
**Test Plan**: Commands table shows natural language equivalents.
**Dependencies**: None

## Phase 3: Team-Lead & Navigation

### T-007: Add team-lead entry to sidebar
**User Story**: US-004, US-005 | **Satisfies ACs**: AC-US4-01, AC-US5-01 | **Status**: [x] completed
**Description**: Add a "Team-Lead Orchestration" entry to the Agent Teams sidebar category in sidebars.ts, linking to the existing agent-teams-and-swarms page with an anchor to the team-lead section.
**Test Plan**: Sidebar shows Team-Lead entry under Agent Teams.
**Dependencies**: None

### T-008: Add dual activation to agent-teams-and-swarms.md
**User Story**: US-004 | **Satisfies ACs**: AC-US4-02 | **Status**: [x] completed
**Description**: Add dual activation examples (slash + natural language) for team-lead operations in the agent-teams-and-swarms page.
**Test Plan**: Team-lead section shows both invocation methods.
**Dependencies**: None

## Phase 4: Mermaid Fixes

### T-009: Fix emoji in Mermaid diagrams
**User Story**: US-006 | **Satisfies ACs**: AC-US6-01 | **Status**: [x] completed
**Description**: Replace emoji characters in Mermaid node labels in workflows/overview.md with text-only labels for reliable cross-browser rendering.
**Test Plan**: No emoji characters in any Mermaid node label text.
**Dependencies**: None

## Phase 5: Verification

### T-010: Verify all changes and update spec
**User Story**: All | **Satisfies ACs**: All | **Status**: [x] completed
**Description**: Cross-check all modifications, mark completed ACs in spec.md, update metadata.json timestamp.
**Test Plan**: All ACs marked [x], metadata updated.
**Dependencies**: T-001 through T-009
