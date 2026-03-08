# Architecture Plan: 0455 - Skill Eval UI

## 1. Architecture Overview

The eval UI is a local-first tool for skill developers, shipped as a `vskill eval serve` subcommand. It follows the same proven pattern as the SpecWeave dashboard: a Node.js `http` server with a minimal Router, SSE for streaming, and a React SPA bundled to static assets at `dist/eval-ui/`.

```
┌──────────────────────────────────────────────────────────────────┐
│  vskill eval serve [--port 3457] [--root ./plugins]             │
│                                                                  │
│  ┌────────────────────────┐     ┌──────────────────────────────┐ │
│  │   eval-server.ts       │     │   dist/eval-ui/              │ │
│  │   (Node http module)   │     │   (React 19 SPA bundle)      │ │
│  │                        │────►│   index.html + assets        │ │
│  │  ┌──────────────────┐  │     └──────────────────────────────┘ │
│  │  │ Router           │  │                                      │
│  │  │  GET  /api/*     │  │     ┌──────────────────────────────┐ │
│  │  │  PUT  /api/*     │  │     │  Existing eval modules       │ │
│  │  │  POST /api/*     │  │────►│  schema.ts, llm.ts, judge.ts │ │
│  │  │  SSE  /api/*/sse │  │     │  benchmark.ts, scanner.ts    │ │
│  │  └──────────────────┘  │     └──────────────────────────────┘ │
│  │                        │                                      │
│  │  ┌──────────────────┐  │     ┌──────────────────────────────┐ │
│  │  │ SSE per-request  │  │     │  New eval modules            │ │
│  │  │ (inline stream)  │  │────►│  comparator.ts               │ │
│  │  └──────────────────┘  │     │  activation-tester.ts        │ │
│  │                        │     │  benchmark-history.ts         │ │
│  └────────────────────────┘     └──────────────────────────────┘ │
└──────────────────────────────────────────────────────────────────┘
```

## 2. Key Decisions

### D-001: Reuse SpecWeave Dashboard Patterns

Adopt the Router, SSE, and static-serving patterns from `specweave/src/dashboard/`. This means:

- **Router class**: Express-like path params (`:plugin`, `:skill`) with `RegExp` matching. Copy and adapt the ~125-line `Router` + `sendJson` + `readBody` helpers -- they are compact, well-tested, and match the zero-dependency constraint.
- **SSE for long-running ops**: Benchmark and comparison runs stream progress events via per-request SSE (not broadcast). The client opens a `fetch()` with `ReadableStream` to `POST /api/.../benchmark` which responds with `text/event-stream`. When the run completes, the server sends a `done` event and closes the stream.
- **Static file serving**: The server resolves the `dist/eval-ui/` directory relative to `__dirname` (the compiled JS location) and serves its contents with correct MIME types. SPA fallback: any non-API, non-asset request returns `index.html`.

**Why not something new?** The dashboard pattern is proven in this codebase, uses zero deps, handles error sanitization, body size limits, and CORS already. Reimplementing would be gratuitous.

### D-002: SSE Per-Request (Not Broadcast)

The SpecWeave dashboard uses broadcast SSE (one `SSEManager` with many connections). The eval UI needs **per-request SSE** instead: a benchmark run is initiated by one client and its progress events are relevant only to that client.

Design:
- `POST /api/skills/:plugin/:skill/benchmark` sets response headers for SSE, then runs the benchmark loop inline. Each assertion result is written as an SSE event. On completion, a final `done` event with the full `BenchmarkResult` is sent, the stream closes, and the result is written to disk.
- This avoids managing connection sets. The `res` object IS the SSE channel -- write to it and close it.
- If the client disconnects mid-run (`res.on('close')`), the server sets an `aborted` flag and stops processing remaining cases.

### D-003: Dual tsconfig -- NodeNext Server, Bundler Client

The vskill repo uses `--moduleResolution nodenext` with `.js` extensions in all imports. The React SPA must use `--moduleResolution bundler` (Vite expects bare imports without extensions, JSX, etc.).

Solution: two `tsconfig` files.

