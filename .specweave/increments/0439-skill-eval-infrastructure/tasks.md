---
increment: 0439-skill-eval-infrastructure
title: "Skill Eval Infrastructure"
generated_by: sw:test-aware-planner
tdd_mode: true
coverage_target: 90
by_user_story:
  US-CLI-001: [T-001, T-002, T-003, T-004]
  US-CLI-002: [T-005, T-006]
  US-CLI-003: [T-007]
  US-CLI-004: [T-008]
  US-CLI-005: [T-001]
  US-WEB-001: [T-009, T-010, T-011]
  US-WEB-002: [T-011, T-012]
  US-SW-001: [T-013]
---

# Tasks: Skill Eval Infrastructure

## Phase 1: CLI Foundation (vskill)

### User Story: US-CLI-005 + US-CLI-001 Foundation — Schema Validation and LLM Client

**Linked ACs**: AC-US5-01, AC-US5-02, AC-US5-03, AC-US1-01, AC-US1-02, AC-US1-05
**Tasks**: 4 total, 0 completed

---

### T-001: Implement evals.json schema validator

**User Story**: US-CLI-005 (also foundational for US-CLI-001)
**Satisfies ACs**: AC-US5-01, AC-US5-02, AC-US5-03, AC-US1-05
**Status**: [ ] pending

**Test Plan**:
- **Given** an evals.json with missing required field `skill_name`
- **When** `loadAndValidateEvals(skillDir)` is called
- **Then** it throws `EvalValidationError` listing `skill_name` as missing

- **Given** an evals.json with duplicate assertion IDs `assert-1` appearing twice in one eval case
- **When** `loadAndValidateEvals(skillDir)` is called
- **Then** it throws `EvalValidationError` identifying the duplicate ID `assert-1`

- **Given** a file that is not valid JSON (`{ broken json`)
- **When** `loadAndValidateEvals(skillDir)` is called
- **Then** it throws `EvalValidationError` with the file path and parse offset

- **Given** a valid evals.json matching the social-media-posting structure
- **When** `loadAndValidateEvals(skillDir)` is called
- **Then** it returns a typed `EvalsFile` object without throwing

**Test Cases**:
1. **Unit**: `repositories/anton-abyzov/vskill/src/eval/__tests__/schema.test.ts`
   - `validatesMissingSkillName()`: throws with path `skill_name`
   - `validatesMissingEvalsArray()`: throws with path `evals`
   - `validatesMissingPromptInCase()`: throws with path `evals[0].prompt`
   - `validatesMissingAssertions()`: throws with path `evals[0].assertions`
   - `validatesDuplicateAssertionIds()`: throws identifying duplicate ID
   - `validatesInvalidJson()`: throws with file path and parse offset
   - `validatesEmptyAssertionsArray()`: throws (min 1 required)
   - `acceptsValidEvalsJson()`: returns typed EvalsFile
   - **Coverage Target**: 95%

**Implementation**:
1. Create `repositories/anton-abyzov/vskill/src/eval/schema.ts` with interfaces `EvalsFile`, `EvalCase`, `Assertion`, `ValidationError`, `EvalValidationError`
2. Implement `loadAndValidateEvals(skillDir: string): EvalsFile` — reads `evals/evals.json`, parses JSON (catch SyntaxError with offset), runs type guards for all required fields, checks assertion ID uniqueness per eval case
3. Export all types and the function
4. Write test file with fixtures (valid and invalid JSON strings)
5. Run `cd repositories/anton-abyzov/vskill && npx vitest run src/eval/__tests__/schema.test.ts`

---

### T-002: Implement Anthropic LLM client wrapper

**User Story**: US-CLI-001
**Satisfies ACs**: AC-US1-01 (prerequisite), AC-US1-02 (prerequisite)
**Status**: [ ] pending

**Test Plan**:
- **Given** `ANTHROPIC_API_KEY` is set and the SDK call succeeds
- **When** `client.generate(systemPrompt, userPrompt)` is called
- **Then** it returns the text content from the LLM response

- **Given** the Anthropic SDK throws a network error
- **When** `client.generate()` is called
- **Then** the error propagates with a message containing the original error text

- **Given** `VSKILL_EVAL_MODEL` is not set
- **When** `createLlmClient()` is called and generate is invoked
- **Then** it uses the default model `claude-sonnet-4-20250514`

