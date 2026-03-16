# Architecture Plan: Skill Eval Infrastructure

**Increment**: 0439-skill-eval-infrastructure
**Architect**: sw:architect
**Date**: 2026-03-05

---

## 1. Architecture Overview

This increment spans three repositories and two runtime environments:

```
                    CLI (vskill)                         Web (vskill-platform)
              ┌──────────────────────┐            ┌──────────────────────────┐
              │  eval init           │            │  /admin/evals            │
              │  eval run            │            │  ├─ Skill selector       │
              │  eval coverage       │            │  ├─ Eval card viewer     │
              │  eval generate-all   │            │  ├─ Inline editor        │
              │  eval view           │            │  └─ GitHub commit flow   │
              └──────────┬───────────┘            └────────────┬─────────────┘
                         │                                     │
                         │ reads/writes                        │ API routes
                         │                                     │
              ┌──────────▼───────────┐            ┌────────────▼─────────────┐
              │  Filesystem          │            │  GitHub Contents API     │
              │  plugins/<p>/skills/ │            │  (GITHUB_EVAL_TOKEN)     │
              │    <s>/evals/        │            │                          │
              │      evals.json      │            │  Prisma DB (existing     │
              │      benchmark.json  │            │  EvalRun/EvalCase for    │
              └──────────────────────┘            │  run history only)       │
                                                  └──────────────────────────┘
```

The CLI is the primary authoring and execution tool. The web UI is an admin-only
viewer/editor that reads evals.json from GitHub and writes back via the Contents API.
The existing platform eval engine (comparator, judge, eval-store) is a separate
"with-skill vs without-skill" pipeline and is NOT reused for CLI eval runs. The CLI
runs its own simpler pipeline: prompt -> LLM -> assertion judge.

---

## 2. Key Architecture Decisions

### AD-01: CLI Eval Command as Commander Subcommand Group

The `eval` command uses Commander's subcommand routing pattern (matching `blocklist`
in `src/commands/blocklist.ts`). A single `eval` command in `src/index.ts` dispatches
to a router in `src/commands/eval.ts`, which routes to separate handler modules.

**Rationale**: Consistent with existing codebase (blocklist pattern). Avoids polluting
the top-level command namespace. Allows each subcommand to be independently tested.

```
src/index.ts                     # registers: program.command("eval [subcommand] [target]")
src/commands/eval.ts             # router: switch(subcommand) -> init|run|coverage|generate-all|view
src/commands/eval/
  init.ts                        # eval init handler
  run.ts                         # eval run handler
  coverage.ts                    # eval coverage handler
  generate-all.ts                # eval generate-all handler
  view.ts                        # eval view handler (local HTTP server)
```

### AD-02: evals.json Schema Validation via Standalone Validator

A shared `src/eval/schema.ts` module validates evals.json on every load. All eval
commands call `loadAndValidateEvals(skillDir)` which returns validated data or throws
with structured error details (missing fields, duplicate IDs, JSON parse errors).

No external schema validation library is introduced. The validator is hand-written
TypeScript with clear error messages, matching the zero-dependency philosophy of the
existing codebase (no Zod, no Ajv -- just type guards and manual checks).

**Schema contract** (backward-compatible with existing social-media-posting evals.json):

```
evals.json
  skill_name: string (required)
  evals: array (required, min 1)
    [].id: number (required)
    [].name: string (required)
    [].prompt: string (required)
    [].expected_output: string (required)
    [].files: string[] (optional, default [])
    [].assertions: array (required, min 1)
      [].id: string (required, unique within parent eval)
      [].text: string (required)
      [].type: "boolean" (required)
```

### AD-03: LLM Integration via Anthropic SDK (Direct, No Platform Dependency)

CLI eval commands use the Anthropic TypeScript SDK directly (`@anthropic-ai/sdk`).
The LLM client is abstracted behind `src/eval/llm.ts` which reads `ANTHROPIC_API_KEY`
and `VSKILL_EVAL_MODEL` from environment. This is a CLI-local dependency, not shared
with the platform (which uses Cloudflare AI bindings).

