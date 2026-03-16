# Plan: Skill-Gen LLM Pivot

## Architecture Overview

Replace the hardcoded keyword-matching pipeline in `src/core/skill-gen/` with LLM-based pattern extraction using the existing `analyzeStructured` abstraction. The change is confined to 5 files (4 existing + 1 new) with no external API surface changes.

```
                     LifecycleHookDispatcher.onIncrementDone()
                                    |
                                    v
                          +------------------+
                          | SignalCollector   |
                          |  .collect()       |---- LLM call via analyzeStructured
                          |  .collectSeed()   |     (batched docs, JSON Schema)
                          +--------+---------+
                                   |
                          +--------v---------+
                          | SuggestionEngine  |
                          |  .evaluate()      |---- reads from shared store
                          +------------------+

     +-----------------+          +-----------------+
     | DriftDetector    |          | utils.ts (NEW)   |
     |  .check()        |          |  collectMdFiles  |
     |  returns         |<---------|  loadStore       |
     |  DriftResult[]   |          |  saveStore       |
     +-----------------+          |  Zod schemas     |
                                  |  sanitizeString  |
                                  |  estimateTokens  |
                                  +-----------------+
```

## Design Decisions

### D-001: Single batched LLM call over per-file analysis

Concatenate all living doc content (up to ~50K tokens) into a single `analyzeStructured` call. Chunk at document boundaries only when total exceeds budget.

**Why**: Minimizes latency and cost. A typical project has <50 living docs totaling <30K tokens -- well within a single Haiku call. Per-file calls would be 10-50x more expensive and slower.

**Trade-off**: Loses per-file attribution from the LLM itself, but the caller already knows which files were included. Evidence is tracked by the collector, not the LLM.

### D-002: Skip-and-warn on LLM unavailability (no keyword fallback)

When the LLM is unavailable (no API key, network error, consent denied), skip pattern detection entirely and log a warning. Do NOT fall back to keyword matching.

**Why**: The spec explicitly states "clean failure is better than misleading results." Keeping the keyword fallback would preserve the exact false-positive problem we are eliminating.

### D-003: Zod schema for signal store validation, JSON Schema for LLM structured output

Use Zod for validating `skill-signals.json` on load (runtime safety) and for internal type guards. Use the existing `JSONSchemaType` interface for `analyzeStructured` calls since that is what the provider abstraction expects.

**Why**: `analyzeStructured` takes `JSONSchemaType<T>`, not Zod schemas. Converting Zod to JSON Schema adds a dependency (zod-to-json-schema) for no benefit. Use each tool where it fits.

### D-004: Confidence = distinct source files / threshold

Replace the current `incrementIds.length / minSignalCount` formula with `uniqueSourceFiles.length / minSignalCount` (capped at 1.0). The `uniqueSourceFiles` field is a new optional `string[]` on `SignalEntry` defaulting to `[]`.

**Why**: The current formula rewards seeing the same pattern in the same file across multiple increment closures. A pattern appearing in 5 different files is stronger evidence than the same pattern seen 5 times in 1 file.

### D-005: DriftDetector returns DriftResult[] instead of console.warn

Change `check()` return type from `Promise<void>` to `Promise<DriftResult[]>`. Add a static exclusion list of ~30 common PascalCase words. Caller decides how to present results.

**Why**: The current console.warn is untestable and couples presentation to detection. Structured returns enable programmatic consumers (e.g., grill reports, CI checks).

### D-006: Evidence array cap at 20 entries (FIFO eviction)

When new evidence arrives and the array is at capacity, evict the oldest entries first.

**Why**: Prevents unbounded growth in long-running projects. 20 entries provide sufficient audit trail without bloating the store file.

## Component Changes

### 1. `utils.ts` (NEW)

Shared utilities extracted from signal-collector and drift-detector.