**Test Cases**:
1. **Unit**: `repositories/anton-abyzov/vskill/src/eval/__tests__/llm.test.ts`
   - `returnsTextOnSuccess()`: mocks SDK, verifies response text returned
   - `propagatesNetworkError()`: mocks SDK rejection, verifies error propagates
   - `usesDefaultModelWhenEnvNotSet()`: verifies default model in SDK call args
   - `usesCustomModelFromEnv()`: sets `VSKILL_EVAL_MODEL`, verifies model arg
   - **Coverage Target**: 90%

**Implementation**:
1. Add `@anthropic-ai/sdk` dependency: `cd repositories/anton-abyzov/vskill && npm install @anthropic-ai/sdk`
2. Create `repositories/anton-abyzov/vskill/src/eval/llm.ts` — exports `LlmClient` interface and `createLlmClient()` function
3. Read `ANTHROPIC_API_KEY` and `VSKILL_EVAL_MODEL` from `process.env`; default model to `claude-sonnet-4-20250514`
4. Implement `generate(systemPrompt, userPrompt)` using `messages.create` with `max_tokens: 4096`
5. Write test using `vi.hoisted()` + `vi.mock("@anthropic-ai/sdk")`
6. Run `npx vitest run src/eval/__tests__/llm.test.ts`

---

### T-003: Implement prompt builder and eval init command

**User Story**: US-CLI-001
**Satisfies ACs**: AC-US1-01, AC-US1-02, AC-US1-03, AC-US1-04, AC-US1-05
**Status**: [ ] pending

**Test Plan**:
- **Given** a skill directory with `SKILL.md` and no existing `evals/evals.json`
- **When** `vskill eval init marketing/social-media-posting` is run
- **Then** `evals/evals.json` is created with valid JSON matching the schema

- **Given** a skill that already has `evals/evals.json`
- **When** `vskill eval init` is run without `--force`
- **Then** the command exits with message "evals.json already exists, use --force to overwrite" and the file is unchanged

- **Given** a skill that already has `evals/evals.json` and `--force` flag is passed
- **When** `vskill eval init --force marketing/social-media-posting` is run
- **Then** the existing file is overwritten with freshly generated content

- **Given** the built LLM prompt
- **When** `buildEvalInitPrompt(skillContent)` is called
- **Then** the resulting string contains the SKILL.md content, the schema description, the social-media-posting example JSON, and the best-practices section

**Test Cases**:
1. **Unit**: `repositories/anton-abyzov/vskill/src/eval/__tests__/prompt-builder.test.ts`
   - `promptContainsSkillContent()`: verifies SKILL.md text present in prompt
   - `promptContainsSchemaReference()`: verifies schema fields listed
   - `promptContainsSocialMediaExample()`: verifies example JSON embedded
   - `promptContainsBestPractices()`: verifies best-practices section present
   - `parseGeneratedEvalsExtractsJson()`: input has ```json fence, output is parsed object
   - `parseGeneratedEvalsThrowsOnMissingFence()`: no code block -> throws
   - **Coverage Target**: 95%

2. **Integration**: `repositories/anton-abyzov/vskill/src/commands/eval/__tests__/init.test.ts`
   - `createsEvalsJsonWhenAbsent()`: mock LLM, verify file written with valid schema
   - `exitsWithMessageWhenEvalsExistNoForce()`: verify exit message, file unchanged
   - `overwritesWhenForceFlag()`: verify file replaced
   - `handlesLlmFailureGracefully()`: mock LLM throws, verify error message to stderr
   - **Coverage Target**: 90%

**Implementation**:
1. Create `repositories/anton-abyzov/vskill/src/eval/prompt-builder.ts` with `buildEvalInitPrompt(skillContent: string): string` and `parseGeneratedEvals(raw: string): EvalsFile`
2. Embed social-media-posting example as a JSON string literal (not filesystem read)
3. Embed best-practices static text block inline
4. `parseGeneratedEvals`: extract JSON from ```json code fences; parse; validate via schema validator
5. Create `repositories/anton-abyzov/vskill/src/commands/eval/init.ts` — accepts `pluginSkillArg: string` and `force: boolean`; reads SKILL.md; calls prompt builder; calls LLM; writes evals.json
6. Run both test files

---

### T-004: Implement skill scanner and eval command router

**User Story**: US-CLI-001, US-CLI-003, US-CLI-004
**Satisfies ACs**: AC-US1-01 (wiring), AC-US3-01 (scanner), AC-US4-01 (scanner)
**Status**: [ ] pending

**Test Plan**:
- **Given** a temp directory with structure `plugins/marketing/skills/social-media-posting/SKILL.md` and a co-located `evals/evals.json`
- **When** `scanSkills("plugins")` is called
- **Then** it returns a `SkillInfo[]` array with one entry where `plugin="marketing"`, `skill="social-media-posting"`, `hasEvals=true`, `hasBenchmark=false`

