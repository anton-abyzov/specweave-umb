# Tasks: MCP-Aware Eval Simulation for Skill Benchmarks

## Task Notation

- `[T###]`: Task ID
- `[P]`: Parallelizable
- `[ ]`: Not started
- `[x]`: Completed
- Model hints: haiku (simple), opus (default)

## Phase 1: Registry Expansion

### US-003: Expand MCP server registry (P1)

#### T-001: Add Notion, Jira, Confluence, Figma, and Sentry to MCP_REGISTRY

**User Story**: US-003 | **Satisfies ACs**: AC-US3-01, AC-US3-02, AC-US3-03 | **Status**: [x] completed

**Description**: Add 5 new entries to the `MCP_REGISTRY` array in `src/eval/mcp-detector.ts`. Each entry needs server name, prefix patterns, MCP server URL, and transport type.

**AC**: AC-US3-01, AC-US3-02, AC-US3-03

**Implementation Details**:
- Notion: server "Notion", prefixes `["notion_"]`, url `https://mcp.notion.com/mcp`, transport "http"
- Jira: server "Jira", prefixes `["jira_"]`, url `https://mcp.atlassian.com/jira/mcp`, transport "http"
- Confluence: server "Confluence", prefixes `["confluence_"]`, url `https://mcp.atlassian.com/confluence/mcp`, transport "http"
- Figma: server "Figma", prefixes `["figma_"]`, url `https://mcp.figma.com/mcp`, transport "http"
- Sentry: server "Sentry", prefixes `["sentry_"]`, url `https://mcp.sentry.dev/mcp`, transport "http"

**Test Plan**:
- **File**: `src/eval/__tests__/mcp-detector.test.ts`
- **Tests**:
  - **TC-001**: Detects Notion tool patterns
    - Given content with "notion_create_page" and "notion_search"
    - When detectMcpDependencies is called
    - Then returns 1 dep with server "Notion" and both tools matched
  - **TC-002**: Detects Jira tool patterns
    - Given content with "jira_create_issue"
    - When detectMcpDependencies is called
    - Then returns 1 dep with server "Jira"
  - **TC-003**: Detects Confluence tool patterns
    - Given content with "confluence_create_page"
    - When detectMcpDependencies is called
    - Then returns 1 dep with server "Confluence"
  - **TC-004**: Detects Figma tool patterns
    - Given content with "figma_get_file"
    - When detectMcpDependencies is called
    - Then returns 1 dep with server "Figma"
  - **TC-005**: Detects Sentry tool patterns
    - Given content with "sentry_list_issues"
    - When detectMcpDependencies is called
    - Then returns 1 dep with server "Sentry"
  - **TC-006**: Detects multiple new servers simultaneously
    - Given content with "notion_create_page" and "jira_create_issue" and "figma_get_file"
    - When detectMcpDependencies is called
    - Then returns 3 deps (Notion, Jira, Figma)

**Dependencies**: None

---

## Phase 2: MCP-Aware Eval Generation

### US-001: MCP-aware eval generation (P1)

#### T-002: Augment buildEvalInitPrompt with MCP simulation context

**User Story**: US-001 | **Satisfies ACs**: AC-US1-01, AC-US1-02, AC-US1-03 | **Status**: [x] completed

**Description**: Modify `buildEvalInitPrompt` in `src/eval/prompt-builder.ts` to call `detectMcpDependencies` on the skill content. When MCP dependencies are found, append instructions telling the LLM to generate assertions that verify tool call demonstration quality rather than expecting real API responses.

**AC**: AC-US1-01, AC-US1-02, AC-US1-03

**Implementation Details**:
- At the start of `buildEvalInitPrompt`, call `detectMcpDependencies(skillContent)`
- If MCP deps found, append a new section to the prompt:
  ```
  ## MCP Simulation Context
  This skill uses MCP tools that will be SIMULATED during evaluation (not connected to real services).
  Tools detected: [server: tool1, tool2]

  When generating assertions:
  - Assert that the output demonstrates the correct tool call workflow (tool name, parameters)
  - Assert that simulated responses are realistic and complete
  - Do NOT assert on real API artifacts (actual URLs, real IDs, live data)
  - Use assertions like "demonstrates calling slack_send_message with channel and message params"
  ```