**Why not reuse platform's judge/comparator**: The platform pipeline
(`src/lib/eval/judge.ts`, `eval-engine.ts`) does with-skill vs without-skill
comparative evaluation using `@cf/meta/llama-4-scout` via Cloudflare AI bindings.
The CLI pipeline is fundamentally different -- it grades individual assertions
against LLM output, not comparative quality. Different models, different APIs,
different grading logic. Sharing code would create forced abstraction.

**Model configuration**:
- `VSKILL_EVAL_MODEL` env var, default: `claude-sonnet-4-20250514`
- Used for both generation (eval init) and judging (eval run)

### AD-04: Eval Generation Prompt Architecture

The `eval init` command sends a single LLM call with a carefully structured prompt
containing four sections:

1. **Skill content**: Full SKILL.md of the target skill
2. **Schema reference**: The evals.json schema with field descriptions
3. **Example**: The social-media-posting evals.json as a concrete reference
4. **Best practices**: Embedded static text from skill-creator guidelines

The prompt is assembled in `src/eval/prompt-builder.ts` as a template literal. The
social-media-posting example is embedded as a JSON string literal (not loaded at
runtime from the filesystem) to avoid path resolution issues when running from
different directories.

**Output parsing**: The LLM response is expected to contain a JSON code block.
`src/eval/prompt-builder.ts` exports a `parseGeneratedEvals(raw: string)` function
that extracts JSON from markdown code fences, validates it against the schema, and
returns the typed result or throws.

### AD-05: Eval Run Pipeline (Assertion-Level Grading)

The `eval run` pipeline is sequential per eval case:

```
For each eval case in evals.json:
  1. Send case.prompt to LLM -> collect output
  2. For each assertion in case.assertions:
     a. Send (output, assertion.text) to LLM judge
     b. Judge returns pass/fail boolean + optional reasoning
  3. Record per-assertion results
  4. Compute per-case pass rate
```

The judge prompt for step 2 is a focused binary evaluation:
"Given this LLM output and this assertion, does the output satisfy the assertion?
Respond with JSON: { pass: boolean, reasoning: string }"

Individual assertion grading (rather than batch) ensures fine-grained results and
prevents the LLM from conflating multiple assertions. The cost is more LLM calls --
for a typical skill with 3 cases x 5 assertions = 15 judge calls. Acceptable for
manual runs; rate-limited in batch.

### AD-06: Benchmark Output Format

`benchmark.json` written by `eval run` at `<skill>/evals/benchmark.json`:

```
benchmark.json
  timestamp: ISO 8601 string
  model: string (model used for both execution and judging)
  skill_name: string
  cases: array
    [].eval_id: number
    [].eval_name: string
    [].status: "pass" | "fail" | "error"
    [].error_message: string | null
    [].pass_rate: number (0.0-1.0)
    [].assertions: array
      [].id: string
      [].text: string
      [].pass: boolean
      [].reasoning: string
```

### AD-07: Batch Generation Concurrency Control

`eval generate-all` processes skills sequentially (no parallel LLM calls) with a
configurable delay between calls. This avoids rate limit issues with the Anthropic
API and prevents token budget spikes.

**Configuration**: `--concurrency 1` is the default and only supported value in V1.
Future versions may support parallel generation with semaphore control.

**Error handling**: On LLM failure for a skill, log a warning and continue. The
summary at the end lists all failures with their error messages.

### AD-08: Coverage Report Data Source

`eval coverage` scans the filesystem by walking `plugins/*/skills/*/` directories.
For each skill directory, it checks:
1. Does `evals/evals.json` exist? (no -> MISSING)
2. Is it valid JSON with the correct schema? (no -> INVALID)
3. Does `evals/benchmark.json` exist? (no -> PENDING)
4. What was the latest benchmark result? (all pass -> PASS, any fail -> FAIL)

The `--root` flag overrides the default `plugins/` root, enabling the same command
to work with specweave's `plugins/` directory layout (which is identical).

### AD-09: Web Eval Editor -- Client-Side State, Server-Side Persistence

The `/admin/evals` page is a client component with three states:

1. **Selector state**: Skill dropdown populated from `/api/v1/admin/evals/skills`
   (lists skills with known evals.json paths from DB skill records)
2. **Viewer state**: Displays eval cards read-only, fetched from GitHub raw content
3. **Editor state**: Inline editing of fields with local React state. No auto-save.
   Explicit "Save" button triggers PUT to `/api/v1/admin/evals/save`