- **Given** the `eval` subcommand is invoked as `vskill eval init <target>`
- **When** the router in `src/commands/eval.ts` receives `subcommand="init"`
- **Then** it delegates to the init handler with the correct target argument

**Test Cases**:
1. **Unit**: `repositories/anton-abyzov/vskill/src/eval/__tests__/skill-scanner.test.ts`
   - `discoversSkillsInPluginsDir()`: temp dir with 2 skills, verifies both returned
   - `setsHasEvalsTrue()`: skill with evals.json, verifies `hasEvals=true`
   - `setsHasBenchmarkTrue()`: skill with benchmark.json, verifies `hasBenchmark=true`
   - `usesCustomRoot()`: `--root` path override respected
   - **Coverage Target**: 90%

2. **Unit**: `repositories/anton-abyzov/vskill/src/commands/__tests__/eval-router.test.ts`
   - `routesInitSubcommand()`: mock init handler, verify called
   - `routesRunSubcommand()`: mock run handler, verify called
   - `routesCoverageSubcommand()`: mock coverage handler, verify called
   - `routesGenerateAllSubcommand()`: mock generate-all handler, verify called
   - **Coverage Target**: 90%

**Implementation**:
1. Create `repositories/anton-abyzov/vskill/src/eval/skill-scanner.ts` with `scanSkills(root: string): Promise<SkillInfo[]>` — recursive readdir to find `<root>/*/skills/*/SKILL.md`
2. Create `repositories/anton-abyzov/vskill/src/commands/eval.ts` router — `switch(subcommand)` dispatching to init/run/coverage/generate-all handlers
3. Register `program.command("eval [subcommand] [target]")` with `--root` and `--force` options in `src/index.ts`
4. All imports use `.js` extensions (ESM `--moduleResolution nodenext`)
5. Run all scanner and router tests

---

## Phase 2: CLI Commands — Eval Run and Assertion Judge

### User Story: US-CLI-002 — Run Evals Locally

**Linked ACs**: AC-US2-01, AC-US2-02, AC-US2-03, AC-US2-04, AC-US2-05
**Tasks**: 2 total, 0 completed

---

### T-005: Implement assertion judge and benchmark writer

**User Story**: US-CLI-002
**Satisfies ACs**: AC-US2-01, AC-US2-03 (benchmark format)
**Status**: [ ] pending

**Test Plan**:
- **Given** an LLM output "The report has been saved to reports/q1.csv" and assertion text "The response mentions a file path"
- **When** `judgeAssertion(output, assertion, client)` is called with a mock LLM returning `{ pass: true, reasoning: "output contains file path" }`
- **Then** it returns `AssertionResult` with `pass=true` and the reasoning text

- **Given** the LLM judge returns malformed JSON (not parseable as `{ pass, reasoning }`)
- **When** `judgeAssertion()` is called
- **Then** it throws an error with a message indicating the LLM returned invalid judge output

- **Given** a completed benchmark result object
- **When** `writeBenchmark(skillDir, result)` is called
- **Then** `evals/benchmark.json` is written with all required fields: `timestamp`, `model`, `skill_name`, `cases[]`

**Test Cases**:
1. **Unit**: `repositories/anton-abyzov/vskill/src/eval/__tests__/judge.test.ts`
   - `returnsPassResult()`: mock LLM returns pass=true, verifies AssertionResult
   - `returnsFailResult()`: mock LLM returns pass=false
   - `throwsOnMalformedJudgeResponse()`: mock LLM returns plain text, verifies throw
   - **Coverage Target**: 95%

2. **Unit**: `repositories/anton-abyzov/vskill/src/eval/__tests__/benchmark.test.ts`
   - `writesBenchmarkJson()`: writes file, reads back, verifies all fields present
   - `readsBenchmarkJson()`: reads existing benchmark.json, verifies typed result
   - `returnsNullForMissingBenchmark()`: no file -> returns null
   - **Coverage Target**: 90%

**Implementation**:
1. Create `repositories/anton-abyzov/vskill/src/eval/judge.ts` — implements `judgeAssertion(output: string, assertion: Assertion, client: LlmClient): Promise<AssertionResult>` with focused binary-evaluation judge prompt
2. Parse LLM response as JSON `{ pass: boolean, reasoning: string }`; throw on malformed
3. Create `repositories/anton-abyzov/vskill/src/eval/benchmark.ts` — exports `writeBenchmark(skillDir: string, result: BenchmarkResult): Promise<void>` and `readBenchmark(skillDir: string): Promise<BenchmarkResult | null>`
4. `BenchmarkResult` shape: `{ timestamp, model, skill_name, cases: [{ eval_id, eval_name, status, error_message, pass_rate, assertions }] }`
5. Run both test files

