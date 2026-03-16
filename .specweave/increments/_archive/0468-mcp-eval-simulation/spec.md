---
increment: 0468-mcp-eval-simulation
title: MCP-Aware Eval Simulation for Skill Benchmarks
type: feature
priority: P1
status: completed
created: 2026-03-10T00:00:00.000Z
structure: user-stories
test_mode: TDD
coverage_target: 90
---

# Feature: MCP-Aware Eval Simulation for Skill Benchmarks

## Overview

The vskill eval system already has basic MCP awareness: `mcp-detector.ts` identifies MCP tool references in SKILL.md content, and `prompt-builder.ts` injects simulation instructions into the eval system prompt when MCP dependencies are detected. However, this initial implementation has gaps that cause MCP-dependent skills to receive lower eval scores than they deserve:

1. **Eval generation ignores MCP context**: `buildEvalInitPrompt` does not inform the LLM about MCP dependencies, so generated eval cases may include assertions that expect real tool outputs (URLs, IDs) instead of simulated ones.
2. **No simulation-aware assertions**: The judge (`judge.ts`) evaluates assertions literally. An assertion like "includes a Slack message URL" will fail against simulated output even though the skill correctly demonstrated the workflow.
3. **Comparator baseline disadvantage**: In A/B comparison mode, the baseline (no skill) has no MCP context at all, making comparison unfair for MCP-heavy skills -- the baseline naturally "fails" at tool usage.
4. **Missing MCP servers**: The `MCP_REGISTRY` in `mcp-detector.ts` only covers Slack, GitHub, Linear, and Google Workspace. Common servers like Notion, Jira, Confluence, Figma, and Sentry are missing.
5. **No simulation quality signal**: There is no way to distinguish a skill that simulated well from one that gave a poor simulation -- the eval pipeline treats simulation output the same as real output.

This increment makes the eval pipeline fully MCP-simulation-aware end-to-end: from eval generation through execution, judging, and comparison.

## User Stories

### US-001: MCP-aware eval generation (P1)
**Project**: vskill

**As a** skill author
**I want** `vskill eval init` to generate eval cases that account for MCP tool simulation
**So that** my MCP-dependent skill's evals have assertions that are fair to simulated output

**Acceptance Criteria**:
- [x] **AC-US1-01**: `buildEvalInitPrompt` detects MCP dependencies in the skill content and appends MCP simulation context to the generation prompt
- [x] **AC-US1-02**: Generated eval assertions for MCP skills reference "simulated" tool calls (e.g. "demonstrates calling slack_send_message with channel and message parameters") rather than expecting real API responses
- [x] **AC-US1-03**: Generated eval cases for non-MCP skills are unchanged (no regression)

---

### US-002: Simulation-aware assertion judging (P1)
**Project**: vskill

**As a** skill author
**I want** the eval judge to understand that tool calls are simulated during evaluation
**So that** assertions are evaluated against the quality of the simulation rather than real API responses

**Acceptance Criteria**:
- [x] **AC-US2-01**: The judge system prompt is augmented with simulation context when the skill has MCP dependencies
- [x] **AC-US2-02**: The judge evaluates whether the LLM demonstrated the correct tool call workflow (tool name, parameters, realistic mock response) rather than checking for real API artifacts
- [x] **AC-US2-03**: Non-MCP skill judging is unaffected (no regression)

---

### US-003: Expand MCP server registry (P1)
**Project**: vskill

**As a** skill author using Notion, Jira, Confluence, Figma, or Sentry MCP tools
**I want** the MCP detector to recognize my tool references
**So that** my skill gets proper simulation instructions during eval

**Acceptance Criteria**:
- [x] **AC-US3-01**: `MCP_REGISTRY` includes entries for Notion (`notion_`), Jira (`jira_`), Confluence (`confluence_`), Figma (`figma_`), and Sentry (`sentry_`)
- [x] **AC-US3-02**: Each new registry entry has a valid server name, prefix array, URL, and transport type
- [x] **AC-US3-03**: `detectMcpDependencies` correctly matches tool references for all new servers

---

### US-004: Fair MCP-aware comparison mode (P2)
**Project**: vskill

**As a** skill author
**I want** the A/B comparison eval to account for MCP simulation so skill vs. baseline is a fair comparison
**So that** my MCP-dependent skill is not unfairly penalized in comparison benchmarks

**Acceptance Criteria**:
- [x] **AC-US4-01**: The comparator's blind judge prompt includes context that both responses may contain simulated tool interactions
- [x] **AC-US4-02**: The comparison judge evaluates simulation quality (realistic parameters, plausible responses, complete workflow) rather than penalizing simulated output
- [x] **AC-US4-03**: Comparison results for non-MCP skills are unchanged

---

### US-005: Simulation quality signal in benchmark results (P2)
**Project**: vskill

**As a** platform operator
**I want** benchmark results to indicate whether MCP simulation was active during the eval run
**So that** I can distinguish eval results for MCP skills from non-MCP skills

**Acceptance Criteria**:
- [x] **AC-US5-01**: `BenchmarkResult` includes an optional `mcpSimulation` field indicating whether simulation mode was active and which servers were simulated
- [x] **AC-US5-02**: The benchmark output (benchmark.json) records MCP simulation metadata when applicable
- [x] **AC-US5-03**: History and stats computations handle the new field without breaking existing data

## Functional Requirements

### FR-001: Augment eval generation prompt with MCP context
`buildEvalInitPrompt` in `prompt-builder.ts` should call `detectMcpDependencies` on the skill content. When MCP deps are found, append instructions to the generation prompt telling the LLM to create assertions that verify correct tool usage workflow demonstration rather than real API output.

### FR-002: Augment judge with simulation awareness
When `judgeAssertion` (or its system prompt) is invoked for an MCP-dependent skill, the judge system prompt should include context that the output contains simulated tool calls. The judge should evaluate whether the simulation is realistic and complete, not whether real API responses are present.

### FR-003: Expand MCP_REGISTRY
Add entries for Notion, Jira, Confluence, Figma, and Sentry to the `MCP_REGISTRY` array in `mcp-detector.ts`. Each entry needs: server name, prefix patterns, MCP server URL, and transport type.

### FR-004: Fair comparison judging
`scoreComparison` in `comparator.ts` should detect MCP skills and augment the comparator system prompt to account for simulated tool interactions in both the skill and baseline responses.

### FR-005: MCP metadata in benchmark output
Add an optional `mcpSimulation` field to `BenchmarkResult` in `benchmark.ts`: `{ active: boolean; servers: string[] }`. Populate it during benchmark runs when MCP dependencies are detected.

## Success Criteria

- MCP-dependent skills achieve comparable eval pass rates to equivalent non-MCP skills (no systematic penalty from simulation)
- All 5 new MCP servers are detected correctly with unit tests
- Existing eval tests continue to pass without modification (non-MCP skills unaffected)
- Benchmark history remains backward-compatible (old entries without `mcpSimulation` load correctly)

## Out of Scope

- Actually connecting to real MCP servers during eval (the entire point is simulation)
- UI changes on vskill-platform to display MCP simulation metadata
- Automatic MCP server discovery beyond the registry
- Custom simulation response templates per MCP server

## Dependencies

- `mcp-detector.ts`: MCP dependency detection (existing, to be extended)
- `prompt-builder.ts`: Eval system prompt assembly (existing, to be extended)
- `judge.ts`: Assertion-level LLM judge (existing, to be extended)
- `comparator.ts`: Blind A/B comparison (existing, to be extended)
- `benchmark.ts`: Benchmark result schema (existing, to be extended)
