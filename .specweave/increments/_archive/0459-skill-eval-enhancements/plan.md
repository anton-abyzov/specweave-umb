# Architecture Plan: 0459-skill-eval-enhancements

## Overview

Four feature areas added to the vskill Eval UI (React 19 + Vite frontend, Node.js http backend). All follow the existing architectural patterns: route files for backend, extracted components for frontend, SSE for streaming, `createLlmClient(overrides)` for per-request model switching.

---

## Architecture Decisions

### AD-1: Separate Route Files for New Endpoints

**Decision**: New endpoints go in `improve-routes.ts` and `model-compare-routes.ts`, registered via the same `Router` instance in `eval-server.ts`.

**Rationale**: `api-routes.ts` is 719 lines (limit 1500). Adding ~100 lines for improve + compare endpoints would push it past 800 and mix concerns. MCP dependency detection is a GET endpoint (10 lines) that fits within `api-routes.ts`.

**Pattern**: Each route file exports a `registerXxxRoutes(router, root)` function matching the existing `registerRoutes` signature. `eval-server.ts` calls all registrations sequentially before `createServer`.

### AD-2: MCP Detector as Pure Function in `src/eval/mcp-detector.ts`

**Decision**: MCP dependency detection is a pure function `detectMcpDependencies(skillContent: string)` in the eval domain layer, not in the server layer.

**Rationale**: Pure functions are trivially testable with TDD. The detector has no I/O -- it takes SKILL.md text and returns structured dependency data. The GET endpoint in `api-routes.ts` simply reads SKILL.md and calls this function.

### AD-3: Frontend Diff Without External Libraries

**Decision**: Line-by-line diff computed in the browser via a simple LCS (longest common subsequence) algorithm, limited to files under ~500 lines (SKILL.md files).

**Rationale**: Spec requires no new runtime deps. SKILL.md files are small (typically 20-100 lines). A basic `O(n*m)` LCS diffing two arrays of lines is fast enough. The diff utility is a pure function in `src/eval-ui/src/utils/diff.ts`, testable independently.

### AD-4: Sequential Model Execution for Compare (Not Parallel)

**Decision**: Model comparison runs Model A, then Model B sequentially with SSE progress updates between.

**Rationale**: `claude-cli` provider spawns a child process and only supports one invocation at a time. Parallel execution would fail for the default provider. SSE events let the UI show "Model A running..." / "Model B running..." states.

### AD-5: No Shared State Mutation for Model Comparison

**Decision**: The `/compare-models` endpoint creates its own `LlmClient` instances via `createLlmClient(overrides)` for each model instead of mutating `currentOverrides`.

**Rationale**: `currentOverrides` is module-level shared state in `api-routes.ts`. Model comparison runs two different models -- mutating shared state would break concurrent requests and leave the server in an unexpected model configuration. `createLlmClient` already accepts per-call overrides, so no new API needed.

### AD-6: Improvement Prompt Includes Failed Assertions Only

**Decision**: The improvement endpoint auto-includes up to 10 most recently failed assertions from the latest benchmark file, not all eval cases.

**Rationale**: Context window safety -- including all failures from all history would blow past token limits. The latest benchmark file is already on disk, readable via `readBenchmark()`. 10 failures provide enough signal for the LLM to identify patterns.

### AD-7: Extract `resolveSkillDir` to Shared Module

**Decision**: Move the `resolveSkillDir` helper from `api-routes.ts` into a new `src/eval-server/skill-resolver.ts` so all route files can import it.

**Rationale**: `improve-routes.ts` and `model-compare-routes.ts` both need to resolve skill directories. Duplicating the function violates DRY. Extracting it before adding new route files prevents import cycles and keeps each route file focused on its endpoints.

---

## Component Architecture

