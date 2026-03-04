---
increment: 0415-brainstorm-skill
title: "sw:brainstorm - Multi-Perspective Ideation Skill"
by_user_story:
  US-001: [T-001, T-002, T-003, T-004, T-005]
  US-002: [T-006, T-007, T-008, T-009, T-010]
  US-003: [T-011, T-012, T-013, T-014, T-015, T-016, T-017, T-018, T-019]
---

## User Story: US-001 - Multi-Perspective Brainstorming Before Implementation

**Linked ACs**: AC-US1-01, AC-US1-02, AC-US1-03, AC-US1-04, AC-US1-05
**Tasks**: 5 total, 0 completed

---

### T-001: Create SKILL.md with correct frontmatter and context

**User Story**: US-001
**Satisfies ACs**: AC-US1-01
**Status**: [ ] pending

**Test Plan**:
- **Given** the specweave plugin exists at `plugins/specweave/`
- **When** the brainstorm SKILL.md is created at `plugins/specweave/skills/brainstorm/SKILL.md`
- **Then** the frontmatter contains `context: fork`, `model: opus`, a description with auto-activation keywords, and an `argument-hint` showing the `--lens` and `--depth` flags

**Test Cases**:
1. **Unit**: `tests/unit/skills/brainstorm-skill-meta.test.ts`
   - testSkillFrontmatterHasContextFork(): Parses SKILL.md YAML frontmatter and asserts `context === "fork"`
   - testSkillFrontmatterHasModelOpus(): Asserts `model === "opus"`
   - testSkillDescriptionContainsKeywords(): Asserts description includes "brainstorm", "SCAMPER", "TRIZ"
   - testArgumentHintContainsDepthAndLens(): Asserts argument-hint includes `--depth` and `--lens`
   - **Coverage Target**: 90%

**Implementation**:
1. Create directory `plugins/specweave/skills/brainstorm/`
2. Create `SKILL.md` with frontmatter: `context: fork`, `model: opus`, `description`, `argument-hint`
3. Verify file is under 600 lines total

---

### T-002: Implement 5-phase ideation flow in SKILL.md

**User Story**: US-001
**Satisfies ACs**: AC-US1-02
**Status**: [ ] pending

**Test Plan**:
- **Given** the SKILL.md is loaded by the LLM
- **When** a user invokes `sw:brainstorm "topic"`
- **Then** the skill executes phases in order: Frame, Diverge, Evaluate, Deepen, Output, and each phase section is clearly defined and sequenced in the document

**Test Cases**:
1. **Unit**: `tests/unit/skills/brainstorm-skill-phases.test.ts`
   - testAllFivePhasesDefinedInOrder(): Reads SKILL.md and asserts sections for all 5 phase names appear in correct order
   - testEachPhaseHasDescription(): Asserts each phase section has a non-empty description block
   - **Coverage Target**: 90%

**Implementation**:
1. Add Phase 1 (Frame) section: problem definition, constraints, stakeholders
2. Add Phase 2 (Diverge) section: idea generation via selected lens
3. Add Phase 3 (Evaluate) section: scoring matrix with Feasibility, Impact, Risk, Effort columns
4. Add Phase 4 (Deepen) section: drill-down into top 3 ideas with pros/cons/sketch/risks
5. Add Phase 5 (Output) section: produce structured document, save to `.specweave/docs/brainstorms/`

---

### T-003: Implement depth mode branching (quick/standard/deep)

**User Story**: US-001
**Satisfies ACs**: AC-US1-03
**Status**: [ ] pending

**Test Plan**:
- **Given** the SKILL.md has depth mode instructions
- **When** a user specifies `--depth quick`
- **Then** only Phase 1 (Frame) and Phase 3 (Evaluate) execute; when `--depth standard` (default) Phases 1-3 and 5 run; when `--depth deep` all 5 phases run

**Test Cases**:
1. **Unit**: `tests/unit/skills/brainstorm-depth-modes.test.ts`
   - testQuickModePhaseSet(): Reads SKILL.md and asserts quick mode instructions reference only Frame and Evaluate
   - testStandardModePhaseSet(): Asserts standard mode instructions reference Frame, Diverge, Evaluate, Output (not Deepen)
   - testDeepModePhaseSet(): Asserts deep mode instructions reference all 5 phases
   - testDefaultDepthIsStandard(): Asserts the document specifies standard as the default depth
   - **Coverage Target**: 90%