---

### T-006: Implement eval run command

**User Story**: US-CLI-002
**Satisfies ACs**: AC-US2-01, AC-US2-02, AC-US2-03, AC-US2-04, AC-US2-05
**Status**: [ ] pending

**Test Plan**:
- **Given** a skill with a valid evals.json containing 2 cases, each with 3 assertions
- **When** `vskill eval run marketing/social-media-posting` is run with mocked LLM returning deterministic pass/fail
- **Then** the terminal table shows 6 rows (2 cases x 3 assertions) with eval name, assertion ID, truncated text (60 chars), and pass/fail status; `benchmark.json` is written

- **Given** a skill where the LLM call for case 2 fails with a timeout error
- **When** `vskill eval run` is run
- **Then** case 2 is marked as "error" in benchmark.json with the error message, case 1 result is still recorded, and the command does not abort

- **Given** a skill with no `evals/evals.json`
- **When** `vskill eval run` is run
- **Then** the command exits with message "No evals.json found at <path>"

**Test Cases**:
1. **Integration**: `repositories/anton-abyzov/vskill/src/commands/eval/__tests__/run.test.ts`
   - `printsResultsTableOnSuccess()`: mock LLM, capture stdout, verify table rows present
   - `writesBenchmarkJsonAfterRun()`: verify benchmark.json written with correct structure
   - `marksErrorCaseOnLlmFailure()`: one LLM call throws, verify error status in benchmark
   - `continuesAfterOneCaseError()`: 2 cases, first fails, second succeeds, both in benchmark
   - `exitsWithErrorForMissingEvalsJson()`: no evals.json, verify error message
   - `exitsWithErrorForInvalidEvalsJson()`: broken JSON, verify validation error message
   - **Coverage Target**: 90%

**Implementation**:
1. Create `repositories/anton-abyzov/vskill/src/commands/eval/run.ts`
2. Load and validate evals.json via `loadAndValidateEvals`; exit with clear message on failure
3. For each eval case: send prompt to LLM client; for each assertion call `judgeAssertion`; wrap in try/catch to record errors as status="error"
4. Collect `BenchmarkResult`; write via `writeBenchmark`
5. Print results table: each row = eval name | assertion ID | text[:60] | PASS/FAIL/ERROR
6. Run integration tests

---

## Phase 3: CLI Commands — Coverage and Batch Generation

### User Story: US-CLI-003 — Eval Coverage Report

**Linked ACs**: AC-US3-01, AC-US3-02, AC-US3-03, AC-US3-04, AC-US3-05
**Tasks**: 1 total, 0 completed

---

### T-007: Implement eval coverage command

**User Story**: US-CLI-003
**Satisfies ACs**: AC-US3-01, AC-US3-02, AC-US3-03, AC-US3-04, AC-US3-05
**Status**: [ ] pending

**Test Plan**:
- **Given** a repository with 3 skills: one with no evals.json, one with evals.json but no benchmark.json, one with both and all assertions passing
- **When** `vskill eval coverage` is run
- **Then** the terminal table shows 3 rows: Status column shows "MISSING", "PENDING", "PASS" respectively; Last Run shows "-", "-", the benchmark timestamp

- **Given** a skill with benchmark.json where 1 of 3 assertions failed
- **When** `vskill eval coverage` is run
- **Then** that skill's Status column shows "FAIL"

**Test Cases**:
1. **Integration**: `repositories/anton-abyzov/vskill/src/commands/eval/__tests__/coverage.test.ts`
   - `showsMissingStatusForSkillWithoutEvals()`: temp dir, no evals.json, verify MISSING row
   - `showsPendingStatusForSkillWithEvalsNoRun()`: evals.json present, no benchmark, verify PENDING
   - `showsPassStatusWhenAllAssertionsPass()`: benchmark with all pass=true, verify PASS
   - `showsFailStatusWhenAnyAssertionFails()`: benchmark with one pass=false, verify FAIL
   - `tableHasAllRequiredColumns()`: verify columns Plugin, Skill, Cases, Assertions, Last Run, Status
   - **Coverage Target**: 90%

**Implementation**:
1. Create `repositories/anton-abyzov/vskill/src/commands/eval/coverage.ts`
2. Call `scanSkills(root)` to get all skill directories
3. For each skill: call `loadAndValidateEvals` (catch errors -> INVALID status), call `readBenchmark` (null -> PENDING)
4. Derive status: no evals.json -> MISSING, no benchmark -> PENDING, all pass -> PASS, any fail -> FAIL
5. Format and print table with all 6 columns: Plugin, Skill, Cases, Assertions, Last Run, Status
6. Support `--root` flag passed through to `scanSkills`
7. Run integration tests

