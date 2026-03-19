# Implementation Plan: Unified Advisor Command

## Overview

A new `src/core/advisor/` module that programmatically invokes existing core functions (doctor, qa-runner, dashboard-data, discrepancy detection, docs-health) in parallel, normalizes their heterogeneous outputs into a uniform `AdvisorItem` shape, scores and ranks items by severity and project phase, and returns a prioritized action list. Exposed via `specweave advisor` CLI command and `/sw:advisor` skill.

Composition over duplication: the advisor owns zero diagnostic logic. It is an orchestrator that calls existing modules and ranks their outputs.

## Architecture

### Decision 1: Programmatic Import (not subprocess)

Import core functions directly (`runDoctor()`, `runQA()`, etc.) rather than spawning `specweave doctor` as a subprocess. Rationale:
- Structured data: we get typed objects, not stdout strings to parse
- Performance: no process overhead, shared module cache
- Testability: easy to mock individual collectors in unit tests

This is the same pattern used by `dashboard-data.ts` which imports `JobScheduler`, `NotificationManager`, and `SyncAuditLogger` directly.

### Decision 2: Module Structure

```
src/core/advisor/
  types.ts          # AdvisorItem, AdvisorReport, AdvisorOptions, PhaseType, CollectorResult
  advisor.ts        # Main orchestrator: runAdvisor() — parallel collection, normalization, ranking
  phase-detector.ts # Detects project phase from filesystem + increment signals
  collectors/
    index.ts        # Re-exports all collectors
    doctor-collector.ts       # Wraps runDoctor() → CollectorResult[]
    qa-collector.ts           # Wraps runQA() → CollectorResult[]
    progress-collector.ts     # Reads increment status → CollectorResult[]
    discrepancy-collector.ts  # Reads discrepancy store → CollectorResult[]
    docs-health-collector.ts  # Wraps EnterpriseDocAnalyzer → CollectorResult[]
  ranker.ts         # Priority scoring algorithm
  formatter.ts      # CLI output formatting (terminal table / markdown)
  index.ts          # Public API re-exports
```

Follows the doctor pattern: orchestrator (`advisor.ts`) delegates to collectors (like doctor delegates to checkers). Each collector implements a `Collector` interface, exactly mirroring the `HealthChecker` interface pattern.

### Decision 3: Collector Interface (mirrors HealthChecker)

```typescript
export interface Collector {
  name: string;
  collect(projectRoot: string, options: AdvisorOptions): Promise<CollectorResult>;
}

export interface CollectorResult {
  source: string;          // e.g. 'doctor', 'qa', 'progress'
  items: RawAdvisorItem[]; // Heterogeneous items from this source
  durationMs: number;
  error?: string;          // If collector failed gracefully
}

export interface RawAdvisorItem {
  title: string;
  description: string;
  severity: 'critical' | 'high' | 'medium' | 'low' | 'info';
  category: 'health' | 'quality' | 'progress' | 'docs' | 'discrepancy';
  source: string;
  fixCommand?: string;     // e.g. 'specweave doctor --fix'
  location?: string;       // e.g. 'spec.md:45'
}
```

### Decision 4: Phase Detection Algorithm

Detect project phase from filesystem signals. No ML, no LLM calls — pure heuristic, deterministic, fast.

```typescript
type PhaseType = 'fresh-init' | 'brownfield' | 'active-dev' | 'mature';
```

| Signal | fresh-init | brownfield | active-dev | mature |
|--------|-----------|------------|------------|--------|
| Increments exist | 0 | 0-2 | 3+ | 10+ |
| Active increments | 0 | 0 | 1+ | 0-1 |
| Completed increments | 0 | 0 | 1+ | 8+ |
| Living docs exist | no | maybe | yes | yes |
| Config has sync enabled | no | no | maybe | yes |
| Git commits in .specweave/ | <5 | <10 | 10-100 | 100+ |

Algorithm:
1. Count increments (total, active, completed, archived)
2. Check for living docs directory
3. Check config.json for sync/external integrations
4. Apply weighted scoring — highest score wins
5. Return phase + confidence (0-1)

Phase affects ranking weights (see Decision 5).

### Decision 5: Priority Ranking Algorithm

Each `RawAdvisorItem` gets a numeric score (0-100) computed as:

```
score = baseSeverityScore + phaseBoost + recencyBoost
```

**Base severity scores**: critical=90, high=70, medium=50, low=30, info=10

**Phase boost** (adds 0-15 points based on phase relevance):

| Category | fresh-init | brownfield | active-dev | mature |
|----------|-----------|------------|------------|--------|
| health   | +15       | +10        | +5         | +5     |
| quality  | +5        | +5         | +15        | +10    |
| progress | +0        | +0         | +15        | +5     |
| docs     | +5        | +15        | +5         | +10    |
| discrepancy | +0    | +10        | +10        | +15    |

**Recency boost**: Items from the currently active increment get +5.

Final list is sorted by score descending, capped at `--limit` (default 10).

### Decision 6: CLI Command — `specweave advisor`

Named `advisor` (not `help`) to avoid conflict with commander.js built-in `.help()` / `--help`. The skill is `/sw:advisor`.

```
specweave advisor [options]

Options:
  --json          Output as JSON
  --verbose       Show all items (not just top 10)
  --limit <n>     Max items to show (default: 10)
  --phase <type>  Override auto-detected phase
  --skip-slow     Skip slow collectors (docs-health, qa)
  --no-cache      Bypass result cache
```

Registration pattern: `registerAdvisorCommand(program: Command)` in `src/cli/commands/advisor.ts`, following the exact pattern of `registerDoctorCommand` and `registerHealthCommand`.