```
src/
  eval-server/
    eval-server.ts           # server entry point
    router.ts                # Router class
    api-routes.ts            # route handlers
    sse-helpers.ts           # SSE utilities
  eval-ui/                   # React SPA source (NOT compiled by tsc)
    tsconfig.json            # module: ESNext, moduleResolution: bundler, jsx: react-jsx
    vite.config.ts
    index.html
    src/
      main.tsx
      ...
```

The root `tsconfig.json` already targets `src/` with NodeNext. The `src/eval-ui/` directory is excluded from root `tsc` compilation via a tsconfig `exclude` entry. Vite compiles the SPA independently using `src/eval-ui/tsconfig.json`.

The `src/eval-server/` files use NodeNext resolution (`.js` extensions) and are compiled by root `tsc` alongside all other server code.

Build script: `"build:eval-ui": "vite build --config src/eval-ui/vite.config.ts"` outputs to `dist/eval-ui/`.

### D-004: Frontend Bundle Committed to dist/

The spec requires the bundle to be in `dist/eval-ui/` so the globally-installed CLI can serve it without build tools. This means:

1. `dist/eval-ui/` is checked into git (added to the `files` array in `package.json`)
2. The `prepublishOnly` script runs `npm run build && npm run build:eval-ui`
3. `.gitignore` has `dist/` but NOT `dist/eval-ui/` -- or alternatively, the `files` field in `package.json` explicitly includes it and the npm pack handles it

Chosen approach: Add `dist/eval-ui/` to the `files` array in `package.json`. Add a `.gitignore` exception: `!dist/eval-ui/`. The CI/prepublish builds the UI. This matches how many CLI tools ship bundled frontends.

### D-005: REST API Design

All API routes are prefixed `/api/` and scoped by plugin and skill:

```
GET    /api/skills                                    -> SkillInfo[] with eval counts
GET    /api/skills/:plugin/:skill/evals               -> EvalsFile
PUT    /api/skills/:plugin/:skill/evals               -> write updated EvalsFile
POST   /api/skills/:plugin/:skill/benchmark           -> SSE stream of benchmark progress
POST   /api/skills/:plugin/:skill/compare             -> SSE stream of comparison progress
GET    /api/skills/:plugin/:skill/history              -> HistorySummary[]
GET    /api/skills/:plugin/:skill/history/:timestamp   -> full BenchmarkResult for one run
POST   /api/skills/:plugin/:skill/activation-test      -> SSE stream of activation test
GET    /api/health                                     -> { ok: true }
```

The SSE endpoints use `POST` because they accept a request body (e.g., which model to use, options). The response is `text/event-stream`. This is unconventional but matches the pattern used by LLM streaming APIs (OpenAI, Anthropic). The client uses `fetch()` + `ReadableStream` parsing instead of `EventSource` (which only supports GET).

### D-006: History Storage as Timestamped Files

Benchmark and comparison results are stored as individual JSON files:

```
plugins/
  my-plugin/
    skills/
      my-skill/
        evals/
          evals.json                    # eval case definitions
          benchmark.json                # latest benchmark (backward compat)
          history/
            2026-03-08T12-00-00Z.json   # individual run
            2026-03-08T14-30-00Z.json
```

Each history file has a `type` discriminator:
- `type: "benchmark"` -- standard benchmark run
- `type: "comparison"` -- WITH vs WITHOUT comparison run

Filenames use `-` instead of `:` in timestamps for filesystem safety (`:` is illegal on Windows).

The `benchmark-history.ts` module provides:
- `listHistory(skillDir)` -- returns sorted list of runs with summary metadata
- `readHistoryEntry(skillDir, timestamp)` -- reads a single file
- `writeHistoryEntry(skillDir, result)` -- writes a timestamped file
- `computeRegressions(current, previous)` -- diffs two runs, returns assertion-level changes

### D-007: Comparator Design (Blind A/B)

`src/eval/comparator.ts` handles the WITH vs WITHOUT skill comparison:

1. For each eval case, generate two outputs:
   - Output A: `client.generate(systemPromptWithSkill, evalCase.prompt)`
   - Output B: `client.generate(systemPromptWithoutSkill, evalCase.prompt)`