- When no MCP deps, the prompt is unchanged (non-regression)

**Test Plan**:
- **File**: `src/eval/__tests__/prompt-builder.test.ts`
- **Tests**:
  - **TC-007**: buildEvalInitPrompt includes MCP context for Slack skill
    - Given skill content containing "slack_send_message"
    - When buildEvalInitPrompt is called
    - Then the prompt contains "MCP Simulation Context" and "Slack"
  - **TC-008**: buildEvalInitPrompt is unchanged for non-MCP skill
    - Given skill content with no MCP tool references
    - When buildEvalInitPrompt is called
    - Then the prompt does NOT contain "MCP Simulation Context"
  - **TC-009**: buildEvalInitPrompt lists all detected MCP servers
    - Given skill content with slack and github tool references
    - When buildEvalInitPrompt is called
    - Then the prompt contains both "Slack" and "GitHub"

**Dependencies**: T-001 (for new server entries, but not blocking)

---

## Phase 3: Simulation-Aware Judging

### US-002: Simulation-aware assertion judging (P1)

#### T-003: Create buildJudgeSystemPrompt function with MCP awareness

**User Story**: US-002 | **Satisfies ACs**: AC-US2-01, AC-US2-02, AC-US2-03 | **Status**: [x] completed

**Description**: Add a `buildJudgeSystemPrompt` function to `src/eval/judge.ts` that returns either the standard judge system prompt or an MCP-augmented version. Modify `judgeAssertion` to accept an optional `mcpDeps` parameter and use the appropriate prompt.

**AC**: AC-US2-01, AC-US2-02, AC-US2-03

**Implementation Details**:
- New exported function `buildJudgeSystemPrompt(mcpDeps?: McpDependency[]): string`
  - When `mcpDeps` is empty/undefined: return existing `JUDGE_SYSTEM` constant
  - When `mcpDeps` has entries: return augmented prompt:
    ```
    You are a binary assertion evaluator. Given an LLM output and an assertion, determine if the output satisfies the assertion.

    IMPORTANT: This output was generated in MCP SIMULATION MODE. The following tools were simulated (not connected to real services): [list].
    When evaluating assertions:
    - A simulated tool call is valid if it names the correct tool and provides realistic parameters
    - A simulated response is valid if it contains plausible data (realistic IDs, timestamps, content)
    - Do NOT fail assertions just because data is simulated rather than real

    Respond with ONLY a JSON object: { "pass": boolean, "reasoning": "brief explanation" }
    ```
- Modify `judgeAssertion` signature: add optional `mcpDeps?: McpDependency[]` parameter
- Call `buildJudgeSystemPrompt(mcpDeps)` instead of using `JUDGE_SYSTEM` directly

**Test Plan**:
- **File**: `src/eval/__tests__/judge.test.ts`
- **Tests**:
  - **TC-010**: buildJudgeSystemPrompt returns standard prompt when no MCP deps
    - Given mcpDeps is undefined
    - When buildJudgeSystemPrompt is called
    - Then it returns the standard JUDGE_SYSTEM prompt text
  - **TC-011**: buildJudgeSystemPrompt returns augmented prompt with MCP deps
    - Given mcpDeps has a Slack entry
    - When buildJudgeSystemPrompt is called
    - Then the prompt contains "SIMULATION MODE" and "Slack"
  - **TC-012**: buildJudgeSystemPrompt lists all simulated servers
    - Given mcpDeps has Slack and GitHub entries
    - When buildJudgeSystemPrompt is called
    - Then the prompt mentions both "Slack" and "GitHub"
  - **TC-013**: judgeAssertion uses standard prompt when mcpDeps not provided
    - Given a call to judgeAssertion without mcpDeps
    - When the function executes
    - Then it passes the standard judge prompt to the LLM client

**Dependencies**: None

---

## Phase 4: Fair Comparison

### US-004: Fair MCP-aware comparison mode (P2)

#### T-004: Augment comparator with MCP simulation awareness

**User Story**: US-004 | **Satisfies ACs**: AC-US4-01, AC-US4-02, AC-US4-03 | **Status**: [x] completed

**Description**: Modify `scoreComparison` in `src/eval/comparator.ts` to accept optional MCP dependency info and augment the comparator system prompt when MCP tools are involved.