```
eval-server/                          eval-ui/src/
  api-routes.ts (modify +15 lines)      pages/SkillDetailPage.tsx (modify +40 lines)
  improve-routes.ts (NEW ~150 lines)    components/SkillContentViewer.tsx (NEW ~200)
  model-compare-routes.ts (NEW ~120)    components/SkillImprovePanel.tsx (NEW ~300)
  skill-resolver.ts (NEW ~15 lines)     components/ModelCompareModal.tsx (NEW ~250)
  eval-server.ts (modify +6 lines)      components/McpDependencies.tsx (NEW ~150)
                                        utils/diff.ts (NEW ~60)
eval/                                   api.ts (modify +20 lines)
  mcp-detector.ts (NEW ~100 lines)      types.ts (modify +25 lines)
```

---

## Feature 1: Skill Definition Viewer

### Data Flow

```
SkillDetailPage
  |-- useEffect: api.getSkillDetail(plugin, skill) -> { skillContent }
  |-- <SkillContentViewer content={skillContent} />
        |-- parseFrontmatter(content) -> { metadata, body }
        |-- Render metadata cards (description, model, context, allowed-tools pills)
        |-- Render body in <pre> block
        |-- Collapsible wrapper (default expanded)
```

### Backend Changes

None. `GET /api/skills/:plugin/:skill` already returns `{ skillContent }` (line 209-217 of api-routes.ts).

### Frontend: `SkillContentViewer.tsx` (~200 lines)

- Props: `{ content: string; defaultExpanded?: boolean }`
- `parseFrontmatter(content)`: splits on `---` delimiters, extracts key-value pairs via regex (no YAML library). Returns `{ metadata: Record<string, string | string[]>, body: string }`.
- For `allowed-tools`: splits comma-separated or newline-list values, renders each as a pill/chip.
- Collapsible section with chevron toggle, default expanded.
- Body displayed in a styled `<pre>` with `max-height: 400px; overflow-y: auto`.

### SkillDetailPage Modifications

- Add `skillContent` state, load in existing `useEffect` via `api.getSkillDetail()`.
- Insert `<SkillContentViewer>` between breadcrumb and action bar (~15 lines added).
- Add `refreshSkillContent()` callback for Feature 2's apply action.

---

## Feature 2: AI-Powered Skill Improvement

### Data Flow

```
SkillDetailPage
  |-- <SkillImprovePanel plugin skill skillContent onApplied />
        |-- Model picker (reuses ProviderInfo from config)
        |-- "Improve" button
        |-- POST /api/skills/:plugin/:skill/improve
        |     Body: { provider, model }
        |     Response: { original, improved, reasoning }
        |-- computeDiff(original, improved) -> DiffLine[]
        |-- Render unified diff view
        |-- "Apply" -> POST /api/skills/:plugin/:skill/apply-improvement
        |     Body: { content: improved }
        |     Response: { ok: true }
        |-- "Discard" -> close panel
```

### Backend: `improve-routes.ts` (~150 lines)

**`POST /api/skills/:plugin/:skill/improve`**:
1. Read SKILL.md from disk via `resolveSkillDir`
2. Read latest benchmark via `readBenchmark(skillDir)`
3. Extract up to 10 failed assertions from benchmark cases
4. Construct improvement prompt with skill content and failures
5. Call `createLlmClient({ provider, model })` with body overrides
6. Return `{ original, improved, reasoning }`

**`POST /api/skills/:plugin/:skill/apply-improvement`**:
1. Read `{ content }` from request body
2. Validate content is non-empty string
3. Write to SKILL.md path via `writeFileSync`
4. Return `{ ok: true }`

### Frontend: `SkillImprovePanel.tsx` (~300 lines)

- Props: `{ plugin, skill, skillContent, onApplied: (newContent: string) => void }`
- State: `{ open, loading, result, selectedProvider, selectedModel }`
- Model picker: fetches config via `api.getConfig()`, shows provider/model dropdowns
- After receiving response: computes diff using `utils/diff.ts`
- Diff view: maps `DiffLine[]` to colored rows (green bg for added, red bg for removed, gray for unchanged)
- Apply button calls `api.applyImprovement()`, then `onApplied(improved)` to refresh parent

### Frontend: `utils/diff.ts` (~60 lines)