---

### User Story: US-CLI-004 — Batch Generate Evals

**Linked ACs**: AC-US4-01, AC-US4-02, AC-US4-03, AC-US4-04
**Tasks**: 1 total, 0 completed

---

### T-008: Implement eval generate-all command

**User Story**: US-CLI-004
**Satisfies ACs**: AC-US4-01, AC-US4-02, AC-US4-03, AC-US4-04
**Status**: [ ] pending

**Test Plan**:
- **Given** a repository with 3 skills where 1 already has evals.json
- **When** `vskill eval generate-all` is run
- **Then** evals.json is generated for the 2 skills lacking it, the 1 with existing evals is skipped, and the summary prints "Scanned: 3, Generated: 2, Skipped: 1, Failed: 0"

- **Given** a skill where the LLM returns invalid JSON
- **When** `vskill eval generate-all` is run
- **Then** that skill is marked as failed with a warning logged, remaining skills continue processing, and the summary includes "Failed: 1" with the skill path listed

- **Given** `--force` flag is passed
- **When** `vskill eval generate-all --force` is run
- **Then** evals.json is regenerated even for skills that already have one (0 skipped)

**Test Cases**:
1. **Integration**: `repositories/anton-abyzov/vskill/src/commands/eval/__tests__/generate-all.test.ts`
   - `generatesForSkillsLackingEvals()`: 3 skills, 1 with evals, mock LLM, verify 2 generated
   - `skipsSkillsWithExistingEvals()`: verify skipped count in summary output
   - `continuesAfterLlmFailure()`: one LLM call fails, verify failed count in summary
   - `includesFailedPathsInSummary()`: verify failed skill paths listed
   - `regeneratesWithForceFlag()`: force=true, skills with existing evals also regenerated
   - **Coverage Target**: 90%

**Implementation**:
1. Create `repositories/anton-abyzov/vskill/src/commands/eval/generate-all.ts`
2. Call `scanSkills(root)` to get all skills
3. For each skill sequentially: if `hasEvals && !force`, increment skipped count and continue; else call init logic (reuse `runEvalInit` from `init.ts`)
4. Add 2-second delay between LLM calls (`await new Promise(r => setTimeout(r, 2000))`)
5. Wrap each skill in try/catch; on error: log warning to stderr, push to failed list
6. Print summary: "Scanned: N, Generated: G, Skipped: S, Failed: F" then list failed paths
7. Run integration tests

---

## Phase 4: Platform — GitHub Eval Content Client and API Routes

### User Story: US-WEB-001 + US-WEB-002 — Web Eval Editor

**Linked ACs**: AC-US6-01, AC-US6-02, AC-US6-03, AC-US6-04, AC-US6-05, AC-US7-01, AC-US7-02, AC-US7-03, AC-US7-04, AC-US7-05
**Tasks**: 4 total, 0 completed

---

### T-009: Implement GitHub eval content client

**User Story**: US-WEB-001, US-WEB-002
**Satisfies ACs**: AC-US7-03, AC-US7-04, AC-US7-05 (GitHub layer)
**Status**: [x] completed

**Test Plan**:
- **Given** a valid GitHub repo URL and skill path, and `GITHUB_EVAL_TOKEN` is available on `env`
- **When** `fetchEvalsContent(repoUrl, skillPath, env)` is called
- **Then** it returns `{ content: string, sha: string }` where content is the decoded file text

- **Given** the skill path does not exist in the repository (GitHub API returns 404)
- **When** `fetchEvalsContent()` is called
- **Then** it throws an error with a message indicating the file was not found

- **Given** a modified content string and the original SHA
- **When** `commitEvalsContent(repoUrl, skillPath, content, sha, message, env)` is called
- **Then** it calls the GitHub Contents API PUT endpoint with base64-encoded content and SHA, and returns `{ commitSha: string }`

- **Given** the SHA is stale (GitHub API returns 409 conflict)
- **When** `commitEvalsContent()` is called
- **Then** it throws an error indicating a conflict, preserving the caller's ability to retry