**AC**: AC-US4-01, AC-US4-02, AC-US4-03

**Implementation Details**:
- Add optional `mcpDeps?: McpDependency[]` parameter to `scoreComparison` and `runComparison`
- When `mcpDeps` has entries, append to `COMPARATOR_SYSTEM_PROMPT`:
  ```
  NOTE: One or both responses may contain SIMULATED MCP tool interactions (tools: [list]).
  Simulated tool calls are valid demonstrations. Evaluate the quality and realism of the
  simulation (correct tool names, realistic parameters, plausible responses) rather than
  penalizing simulated output vs. real output.
  ```
- `runComparison` should detect MCP deps from `skillContent` and pass to `scoreComparison`
- When no MCP deps, behavior is unchanged

**Test Plan**:
- **File**: `src/eval/__tests__/comparator.test.ts`
- **Tests**:
  - **TC-014**: scoreComparison uses standard prompt when no MCP deps
    - Given mcpDeps is undefined
    - When scoreComparison builds the prompt
    - Then it does NOT contain "SIMULATED MCP"
  - **TC-015**: scoreComparison augments prompt when MCP deps present
    - Given mcpDeps has a Slack entry
    - When scoreComparison builds the prompt
    - Then it contains "SIMULATED MCP" and "Slack"
  - **TC-016**: runComparison auto-detects MCP deps from skill content
    - Given skill content containing "slack_send_message"
    - When runComparison is called
    - Then MCP detection runs and comparison prompt is augmented

**Dependencies**: T-001

---

## Phase 5: Benchmark Metadata

### US-005: Simulation quality signal in benchmark results (P2)

#### T-005: Add mcpSimulation field to BenchmarkResult

**User Story**: US-005 | **Satisfies ACs**: AC-US5-01, AC-US5-02, AC-US5-03 | **Status**: [x] completed

**Description**: Extend the `BenchmarkResult` interface in `src/eval/benchmark.ts` with an optional `mcpSimulation` field. Ensure backward compatibility with existing benchmark.json files and history.

**AC**: AC-US5-01, AC-US5-02, AC-US5-03

**Implementation Details**:
- Add to `BenchmarkResult` interface:
  ```typescript
  mcpSimulation?: {
    active: boolean;
    servers: string[];
  };
  ```
- Verify `readBenchmark` handles missing field (it already does via JSON.parse)
- Verify `listHistory`, `computeStats`, `computeRegressions` in `benchmark-history.ts` handle the new field without errors
- No changes needed in history functions since they don't reference the field

**Test Plan**:
- **File**: `src/eval/__tests__/benchmark.test.ts`
- **Tests**:
  - **TC-017**: BenchmarkResult with mcpSimulation serializes correctly
    - Given a BenchmarkResult with mcpSimulation { active: true, servers: ["Slack", "GitHub"] }
    - When writeBenchmark writes and readBenchmark reads it back
    - Then mcpSimulation field is preserved
  - **TC-018**: BenchmarkResult without mcpSimulation reads correctly
    - Given an existing benchmark.json without mcpSimulation
    - When readBenchmark reads it
    - Then the result has mcpSimulation as undefined (no crash)
  - **TC-019**: History functions handle mcpSimulation gracefully
    - Given benchmark history with mixed entries (some with mcpSimulation, some without)
    - When listHistory and computeStats are called
    - Then they complete without errors

**Dependencies**: None

---

## Phase 6: Integration Verification

#### T-006: End-to-end verification with MCP-dependent skill

**User Story**: All | **Satisfies ACs**: All | **Status**: [x] completed

**Description**: Run the full eval pipeline (`vskill eval init` + `vskill eval run` + `vskill eval compare`) against a known MCP-dependent skill to verify the end-to-end flow works correctly with simulation awareness.

**Test Plan**:
- Run `vskill eval init` on a skill that uses slack_send_message -- verify generated evals have simulation-aware assertions
- Run `vskill eval run` on that skill -- verify benchmark.json includes mcpSimulation metadata
- Run `vskill eval compare` -- verify comparison judge accounts for simulation
- Run all existing unit tests: `npx vitest run src/eval/` -- verify no regressions

**Dependencies**: T-001, T-002, T-003, T-004, T-005