```typescript
export interface DiffLine {
  type: "added" | "removed" | "unchanged";
  content: string;
  lineNumber?: number;
}

export function computeDiff(original: string, improved: string): DiffLine[];
```

Split both strings by `\n`, compute LCS, walk both arrays producing DiffLine entries. No external dependency.

---

## Feature 3: Per-Test-Case Model A/B Comparison

### Data Flow

```
SkillDetailPage
  |-- "Compare Models" button on each eval case
  |-- <ModelCompareModal plugin skill evalCase onClose />
        |-- Two model selectors (provider + model)
        |-- "Compare" button
        |-- POST /api/skills/:plugin/:skill/compare-models (SSE)
        |     Body: { eval_id, modelA: { provider, model }, modelB: { provider, model } }
        |     SSE events: model_a_start, model_a_result, model_b_start, model_b_result, done
        |-- Side-by-side results display
        |-- Dismiss modal (ephemeral, not saved)
```

### Backend: `model-compare-routes.ts` (~120 lines)

**`POST /api/skills/:plugin/:skill/compare-models`** (SSE):
1. Parse body: `{ eval_id, modelA: { provider, model }, modelB: { provider, model } }`
2. Load evals, find eval case by `eval_id`
3. Read SKILL.md, construct system prompt
4. Init SSE response
5. Run Model A: create client via `createLlmClient(modelA)`, generate output, judge assertions, send `model_a_start` and `model_a_result` SSE events
6. Run Model B: same sequence with `modelB`, send `model_b_start` and `model_b_result`
7. Send `done` with both results
8. Results NOT written to history (ephemeral)

### Frontend: `ModelCompareModal.tsx` (~250 lines)

- Props: `{ plugin, skill, evalCase: EvalCase, onClose: () => void }`
- Two independent model selectors (provider + model dropdowns)
- Uses `useSSE` hook for streaming
- State: `idle -> running_a -> running_b -> complete`
- Side-by-side layout: Model A (left), Model B (right)
- Each side: model name, output, assertion pass/fail, duration, tokens
- Dismiss closes, no persistence

---

## Feature 4: MCP Dependency Visibility

### Data Flow

```
SkillDetailPage
  |-- <McpDependencies plugin skill />
        |-- useEffect: api.getMcpDependencies(plugin, skill)
        |-- Render dependency cards or empty state
```

### Backend: `mcp-detector.ts` (Pure Function, ~100 lines)

```typescript
export interface McpDependency {
  server: string;         // "Slack", "Google Workspace", etc.
  url: string;            // "https://mcp.slack.com/mcp"
  transport: "http" | "stdio";
  matchedTools: string[]; // tool names that matched
  configSnippet: string;  // JSON for .mcp.json
}

export function detectMcpDependencies(skillContent: string): McpDependency[];
```

**Known MCP registry** (hardcoded):

| Pattern Prefix | Server | URL | Transport |
|---|---|---|---|
| `slack_` | Slack | `https://mcp.slack.com/mcp` | http |
| `github_` | GitHub | `https://api.githubcopilot.com/mcp/` | http |
| `linear_` | Linear | `https://mcp.linear.app/mcp` | http |
| `gws_`, `drive_`, `gmail_`, `sheets_`, `calendar_`, `chat_` | Google Workspace | `https://mcp.google.com/mcp` | http |

**Detection**: parse `allowed-tools` from frontmatter + scan body for tool name patterns via word-boundary regex. Deduplicate, group by server, generate config snippets.

### Backend: GET Endpoint in `api-routes.ts` (+10 lines)

Add `GET /api/skills/:plugin/:skill/mcp-dependencies` that reads SKILL.md and calls `detectMcpDependencies()`.

### Frontend: `McpDependencies.tsx` (~150 lines)

- Props: `{ plugin: string; skill: string }`
- Fetches dependencies on mount
- Cards: server name, matched tools as pills, "Copy Config" button
- Copy Config: `navigator.clipboard.writeText(configSnippet)`
- Empty state: "No MCP dependencies detected"