2. Randomize the order (A/B or B/A) before sending to the comparator LLM
3. The comparator prompt asks for:
   - Content score (1-5) for each output
   - Structure score (1-5) for each output
   - "Which is better?" verdict ("first" | "second" | "tie")
4. After scoring, the server maps back from randomized positions to WITH/WITHOUT labels
5. The UI reveals the mapping only when the user clicks "Reveal"

The comparator uses the same `LlmClient` -- no new provider infrastructure needed. It uses a different system prompt optimized for comparative evaluation.

### D-008: Activation Tester Design

`src/eval/activation-tester.ts` evaluates whether sample prompts would trigger a skill's `SKILL.md` description:

1. Input: array of `{ prompt: string, expected: "should_activate" | "should_not_activate" }` and the SKILL.md content
2. For each prompt, ask the LLM: "Given this skill description, would this user prompt trigger this skill? Respond with JSON: `{ activate: boolean, confidence: 'high' | 'medium' | 'low', reasoning: '...' }`"
3. Compare `activate` against `expected` to classify as TP/TN/FP/FN
4. Compute precision = TP/(TP+FP), recall = TP/(TP+FN), reliability = (TP+TN)/total

This is a P2 feature -- the UI tab exists but implementation is deferred after all P1 stories.

## 3. Component Breakdown

### 3.1 Backend Components (src/eval-server/)

| File | Responsibility | Lines (est.) |
|------|---------------|------|
| `eval-server.ts` | HTTP server, static file serving, route registration, graceful shutdown | ~200 |
| `router.ts` | Router class (adapted from specweave dashboard pattern) | ~130 |
| `api-routes.ts` | All `/api/*` route handlers | ~300 |
| `sse-helpers.ts` | `sendSSE(res, event, data)` and `sendSSEDone(res, data)` utilities | ~30 |

### 3.2 New Eval Modules (src/eval/)

| File | Responsibility | Lines (est.) |
|------|---------------|------|
| `benchmark-history.ts` | Read/write/list history files, regression diff | ~120 |
| `comparator.ts` | Blind A/B comparison scoring | ~100 |
| `activation-tester.ts` | SKILL.md activation analysis (P2) | ~80 |

### 3.3 CLI Integration (src/commands/)

| File | Change |
|------|--------|
| `eval.ts` | Add `serve` case to the switch, import and call `startEvalServer` |
| `eval/serve.ts` | Parse `--port` and `--root` options, call `startEvalServer()` |

### 3.4 Frontend Components (src/eval-ui/)

```
src/eval-ui/
  index.html
  tsconfig.json
  vite.config.ts
  src/
    main.tsx                         # React root + router setup
    App.tsx                          # Layout shell with sidebar + routing
    api.ts                           # fetch wrapper for /api/* calls
    sse.ts                           # fetch+ReadableStream SSE consumer
    types.ts                         # Shared types (mirrors backend)
    pages/
      SkillListPage.tsx              # Skill browser with eval counts
      SkillDetailPage.tsx            # Eval cases CRUD for a skill
      BenchmarkPage.tsx              # Benchmark runner + results
      ComparisonPage.tsx             # WITH vs WITHOUT comparison
      HistoryPage.tsx                # Benchmark history + regression view
      ActivationTestPage.tsx         # Activation testing (P2)
    components/
      EvalCaseForm.tsx               # Create/edit eval case form
      AssertionEditor.tsx            # Inline assertion add/edit/delete
      BenchmarkProgress.tsx          # Real-time progress during run
      BenchmarkResults.tsx           # Final results with pass/fail badges
      ComparisonView.tsx             # Side-by-side comparison display
      HistoryTimeline.tsx            # Chronological run list
      RegressionDiff.tsx             # Assertion diff between two runs
      ScoreBadge.tsx                 # Content/structure score display
```

### 3.5 Frontend Architecture Notes

