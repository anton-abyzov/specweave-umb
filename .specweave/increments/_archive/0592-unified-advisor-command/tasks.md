# Tasks: Unified Advisor Command

## Task Notation

- `[T###]`: Task ID
- `[P]`: Parallelizable
- `[ ]`: Not started
- `[x]`: Completed
- Model hints: haiku (simple), sonnet (default), opus (complex reasoning)

---

## Phase 1: Foundation — Types, Phase Detector, Ranker

### T-001: Define core types (types.ts)

**Description**: Create `src/core/advisor/types.ts` with all interfaces and type aliases needed by the advisor module.

**Implementation Details**:
- `PhaseType = 'fresh-init' | 'brownfield' | 'active-dev' | 'mature'`
- `Collector` interface (mirrors `HealthChecker`): `name`, `collect(projectRoot, options): Promise<CollectorResult>`
- `CollectorResult`: `source`, `items: RawAdvisorItem[]`, `durationMs`, optional `error`
- `RawAdvisorItem`: `title`, `description`, `severity` (critical|high|medium|low|info), `category` (health|quality|progress|docs|discrepancy), `source`, optional `fixCommand`, optional `location`
- `AdvisorItem` extends `RawAdvisorItem` with `score: number`, `rank: number`
- `AdvisorOptions`: `json?`, `verbose?`, `limit?`, `phase?`, `skipSlow?`, `noCache?`
- `AdvisorReport`: `timestamp`, `projectRoot`, `phase`, `phaseConfidence`, `items: AdvisorItem[]`, `summary` (total, bySeverity counts, byCategory counts, collectorsRan, collectorsFailed), `durationMs`
- `PhaseDetectionResult`: `phase: PhaseType`, `confidence: number`, `signals: Record<string, number | boolean>`

**Test Plan**:
- **File**: `tests/unit/core/advisor/types.test.ts`
- **Tests**:
  - **TC-001**: Type imports resolve without error (compile-time only — import and instantiate minimal objects matching each interface)
  - **TC-002**: Severity values are exhaustive (critical, high, medium, low, info)
  - **TC-003**: Category values are exhaustive (health, quality, progress, docs, discrepancy)
  - **TC-004**: PhaseType values are exhaustive (fresh-init, brownfield, active-dev, mature)

**Dependencies**: None
**Status**: [ ] Not Started

---

### T-002: Implement phase-detector.ts [P]

**Description**: Create `src/core/advisor/phase-detector.ts` — pure filesystem heuristic that detects project phase with confidence score.

**Implementation Details**:
- Export `detectPhase(projectRoot: string): Promise<PhaseDetectionResult>`
- Read `.specweave/increments/*/metadata.json` — count total, active (status=active), completed (status=completed/archived)
- Check if `.specweave/docs/` exists and has living docs
- Read `.specweave/config.json` — check for sync/external integration keys
- Run `git log --oneline -- .specweave/` to count commits (cap at 200 for perf)
- Apply weighted scoring table from plan.md Decision 4
- Return `{ phase, confidence, signals }` — confidence = winning score / max possible
- Handle missing `.specweave/` dir gracefully (return `fresh-init`, confidence 0.5)

**Test Plan**:
- **File**: `tests/unit/core/advisor/phase-detector.test.ts`
- **Tests**:
  - **TC-001**: Given no `.specweave/` dir → When detectPhase() called → Then returns `{ phase: 'fresh-init', confidence: 0.5 }`
  - **TC-002**: Given `.specweave/` with 0 increments, no docs → When detectPhase() → Then returns fresh-init
  - **TC-003**: Given `.specweave/` with 1-2 increments (all completed), no active, no living docs → When detectPhase() → Then returns brownfield
  - **TC-004**: Given `.specweave/` with 3+ increments, 1+ active → When detectPhase() → Then returns active-dev
  - **TC-005**: Given `.specweave/` with 10+ increments, 8+ completed, living docs, sync enabled → When detectPhase() → Then returns mature
  - **TC-006**: Signals record contains expected keys (incrementCount, activeCount, completedCount, hasLivingDocs, hasSyncEnabled, gitCommitCount)
  - **TC-007**: Missing config.json is handled gracefully (no throw)
  - **TC-008**: `--phase` override option bypasses detection, returns confidence 1.0

**Dependencies**: T-001
**Status**: [ ] Not Started

---

### T-003: Implement ranker.ts [P]