**Implementation**:
1. Add depth mode branching section to SKILL.md after arg parsing instructions
2. Define quick mode: Frame -> Evaluate -> Output
3. Define standard mode: Frame -> Diverge -> Evaluate -> Output (default)
4. Define deep mode: Frame -> Diverge -> Evaluate -> Deepen -> Output

---

### T-004: Embed DOT-notation process flow graph in SKILL.md

**User Story**: US-001
**Satisfies ACs**: AC-US1-04
**Status**: [ ] pending

**Test Plan**:
- **Given** the SKILL.md contains a DOT graph
- **When** the Output phase runs
- **Then** the embedded DOT digraph is reproduced in the output document showing phase transitions and depth-mode edges

**Test Cases**:
1. **Unit**: `tests/unit/skills/brainstorm-dot-graph.test.ts`
   - testDotGraphPresentInSkillMd(): Reads SKILL.md and asserts a `digraph brainstorm {` block exists
   - testDotGraphContainsAllNodes(): Asserts all 7 nodes (start, check_state, frame, diverge, evaluate, deepen, output) appear in the graph
   - testDotGraphContainsDepthEdges(): Asserts edge labels `depth=quick`, `depth=standard`, `depth=deep` appear in the graph
   - **Coverage Target**: 90%

**Implementation**:
1. Embed the DOT digraph (from plan.md Component 1) into SKILL.md
2. Add Output phase instruction to reproduce the graph in the brainstorm document
3. Annotate graph with a brief legend explaining node shapes

---

### T-005: Define per-phase token budgets in SKILL.md

**User Story**: US-001
**Satisfies ACs**: AC-US1-05
**Status**: [ ] pending

**Test Plan**:
- **Given** each phase in SKILL.md has a token budget advisory
- **When** the SKILL.md is parsed
- **Then** Frame <= 500, Diverge <= 800, Evaluate <= 600, Deepen <= 1000, Output <= 400 token budgets appear as explicit advisory notes per phase

**Test Cases**:
1. **Unit**: `tests/unit/skills/brainstorm-token-budgets.test.ts`
   - testFrameTokenBudget(): Asserts "500" appears adjacent to Frame phase token budget note
   - testDivergeTokenBudget(): Asserts "800" appears adjacent to Diverge phase token budget note
   - testEvaluateTokenBudget(): Asserts "600" appears adjacent to Evaluate phase token budget note
   - testDeepenTokenBudget(): Asserts "1000" appears adjacent to Deepen phase token budget note
   - testOutputTokenBudget(): Asserts "400" appears adjacent to Output phase token budget note
   - **Coverage Target**: 85%

**Implementation**:
1. Add token budget advisory comment to each phase section header in SKILL.md
2. Use inline note format per phase: e.g. `<!-- Token budget: ~500 tokens -->`

---

## User Story: US-002 - Structured Ideation with Cognitive Frameworks

**Linked ACs**: AC-US2-01, AC-US2-02, AC-US2-03, AC-US2-04, AC-US2-05
**Tasks**: 5 total, 0 completed

---

### T-006: Define all 5 cognitive lenses in SKILL.md

**User Story**: US-002
**Satisfies ACs**: AC-US2-01, AC-US2-05
**Status**: [ ] pending

**Test Plan**:
- **Given** the SKILL.md defines available lenses
- **When** the lens section is parsed
- **Then** exactly 5 lenses are defined: Default, Six Thinking Hats, SCAMPER, TRIZ, Adjacent Possible, and when no `--lens` flag is provided the Default lens is used

**Test Cases**:
1. **Unit**: `tests/unit/skills/brainstorm-lenses.test.ts`
   - testExactlyFiveLensesDefined(): Reads SKILL.md and asserts exactly 5 lens names appear in the lenses section
   - testSixHatsFacetsCount(): Asserts 6 hat facets listed (White, Red, Black, Yellow, Green, Blue)
   - testScamperOperatorsCount(): Asserts 7 SCAMPER operators listed
   - testTrizFacetsCount(): Asserts 3 TRIZ facets listed
   - testAdjacentPossibleFacetCount(): Asserts Adjacent Possible is a single-facet lens
   - testDefaultLensIsDefault(): Asserts the Default lens is specified as the no-flag fallback
   - **Coverage Target**: 90%

**Implementation**:
1. Add Lenses section to SKILL.md with all 5 lens definitions
2. For each lens: name, facet list with descriptions, facet count note
3. Add arg parsing instruction: if `--lens` omitted, use Default
4. Keep each lens description concise (20-30 lines) per plan.md progressive disclosure constraint