**Exports**:
- `collectMarkdownFiles(dir: string): Promise<string[]>` -- recursive markdown file discovery
- `loadSignalStore(projectRoot: string): Promise<SignalStore>` -- load + Zod validate + fallback to empty
- `saveSignalStore(projectRoot: string, store: SignalStore): Promise<void>` -- atomic write with mkdir
- `sanitizeString(s: string, maxLen?: number): string` -- strip control chars, truncate to 200 chars
- `estimateTokenCount(text: string): number` -- rough char/4 estimate for budget checks
- `capEvidence(evidence: string[], cap?: number): string[]` -- FIFO cap at 20
- `SignalStoreSchema` -- Zod schema for runtime validation
- `SignalEntrySchema` -- Zod schema for individual entries
- `LLM_PATTERN_SCHEMA` -- JSON Schema object for `analyzeStructured` response shape
- `TOKEN_BUDGET` -- constant 50000
- `MAX_EVIDENCE` -- constant 20
- `MAX_STRING_LENGTH` -- constant 200

**Zod schema for SignalStore**:
```typescript
const SignalEntrySchema = z.object({
  id: z.string(),
  pattern: z.string(),
  category: z.string(),
  description: z.string(),
  incrementIds: z.array(z.string()),
  firstSeen: z.string(),
  lastSeen: z.string(),
  confidence: z.number().min(0).max(1),
  evidence: z.array(z.string()),
  uniqueSourceFiles: z.array(z.string()).optional().default([]),
  suggested: z.boolean(),
  declined: z.boolean(),
  generated: z.boolean(),
});
```

**JSON Schema for LLM response** (passed to `analyzeStructured`):
```typescript
const LLM_PATTERN_SCHEMA: JSONSchemaType<LLMPatternResponse> = {
  type: 'object',
  properties: {
    patterns: {
      type: 'array',
      items: {
        type: 'object',
        properties: {
          category: { type: 'string', description: 'Kebab-case category slug' },
          name: { type: 'string', description: 'Short pattern name' },
          description: { type: 'string', description: 'What and why' },
          evidence: { type: 'array', items: { type: 'string' } },
        },
        required: ['category', 'name', 'description', 'evidence'],
      },
    },
  },
  required: ['patterns'],
};
```

### 2. `types.ts` (MODIFY)

Changes:
- **Add** `uniqueSourceFiles?: string[]` to `SignalEntry` interface (optional, defaults to `[]`)
- **Add** `DriftResult` type: `{ skillFile: string; staleRefs: string[]; validRefs: string[] }`
- **Add** `LLMPatternResponse` type: `{ patterns: Array<{ category: string; name: string; description: string; evidence: string[] }> }`
- **Remove** `SignalCategory` type union (categories become dynamic strings, `category` field becomes plain `string`)
- **Remove** the `| string` escape hatch comment since all categories are now dynamic

### 3. `signal-collector.ts` (MODIFY)

Major rewrite. Changes:
- **Remove** `PATTERN_CATEGORIES` constant and `MIN_KEYWORD_HITS`
- **Remove** private `loadStore()`, `saveStore()`, `collectMarkdownFiles()` -- use shared utils
- **Remove** `detectPatterns()` keyword-based method
- **Add** LLM-based `detectPatternsLLM()`:
  1. Collect markdown files via `collectMarkdownFiles()`
  2. Read content, estimate tokens via `estimateTokenCount()`
  3. If total <= TOKEN_BUDGET: single `analyzeStructured` call
  4. If total > TOKEN_BUDGET: chunk at document boundaries, multiple calls, merge results
  5. Deduplicate by `category + name`
  6. Sanitize all strings via `sanitizeString()`
- **Add** `collectSeed()` public method:
  1. Scans ALL living docs in one pass (same LLM call path as regular collection)
  2. Creates signals with `firstSeen` = now, no increment ID association
  3. Deduplicates against existing store entries by `category + name`
- **Update** `upsertSignal()`:
  - Track `uniqueSourceFiles` (Set semantics, dedup on insert)
  - Confidence = `uniqueSourceFiles.length / minSignalCount` (capped at 1.0)
  - Cap evidence via `capEvidence()`