**Description**: Create `src/core/advisor/ranker.ts` — scoring and sorting algorithm that converts `RawAdvisorItem[]` → `AdvisorItem[]`.

**Implementation Details**:
- Export `rankItems(items: RawAdvisorItem[], phase: PhaseType, options: AdvisorOptions): AdvisorItem[]`
- Base severity scores: critical=90, high=70, medium=50, low=30, info=10
- Phase boost matrix (from plan.md Decision 5): per category × per phase
- Recency boost: +5 if `source` matches active increment id (read from `.specweave/increments/*/metadata.json` where status='active')
- Sort descending by score, assign `rank` (1-based), apply `options.limit` (default 10) — `--verbose` skips limit
- Return enriched `AdvisorItem[]`

**Test Plan**:
- **File**: `tests/unit/core/advisor/ranker.test.ts`
- **Tests**:
  - **TC-001**: Critical severity → base score 90
  - **TC-002**: Health category in fresh-init → +15 phase boost → score = 90+15 = 105 for critical
  - **TC-003**: Progress category in active-dev → +15 phase boost
  - **TC-004**: Items sorted descending by score
  - **TC-005**: Rank assigned starting at 1
  - **TC-006**: Default limit=10 applied when verbose=false and more than 10 items exist
  - **TC-007**: verbose=true returns all items beyond limit
  - **TC-008**: Items with equal scores maintain stable sort (by original order)
  - **TC-009**: Phase boost matrix covers all 5 categories × 4 phases

**Dependencies**: T-001
**Status**: [ ] Not Started

---

## Phase 2: Collectors

### T-004: Implement doctor-collector.ts [P]

**Description**: Create `src/core/advisor/collectors/doctor-collector.ts` — wraps `runDoctor()` and maps warn/fail checks to `RawAdvisorItem[]`.

**Implementation Details**:
- Implements `Collector` interface, `name = 'doctor'`
- Import `runDoctor` from `../../doctor/doctor.js`
- Call `runDoctor(projectRoot, { quick: true })` with timing
- Map `CategoryResult[]` → filter checks where `status === 'warn' || status === 'fail'`
- Map each failing check: `title = check.name`, `description = check.message`, `severity` ('fail'→'high', 'warn'→'medium'), `category = 'health'`, `source = 'doctor'`, `fixCommand = check.fixSuggestion`
- Wrap in `CollectorResult`, include `durationMs`
- Catch and return `error` string if `runDoctor` throws (never let it propagate)

**Test Plan**:
- **File**: `tests/unit/core/advisor/collectors/doctor-collector.test.ts`
- **Tests**:
  - **TC-001**: Given `runDoctor` returns checks with `status=fail` → Then mapped to severity=high items
  - **TC-002**: Given `runDoctor` returns checks with `status=warn` → Then mapped to severity=medium items
  - **TC-003**: Given `runDoctor` returns all pass → Then items array is empty
  - **TC-004**: Given `runDoctor` throws → Then CollectorResult has `error` string, items=[]
  - **TC-005**: `fixSuggestion` from check becomes `fixCommand` on item
  - **TC-006**: `durationMs` is a positive number

**Dependencies**: T-001
**Status**: [ ] Not Started

---

### T-005: Implement progress-collector.ts [P]

**Description**: Create `src/core/advisor/collectors/progress-collector.ts` — filesystem-only collector that flags stale increments, blocked tasks, WIP limit violations.

**Implementation Details**:
- Implements `Collector`, `name = 'progress'`
- Read `.specweave/increments/*/metadata.json` and `tasks.md` directly (no external module dependency)
- Flag stale active increments: `lastActivity` older than 7 days → severity=medium, category=progress
- Flag tasks with `[ ]` items after `[x]` completed items in the same US block (blocked tasks heuristic) → severity=high
- WIP limit violation: more than 3 active increments simultaneously → severity=high
- No external process calls

**Test Plan**:
- **File**: `tests/unit/core/advisor/collectors/progress-collector.test.ts`
- **Tests**:
  - **TC-001**: Given no `.specweave/increments/` → Then items=[], no error
  - **TC-002**: Given active increment with `lastActivity` > 7 days ago → Then 1 item with severity=medium
  - **TC-003**: Given active increment with recent `lastActivity` → Then no stale item
  - **TC-004**: Given 4+ active increments → Then WIP violation item severity=high
  - **TC-005**: Given 3 or fewer active increments → Then no WIP violation