- **Routing**: React Router with hash-based routing (`#/skills`, `#/skills/:plugin/:skill`, etc.) to avoid server-side route handling. All SPA routes resolve to `index.html`.
- **State management**: No global store. Each page fetches data via `useEffect` + `api.ts`. Benchmark/comparison progress uses the `sse.ts` hook which returns an updating state array.
- **Styling**: Tailwind CSS v4 via `@tailwindcss/vite` plugin. Dark theme by default (matches specweave dashboard).
- **No runtime deps on backend**: React, Vite, Tailwind, React Router are all `devDependencies`. The built SPA is static HTML/JS/CSS served from `dist/eval-ui/`.

## 4. Data Flow

### 4.1 Benchmark Run (US-003)

```
Client                     Server                    Disk
  |                          |                         |
  |  POST /api/.../benchmark |                         |
  |------------------------->|                         |
  |                          | load evals.json         |
  |                          |------------------------>|
  |                          |                         |
  |  SSE: case_start         | for each eval case:     |
  |<-------------------------|  generate LLM output    |
  |  SSE: assertion_result   |  judge each assertion   |
  |<-------------------------|                         |
  |  SSE: case_complete      |                         |
  |<-------------------------|                         |
  |  ...                     |                         |
  |  SSE: done (full result) | write history + latest  |
  |<-------------------------|------------------------>|
  |  (stream closes)         |                         |
```

### 4.2 WITH vs WITHOUT Comparison (US-004)

```
Client                     Server                    Disk
  |                          |                         |
  |  POST /api/.../compare   |                         |
  |------------------------->|                         |
  |                          | for each eval case:     |
  |  SSE: case_start         |  generate WITH output   |
  |<-------------------------|  generate WITHOUT output|
  |  SSE: outputs_ready      |  randomize order        |
  |<-------------------------|  send to comparator LLM |
  |  SSE: comparison_scored  |  map back to labels     |
  |<-------------------------|                         |
  |  ...                     |                         |
  |  SSE: done               | write history (type:    |
  |<-------------------------|  "comparison")          |
```

## 5. Type Sharing Strategy

Backend types (in `src/eval/`) use `.js` extensions and `NodeNext` resolution. Frontend types need `bundler` resolution. Rather than creating a complex shared package:

1. Define canonical types in `src/eval/schema.ts`, `src/eval/benchmark.ts`, etc. (already done)
2. Create `src/eval-ui/src/types.ts` that re-declares the API response types as plain TypeScript interfaces (no imports from backend). This is ~50 lines and avoids any cross-tsconfig import issues.
3. Keep them in sync manually -- the API routes validate shapes on both sides.

This trades a small amount of duplication for zero build complexity. The types are simple data shapes (no methods, no inheritance), so drift risk is low.

## 6. Build Integration

### package.json changes

```json
{
  "scripts": {
    "build": "tsc",
    "build:eval-ui": "vite build --config src/eval-ui/vite.config.ts",
    "dev:eval-ui": "vite dev --config src/eval-ui/vite.config.ts",
    "prepublishOnly": "npm run build && npm run build:eval-ui"
  },
  "devDependencies": {
    "react": "^19.0.0",
    "react-dom": "^19.0.0",
    "react-router-dom": "^7.0.0",
    "@types/react": "^19.0.0",
    "@types/react-dom": "^19.0.0",
    "@vitejs/plugin-react": "^4.0.0",
    "vite": "^6.0.0",
    "tailwindcss": "^4.0.0",
    "@tailwindcss/vite": "^4.0.0"
  }
}
```

The existing `"files": ["dist", ...]` in package.json already covers `dist/eval-ui/`. No `files` array change needed.

### tsconfig exclusion

Root `tsconfig.json` gains:

```json
{
  "exclude": ["src/eval-ui"]
}
```

This prevents `tsc` from trying to compile `.tsx` files with `NodeNext` resolution.

## 7. Testing Strategy

### Unit Tests (Vitest)

New eval modules get unit tests following the existing `src/eval/__tests__/` pattern:

- `benchmark-history.test.ts` -- read/write/list/regression logic with temp dirs
- `comparator.test.ts` -- randomization, score parsing, label mapping
- `activation-tester.test.ts` -- classification, precision/recall calculation
- `router.test.ts` -- route matching, param extraction
- `api-routes.test.ts` -- handler logic with mocked eval modules

All tests mock `LlmClient` (never make real LLM calls in tests).