**Data flow**:
```
Skill selector -> GET /api/v1/admin/evals/content?skill=<name>
                  (fetches evals.json from GitHub via Contents API)
                  -> renders eval cards

Edit mode     -> local React state mutations
Save          -> PUT /api/v1/admin/evals/save { skillName, content }
                  (writes to GitHub via Contents API, returns new SHA)

Commit        -> POST /api/v1/admin/evals/commit { skillName, content, message }
                  (creates commit via GitHub Contents API, returns commit SHA)
```

The "Save" action in the spec (AC-US6-04) and the "Commit to GitHub" action
(AC-US7-01-05) are actually two distinct operations. "Save" persists to GitHub as a
commit (since there is no intermediate storage -- evals.json lives in git, not in a
database). The "Commit to GitHub" with diff preview is a separate UX flow that shows
the diff before committing.

Implementation simplification: Merge Save and Commit into a single flow:
1. User edits inline
2. User clicks "Save & Commit"
3. Diff preview shown (current GitHub content vs edited content)
4. User confirms -> commit via Contents API -> success with SHA

This satisfies both US-WEB-001 AC-US6-04 and US-WEB-002 AC-US7-01 through AC-US7-05.

### AD-10: GitHub Contents API Integration (Platform Side)

A new server-side utility at `src/lib/github/eval-content.ts` handles all GitHub
operations for the eval editor:

```typescript
// Fetch evals.json content from a skill's repo
fetchEvalsContent(repoUrl: string, skillPath: string): Promise<{ content: string; sha: string }>

// Commit updated evals.json
commitEvalsContent(repoUrl: string, skillPath: string, content: string, sha: string, message: string): Promise<{ commitSha: string }>
```

Uses `GITHUB_EVAL_TOKEN` (Cloudflare secret, `env` handler parameter -- NOT
`process.env`). Token requires `repo` scope for write access to skill repositories.

The existing `fetchSkillContent()` in `admin/eval/direct/route.ts` fetches raw
content from GitHub but uses unauthenticated raw.githubusercontent.com URLs. The new
module uses the authenticated Contents API (api.github.com) because:
1. Write operations require authentication
2. We need the file SHA for conditional updates (prevents race conditions)
3. Rate limits are higher with authenticated requests

### AD-11: Eval View Command (Local HTTP Server)

`vskill eval view <plugin>/<skill>` opens a local browser-based viewer for
evals.json and benchmark.json. This mirrors the existing `generate_review.py`
viewer pattern but in Node.js.

Implementation: `src/commands/eval/view.ts` starts a `node:http` server on a random
available port, serves a single-page HTML/JS app that renders eval cards and
benchmark results, and opens the browser. The HTML is a template string embedded in
the TypeScript source (no build step, no external files).

Edit mode: When `--edit` flag is passed, the viewer includes editable fields and a
"Save" button that POSTs back to the local server, which writes to the filesystem.
This is the CLI-local alternative to the web editor for users who prefer terminal
workflows.

---

## 3. Component Breakdown

### 3.1 vskill CLI Components (New Files)

```
src/commands/eval.ts              # Subcommand router
src/commands/eval/
  init.ts                         # LLM-powered evals.json scaffolding
  run.ts                          # Eval execution with assertion grading
  coverage.ts                     # Coverage table across all skills
  generate-all.ts                 # Batch generation
  view.ts                         # Local HTTP viewer/editor
src/eval/
  schema.ts                       # evals.json schema validation
  llm.ts                          # Anthropic SDK wrapper
  prompt-builder.ts               # Generation prompt assembly + response parsing
  judge.ts                        # Assertion-level LLM judge
  benchmark.ts                    # benchmark.json read/write
  skill-scanner.ts                # Filesystem scanner for plugins/*/skills/*
```

### 3.2 vskill-platform Components (New Files)

```
src/app/admin/evals/
  page.tsx                        # Admin eval viewer/editor page
src/app/api/v1/admin/evals/
  content/route.ts                # GET: fetch evals.json from GitHub
  skills/route.ts                 # GET: list skills with known repos
  commit/route.ts                 # POST: commit evals.json to GitHub
src/lib/github/
  eval-content.ts                 # GitHub Contents API operations
```