**Dependencies**: T-001
**Status**: [ ] Not Started

---

### T-006: Implement discrepancy-collector.ts [P]

**Description**: Create `src/core/advisor/collectors/discrepancy-collector.ts` — reads `.specweave/state/discrepancies.json` and maps pending discrepancies to items.

**Implementation Details**:
- Implements `Collector`, `name = 'discrepancy'`
- Read `.specweave/state/discrepancies.json` — if missing, return empty items (not an error)
- Map pending/open discrepancies to `RawAdvisorItem`: severity based on discrepancy severity field, category=discrepancy, source=discrepancy
- Include `location` if discrepancy has a file reference
- Limit to 10 discrepancy items max (avoid flooding)

**Test Plan**:
- **File**: `tests/unit/core/advisor/collectors/discrepancy-collector.test.ts`
- **Tests**:
  - **TC-001**: Given no discrepancies.json → Then items=[], no error
  - **TC-002**: Given discrepancies.json with 2 pending entries → Then 2 items returned
  - **TC-003**: Given discrepancies.json with 15 entries → Then max 10 items returned
  - **TC-004**: Given malformed JSON → Then CollectorResult.error is set, items=[]
  - **TC-005**: Discrepancy `location` field populated when source has file path

**Dependencies**: T-001
**Status**: [ ] Not Started

---

### T-007: Implement qa-collector.ts [P]

**Description**: Create `src/core/advisor/collectors/qa-collector.ts` — wraps QA runner, maps dimension scores below 70 to items. Only runs if active increment exists.

**Implementation Details**:
- Implements `Collector`, `name = 'qa'`
- Check if any active increment exists first; if not, return empty items immediately
- Import `runQA` from `../../qa/qa-runner.js`
- Map `QualityAssessment` dimension scores < 70 → items with severity based on score (score < 50 → high, 50-70 → medium), category=quality
- Skip if `options.skipSlow === true`
- Catch errors gracefully

**Test Plan**:
- **File**: `tests/unit/core/advisor/collectors/qa-collector.test.ts`
- **Tests**:
  - **TC-001**: Given no active increment → Then items=[] without calling runQA
  - **TC-002**: Given active increment and QA dimension score 45 → Then item with severity=high
  - **TC-003**: Given active increment and QA dimension score 60 → Then item with severity=medium
  - **TC-004**: Given active increment and all QA dimensions >= 70 → Then items=[]
  - **TC-005**: Given `skipSlow=true` → Then items=[] without calling runQA
  - **TC-006**: Given runQA throws → Then CollectorResult.error set, items=[]

**Dependencies**: T-001
**Status**: [ ] Not Started

---

### T-008: Implement docs-health-collector.ts [P]

**Description**: Create `src/core/advisor/collectors/docs-health-collector.ts` — wraps EnterpriseDocAnalyzer, maps health score < 70 and issues to items.

**Implementation Details**:
- Implements `Collector`, `name = 'docs-health'`
- Import `EnterpriseDocAnalyzer` from `../../../living-docs/enterprise-analyzer.js`
- Skip (return empty) if `.specweave/docs/` doesn't exist — graceful early exit
- Skip if `options.skipSlow === true`
- Map overall health score < 70 and individual doc issues → items, category=docs
- Severity: score < 50 → high, 50-70 → medium, per-issue severity if available
- Catch and return error string gracefully

**Test Plan**:
- **File**: `tests/unit/core/advisor/collectors/docs-health-collector.test.ts`
- **Tests**:
  - **TC-001**: Given no `.specweave/docs/` dir → Then items=[], no analyzer called
  - **TC-002**: Given `skipSlow=true` → Then items=[], no analyzer called
  - **TC-003**: Given analyzer returns health score 40 → Then item with severity=high
  - **TC-004**: Given analyzer returns health score 65 → Then item with severity=medium
  - **TC-005**: Given analyzer returns health score 80 → Then items=[]
  - **TC-006**: Given analyzer throws → Then CollectorResult.error set, items=[]

**Dependencies**: T-001
**Status**: [ ] Not Started

---

### T-009: Create collectors/index.ts [P]

**Description**: Create `src/core/advisor/collectors/index.ts` re-exporting all collectors and a convenience function to get all default collectors.

**Implementation Details**:
- Re-export `DoctorCollector`, `ProgressCollector`, `DiscrepancyCollector`, `QaCollector`, `DocsHealthCollector`
- Export `getDefaultCollectors(): Collector[]` — returns instances of all 5 collectors