**Test Cases**:
1. **Unit**: `repositories/anton-abyzov/vskill-platform/src/lib/github/__tests__/eval-content.test.ts`
   - `fetchesEvalsContentSuccessfully()`: mock fetch, verify decoded content and SHA returned
   - `throwsOnNotFound()`: mock fetch returns 404, verify error thrown
   - `commitsEvalsContentSuccessfully()`: mock fetch PUT, verify base64 content and SHA in request body
   - `throwsOnConflict()`: mock fetch returns 409, verify conflict error thrown
   - `throwsOnAuthFailure()`: mock fetch returns 403, verify auth error thrown
   - `usesEnvTokenNotProcessEnv()`: verify `env.GITHUB_EVAL_TOKEN` used in Authorization header
   - **Coverage Target**: 95%

**Implementation**:
1. Create `repositories/anton-abyzov/vskill-platform/src/lib/github/eval-content.ts`
2. Implement `fetchEvalsContent(repoUrl: string, skillPath: string, env: { GITHUB_EVAL_TOKEN: string }): Promise<{ content: string; sha: string }>` using `api.github.com/repos/{owner}/{repo}/contents/{path}` with `Authorization: Bearer` header
3. Decode base64 content from API response (`atob` or `Buffer.from(x, 'base64').toString()`)
4. Implement `commitEvalsContent(repoUrl, skillPath, content, sha, message, env): Promise<{ commitSha: string }>` — PUT to same endpoint with `{ message, content: btoa(content), sha }`
5. Handle 404 -> "file not found", 409 -> "conflict", 403 -> "insufficient permissions"
6. Write tests with mocked `fetch` via `vi.hoisted()` + `vi.mock("node-fetch")` or global fetch mock
7. Run `cd repositories/anton-abyzov/vskill-platform && npx vitest run src/lib/github/__tests__/eval-content.test.ts`

---

### T-010: Implement platform API routes for eval editor

**User Story**: US-WEB-001, US-WEB-002
**Satisfies ACs**: AC-US6-01, AC-US6-04, AC-US7-03, AC-US7-04, AC-US7-05
**Status**: [x] completed

**Test Plan**:
- **Given** an admin-authenticated request to `GET /api/v1/admin/evals/skills`
- **When** the route handler is called
- **Then** it returns `{ skills: [{ name, repoUrl, skillPath }] }` listing skills from DB

- **Given** a valid skill name in `GET /api/v1/admin/evals/content?skill=<name>`
- **When** the route handler is called
- **Then** it calls `fetchEvalsContent` and returns `{ content, sha, path }`

- **Given** a `POST /api/v1/admin/evals/commit` request with `{ skillName, content, sha, message }`
- **When** the route handler is called
- **Then** it calls `commitEvalsContent` and returns `{ commitSha, url }`

- **Given** a `POST /api/v1/admin/evals/commit` where the skill is not found in DB
- **When** the route handler is called
- **Then** it returns 404 with a descriptive error message

**Test Cases**:
1. **Integration**: `repositories/anton-abyzov/vskill-platform/src/app/api/v1/admin/evals/__tests__/routes.test.ts`
   - `skillsRouteReturnsSkillList()`: mock DB query, verify response shape
   - `contentRouteReturnsFetchedContent()`: mock GitHub client, verify content and SHA
   - `contentRouteReturns404ForUnknownSkill()`: skill not in DB, verify 404
   - `commitRouteCommitsSuccessfully()`: mock GitHub client, verify commitSha returned
   - `commitRouteReturns409OnConflict()`: mock throws conflict, verify 409 response
   - `routesRequireAdminAuth()`: missing token returns 401
   - **Coverage Target**: 90%

**Implementation**:
1. Create `repositories/anton-abyzov/vskill-platform/src/app/api/v1/admin/evals/skills/route.ts` — GET handler queries DB (Prisma) for skills with known `repoUrl`, returns `{ skills }` array
2. Create `repositories/anton-abyzov/vskill-platform/src/app/api/v1/admin/evals/content/route.ts` — GET handler reads skill from DB, calls `fetchEvalsContent(repoUrl, skillPath, env)`, returns `{ content, sha, path }`
3. Create `repositories/anton-abyzov/vskill-platform/src/app/api/v1/admin/evals/commit/route.ts` — POST handler validates body, calls `commitEvalsContent`, returns `{ commitSha, url }`
4. All routes use existing admin auth middleware pattern (match existing `/api/v1/admin/` routes)
5. Pass `env` from Cloudflare handler context via `getCloudflareContext()` — NOT `process.env` for `GITHUB_EVAL_TOKEN`
6. Run integration tests

---

### T-011: Implement admin evals viewer page (read-only states)

**User Story**: US-WEB-001
**Satisfies ACs**: AC-US6-01, AC-US6-02, AC-US6-05
**Status**: [ ] pending

