# Tasks: Update introduction page with recent features

## Status Summary
- Total: 6 tasks
- Completed: 6
- In Progress: 0
- Pending: 0

---

### T-001: Add "No Commands to Memorize" section
**User Story**: US-005 | **Satisfies ACs**: AC-US5-01 | **Status**: [x] completed
**AC**: AC-US5-01

Add the natural language routing table after "The Solution" section. Include an introductory paragraph and the "You say / Your AI runs" table (8 rows covering increment, do, done, brainstorm, brownfield, team-lead, progress, next). Include a closing line about direct invocation.

**Test Plan**: Given the introduction.md file is read, When searching for the natural language routing table, Then the heading "No Commands to Memorize" (or equivalent) exists, the table includes at least 6 "You say" rows with corresponding skill commands, and brainstorming triggers appear in the table.

---

### T-002: Replace "How It Works" with workflow narratives
**User Story**: US-005 | **Satisfies ACs**: AC-US5-02, AC-US5-04 | **Status**: [x] completed
**AC**: AC-US5-02, AC-US5-04

Replace the current three-step CommandTabs "How It Works" section with four workflow narratives adapted from README: main workflow (conversational format showing AI + user exchange), solo developer variant, agent team (parallel) variant, and brownfield project variant. Preserve the section heading level. Remove the duplicate CommandTabs that repeat Getting Started steps.

**Test Plan**: Given the updated introduction.md, When reviewing the workflow section, Then the "How It Works" section is replaced with narrative content covering solo, agent team, and brownfield variants, the three CommandTabs blocks are removed from this section, and all existing section headings beyond this section remain intact (no content regression).

---

### T-003: Add "Agent Swarms" section
**User Story**: US-001 | **Satisfies ACs**: AC-US1-01, AC-US1-02, AC-US1-03 | **Status**: [x] completed
**AC**: AC-US1-01, AC-US1-02, AC-US1-03

Add a new "Agent Swarms" section after the workflow section. Include the ASCII art showing 3 parallel agents in iTerm2/tmux panes, a brief explanation of `/sw:team-lead` with its 6 modes (brainstorm, plan, implement, review, research, test), a note that it uses Claude Code's native TeamCreate for true parallelism, and a link to the full agent teams guide.

**Test Plan**: Given the updated introduction.md, When searching for agent swarm content, Then an "Agent Swarms" (or equivalent) section heading exists, the ASCII art pane diagram is present, `/sw:team-lead` is mentioned, at least 4 of the 6 modes are listed, and "TeamCreate" or "true parallelism" is referenced.

---

### T-004: Add brainstorming to natural language routing and workflow
**User Story**: US-002 | **Satisfies ACs**: AC-US2-01, AC-US2-02 | **Status**: [x] completed
**AC**: AC-US2-01, AC-US2-02

Ensure brainstorming is represented in two places: (1) the natural language routing table from T-001 includes a brainstorming trigger row (e.g., "Brainstorm approaches for X" → `/sw:brainstorm`), and (2) the workflow narratives from T-002 mention brainstorming as an optional step before planning for medium-complexity features.

**Test Plan**: Given the updated introduction.md, When searching for brainstorm references, Then the word "brainstorm" (case-insensitive) appears at least twice — once in the routing table and once in workflow narrative or callout text, and `/sw:brainstorm` is referenced at least once.

---

### T-005: Add brownfield support and integrations sections
**User Story**: US-003, US-004 | **Satisfies ACs**: AC-US3-01, AC-US3-02, AC-US4-01, AC-US4-02 | **Status**: [x] completed
**AC**: AC-US3-01, AC-US3-02, AC-US4-01, AC-US4-02

Two additions:

**Brownfield**: The brownfield workflow narrative in T-002 must show `specweave get` capabilities. The "Who Should Use SpecWeave?" section should be enhanced to highlight brownfield support with `specweave get` (single repo, bulk clone, org-wide).

**Integrations**: Add a new "Integrations" section (after "What You Get vs. Current State", before "Built With SpecWeave") with a table showing GitHub, JIRA, Azure DevOps, and Verified Skills with what syncs for each. Include a brief note about the circuit breaker resilience pattern (per-provider, 3-failure threshold, 5-min auto-reset).

**Test Plan**: Given the updated introduction.md, When reviewing brownfield and integrations content, Then `specweave get` appears in the brownfield workflow or "Who Should Use" section, an "Integrations" section heading exists, the integrations table contains rows for GitHub, JIRA, and Azure DevOps, and "circuit breaker" or "3-failure" is mentioned.

---

### T-006: Streamline Getting Started and verify page health
**User Story**: US-005 | **Satisfies ACs**: AC-US5-03, AC-US5-04, AC-US5-05 | **Status**: [x] completed
**AC**: AC-US5-03, AC-US5-04, AC-US5-05

Streamline the "Getting Started" section: keep the 3-line install block (`npm install -g specweave`, `cd your-project`, `specweave init .`), one brief example, and a link to the full Getting Started page. Remove the duplicate CommandTabs blocks that repeat the workflow already shown above.

Then verify overall page health:
- Final line count is in the 280-350 range
- All internal links (`/docs/...`) are syntactically valid
- The `CommandTabs` import is still used (or removed if no longer needed)
- All existing sections marked "keep" (Title+Hero, The Problem, The Solution, Who Should Use, Core Features, What You Get, Built With, Next Steps) are present and unmodified
- Page uses clear headings, short paragraphs, and tables over prose

**Test Plan**: Given the final introduction.md, When reviewing structure and length, Then the file has between 280 and 350 lines, the install block with `npm install -g specweave` is present, no duplicate CommandTabs blocks for the same workflow step exist, all 8 "keep" sections are present, and the page has at least 3 markdown tables.