- **Update** `collect()`:
  - Load LLM config via `loadLLMConfig(projectRoot)`
  - If no config or provider unavailable: log warning, return early (no error)
  - Create provider via `createProvider(config)`
  - Pass provider to `detectPatternsLLM()`

**LLM prompt design** (system prompt + user content):
```
System: You are a software architecture analyst. Given project documentation,
identify recurring implementation patterns. Return structured JSON only.

User: Analyze these project documents and identify recurring patterns.
For each pattern provide: category (kebab-case slug), name (short identifier),
description (1-2 sentences explaining what the pattern is and why it matters),
and evidence (list of relevant quotes or references from the docs, max 5 per pattern).

<documents>
--- file: .specweave/docs/internal/specs/auth-module.md ---
[content]
--- file: .specweave/docs/internal/specs/api-gateway.md ---
[content]
</documents>
```

**Constructor changes**: Accept optional `LLMProvider` for dependency injection in tests.

### 4. `drift-detector.ts` (MODIFY)

Changes:
- **Remove** private `collectMarkdownFiles()` -- use shared import
- **Add** `PASCAL_CASE_EXCLUSIONS` constant: ~30 common PascalCase words that trigger false positives (TypeScript, JavaScript, SpecWeave, ReactComponent, NextJs, NodeModule, ErrorBoundary, PascalCase, CamelCase, etc.)
- **Update** `extractModuleReferences()`: filter against exclusion list
- **Change** `check()` return type: `Promise<void>` -> `Promise<DriftResult[]>`
- **Remove** `console.warn` calls -- return structured results instead
- **Add** `validRefs` to each result (refs that DO appear in docs, for context)

### 5. `suggestion-engine.ts` (MODIFY)

Changes:
- **Remove** private `loadStore()`, `saveStore()` -- use shared imports from `utils.ts`
- **Update** qualifying filter: use `uniqueSourceFiles.length >= minCount` instead of `incrementIds.length >= minCount` (with fallback to incrementIds for backward compat)

### 6. Integration Point: `LifecycleHookDispatcher.ts` (NO CHANGE)

Lines 329-355 remain unchanged. The dispatcher already imports `SignalCollector` and calls `collector.collect(incrementId)`. The internal implementation change is transparent.

The only new integration is the `--seed` CLI flag which routes to `collectSeed()` -- this is handled in the CLI command layer, not the hook dispatcher.

## Data Flow

### Regular collection (on increment close)

```
onIncrementDone(incrementId)
  +-> SignalCollector.collect(incrementId)
        +-> loadSignalStore()           -- from utils.ts, Zod-validated
        +-> collectMarkdownFiles()      -- from utils.ts
        +-> read file contents
        +-> estimateTokenCount()        -- from utils.ts
        +-> chunk if > TOKEN_BUDGET
        +-> provider.analyzeStructured() -- via LLM abstraction
        +-> sanitizeString() each field  -- from utils.ts
        +-> deduplicate by category+name
        +-> upsertSignal() for each pattern
        |     +-> update uniqueSourceFiles (Set semantics)
        |     +-> recalculate confidence = files/threshold
        |     +-> capEvidence(20)
        +-> pruneIfNeeded()
        +-> saveSignalStore()           -- from utils.ts
```

### Seed mode (manual invocation)

```
CLI --seed flag
  +-> SignalCollector.collectSeed()
        +-> loadSignalStore()
        +-> collectMarkdownFiles()      -- ALL docs
        +-> [same LLM call path as regular]
        +-> for each pattern:
        |     +-> skip if category+name already in store
        |     +-> create new signal (firstSeen=now, no incrementId)
        +-> saveSignalStore()
```

## Error Handling Strategy

| Error Source | Handling | User Impact |
|---|---|---|
| No LLM config | Log warning, skip pattern detection | None (silent skip) |
| Consent denied | Log warning, skip | None |
| Network/API error | Catch in `collect()`, log warning | None (increment closes normally) |
| `analyzeStructured` parse failure | Catch, log, skip that chunk | Partial results from other chunks |
| Malformed store on disk | Zod validation fails, backup `.bak`, start fresh | Loses old signals, warns |
| LLM returns garbage strings | `sanitizeString()` strips control chars, caps length | Safe but possibly low-quality |