---

### T-007: Implement parallel subagent dispatch for Six Thinking Hats (deep mode)

**User Story**: US-002
**Satisfies ACs**: AC-US2-02
**Status**: [ ] pending

**Test Plan**:
- **Given** the user selects `--lens six-hats --depth deep`
- **When** the Diverge phase runs
- **Then** the SKILL.md instructs the skill to dispatch each of the 6 hat facets as a separate parallel `Agent()` call, collect results, and merge before Evaluate

**Test Cases**:
1. **Unit**: `tests/unit/skills/brainstorm-parallel-dispatch.test.ts`
   - testSixHatsDeepModeDispatchInstructions(): Reads SKILL.md and asserts six-hats deep mode section contains Agent() dispatch instructions for each of 6 hats
   - testMergeInstructionAfterDispatch(): Asserts a "collect and merge" step follows parallel dispatch instructions
   - testEachFacetAgentPromptUnder200Lines(): Asserts per-facet agent prompt template specifies "under 150 lines" output limit
   - **Coverage Target**: 90%

**Implementation**:
1. Add deep-mode parallel dispatch section to SKILL.md under Diverge phase
2. Define Agent() call template for six-hats with facet-name substitution
3. Add collection and merge instruction after all Agent() calls
4. Specify "output under 150 lines" in each facet agent prompt

---

### T-008: Implement parallel subagent dispatch for SCAMPER (deep mode)

**User Story**: US-002
**Satisfies ACs**: AC-US2-03
**Status**: [ ] pending

**Test Plan**:
- **Given** the user selects `--lens scamper --depth deep`
- **When** the Diverge phase runs
- **Then** the SKILL.md instructs the skill to dispatch each of the 7 SCAMPER operators as a separate parallel `Agent()` call

**Test Cases**:
1. **Unit**: `tests/unit/skills/brainstorm-parallel-dispatch.test.ts`
   - testScamperDeepModeDispatchInstructions(): Asserts SCAMPER deep mode section contains Agent() dispatch for all 7 operators
   - testScamperFacetNamesInDispatch(): Asserts all 7 operator names (Substitute, Combine, Adapt, Modify, Put-to-other-uses, Eliminate, Reverse) appear in dispatch instructions
   - **Coverage Target**: 90%

**Implementation**:
1. Add SCAMPER deep-mode parallel dispatch section analogous to six-hats
2. Define Agent() call template for each of 7 SCAMPER operators
3. Add collection and merge step

---

### T-009: Implement sequential lens execution for quick/standard depth modes

**User Story**: US-002
**Satisfies ACs**: AC-US2-04
**Status**: [ ] pending

**Test Plan**:
- **Given** the user selects a lens with `--depth quick` or `--depth standard`
- **When** the Diverge phase runs (standard only; quick skips Diverge)
- **Then** the SKILL.md instructs the skill to execute all lens facets sequentially in the current agent context without spawning subagents

**Test Cases**:
1. **Unit**: `tests/unit/skills/brainstorm-sequential-execution.test.ts`
   - testStandardModeUsesSequentialExecution(): Reads SKILL.md and asserts standard mode Diverge section explicitly states sequential (not parallel) execution
   - testQuickModeSkipsDiverge(): Asserts quick mode instructions do not reference the Diverge phase
   - testNoAgentCallsInStandardMode(): Asserts Agent() calls appear only within deep mode conditional blocks
   - **Coverage Target**: 90%

**Implementation**:
1. Add sequential execution instruction to standard-mode Diverge section
2. Explicitly note "no subagent dispatch" in quick and standard modes
3. Ensure depth-mode conditionals clearly separate parallel vs sequential paths

---

### T-010: Validate SKILL.md total line count stays under 600

**User Story**: US-002
**Satisfies ACs**: AC-US2-01, AC-US2-02, AC-US2-03, AC-US2-04
**Status**: [ ] pending

**Test Plan**:
- **Given** the completed SKILL.md with all lenses, phases, and dispatch instructions
- **When** the file line count is checked
- **Then** the total number of lines is at most 600

**Test Cases**:
1. **Unit**: `tests/unit/skills/brainstorm-skill-size.test.ts`
   - testSkillMdUnder600Lines(): Reads SKILL.md and asserts `lines.length <= 600`
   - **Coverage Target**: 80%

**Implementation**:
1. Read current SKILL.md line count after all other US-001 and US-002 tasks complete
2. If over 600 lines, condense lens descriptions using progressive disclosure
3. Verify final count <= 600