### 3.3 specweave Repository (Content Only)

No code changes to specweave. Eval generation for specweave skills is performed by
running `vskill eval generate-all --root <path-to-specweave-repo>/plugins` from the
vskill CLI. The generated evals.json files are committed to the specweave repo.

---

## 4. Data Flow Diagrams

### 4.1 eval init

```
User: vskill eval init marketing/social-media-posting
  |
  +-- Read plugins/marketing/skills/social-media-posting/SKILL.md
  +-- Check evals/evals.json exists? (yes -> exit unless --force)
  +-- Build prompt (SKILL.md + schema + example + best practices)
  +-- Call Anthropic API (VSKILL_EVAL_MODEL)
  +-- Parse JSON response
  +-- Validate against schema
  +-- Write evals/evals.json
```

### 4.2 eval run

```
User: vskill eval run marketing/social-media-posting
  |
  +-- Load & validate evals/evals.json
  +-- For each eval case:
  |   +-- Send prompt to Anthropic API -> collect output
  |   +-- For each assertion:
  |   |   +-- Judge (output, assertion.text) -> pass/fail
  |   +-- Compute per-case pass rate
  +-- Print results table (eval name | assertion | status)
  +-- Write evals/benchmark.json
```

### 4.3 Web Editor Flow

```
Admin: /admin/evals
  |
  +-- Select skill from dropdown
  |   +-- GET /api/v1/admin/evals/content?skill=<name>
  |       +-- Server: fetch evals.json from GitHub (Contents API)
  |
  +-- View eval cards (read-only)
  +-- Click "Edit" -> inline editing (local React state)
  +-- Click "Save & Commit"
  |   +-- Show diff preview (current GitHub vs edited)
  |   +-- User confirms
  |   +-- POST /api/v1/admin/evals/commit
  |       +-- Server: commit via GitHub Contents API
  +-- Show success with commit SHA
```

---

## 5. Interface Contracts

### 5.1 CLI Eval Module Public API

```typescript
// src/eval/schema.ts
interface EvalsFile {
  skill_name: string;
  evals: EvalCase[];
}
interface EvalCase {
  id: number;
  name: string;
  prompt: string;
  expected_output: string;
  files: string[];
  assertions: Assertion[];
}
interface Assertion {
  id: string;
  text: string;
  type: "boolean";
}
interface ValidationError {
  path: string;
  message: string;
}
function loadAndValidateEvals(skillDir: string): EvalsFile;
// Throws EvalValidationError with errors: ValidationError[]

// src/eval/llm.ts
interface LlmClient {
  generate(systemPrompt: string, userPrompt: string): Promise<string>;
}
function createLlmClient(): LlmClient;
// Reads ANTHROPIC_API_KEY, VSKILL_EVAL_MODEL from env

// src/eval/judge.ts
interface AssertionResult {
  id: string;
  text: string;
  pass: boolean;
  reasoning: string;
}
function judgeAssertion(
  output: string,
  assertion: Assertion,
  client: LlmClient
): Promise<AssertionResult>;

// src/eval/skill-scanner.ts
interface SkillInfo {
  plugin: string;
  skill: string;
  dir: string;
  hasEvals: boolean;
  hasBenchmark: boolean;
}
function scanSkills(root: string): Promise<SkillInfo[]>;
```

### 5.2 Platform API Contracts

```
GET /api/v1/admin/evals/skills
  Auth: admin token
  Response: { skills: Array<{ name: string; repoUrl: string; skillPath: string }> }

GET /api/v1/admin/evals/content?skill=<name>
  Auth: admin token
  Response: { content: string; sha: string; path: string }
  Error 404: skill not found or no evals.json

POST /api/v1/admin/evals/commit
  Auth: admin token
  Body: { skillName: string; content: string; sha: string; message?: string }
  Response: { commitSha: string; url: string }
  Error 409: conflict (SHA mismatch)
  Error 403: token lacks write permission
```

---

## 6. Testing Strategy

### 6.1 vskill CLI Tests

All tests use Vitest with ESM. Test files co-located at `src/eval/__tests__/` and
`src/commands/eval/__tests__/`.