## Testing Strategy

All tests use mocked LLM providers -- no real API calls in CI.

### Unit Tests (Vitest)

1. **utils.test.ts** (NEW):
   - `collectMarkdownFiles`: finds .md files recursively, skips non-.md
   - `loadSignalStore`: valid JSON, corrupt JSON (falls back), missing file (empty store)
   - `saveSignalStore`: creates dir, writes JSON
   - `sanitizeString`: strips control chars, truncates, handles empty/null
   - `estimateTokenCount`: rough estimate matches expectations
   - `capEvidence`: FIFO eviction at cap, no-op below cap

2. **signal-collector.test.ts** (REWRITE):
   - LLM call: correct prompt structure, schema passed to `analyzeStructured`
   - Batching: single call when under budget, multiple when over
   - Deduplication: same category+name merged
   - Confidence: tracks uniqueSourceFiles, calculates correctly
   - Evidence cap: stops at 20
   - No LLM config: skips gracefully
   - LLM failure: catches, warns, does not throw
   - Seed mode: scans all docs, deduplicates against existing store

3. **drift-detector.test.ts** (UPDATE):
   - Exclusion list: common PascalCase words not flagged
   - Returns `DriftResult[]` with staleRefs and validRefs
   - No console.warn calls (spy verification)
   - Uses shared `collectMarkdownFiles`

4. **suggestion-engine.test.ts** (UPDATE):
   - Uses `uniqueSourceFiles.length` for qualifying filter
   - Backward compat: works with store entries missing `uniqueSourceFiles`

5. **integration.test.ts** (UPDATE):
   - TypeScript project fixture: detects error-handling, testing, architecture patterns
   - Python ML fixture: detects data-pipeline, model-training patterns
   - Empty project: no LLM call, zero signals
   - Full pipeline: signal -> suggestion -> store persistence

### Mock Strategy

```typescript
const mockProvider: LLMProvider = {
  name: 'anthropic',
  defaultModel: 'haiku',
  analyze: vi.fn(),
  analyzeStructured: vi.fn().mockResolvedValue({
    data: {
      patterns: [
        { category: 'error-handling', name: 'boundary-pattern',
          description: 'Uses error boundaries', evidence: ['ref1'] },
      ],
    },
    usage: { inputTokens: 100, outputTokens: 50, totalTokens: 150 },
    estimatedCost: 0.001,
  }),
  estimateCost: vi.fn().mockReturnValue(0),
  isAvailable: vi.fn().mockResolvedValue(true),
  getStatus: vi.fn().mockResolvedValue({ available: true }),
};
```

## Implementation Order

1. **T-001**: Create `utils.ts` with shared utilities and Zod schemas
2. **T-002**: Update `types.ts` (add `uniqueSourceFiles`, `DriftResult`, `LLMPatternResponse`; remove `SignalCategory` union)
3. **T-003**: Rewrite `signal-collector.ts` with LLM-based detection and seed mode
4. **T-004**: Update `drift-detector.ts` with exclusion list and structured returns
5. **T-005**: Update `suggestion-engine.ts` to use shared utils and file-based confidence
6. **T-006**: Write/update all unit tests
7. **T-007**: Write integration tests with realistic fixtures

## Risk Mitigations

- **PATTERN_CATEGORIES removal**: Search all files importing from `types.ts` for `SignalCategory` references before removing. The only consumers are within `src/core/skill-gen/` (confirmed by reading the code).
- **Backward compatibility**: `uniqueSourceFiles` is optional with `[]` default in both TypeScript interface and Zod schema. Old stores load without error.
- **LLM quality**: Integration tests use realistic fixture docs and verify expected pattern categories appear. Prompt will be iterated during implementation if test fixtures reveal gaps.