---

## User Story: US-003 - Persistent Brainstorm Documents with Increment Handoff

**Linked ACs**: AC-US3-01, AC-US3-02, AC-US3-03, AC-US3-04, AC-US3-05, AC-US3-06, AC-US3-07, AC-US3-08, AC-US3-09
**Tasks**: 9 total, 0 completed

---

### T-011: Define output document structure and save path in SKILL.md

**User Story**: US-003
**Satisfies ACs**: AC-US3-01
**Status**: [ ] pending

**Test Plan**:
- **Given** the Output phase completes
- **When** the SKILL.md output instructions are followed
- **Then** a markdown document is saved to `.specweave/docs/brainstorms/{YYYY-MM-DD}-{slug}.md` containing topic, lens, depth, all phase outputs, the DOT graph, and a ranked ideas list with scores

**Test Cases**:
1. **Unit**: `tests/unit/skills/brainstorm-output-structure.test.ts`
   - testOutputPathFormatInSkillMd(): Reads SKILL.md and asserts the save path pattern `.specweave/docs/brainstorms/` is specified
   - testOutputDocSectionsListed(): Asserts Output phase section references all required document sections (Problem Frame, Approaches, Evaluation Matrix, Deep Dives, Idea Tree, Next Steps)
   - testSlugAndDateInFilename(): Asserts path instruction includes `{YYYY-MM-DD}` and `{slug}` placeholders
   - **Coverage Target**: 90%

**Implementation**:
1. Add Output phase document structure to SKILL.md using plan.md Component 3 template
2. Specify exact save path: `.specweave/docs/brainstorms/{YYYY-MM-DD}-{slug}.md`
3. Instruct skill to create directory if it does not exist
4. Include instruction to embed the DOT process graph in the Idea Tree section

---

### T-012: Define session state file schema and resumability in SKILL.md

**User Story**: US-003
**Satisfies ACs**: AC-US3-02
**Status**: [ ] pending

**Test Plan**:
- **Given** a brainstorm session is interrupted mid-phase
- **When** the user re-invokes `sw:brainstorm` with the same topic
- **Then** the SKILL.md instructs the skill to read `.specweave/state/brainstorm-{session-id}.json`, identify the last completed phase, and resume from there

**Test Cases**:
1. **Unit**: `tests/unit/skills/brainstorm-state-schema.test.ts`
   - testStateFilePathPatternInSkillMd(): Reads SKILL.md and asserts `.specweave/state/brainstorm-` path is specified
   - testStateSchemaFieldsInSkillMd(): Asserts SKILL.md documents all required state fields: sessionId, topic, lens, depth, startedAt, phases with per-phase status
   - testResumeInstructionInSkillMd(): Asserts SKILL.md contains explicit "check state file before starting" instruction
   - testPerFacetStatusInStateSchema(): Asserts state schema shows facets array with individual status tracking
   - **Coverage Target**: 90%

**Implementation**:
1. Add state management section to SKILL.md: create state file at session start
2. Define JSON schema (per plan.md Component 2) inline in SKILL.md as example
3. Add "check for existing state file" instruction at top of execution flow
4. Add "update state after each phase completes" instruction within each phase section
5. Add resume logic: read phases object, skip completed phases, resume from last incomplete

---

### T-013: Implement increment handoff protocol in SKILL.md

**User Story**: US-003
**Satisfies ACs**: AC-US3-03
**Status**: [ ] pending

**Test Plan**:
- **Given** the brainstorm Output phase has completed and produced a document
- **When** the user says "proceed to increment" or similar
- **Then** SKILL.md instructs the skill to invoke `sw:increment` with the brainstorm doc path as args, and the convention for placing it in spec.md's `## Background` section is documented

**Test Cases**:
1. **Unit**: `tests/unit/skills/brainstorm-handoff.test.ts`
   - testHandoffSkillCallInSkillMd(): Reads SKILL.md and asserts `sw:increment` invocation pattern with `--brainstorm-doc` arg appears
   - testHandoffTriggerPhrasesInSkillMd(): Asserts "proceed to increment" and similar phrases are listed as handoff triggers
   - testBackgroundSectionConventionInSkillMd(): Asserts SKILL.md documents the `## Background` section convention for spec.md
   - **Coverage Target**: 90%

**Implementation**:
1. Add handoff section to SKILL.md at end of Output phase instructions
2. List trigger phrases: "proceed to increment", "start planning", "create increment"
3. Define `Skill({ skill: "sw:increment", args: "{topic} --brainstorm-doc {path}" })` call
4. Document `## Background` convention for the PM skill to follow