| Layer | What | Approach |
|-------|------|----------|
| Schema validation | `schema.test.ts` | Unit: valid/invalid JSON fixtures, missing fields, duplicate IDs |
| LLM client | `llm.test.ts` | Unit: mock Anthropic SDK, test error handling, timeout |
| Prompt builder | `prompt-builder.test.ts` | Unit: verify prompt contains all 4 sections, test JSON parsing from code fences |
| Judge | `judge.test.ts` | Unit: mock LLM, test pass/fail/error responses |
| Skill scanner | `skill-scanner.test.ts` | Unit: mock filesystem (tmp dirs), test discovery |
| Init command | `init.test.ts` | Integration: mock LLM, verify file written, test --force |
| Run command | `run.test.ts` | Integration: mock LLM, verify table output, benchmark.json written |
| Coverage command | `coverage.test.ts` | Integration: mock filesystem, verify table format |
| Generate-all | `generate-all.test.ts` | Integration: mock LLM, verify skip/fail/success counts |

### 6.2 vskill-platform Tests

| Layer | What | Approach |
|-------|------|----------|
| GitHub client | `eval-content.test.ts` | Unit: mock fetch, test SHA handling, error cases |
| API routes | `content/route.test.ts`, `commit/route.test.ts` | Integration: mock DB + GitHub, test auth |
| Admin page | `evals/page.test.tsx` | Component: render states (selector, viewer, editor) |

---

## 7. Risk Analysis

| Risk | Impact | Probability | Mitigation |
|------|--------|-------------|------------|
| Anthropic API rate limits during batch generation | Medium | Medium | Sequential processing, configurable delay (default 2s between calls) |
| LLM produces invalid JSON in eval init | Medium | Low | Retry once with explicit JSON instruction; fallback error with raw output logged |
| GitHub token lacks write scope | High | Low | Validate token permissions on first commit attempt; clear error message |
| evals.json schema drift | Low | Low | Schema version field reserved but not enforced in V1; validator is the contract |
| Large SKILL.md exceeds context window | Medium | Low | Truncate to 8000 chars with warning; most skills are under 2000 chars |

---

## 8. Dependency Summary

### New Dependencies (vskill CLI only)

| Package | Purpose | Size |
|---------|---------|------|
| `@anthropic-ai/sdk` | LLM API calls for eval init and eval run | ~50KB |

No new dependencies for vskill-platform (uses existing `fetch` for GitHub API).

### Environment Variables (vskill CLI)

| Variable | Required | Default | Purpose |
|----------|----------|---------|---------|
| `ANTHROPIC_API_KEY` | Yes (for init/run) | none | Anthropic API authentication |
| `VSKILL_EVAL_MODEL` | No | `claude-sonnet-4-20250514` | Model for generation and judging |

### Cloudflare Secrets (vskill-platform)

| Secret | Required | Purpose |
|--------|----------|---------|
| `GITHUB_EVAL_TOKEN` | Yes (for web editor) | GitHub token with `repo` scope for Contents API |

---

## 9. Implementation Order

The implementation follows dependency order, with CLI foundation first:

1. **Schema validation** (`src/eval/schema.ts`) -- no LLM dependency, enables all other commands
2. **LLM client** (`src/eval/llm.ts`) -- Anthropic SDK wrapper
3. **Skill scanner** (`src/eval/skill-scanner.ts`) -- filesystem discovery
4. **Eval init** -- depends on 1, 2
5. **Eval run + judge** -- depends on 1, 2
6. **Eval coverage** -- depends on 1, 3
7. **Eval generate-all** -- depends on 4 (reuses init logic)
8. **Eval view** -- depends on 1 (read-only viewer for evals/benchmark)
9. **CLI command registration** -- wiring in `src/index.ts` and `src/commands/eval.ts`
10. **Platform: GitHub eval content client** -- independent of CLI
11. **Platform: API routes** -- depends on 10
12. **Platform: Admin evals page** -- depends on 11
13. **Specweave batch generation** -- depends on 7 (run CLI against specweave repo)

---

## 10. Out of Scope (Confirmed)

- No changes to the platform's existing eval engine (comparator, judge, eval-store)
- No Prisma schema changes (the CLI pipeline writes to filesystem, not DB)
- No CI/CD pipeline integration (future increment)
- No public-facing eval results page changes
- No auto-fix for invalid evals.json