---

## File Modifications Summary

### Modified Files

| File | Changes | Est. New Total |
|---|---|---|
| `eval-server.ts` | Import + call `registerImproveRoutes`, `registerModelCompareRoutes` | ~130 lines |
| `api-routes.ts` | Import `detectMcpDependencies` + `resolveSkillDir` from shared, add MCP GET endpoint | ~720 lines |
| `SkillDetailPage.tsx` | Add `skillContent` state, load via API, component slots for viewer/improve/mcp/compare | ~860 lines |
| `api.ts` | Add `improveSkill`, `applyImprovement`, `getMcpDependencies` | ~130 lines |
| `types.ts` | Add `McpDependency`, `ImproveResult`, `ModelCompareResult` interfaces | ~195 lines |

### New Files

| File | Lines (est.) | Purpose |
|---|---|---|
| `src/eval-server/skill-resolver.ts` | ~15 | Shared `resolveSkillDir` function |
| `src/eval-server/improve-routes.ts` | ~150 | Improve + apply endpoints |
| `src/eval-server/model-compare-routes.ts` | ~120 | Model A/B comparison SSE endpoint |
| `src/eval/mcp-detector.ts` | ~100 | Pure MCP dependency detection |
| `src/eval-ui/src/components/SkillContentViewer.tsx` | ~200 | SKILL.md viewer with frontmatter |
| `src/eval-ui/src/components/SkillImprovePanel.tsx` | ~300 | AI improvement with diff |
| `src/eval-ui/src/components/ModelCompareModal.tsx` | ~250 | Model A/B comparison modal |
| `src/eval-ui/src/components/McpDependencies.tsx` | ~150 | MCP dependency display |
| `src/eval-ui/src/utils/diff.ts` | ~60 | Line-by-line diff computation |

### New Test Files

| File | Purpose |
|---|---|
| `src/eval/__tests__/mcp-detector.test.ts` | Detection: known patterns, frontmatter, empty, dedup |
| `src/eval-ui/src/utils/__tests__/diff.test.ts` | Diff: identical, additions, deletions, mixed |

---

## Implementation Order

1. **Extract `resolveSkillDir`** to `skill-resolver.ts` -- prerequisite for Features 2 and 3
2. **Skill Content Viewer** (Feature 1) -- no backend changes, establishes `skillContent` state in SkillDetailPage
3. **MCP Detector + Dependencies** (Feature 4) -- pure function TDD, simple GET endpoint
4. **Skill Improvement** (Feature 2) -- new route file, diff utility, improve panel
5. **Model A/B Comparison** (Feature 3) -- SSE endpoint + modal, most self-contained

---

## Testing Strategy

### TDD (RED -> GREEN -> REFACTOR)

**Unit tests** (Vitest):
- `mcp-detector.test.ts`: each known pattern, combined patterns, empty content, frontmatter-only, body-only, config snippet format
- `diff.test.ts`: identical strings, pure additions, pure deletions, mixed edits, empty inputs
- `improve-routes` integration: mock `createLlmClient`, verify prompt construction, response format, file write
- `model-compare-routes` integration: mock `createLlmClient`, verify sequential execution, SSE events, no history write

**Manual verification gates**:
- Load skill detail page -> SKILL.md content displayed
- View slack-messaging skill -> Slack MCP dependency shown
- Click "Improve Skill" -> diff displayed, apply writes to disk
- Click "Compare Models" -> side-by-side model outputs

---

## Risk Mitigation

| Risk | Mitigation |
|---|---|
| `resolveSkillDir` extraction breaks imports | Extract in its own commit, run tests immediately |
| LLM returns unparseable improvement | Wrap in try/catch, return raw text as `improved` with error flag |
| Diff too slow on large files | SKILL.md <200 lines; guard falls back to "show both" for >1000 lines |
| SSE drops during model comparison | `useSSE` handles AbortError; show partial results |
| claude-cli timeout during comparison | Existing 120s timeout in `createClaudeCliClient` handles this |