**Test Plan**:
- **Given** the admin navigates to `/admin/evals`
- **When** the page renders in selector state
- **Then** a skill dropdown is visible listing all skills from the skills API

- **Given** a skill is selected from the dropdown
- **When** the content API returns eval data
- **Then** eval cards are rendered showing name, prompt, expected_output, and each assertion with its ID and text

- **Given** a skill is selected but the API returns 404 (no evals.json)
- **When** the content loads
- **Then** a "No evals found" message is displayed

**Test Cases**:
1. **Component**: `repositories/anton-abyzov/vskill-platform/src/app/admin/evals/__tests__/page.test.tsx`
   - `rendersSkillSelectorOnLoad()`: mock skills API, verify dropdown rendered with skill options
   - `rendersEvalCardsOnSkillSelection()`: mock content API, verify eval cards with name/prompt/assertions
   - `rendersNoEvalsMessageWhen404()`: mock content API returns 404, verify message shown
   - `rendersAllAssertionFields()`: verify assertion ID and text visible in card
   - **Coverage Target**: 85%

**Implementation**:
1. Create `repositories/anton-abyzov/vskill-platform/src/app/admin/evals/page.tsx` as a client component (`"use client"`)
2. On mount: fetch `/api/v1/admin/evals/skills` -> populate skill dropdown
3. On skill selection: fetch `/api/v1/admin/evals/content?skill=<name>` -> store `{ content, sha }` in state; render eval cards
4. Eval card component: show eval name, prompt (full text), expected_output, assertions list (each shows ID and text)
5. Handle 404: show "No evals found for this skill" message
6. Use existing admin page layout/styling patterns (match `/admin/eval` or `/admin/skills` page)
7. Run component tests with `npx vitest run src/app/admin/evals/__tests__/page.test.tsx`

---

### T-012: Implement edit mode and Save & Commit flow

**User Story**: US-WEB-001, US-WEB-002
**Satisfies ACs**: AC-US6-03, AC-US6-04, AC-US7-01, AC-US7-02, AC-US7-03, AC-US7-04, AC-US7-05
**Status**: [ ] pending

**Test Plan**:
- **Given** an eval is loaded in viewer state
- **When** the admin clicks "Edit"
- **Then** the view switches to edit mode with input fields for name, prompt, expected_output, and controls to add/remove/edit assertions; a "Save & Commit" button is visible

- **Given** the admin has modified a field and clicks "Save & Commit"
- **When** the diff preview modal appears
- **Then** it shows a diff between the current GitHub content and the edited version (side-by-side or unified diff)

- **Given** the admin confirms the commit
- **When** the commit API responds with a SHA
- **Then** a success message with the commit SHA is displayed and the view returns to viewer state

- **Given** the commit API returns a 409 conflict
- **When** the commit fails
- **Then** an error message is shown and the edited content is preserved in local state

**Test Cases**:
1. **Component**: `repositories/anton-abyzov/vskill-platform/src/app/admin/evals/__tests__/page.test.tsx` (additional tests in same file)
   - `switchesToEditModeOnEditClick()`: click Edit button, verify input fields rendered
   - `showsDiffPreviewOnSaveAndCommitClick()`: modify a field, click Save & Commit, verify diff modal shown
   - `callsCommitApiOnConfirm()`: mock commit API, click confirm, verify API called with content + SHA
   - `showsSuccessWithCommitSha()`: mock returns commitSha, verify success message displayed
   - `preservesEditsOnCommitFailure()`: mock commit returns 409, verify edited values still in inputs
   - `noAutoSave()`: verify no API calls made while typing (only on explicit Save & Commit click)
   - **Coverage Target**: 85%

**Implementation**:
1. Extend `page.tsx`: add `editMode: boolean` and `editedContent: EvalsFile | null` to local React state
2. "Edit" button sets `editMode=true`, deep-copies fetched content to `editedContent`
3. In edit mode: render text inputs for name/prompt/expected_output; assertion list with add/remove row controls
4. "Save & Commit" button: compute JSON diff (compare `JSON.stringify(originalContent, null, 2)` vs `JSON.stringify(editedContent, null, 2)`); show diff preview modal
5. Confirm in modal: POST to `/api/v1/admin/evals/commit` with `{ skillName, content: JSON.stringify(editedContent), sha, message: "Update evals.json via web editor" }`
6. On 200: show success message with commitSha, set `editMode=false`, refresh content from API
7. On error (409 or other): show error message, keep edit mode and edited values intact
8. Run all component tests including new edit-mode tests

---

## Phase 5: SpecWeave Content Generation

### User Story: US-SW-001 — Eval Content for SpecWeave Skills