---

### T-014: Register brainstorm skill in specweave PLUGIN.md

**User Story**: US-003
**Satisfies ACs**: AC-US3-04
**Status**: [ ] pending

**Test Plan**:
- **Given** the specweave PLUGIN.md skill table
- **When** the skill table is read
- **Then** `brainstorm` appears as an entry with a description referencing cognitive frameworks

**Test Cases**:
1. **Unit**: `tests/unit/plugins/specweave-plugin-registration.test.ts`
   - testBrainstormInPluginMdTable(): Reads `plugins/specweave/PLUGIN.md` and asserts a table row with `brainstorm` exists
   - testBrainstormDescriptionMentionsCognitiveFrameworks(): Asserts the description includes "cognitive frameworks" or equivalent keywords
   - **Coverage Target**: 85%

**Implementation**:
1. Open `plugins/specweave/PLUGIN.md`
2. Add table row: `| brainstorm | Multi-perspective ideation with cognitive frameworks (Six Thinking Hats, SCAMPER, TRIZ) and depth-configurable exploration |`
3. Place row in alphabetical order within the skills table

---

### T-015: Add deprecation notice to specweave-docs PLUGIN.md

**User Story**: US-003
**Satisfies ACs**: AC-US3-05
**Status**: [ ] pending

**Test Plan**:
- **Given** the specweave-docs PLUGIN.md lists `spec-driven-brainstorming`
- **When** this task is complete
- **Then** the entry for `spec-driven-brainstorming` includes the text "DEPRECATED" and directs users to `sw:brainstorm`

**Test Cases**:
1. **Unit**: `tests/unit/plugins/specweave-docs-deprecation.test.ts`
   - testSpecDrivenBrainstormingMarkedDeprecated(): Reads `plugins/specweave-docs/PLUGIN.md` and asserts the `spec-driven-brainstorming` row contains "DEPRECATED"
   - testDeprecationNoteReferencesSwBrainstorm(): Asserts the row mentions `sw:brainstorm`
   - **Coverage Target**: 85%

**Implementation**:
1. Open `plugins/specweave-docs/PLUGIN.md`
2. Find the `spec-driven-brainstorming` row in the skills table
3. Prepend "**DEPRECATED** -- Use `sw:brainstorm` instead." to its description

---

### T-016: Update source code references in 3 TypeScript files

**User Story**: US-003
**Satisfies ACs**: AC-US3-06
**Status**: [ ] pending

**Test Plan**:
- **Given** the 3 TypeScript source files that reference the old brainstorming skill
- **When** the changes are applied
- **Then** `claude-md-generator.ts` uses `brainstorm` in both the filter list and the activation map, `agents-md-generator.ts` uses `brainstorm` in its activation map, and `llm-plugin-detector.ts` has `docs:brainstorming` removed from the docs group

**Test Cases**:
1. **Unit**: `tests/unit/adapters/claude-md-generator.test.ts`
   - testFrameworkSkillsFilterContainsBrainstorm(): Calls `generateFrameworkSkillsTable()` with a mock skill list including `brainstorm` and asserts it appears in output
   - testFrameworkSkillsFilterExcludesOldName(): Asserts `spec-driven-brainstorming` no longer triggers inclusion
   - testSkillActivationMapContainsBrainstorm(): Calls `getSkillActivation("brainstorm")` and asserts non-empty result
2. **Unit**: `tests/unit/adapters/agents-md-generator.test.ts`
   - testAgentsMdActivationMapContainsBrainstorm(): Asserts brainstorm key exists in activation map
3. **Unit**: `tests/unit/core/llm-plugin-detector.test.ts`
   - testDocsGroupExcludesBrainstorming(): Asserts the docs group string does not contain `docs:brainstorming`
   - **Coverage Target**: 90%

**Implementation**:
1. Edit `src/adapters/claude-md-generator.ts`: replace `'spec-driven-brainstorming'` with `'brainstorm'` in filter list (line ~200) and activation map key (line ~264)
2. Edit `src/adapters/agents-md-generator.ts`: replace `'spec-driven-brainstorming'` key with `'brainstorm'` in activation map (line ~141), update description
3. Edit `src/core/lazy-loading/llm-plugin-detector.ts`: remove `docs:brainstorming` from the docs group string (line ~676)
4. Verify `src/utils/generate-skills-index.ts` requires no changes (categorizeSkill already matches `nameLower.includes('brainstorm')`)