**Test Plan**:
- **File**: (covered by integration test in T-012)

**Dependencies**: T-004, T-005, T-006, T-007, T-008
**Status**: [ ] Not Started

---

## Phase 3: Orchestrator, Formatter, CLI

### T-010: Implement advisor.ts orchestrator with caching

**Description**: Create `src/core/advisor/advisor.ts` — main orchestrator that runs collectors in parallel, normalizes outputs, and builds `AdvisorReport`.

**Implementation Details**:
- Export `runAdvisor(projectRoot: string, options: AdvisorOptions): Promise<AdvisorReport>`
- Detect phase via `detectPhase()` (or use `options.phase` override)
- Module-level `Map` cache keyed by `${projectRoot}:${collectorName}` — TTL per collector: doctor=5min, qa=10min, progress=30sec, discrepancy=5min, docs-health=10min
- `--no-cache` flag bypasses cache entirely
- Run all collectors via `Promise.allSettled()` — never let one failure block others
- Settled rejections → info-level item: "{collector} collector unavailable: {reason}"
- Flatten `CollectorResult[]` → `RawAdvisorItem[]`, call `rankItems()`, build `AdvisorReport`
- Report includes `summary.collectorsRan`, `summary.collectorsFailed`

**Test Plan**:
- **File**: `tests/unit/core/advisor/advisor.test.ts`
- **Tests**:
  - **TC-001**: Given all collectors succeed → Then AdvisorReport.items is ranked
  - **TC-002**: Given one collector throws → Then report still returns with remaining items and 1 collectorsFailed
  - **TC-003**: Given all collectors fail → Then report returns with 0 items from collectors (still has error info items), collectorsFailed=5
  - **TC-004**: Cache hit: second call within TTL does not re-invoke collector
  - **TC-005**: `noCache=true` bypasses cached result, collector re-invoked
  - **TC-006**: `options.phase` override passed to ranker (detectPhase not called)
  - **TC-007**: `AdvisorReport.phase` matches detected or overridden phase
  - **TC-008**: `durationMs` is populated and > 0
  - **TC-009**: `Promise.allSettled` used (not `Promise.all`) — verify by testing partial failure scenario

**Dependencies**: T-002, T-003, T-009
**Status**: [ ] Not Started

---

### T-011: Implement formatter.ts

**Description**: Create `src/core/advisor/formatter.ts` — formats `AdvisorReport` for terminal or JSON output.

**Implementation Details**:
- Export `formatAdvisorReport(report: AdvisorReport, options: AdvisorOptions): string`
- JSON mode: return `JSON.stringify(report, null, 2)`
- Terminal mode: use chalk for colors, same `getStatusIcon()` helper pattern as doctor
- Group items by category with headers
- Each item shows: rank, severity icon (■ critical=red, ▲ high=yellow, ● medium=blue, ○ low=gray, · info=dim), title, description, fix command if present
- Show summary footer: phase, confidence, X items from Y collectors, Z collectors failed
- Respect `--verbose` (show all) vs default (show top N)

**Test Plan**:
- **File**: `tests/unit/core/advisor/formatter.test.ts`
- **Tests**:
  - **TC-001**: JSON mode returns valid JSON parseable to AdvisorReport shape
  - **TC-002**: Terminal mode includes phase name in output
  - **TC-003**: Terminal mode includes severity icon for critical item
  - **TC-004**: Terminal mode includes fixCommand when present
  - **TC-005**: Empty items list formats without crash
  - **TC-006**: Items grouped by category (category headers appear)

**Dependencies**: T-001
**Status**: [ ] Not Started

---

### T-012: Create advisor CLI command (advisor.ts in cli/commands)

**Description**: Create `src/cli/commands/advisor.ts` and register it in `bin/specweave.js`.

**Implementation Details**:
- Export `advisorCommand(projectRoot, options)` — calls `runAdvisor()`, calls `formatAdvisorReport()`, prints to console
- Export `registerAdvisorCommand(program: Command)` following exact pattern of `registerDoctorCommand`
- Options: `--json`, `--verbose`, `--limit <n>`, `--phase <type>`, `--skip-slow`, `--no-cache`
- Exit code 0 always (advisor is informational, not a gate)
- Register in `bin/specweave.js` with inline `.command('advisor')` block, same pattern as doctor/health commands
- `.js` import extensions required (ESM)