### Decision 7: Caching Strategy

Follow the `DashboardDataProvider` TTL cache pattern:

```typescript
interface CacheEntry<T> {
  data: T;
  expiresAt: number;
}
```

- **Doctor results**: 5-minute TTL (filesystem checks are fast but not instant)
- **QA results**: 10-minute TTL (expensive, changes rarely between runs)
- **Progress data**: 30-second TTL (changes frequently during active work)
- **Discrepancies**: 5-minute TTL
- **Docs health**: 10-minute TTL (slowest collector)

Cache stored in-memory (module-level Map). Cache key = `${projectRoot}:${collectorName}`. Invalidated by `--no-cache` flag.

### Decision 8: No ADR Created

This feature follows established patterns (doctor checkers, dashboard aggregation, TTL caching). No novel architectural decisions warrant a standalone ADR. The plan.md serves as the design record.

## Components

### advisor.ts (Orchestrator)

Main export: `runAdvisor(projectRoot: string, options: AdvisorOptions): Promise<AdvisorReport>`

1. Detect phase via `detectPhase(projectRoot)`
2. Run all collectors in parallel via `Promise.allSettled()` (fault-tolerant — one failing collector does not block others)
3. Flatten `CollectorResult[]` into `RawAdvisorItem[]`
4. Score and rank via `rankItems(items, phase, options)`
5. Build `AdvisorReport` with items, phase, summary stats, timing

### phase-detector.ts

Export: `detectPhase(projectRoot: string): Promise<{ phase: PhaseType; confidence: number; signals: Record<string, number | boolean> }>`

Pure filesystem reads. No external calls. Testable with fixture directories.

### collectors/*

Each collector:
1. Imports the relevant core module
2. Calls it with appropriate options (e.g., `runDoctor(projectRoot, { quick: true })`)
3. Maps the source-specific output to `RawAdvisorItem[]`
4. Returns `CollectorResult` with timing

**doctor-collector**: Maps `CategoryResult[]` → items where status is 'warn' or 'fail'
**qa-collector**: Maps `QualityAssessment` dimension scores below 70 → items. Only runs if active increment exists.
**progress-collector**: Reads `.specweave/increments/*/metadata.json` directly. Flags: stale increments (>7 days no activity), blocked tasks, WIP limit violations.
**discrepancy-collector**: Reads `.specweave/state/discrepancies.json` if it exists. Maps pending discrepancies to items.
**docs-health-collector**: Imports `EnterpriseDocAnalyzer`. Maps health score < 70 and individual issues to items.

### ranker.ts

Export: `rankItems(items: RawAdvisorItem[], phase: PhaseType, options: AdvisorOptions): AdvisorItem[]`

Applies scoring formula, sorts descending, applies limit. Returns enriched `AdvisorItem` (adds `score`, `rank` fields).

### formatter.ts

Export: `formatAdvisorReport(report: AdvisorReport, options: AdvisorOptions): string`

Terminal output with status icons (same `getStatusIcon()` helper from doctor). Groups by category, shows top N items with severity indicator, score, fix command.

## Technology Stack

- **Language**: TypeScript (ESM, `.js` import extensions)
- **Libraries**: chalk (terminal colors), ora (spinners during collection) — both already in project deps
- **Testing**: Vitest with vi.mock() for collector isolation
- **No new dependencies required**

## Implementation Phases

### Phase 1: Foundation (T-001 through T-004)
- types.ts with all interfaces
- phase-detector.ts with filesystem heuristics
- ranker.ts with scoring algorithm
- Unit tests for phase detection and ranking

### Phase 2: Collectors (T-005 through T-009)
- Doctor collector
- Progress collector (simplest — filesystem only)
- QA collector
- Discrepancy collector
- Docs-health collector
- Unit tests for each collector with mocked core functions

### Phase 3: Orchestrator + CLI (T-010 through T-012)
- advisor.ts orchestrator with parallel collection + caching
- CLI command registration in specweave.js
- formatter.ts for terminal output
- Integration test: full advisor run on test fixture project

### Phase 4: Skill + Polish (T-013 through T-014)
- `/sw:advisor` skill markdown (plugins/specweave/commands/advisor.md)
- Edge cases: no .specweave dir, empty project, all collectors fail gracefully

## Testing Strategy

- **Unit tests**: Each collector mocked in isolation. Phase detector with fixture dirs. Ranker with known inputs.
- **Integration test**: Full `runAdvisor()` on a fixture `.specweave/` directory with known issues.
- **No E2E**: CLI tested via unit test of `advisorCommand()` function, not subprocess.
- **Coverage target**: 90% (per increment config)

## Technical Challenges

### Challenge 1: Heterogeneous Source Output Normalization
**Problem**: Doctor returns `CategoryResult[]`, QA returns `QualityAssessment`, progress is raw filesystem reads — all different shapes.
**Solution**: Each collector owns the mapping to `RawAdvisorItem`. The advisor never touches source-specific types. Collector tests verify mapping correctness.

### Challenge 2: Graceful Degradation
**Problem**: If docs-health analyzer crashes (e.g., no living docs), the entire advisor should not fail.
**Solution**: `Promise.allSettled()` in the orchestrator. Failed collectors produce a single info-level item: "docs-health collector unavailable: [error]". The report always returns, even if all collectors fail.

### Challenge 3: Performance Budget
**Problem**: Running all checks serially would take 10+ seconds.
**Solution**: All collectors run in parallel. Fast collectors (progress, discrepancies) return in <100ms. Slow collectors (docs-health, qa) have TTL caching. The `--skip-slow` flag excludes docs-health and qa entirely. Target: <2s for cached runs, <5s for uncached.
