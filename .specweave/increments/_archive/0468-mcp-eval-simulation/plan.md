# Implementation Plan: MCP-Aware Eval Simulation for Skill Benchmarks

## Overview

Make the vskill eval pipeline fully MCP-simulation-aware by extending five existing modules: `mcp-detector.ts` (registry expansion), `prompt-builder.ts` (generation + execution prompts), `judge.ts` (simulation-aware judging), `comparator.ts` (fair comparison), and `benchmark.ts` (simulation metadata). All changes are additive -- existing non-MCP eval behavior is preserved.

## Architecture

### Components

- **mcp-detector.ts** (extend): Add 5 new MCP server entries to `MCP_REGISTRY`. No structural changes.
- **prompt-builder.ts** (extend): Augment `buildEvalInitPrompt` to detect MCP dependencies and inject simulation-aware generation instructions. The existing `buildEvalSystemPrompt` already handles execution-time simulation -- no changes needed there.
- **judge.ts** (extend): Add MCP-simulation context to the judge system prompt. New function `buildJudgeSystemPrompt(mcpDeps?)` that returns the base prompt or an augmented version depending on whether MCP dependencies are present.
- **comparator.ts** (extend): Augment `COMPARATOR_SYSTEM_PROMPT` with simulation awareness when MCP dependencies are detected. Pass skill content through the comparison flow so MCP detection can happen.
- **benchmark.ts** (extend): Add optional `mcpSimulation` field to `BenchmarkResult` interface.

### Data Model

Extended `BenchmarkResult`:
```typescript
interface BenchmarkResult {
  // ... existing fields ...
  mcpSimulation?: {
    active: boolean;
    servers: string[];
  };
}
```

This is backward-compatible -- existing benchmark.json files without `mcpSimulation` will parse correctly since the field is optional.

### Flow

```
eval init:  SKILL.md → detectMcpDeps → buildEvalInitPrompt (MCP-augmented) → LLM → evals.json
eval run:   SKILL.md → detectMcpDeps → buildEvalSystemPrompt (already MCP-aware) → LLM → output
judge:      output + assertion → buildJudgeSystemPrompt(mcpDeps) → LLM → pass/fail
comparison: skill vs baseline → detectMcpDeps → augmented COMPARATOR prompt → LLM → scores
benchmark:  results + mcpDeps → BenchmarkResult { mcpSimulation: { active, servers } }
```

## Technology Stack

- **Language**: TypeScript (Node.js ESM)
- **Testing**: Vitest
- **No new dependencies**: All changes are within existing modules

**Architecture Decisions**:
- **Registry-based detection over heuristic**: Continue using the prefix-based `MCP_REGISTRY` pattern rather than trying to auto-detect unknown MCP tools. This keeps detection deterministic and testable.
- **Judge prompt augmentation over output post-processing**: Instead of trying to transform simulated output before judging, we augment the judge's understanding. This is simpler and more robust.
- **Optional metadata over required**: `mcpSimulation` is optional to maintain backward compatibility with existing benchmark history files.

## Implementation Phases

### Phase 1: Registry expansion (US-003)
1. Add Notion, Jira, Confluence, Figma, and Sentry entries to `MCP_REGISTRY`
2. Add unit tests for each new server detection

### Phase 2: MCP-aware eval generation (US-001)
1. Modify `buildEvalInitPrompt` to call `detectMcpDependencies`
2. When MCP deps found, append simulation-aware generation instructions
3. Add unit tests verifying prompt augmentation and non-regression

### Phase 3: Simulation-aware judging (US-002)
1. Create `buildJudgeSystemPrompt` function in `judge.ts`
2. Modify `judgeAssertion` to accept optional MCP dependency info
3. Add unit tests for augmented vs. standard judge prompts

### Phase 4: Fair comparison (US-004)
1. Detect MCP deps from skill content in comparison flow
2. Augment comparator system prompt with simulation context
3. Add unit tests for MCP-aware comparison prompts

### Phase 5: Benchmark metadata (US-005)
1. Add `mcpSimulation` to `BenchmarkResult` interface
2. Populate during benchmark runs
3. Verify backward compatibility with history/stats

## Testing Strategy

- **Unit tests (TDD)**: Every module change gets tests written first
  - `mcp-detector.test.ts`: New server detection tests
  - `prompt-builder.test.ts`: MCP-aware generation prompt tests
  - `judge.test.ts`: Simulation-aware judge prompt tests
  - `comparator.test.ts`: MCP-aware comparison tests
  - `benchmark.test.ts`: `mcpSimulation` field serialization/deserialization
- **Regression**: All existing tests must continue to pass unchanged
- **Integration**: Manual `vskill eval run` against a known MCP-dependent skill

## Technical Challenges

### Challenge 1: Judge prompt precision
**Solution**: The simulation-aware judge prompt must be specific enough that the LLM evaluates simulation quality (correct tool names, realistic parameters, plausible responses) without being so loose that any output passes. Use concrete examples in the prompt.
**Risk**: Medium -- LLM judge behavior is non-deterministic. Mitigate with multiple test cases.

### Challenge 2: Backward compatibility of benchmark history
**Solution**: `mcpSimulation` is optional. `listHistory`, `computeStats`, and `computeRegressions` already use optional chaining patterns. Add a null check in any new code that reads the field.
**Risk**: Low -- TypeScript's type system enforces optional field handling.