### E2E Tests (Playwright)

Per US-008:

- Start the eval server programmatically in `globalSetup`
- Use `page.route()` to intercept LLM-backed API calls and return deterministic mock SSE responses
- Fixture directory with sample plugins/skills/evals
- Cover: skill browsing, eval CRUD, benchmark flow, comparison flow, history view

### Test Isolation

- Backend tests: mock the filesystem (or use `tmp` dirs) and the LLM client
- Frontend tests: Vite test setup with React Testing Library for component tests
- E2E: fully mocked LLM via `page.route()`

## 8. Risk Mitigation

| Risk | Mitigation |
|------|-----------|
| SSE via POST is non-standard | `EventSource` only supports GET. Use `fetch()` with `ReadableStream` on the client to consume POST SSE. This is a well-known pattern (used by OpenAI, Anthropic streaming APIs). |
| Bundle size grows over time | Vite tree-shaking + code splitting. Monitor with `vite-bundle-analyzer`. |
| Dual tsconfig confusion | Clear directory separation (`eval-server/` vs `eval-ui/`). Root tsconfig excludes `eval-ui/`. |
| LLM timeout during benchmark | Existing 120s timeout in `llm.ts`. Server catches errors per-case, reports via SSE, continues to next case (AC-US3-04). |
| History dir grows large | Individual JSON files are small (~2-5KB). Even 1000 runs = ~5MB. No cleanup needed for local-first tool. |

## 9. File Tree Summary

New and modified files in `repositories/anton-abyzov/vskill/`:

```
src/
  commands/
    eval.ts                          # MODIFIED: add "serve" case
    eval/
      serve.ts                       # NEW: parse CLI opts, start server
  eval/
    comparator.ts                    # NEW: blind A/B comparison
    activation-tester.ts             # NEW: SKILL.md activation analysis (P2)
    benchmark-history.ts             # NEW: history read/write/list/regression
    __tests__/
      benchmark-history.test.ts      # NEW
      comparator.test.ts             # NEW
      activation-tester.test.ts      # NEW
  eval-server/
    eval-server.ts                   # NEW: HTTP server + static serving
    router.ts                        # NEW: Router (adapted from specweave)
    api-routes.ts                    # NEW: all API route handlers
    sse-helpers.ts                   # NEW: SSE utilities
    __tests__/
      router.test.ts                 # NEW
      api-routes.test.ts             # NEW
  eval-ui/
    index.html                       # NEW
    tsconfig.json                    # NEW: bundler resolution
    vite.config.ts                   # NEW
    src/
      main.tsx                       # NEW
      App.tsx                        # NEW
      api.ts                         # NEW
      sse.ts                         # NEW
      types.ts                       # NEW
      pages/                         # NEW: 6 page components
      components/                    # NEW: 8 UI components
tsconfig.json                        # MODIFIED: exclude eval-ui
package.json                         # MODIFIED: scripts + devDeps
e2e/
  eval-ui.spec.ts                    # NEW: Playwright E2E tests
  fixtures/                          # NEW: test plugins/skills/evals
playwright.config.ts                 # NEW (or MODIFIED if exists)
```

## 10. Implementation Order

1. **New eval modules** (comparator, benchmark-history, activation-tester) -- pure logic, no server dependency, unit-testable
2. **Eval server** (router, api-routes, sse-helpers, eval-server) -- depends on eval modules
3. **CLI integration** (eval.ts + serve.ts) -- depends on eval server
4. **Frontend SPA** (eval-ui/) -- depends on API being defined
5. **E2E tests** -- depends on both server and frontend
6. **Build integration** (tsconfig, package.json, prepublish) -- final wiring

## 11. Domain Skill Delegation

No additional domain skills are needed. The tech stack is:
- **Backend**: Node.js `http` module (no framework) -- covered by this plan
- **Frontend**: React 19 + Vite + Tailwind v4 -- standard tooling, no framework-specific architecture decisions needed beyond what is specified here

The complexity level is **medium** (auth-less local tool with moderate UI). The patterns are established by the specweave dashboard reference. No frontend:architect or backend:* skill invocation is warranted.