---

### T-017: Update CLAUDE.md template to clarify brainstorm opt-out

**User Story**: US-003
**Satisfies ACs**: AC-US3-07
**Status**: [ ] pending

**Test Plan**:
- **Given** the CLAUDE.md template at `src/templates/CLAUDE.md.template`
- **When** this change is applied
- **Then** the auto-detection section contains a note clarifying that "Just brainstorm first" routes to `sw:brainstorm` and "Don't plan yet" is for unstructured discussion

**Test Cases**:
1. **Unit**: `tests/unit/templates/claude-md-template.test.ts`
   - testBrainstormOptOutNotePresent(): Reads `src/templates/CLAUDE.md.template` and asserts a note referencing `sw:brainstorm` appears near the "Just brainstorm first" opt-out phrase
   - testDontPlanYetAlternativePresent(): Asserts "Don't plan yet" is mentioned as the unstructured discussion opt-out
   - **Coverage Target**: 85%

**Implementation**:
1. Open `src/templates/CLAUDE.md.template`
2. Locate the auto-detection opt-out section containing "Just brainstorm first"
3. Add note: `**Note**: "Just brainstorm first" routes to \`sw:brainstorm\` for structured ideation. Use "Don't plan yet" if you want unstructured discussion instead.`

---

### T-018: Update docs-site with sw:brainstorm documentation

**User Story**: US-003
**Satisfies ACs**: AC-US3-08
**Status**: [ ] pending

**Test Plan**:
- **Given** the docs-site documentation files
- **When** the changes are applied
- **Then** `docs-site/docs/reference/skills.md` lists `sw:brainstorm` in the Core Skills table with usage examples and auto-activation keywords, and `docs-site/docs/workflows/planning.md` references brainstorming as an optional pre-increment step

**Test Cases**:
1. **Unit**: `tests/unit/docs/skills-reference.test.ts`
   - testSwBrainstormInSkillsTable(): Reads `docs-site/docs/reference/skills.md` and asserts `sw:brainstorm` appears in the skills table
   - testBrainstormUsageExamplePresent(): Asserts a usage example section for brainstorm is present
   - testAutoActivationKeywordsListed(): Asserts at least 3 auto-activation keywords are listed
2. **Unit**: `tests/unit/docs/planning-workflow.test.ts`
   - testBrainstormStepInPlanningDoc(): Reads `docs-site/docs/workflows/planning.md` and asserts brainstorm is referenced as a pre-increment step
   - testOptionalStepLabelPresent(): Asserts the brainstorm step is marked as optional
   - **Coverage Target**: 85%

**Implementation**:
1. Edit `docs-site/docs/reference/skills.md`: add `sw:brainstorm` to Core Skills table and add detailed reference section with depth modes table, lens list, usage examples, and auto-activation keywords
2. Edit `docs-site/docs/workflows/planning.md`: add optional "Step 0: Brainstorm" before the existing planning flow, update the mermaid diagram to show brainstorm-to-increment path, add guidance on when to brainstorm vs skip to increment

---

### T-019: Verify auto-activation keywords in SKILL.md frontmatter

**User Story**: US-003
**Satisfies ACs**: AC-US3-09
**Status**: [ ] pending

**Test Plan**:
- **Given** the SKILL.md frontmatter description field
- **When** auto-activation keyword detection runs
- **Then** the description contains all required keywords: "brainstorm", "explore ideas", "think through", "what if", "ideate", "diverge"

**Test Cases**:
1. **Unit**: `tests/unit/skills/brainstorm-auto-activation.test.ts`
   - testBrainstormKeywordPresent(): Asserts "brainstorm" in SKILL.md description
   - testExploreIdeasKeywordPresent(): Asserts "explore ideas" in SKILL.md description
   - testThinkThroughKeywordPresent(): Asserts "think through" in SKILL.md description
   - testWhatIfKeywordPresent(): Asserts "what if" in SKILL.md description
   - testIdeateKeywordPresent(): Asserts "ideate" in SKILL.md description
   - testDivergeKeywordPresent(): Asserts "diverge" in SKILL.md description
   - **Coverage Target**: 85%

**Implementation**:
1. Review the SKILL.md frontmatter description written in T-001
2. Ensure all 6 required auto-activation keywords are present in the description
3. If any are missing, update the description field to include them
4. Also verify description mentions "design thinking", "six hats", "SCAMPER", "TRIZ" per plan.md frontmatter spec