**Linked ACs**: AC-US8-01, AC-US8-02, AC-US8-03
**Tasks**: 1 total, 0 completed

---

### T-013: Verify --root flag and batch-generate evals for specweave skills

**User Story**: US-SW-001
**Satisfies ACs**: AC-US8-01, AC-US8-02, AC-US8-03
**Status**: [ ] pending

**Test Plan**:
- **Given** the `--root` flag is passed with a path to specweave's skills directory
- **When** `vskill eval coverage --root <specweave-path>/plugins` is run
- **Then** the coverage table reflects specweave's skill layout, not vskill's default `plugins/`

- **Given** specweave repo with 48 skills lacking evals.json
- **When** `vskill eval generate-all --root repositories/anton-abyzov/specweave/plugins` is run
- **Then** each skill directory that lacks evals.json gets a generated `evals/evals.json` file

- **Given** the generated evals for a specweave skill
- **When** the evals.json is loaded and validated
- **Then** it passes schema validation with 2-3 test cases containing realistic prompts specific to that skill's domain

**Test Cases**:
1. **Integration**: `repositories/anton-abyzov/vskill/src/commands/eval/__tests__/generate-all.test.ts` (additional test)
   - `respectsCustomRootForSpecweavePath()`: mock fs with specweave-style layout, verify scanner uses custom root
   - **Coverage Target**: 90%

2. **Manual verification** (human gate — request user to verify):
   - Run `vskill eval generate-all --root repositories/anton-abyzov/specweave/plugins`
   - Inspect 3 randomly sampled generated evals.json files for realistic prompts and valid schema
   - Run `vskill eval coverage --root repositories/anton-abyzov/specweave/plugins` and confirm all 48 skills show PENDING or PASS status

**Implementation**:
1. Verify `--root` flag is threaded through `eval.ts` router -> `coverage.ts` -> `generate-all.ts` -> `scanSkills(root)` (should already work from T-004/T-007/T-008)
2. Add integration test for custom root with specweave-style layout
3. Scan specweave repo to identify skills already with evals.json: `find repositories/anton-abyzov/specweave -name "evals.json"`
4. Run batch generation against specweave repo (real LLM calls, requires `ANTHROPIC_API_KEY`)
5. Commit generated evals.json files to specweave repo
6. Run coverage report to confirm 100% coverage
7. Ask user to manually verify content quality of generated evals

---

## Task Summary

| Task | User Story | ACs Covered | Status |
|------|-----------|-------------|--------|
| T-001 | US-CLI-005 | AC-US5-01, AC-US5-02, AC-US5-03, AC-US1-05 | [ ] pending |
| T-002 | US-CLI-001 | AC-US1-01 (prereq), AC-US1-02 (prereq) | [ ] pending |
| T-003 | US-CLI-001 | AC-US1-01, AC-US1-02, AC-US1-03, AC-US1-04, AC-US1-05 | [ ] pending |
| T-004 | US-CLI-001, US-CLI-003, US-CLI-004 | AC-US1-01 (wiring), AC-US3-01, AC-US4-01 | [ ] pending |
| T-005 | US-CLI-002 | AC-US2-01, AC-US2-03 (format) | [ ] pending |
| T-006 | US-CLI-002 | AC-US2-01, AC-US2-02, AC-US2-03, AC-US2-04, AC-US2-05 | [ ] pending |
| T-007 | US-CLI-003 | AC-US3-01, AC-US3-02, AC-US3-03, AC-US3-04, AC-US3-05 | [ ] pending |
| T-008 | US-CLI-004 | AC-US4-01, AC-US4-02, AC-US4-03, AC-US4-04 | [ ] pending |
| T-009 | US-WEB-001, US-WEB-002 | AC-US7-03, AC-US7-04, AC-US7-05 (GitHub layer) | [ ] pending |
| T-010 | US-WEB-001, US-WEB-002 | AC-US6-01, AC-US6-04, AC-US7-03, AC-US7-04, AC-US7-05 | [ ] pending |
| T-011 | US-WEB-001 | AC-US6-01, AC-US6-02, AC-US6-05 | [ ] pending |
| T-012 | US-WEB-001, US-WEB-002 | AC-US6-03, AC-US6-04, AC-US7-01, AC-US7-02, AC-US7-03, AC-US7-04, AC-US7-05 | [ ] pending |
| T-013 | US-SW-001 | AC-US8-01, AC-US8-02, AC-US8-03 | [ ] pending |

**Total**: 13 tasks, 0 completed
**AC Coverage**: All 28 ACs from spec.md covered (AC-US1-01 through AC-US8-03)