**Test Plan**:
- **File**: `tests/unit/cli/commands/advisor.test.ts`
- **Tests**:
  - **TC-001**: `advisorCommand()` calls `runAdvisor` with correct projectRoot and options
  - **TC-002**: `advisorCommand()` calls `formatAdvisorReport` and prints result
  - **TC-003**: `--json` flag passed through to options
  - **TC-004**: `--skip-slow` flag passed through
  - **TC-005**: `--limit 5` parsed as number 5
  - **TC-006**: `registerAdvisorCommand` adds 'advisor' command to program
  - **TC-007**: Exit code is always 0 (even if collectors fail)

**Dependencies**: T-010, T-011
**Status**: [ ] Not Started

---

### T-013: Create advisor/index.ts public API

**Description**: Create `src/core/advisor/index.ts` — public API re-exports for the advisor module.

**Implementation Details**:
- Re-export `runAdvisor` from `./advisor.js`
- Re-export all types from `./types.js`
- Re-export `detectPhase` from `./phase-detector.js`
- Re-export `rankItems` from `./ranker.js`
- Re-export `formatAdvisorReport` from `./formatter.js`

**Test Plan**:
- (Covered by T-010 and T-012 tests via import)

**Dependencies**: T-010, T-011, T-002, T-003
**Status**: [ ] Not Started

---

## Phase 4: Skill + Edge Cases

### T-014: Create /sw:advisor skill markdown

**Description**: Create `plugins/specweave/commands/advisor.md` — the skill file that activates when user types `/sw:advisor`.

**Implementation Details**:
- Frontmatter: `description`, `argument-hint: "[--skip-slow] [--verbose] [--phase <type>]"`
- Skill body: brief explanation, usage section, what it checks (lists 5 collectors), output format description
- Bash block: `specweave advisor $ARGUMENTS`
- Follow exact structure of `doctor.md` and `qa.md` in same directory
- Trigger words: "advisor", "what should I do", "next steps", "prioritized list", "action items"

**Test Plan**:
- **File**: (manual verification — skill invocation test)
- **Tests**:
  - **TC-001**: `specweave advisor` CLI runs without error on a real project dir (smoke test)
  - **TC-002**: `specweave advisor --json` outputs valid JSON

**Dependencies**: T-012
**Status**: [ ] Not Started

---

### T-015: Edge case hardening + integration test

**Description**: Verify graceful behavior for edge cases: no `.specweave/` dir, empty project, all collectors fail, `--skip-slow` mode.

**Implementation Details**:
- Create fixture directory at `tests/fixtures/advisor/` with minimal `.specweave/` structure (config.json, 2 increments with metadata.json, one active with stale lastActivity)
- Integration test: call `runAdvisor(fixtureDir, {})` — assert report is returned, phase detected, items present from progress collector (stale increment), doctor items (if any warnings)
- Test `--skip-slow`: qa and docs-health collectors not called when `skipSlow=true`
- Test no-`.specweave/`: `runAdvisor('/tmp/empty-dir', {})` returns valid report with phase=fresh-init and 0 collector errors

**Test Plan**:
- **File**: `tests/integration/advisor.test.ts`
- **Tests**:
  - **TC-001**: Given fixture project → When `runAdvisor()` → Then returns AdvisorReport with items from progress collector
  - **TC-002**: Given `skipSlow=true` → When `runAdvisor()` → Then qa-collector and docs-health-collector not invoked
  - **TC-003**: Given empty project dir (no .specweave) → When `runAdvisor()` → Then returns report with phase=fresh-init, no crash
  - **TC-004**: Given all collectors mocked to throw → When `runAdvisor()` → Then report has collectorsFailed=5, items contain error info items

**Dependencies**: T-010, T-004, T-005, T-006, T-007, T-008
**Status**: [ ] Not Started

---

## Summary

| Phase | Tasks | Parallelizable |
|-------|-------|---------------|
| 1: Foundation | T-001, T-002, T-003 | T-002, T-003 after T-001 |
| 2: Collectors | T-004 through T-009 | T-004 through T-008 all parallel |
| 3: Orchestrator+CLI | T-010, T-011, T-012, T-013 | T-010 after Phase 2; T-011 parallel with T-010; T-012 after both |
| 4: Skill+Polish | T-014, T-015 | T-014 parallel with T-015 |

**Total tasks**: 15
**Coverage target**: 90% (per increment config)
**TDD mode**: RED → GREEN → REFACTOR per task
