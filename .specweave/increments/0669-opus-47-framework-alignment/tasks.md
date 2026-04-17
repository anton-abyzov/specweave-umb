# Tasks: Opus 4.7 Framework Alignment

**Increment**: 0669-opus-47-framework-alignment
**Total ACs**: 77 across 12 user stories
**Wave structure**: 5 waves (P0 → P4)
**TDD enforcement**: STRICT — TypeScript files require [RED] before [GREEN]

---

## Wave 1 — P0 Ship-Blocking Correctness Fixes

### T-001: Remove "extended thinking" and "ULTRATHINK BY DEFAULT" from judge-llm SKILL.md
**User Story**: US-001 | **Satisfies ACs**: AC-US1-01, AC-US1-02 | **Status**: [x] completed
**Model**: opus
**Test Plan**: Given `plugins/specweave/skills/judge-llm/SKILL.md` contains "ULTRATHINK BY DEFAULT" and "extended thinking" → When the file is edited to use adaptive-thinking prompt-hint language and the `xhigh` effort section → Then `grep -c "extended thinking" SKILL.md` returns 0, `grep -c "ULTRATHINK BY DEFAULT" SKILL.md` returns 0, and a "think carefully and step-by-step" hint block exists in the file

---

### T-002: Add adaptive-thinking prompt hint to grill SKILL.md
**User Story**: US-001 | **Satisfies ACs**: AC-US1-03 | **Status**: [x] completed
**Model**: opus
**Test Plan**: Given `plugins/specweave/skills/grill/SKILL.md` has no adaptive-thinking hint → When the review procedure section is edited to add a prompt hint ("think carefully and step-by-step — this evaluation is harder than it looks") → Then `grep -c "think carefully" SKILL.md` returns ≥ 1 and the hint is within the review procedure section (not the frontmatter)

---

### T-003: Verify no SKILL.md contains retired thinking parameter strings
**User Story**: US-001 | **Satisfies ACs**: AC-US1-04 | **Status**: [x] completed
**Model**: opus
**Test Plan**: Given all SKILL.md files under `plugins/specweave/skills/` → When `grep -r "thinking.budget_tokens\|budget_tokens:\|\"thinking\": {" plugins/specweave/skills/**/SKILL.md` is run → Then zero matches are returned (matches in code comments explaining migration are exempt if inside a `<!-- migration note -->` block)

---

### T-004 [RED]: Write failing test for skill-judge.ts model-version thinking guard
**User Story**: US-001 | **Satisfies ACs**: AC-US1-05 | **Status**: [x] completed
**Model**: opus
**Test Plan**: Given `src/core/skills/skill-judge.ts` currently passes a `thinking` parameter unconditionally → When a unit test in `src/core/skills/skill-judge.test.ts` asserts that for a model ID matching `claude-opus-4-7*` no `thinking` param is present in the constructed API request, and that for `claude-opus-4-5*` the param IS present → Then the test file exists and both assertions FAIL (red) because the guard does not yet exist

---

### T-005 [GREEN]: Implement model-version thinking guard in skill-judge.ts
**User Story**: US-001 | **Satisfies ACs**: AC-US1-05 | **Status**: [x] completed
**Model**: opus
**Test Plan**: Given the failing tests from T-004 exist → When `src/core/skills/skill-judge.ts` is edited to add an `isOpus47Family(modelId)` helper and a conditional that omits the `thinking` parameter for 4.7-family models (and a legacy-mode override if `quality.thinkingBudget === "legacy"`) → Then both assertions in `src/core/skills/skill-judge.test.ts` pass (green)

---

### T-006: Create opus-47-migration.md with Wave 1 before/after examples
**User Story**: US-001, US-005 | **Satisfies ACs**: AC-US1-06, AC-US5-10 | **Status**: [x] completed
**Model**: opus
**Test Plan**: Given `.specweave/docs/internal/specs/opus-47-migration.md` does not exist → When the file is created with sections for every Wave 1 change (adaptive thinking removal, team-lead spawn heuristic, TASK_CAP raise) each containing a before/after code sample → Then the file exists, contains the string "before:" and "after:" at least 3 times, and a `grep -c "adaptive-thinking" opus-47-migration.md` returns ≥ 1

---

### T-007: Remove "spawn agents anyway" directive and add fan-out heuristic in team-lead SKILL.md
**User Story**: US-002 | **Satisfies ACs**: AC-US2-01, AC-US2-02 | **Status**: [x] completed
**Model**: opus
**Test Plan**: Given `plugins/specweave/skills/team-lead/SKILL.md` line ~16 contains "Even if the work seems simple enough to do directly — spawn agents anyway" → When the directive is removed and replaced with a heuristic block ("spawn agents when domains ≥ 3 OR tasks ≥ 15 OR `--parallel` flag set") → Then `grep -c "spawn agents anyway" SKILL.md` returns 0 and `grep -c "domains ≥ 3" SKILL.md` returns ≥ 1

---

### T-008: Raise TASK_CAP from 15 to 40 in team-lead SKILL.md
**User Story**: US-005 | **Satisfies ACs**: AC-US5-01 | **Status**: [x] completed
**Model**: opus
**Test Plan**: Given `plugins/specweave/skills/team-lead/SKILL.md` lines ~624-639 contain a `TASK_CAP` constant or prose set to 15 → When the constant is updated to 40 and surrounding prose references the 4.7 long-horizon rationale → Then `grep -c "TASK_CAP.*15\b" SKILL.md` returns 0 and `grep -c "TASK_CAP.*40\b\|40.*tasks" SKILL.md` returns ≥ 1

---

### T-009 [RED]: Write failing backwards-compatibility regression test suite
**User Story**: US-001, US-002, US-005 | **Satisfies ACs**: NFR-1.1 | **Status**: [x] completed
**Model**: opus
**Test Plan**: Given `test/integration/backwards-compat-0669.test.ts` does not exist → When the test file is created with 5 test cases each simulating open/resume/close on a known archived increment fixture → Then the test file exists, all 5 tests FAIL (red) with fixture-missing or not-implemented errors

---

### T-010 [GREEN]: Implement backwards-compatibility test suite with 5 archived increment fixtures
**User Story**: US-001, US-002, US-005 | **Satisfies ACs**: NFR-1.1 | **Status**: [x] completed
**Model**: opus
**Test Plan**: Given the failing test file from T-009 exists → When fixtures for 5 archived increments are created under `test/fixtures/` and the test body is implemented to exercise open/resume/close on each fixture → Then all 5 tests pass (green) confirming existing increment state is unaffected by Wave 1 changes

---

### T-011: Create skill-lint.yml CI workflow enforcing no retired phrases
**User Story**: US-006, NFR-4 | **Satisfies ACs**: AC-US6-06, NFR-4.1 | **Status**: [x] completed
**Model**: opus
**Test Plan**: Given `.github/workflows/skill-lint.yml` does not exist → When the workflow file is created with a grep step that fails if any SKILL.md contains `extended thinking`, `ULTRATHINK BY DEFAULT`, `spawn agents anyway`, or `thinking.budget_tokens` → Then the workflow YAML is valid (`yamllint` returns 0) and a test run with a temporarily injected retired phrase causes the CI step to exit non-zero

---

## Wave 2 — P1 High-Leverage Wins

### T-012 [RED]: Write failing tests for static-context-loader.ts
**User Story**: US-003, US-009 | **Satisfies ACs**: AC-US3-01 | **Status**: [x] completed
**Model**: opus
**Test Plan**: Given `src/core/cache/static-context-loader.ts` does not exist → When tests in `src/core/cache/static-context-loader.test.ts` assert that `loadStaticContext(files)` returns an array with `cache_control: { type: "ephemeral" }` blocks, handles mtime invalidation, and accepts a glob-style list → Then all three assertions FAIL (red) with module-not-found or not-implemented errors

---

### T-013 [GREEN]: Implement static-context-loader.ts
**User Story**: US-003, US-009 | **Satisfies ACs**: AC-US3-01, AC-US9-02 | **Status**: [x] completed
**Model**: opus
**Test Plan**: Given the failing tests from T-012 → When `src/core/cache/static-context-loader.ts` is created with a `loadStaticContext(files: string[]): CacheBlock[]` export that reads each file, checks mtime, and attaches `cache_control: { type: "ephemeral" }` to an aggregated breakpoint → Then all tests in `src/core/cache/static-context-loader.test.ts` pass (green)

---

### T-014 [RED]: Write failing tests for config schema additions
**User Story**: US-009 | **Satisfies ACs**: AC-US9-01, AC-US9-02, AC-US9-03, AC-US9-04 | **Status**: [x] completed
**Model**: opus
**Test Plan**: Given `src/core/config/schema.ts` does not have `quality.thinkingBudget`, `cache.staticContextFiles`, `quality.grillConfidenceThreshold`, or `quality.tokenBudgets` → When tests in `src/core/config/schema.test.ts` assert that parsing a config object with each new key returns the correct default and that unknown values are rejected → Then all assertions FAIL (red)

---

### T-015 [GREEN]: Extend config schema with new quality and cache knobs
**User Story**: US-009 | **Satisfies ACs**: AC-US9-01, AC-US9-02, AC-US9-03, AC-US9-04 | **Status**: [x] completed
**Model**: opus
**Test Plan**: Given failing schema tests from T-014 → When `src/core/config/schema.ts` is edited to add `quality.thinkingBudget` (default `"xhigh"`), `cache.staticContextFiles` (default list), `quality.grillConfidenceThreshold` (default 50), and `quality.tokenBudgets` (default map) → Then all schema tests pass (green)

---

### T-016: Integrate static-context-loader into skill-judge.ts (prompt caching)
**User Story**: US-003 | **Satisfies ACs**: AC-US3-03 | **Status**: [x] completed
**Model**: opus
**Test Plan**: Given `src/core/skills/skill-judge.ts` does not use `static-context-loader` → When the implementation is edited to call `loadStaticContext` and place the resulting cache block before dynamic task content in the API request → Then the existing `skill-judge.test.ts` tests still pass and a new assertion verifies the constructed request has a `cache_control` breakpoint before the first user-message content block

---

### T-017 [RED]: Write failing prompt-caching integration test
**User Story**: US-003 | **Satisfies ACs**: AC-US3-05 | **Status**: [x] completed
**Model**: opus
**Test Plan**: Given `test/integration/prompt-caching.test.ts` does not exist → When the test file is created with an assertion that two consecutive `sw:judge-llm` invocations on the same increment produce `cache_read_input_tokens > 0` in the Anthropic response on the second call → Then the test FAILS (red) because the integration has not yet been wired

---

### T-018 [GREEN]: Wire prompt-caching integration test to pass
**User Story**: US-003 | **Satisfies ACs**: AC-US3-05 | **Status**: [x] completed
**Model**: opus
**Test Plan**: Given the failing integration test from T-017 and the static-context-loader from T-013 → When the test is run against the updated `skill-judge.ts` implementation (T-016) with a real or stubbed Anthropic response that includes `cache_read_input_tokens` → Then the test assertion `cache_read_input_tokens > 0` passes (green)

---

### T-019 [RED]: Write failing test for increment.ts --parallel flag parsing
**User Story**: US-004 | **Satisfies ACs**: AC-US4-03 | **Status**: [x] completed
**Model**: opus
**Test Plan**: Given `src/cli/commands/increment.ts` does not parse a `--parallel` flag → When a unit test asserts that parsing `["--parallel"]` from the argv array sets `options.parallel = true` and parsing `[]` sets it to `false` → Then both assertions FAIL (red)

---

### T-020 [GREEN]: Parse --parallel flag in increment.ts and flow into skill invocation
**User Story**: US-004 | **Satisfies ACs**: AC-US4-03 | **Status**: [x] completed
**Model**: opus
**Test Plan**: Given failing tests from T-019 → When `src/cli/commands/increment.ts` is edited to declare and parse `--parallel` and pass `{ parallel: true }` into the skill invocation options → Then the unit tests pass (green)

---

### T-021 [RED]: Write failing increment single-agent parity test
**User Story**: US-004 | **Satisfies ACs**: AC-US4-04 | **Status**: [x] completed
**Model**: opus
**Test Plan**: Given `test/integration/increment-single-agent-parity.test.ts` does not exist → When the test file is created asserting that single-agent planning output contains `spec.md`, `plan.md`, `tasks.md`, and `rubric.md` with the same top-level structure as the 3-agent path → Then the test FAILS (red) because single-agent path does not yet exist

---

### T-022 [GREEN]: Implement single-agent planning default in increment SKILL.md and pass parity test
**User Story**: US-004 | **Satisfies ACs**: AC-US2-05, AC-US4-01, AC-US4-02, AC-US4-04 | **Status**: [x] completed
**Model**: opus
**Test Plan**: Given failing parity test from T-021 → When `plugins/specweave/skills/increment/SKILL.md` Step 4 is updated to default single-agent and Step 4a is gated behind `--parallel` / ≥10 user stories / keywords, AND the integration test is wired against a test fixture → Then the parity test passes (green) and `grep -c "\-\-parallel" increment/SKILL.md` returns ≥ 1

---

### T-023: Add [DEPRECATED] prefix and migration note to github-sync SKILL.md
**User Story**: US-006 | **Satisfies ACs**: AC-US6-01, AC-US6-04 | **Status**: [x] completed
**Model**: opus
**Test Plan**: Given `plugins/specweave/skills/github-sync/SKILL.md` frontmatter description does not start with `[DEPRECATED]` → When the file is edited to add `[DEPRECATED]` prefix to the description and a `## Migration` section pointing to `sw-github:sync-spec`, plus a one-line deprecation warning at the top of the skill body → Then `grep -c "\[DEPRECATED\]" SKILL.md` returns ≥ 1 and `grep -c "DEPRECATED.*migration\|migration.*DEPRECATED" SKILL.md` returns ≥ 1

---

### T-024: Add [DEPRECATED] prefix and migration note to jira-sync SKILL.md
**User Story**: US-006 | **Satisfies ACs**: AC-US6-01, AC-US6-04 | **Status**: [x] completed
**Model**: opus
**Test Plan**: Given `plugins/specweave/skills/jira-sync/SKILL.md` has no deprecation notice → When edited with `[DEPRECATED]` prefix in description and migration note pointing to `sw-jira:push/pull` plus a deprecation warning line → Then `grep -c "\[DEPRECATED\]" SKILL.md` returns ≥ 1 and `grep -c "sw-jira" SKILL.md` returns ≥ 1

---

### T-025: Add [DEPRECATED] prefix and migration note to ado-sync SKILL.md
**User Story**: US-006 | **Satisfies ACs**: AC-US6-01, AC-US6-04 | **Status**: [x] completed
**Model**: opus
**Test Plan**: Given `plugins/specweave/skills/ado-sync/SKILL.md` has no deprecation notice → When edited with `[DEPRECATED]` prefix and migration note pointing to `sw-ado:push/pull` plus a deprecation warning line → Then `grep -c "\[DEPRECATED\]" SKILL.md` returns ≥ 1 and `grep -c "sw-ado" SKILL.md` returns ≥ 1

---

### T-026: Add [DEPRECATED] prefix and migration note to tdd-red SKILL.md
**User Story**: US-006, US-007 | **Satisfies ACs**: AC-US6-01, AC-US6-04, AC-US7-01 | **Status**: [x] completed
**Model**: opus
**Test Plan**: Given `plugins/specweave/skills/tdd-red/SKILL.md` has no deprecation notice → When edited with `[DEPRECATED]` prefix and migration pointing to `sw:tdd-cycle --phase red` plus deprecation warning → Then `grep -c "\[DEPRECATED\]" SKILL.md` returns ≥ 1 and `grep -c "tdd-cycle.*red\|phase red" SKILL.md` returns ≥ 1

---

### T-027: Add [DEPRECATED] prefix and migration note to tdd-green SKILL.md
**User Story**: US-006, US-007 | **Satisfies ACs**: AC-US6-01, AC-US6-04, AC-US7-01 | **Status**: [x] completed
**Model**: opus
**Test Plan**: Given `plugins/specweave/skills/tdd-green/SKILL.md` has no deprecation notice → When edited with `[DEPRECATED]` prefix and migration pointing to `sw:tdd-cycle --phase green` plus deprecation warning → Then `grep -c "\[DEPRECATED\]" SKILL.md` returns ≥ 1 and `grep -c "tdd-cycle.*green\|phase green" SKILL.md` returns ≥ 1

---

### T-028: Add [DEPRECATED] prefix and migration note to tdd-refactor SKILL.md
**User Story**: US-006, US-007 | **Satisfies ACs**: AC-US6-01, AC-US6-04, AC-US7-01 | **Status**: [x] completed
**Model**: opus
**Test Plan**: Given `plugins/specweave/skills/tdd-refactor/SKILL.md` has no deprecation notice → When edited with `[DEPRECATED]` prefix and migration pointing to `sw:tdd-cycle --phase refactor` plus deprecation warning → Then `grep -c "\[DEPRECATED\]" SKILL.md` returns ≥ 1 and `grep -c "tdd-cycle.*refactor\|phase refactor" SKILL.md` returns ≥ 1

---

### T-029: Deprecate github-issue-standard SKILL.md and move content to docs
**User Story**: US-006 | **Satisfies ACs**: AC-US6-01, AC-US6-02, AC-US6-04 | **Status**: [x] completed
**Model**: opus
**Test Plan**: Given `plugins/specweave/skills/github-issue-standard/SKILL.md` contains the full standard inline → When the full content is moved to `.specweave/docs/internal/specs/github-issue-standard.md` and the SKILL.md becomes a thin redirect ("See: docs/internal/specs/github-issue-standard.md") with `[DEPRECATED]` prefix → Then the docs file exists with content > 50 lines, and `wc -l SKILL.md` returns < 20

---

### T-030: Update tdd-cycle SKILL.md to support --phase flag
**User Story**: US-007 | **Satisfies ACs**: AC-US7-01 | **Status**: [x] completed
**Model**: opus
**Test Plan**: Given `plugins/specweave/skills/tdd-cycle/SKILL.md` does not document `--phase red|green|refactor|all` → When the skill body is updated to document the flag and `--phase all` is called out as the full-cycle default → Then `grep -c "\-\-phase" tdd-cycle/SKILL.md` returns ≥ 3 (once per phase value) and `grep -c "phase all" SKILL.md` returns ≥ 1

---

### T-031: Hide deprecated skills from default /sw:help listing; add --deprecated flag
**User Story**: US-006 | **Satisfies ACs**: AC-US6-03 | **Status**: [x] completed
**Model**: opus
**Test Plan**: Given `plugins/specweave/skills/help/SKILL.md` lists all skills including deprecated ones by default → When the listing logic section is updated to filter out skills with `deprecated: true` in marketplace.json by default, and a `--deprecated` flag is added that surfaces them with migration notes → Then `grep -c "\-\-deprecated" help/SKILL.md` returns ≥ 1 and the filtering logic is documented in the skill body

---

### T-032: Create skill-deprecation-policy.md
**User Story**: US-006 | **Satisfies ACs**: AC-US6-05 | **Status**: [x] completed
**Model**: opus
**Test Plan**: Given `.specweave/docs/internal/specs/skill-deprecation-policy.md` does not exist → When the file is created documenting: deprecated phase (hidden from /sw:help, warning on invoke), hidden phase (removed from discovery), removed phase (deleted), 3-minor-release lifecycle, and listing the 7 current deprecated skills → Then the file exists, `grep -c "deprecated" skill-deprecation-policy.md` returns ≥ 5, and the 7 skill names are present

---

### T-033: Update marketplace.json with deprecated flags and alias routing entries
**User Story**: US-006, US-007 | **Satisfies ACs**: AC-US7-07, NFR-1.4 | **Status**: [x] completed
**Model**: opus
**Test Plan**: Given `plugins/specweave/marketplace.json` has no `deprecated` or `alias` fields → When the file is edited to add `"deprecated": true` on the 7 skills (github-sync, jira-sync, ado-sync, tdd-red, tdd-green, tdd-refactor, github-issue-standard) and alias entries mapping `/sw:tdd-red` → `/sw:tdd-cycle --phase red` etc. → Then `jq '[.skills[] | select(.deprecated == true)] | length' marketplace.json` returns 7 and alias entries exist for all 3 TDD skills

---

### T-034: Create _protocol.md shared agent protocol file
**User Story**: US-008 | **Satisfies ACs**: AC-US8-02 | **Status**: [x] completed
**Model**: opus
**Test Plan**: Given `plugins/specweave/skills/team-lead/agents/_protocol.md` does not exist → When the file is created by extracting the common messaging/TaskUpdate/shutdown-response/PLAN_READY/COMPLETION signal boilerplate from existing agent templates → Then the file exists, `wc -l _protocol.md` returns ≥ 40 (substantive extraction), and the file contains "TaskUpdate", "PLAN_READY", and "COMPLETION" keywords

---

### T-035: Update all agent templates to reference _protocol.md and remove duplicated content
**User Story**: US-008 | **Satisfies ACs**: AC-US8-01, AC-US8-03, AC-US8-04 | **Status**: [x] completed
**Model**: opus
**Test Plan**: Given all agent templates under `plugins/specweave/skills/team-lead/agents/*.md` (excluding _protocol.md) contain duplicated protocol lines → When each template is edited to add "See shared protocol: _protocol.md" header block and duplicated protocol content is removed → Then total line count across `agents/*.md` (excluding _protocol.md) is ≥ 30% less than before the edit (verified by recording pre-edit count and post-edit count), and `grep -rn "See shared protocol" agents/*.md` returns a match per template file

---

### T-036: Delete reviewer-logic.md and reviewer-performance.md orphan templates
**User Story**: US-008 | **Satisfies ACs**: AC-US8-01 | **Status**: [x] completed
**Model**: opus
**Test Plan**: Given `plugins/specweave/skills/team-lead/agents/reviewer-logic.md` and `reviewer-performance.md` exist as orphan templates → When both files are deleted and a git-grep confirms no other file references them → Then `ls plugins/specweave/skills/team-lead/agents/reviewer-logic.md` exits non-zero and `git grep "reviewer-logic\|reviewer-performance" -- '*.md' '*.ts' '*.json'` returns zero matches

---

### T-037 [RED]: Write failing test for template-loader.ts _protocol.md auto-prepend
**User Story**: US-008 | **Satisfies ACs**: AC-US8-05 | **Status**: [x] completed
**Model**: opus
**Test Plan**: Given `src/core/team-lead/template-loader.ts` does not auto-prepend `_protocol.md` content → When a unit test asserts that `loadTemplate("domain-agent.md")` returns a string that starts with the content of `_protocol.md` → Then the assertion FAILS (red) because auto-prepend is not implemented

---

### T-038 [GREEN]: Implement _protocol.md auto-prepend in template-loader.ts
**User Story**: US-008 | **Satisfies ACs**: AC-US8-05 | **Status**: [x] completed
**Model**: opus
**Test Plan**: Given failing test from T-037 → When `src/core/team-lead/template-loader.ts` is edited to read `_protocol.md` and prepend its content before the domain template content → Then the unit test passes (green) and the assembled prompt starts with the shared protocol block

---

### T-039 [RED]: Write failing tests for migrate-config-0669.ts
**User Story**: US-009 | **Satisfies ACs**: AC-US9-06 | **Status**: [x] completed
**Model**: opus
**Test Plan**: Given `scripts/migrate-config-0669.ts` does not exist → When tests in `scripts/migrate-config-0669.test.ts` assert that running the script on a minimal config adds missing keys with defaults, is idempotent on second run, and creates a `.bak-0669` backup → Then all assertions FAIL (red)

---

### T-040 [GREEN]: Implement config migration script
**User Story**: US-009 | **Satisfies ACs**: AC-US9-06 | **Status**: [x] completed
**Model**: opus
**Test Plan**: Given failing tests from T-039 → When `scripts/migrate-config-0669.ts` is created with idempotent key-insertion logic and backup creation → Then all three assertions (adds defaults, idempotent, creates backup) pass (green)

---

### T-041 [RED]: Write failing tests for doctor.ts quality/cache key reporting
**User Story**: US-009 | **Satisfies ACs**: AC-US9-07 | **Status**: [x] completed
**Model**: opus
**Test Plan**: Given `src/cli/commands/doctor.ts` does not report missing `quality.*` or `cache.*` keys → When a unit test asserts that running the doctor against a config missing `quality.thinkingBudget` returns a report containing that key name as a warning → Then the assertion FAILS (red)

---

### T-042 [GREEN]: Extend doctor.ts to report missing quality.* and cache.* keys
**User Story**: US-009 | **Satisfies ACs**: AC-US9-07 | **Status**: [x] completed
**Model**: opus
**Test Plan**: Given failing test from T-041 → When `src/cli/commands/doctor.ts` is edited to check for all new config keys and emit a warning for each missing one → Then the unit test passes (green) and running `specweave doctor` on a minimal config emits warnings for the new keys

---

### T-043: Add prompt-caching sections to grill, code-reviewer, and done SKILL.md files
**User Story**: US-003 | **Satisfies ACs**: AC-US3-04 | **Status**: [x] completed
**Model**: opus
**Test Plan**: Given `plugins/specweave/skills/{grill,code-reviewer,done}/SKILL.md` have no "Prompt Caching" section → When each file is edited to add a section explaining which files are cached and how to extend the list via `cache.staticContextFiles` → Then `grep -c "Prompt Caching" grill/SKILL.md` returns ≥ 1 and same for code-reviewer and done

---

### T-044: Create config-reference.md documenting all new config knobs
**User Story**: US-009 | **Satisfies ACs**: AC-US9-05 | **Status**: [x] completed
**Model**: opus
**Test Plan**: Given `.specweave/docs/internal/specs/config-reference.md` does not exist → When the file is created with entries for each of the 4 new knobs (`quality.thinkingBudget`, `cache.staticContextFiles`, `quality.grillConfidenceThreshold`, `quality.tokenBudgets`), each with default value, allowed values, and description → Then the file exists and `grep -c "Default:" config-reference.md` returns ≥ 4

---

### T-045: Create planning-modes.md documenting single-agent vs parallel modes
**User Story**: US-004 | **Satisfies ACs**: AC-US4-05 | **Status**: [x] completed
**Model**: opus
**Test Plan**: Given `.specweave/docs/internal/specs/planning-modes.md` does not exist → When the file is created with a decision matrix (feature size, user-story count, `--parallel` flag, explicit keywords) and before/after examples → Then the file exists, `grep -c "\-\-parallel" planning-modes.md` returns ≥ 2, and a table or list with decision criteria exists

---

### T-046: Update team-merge SKILL.md to run closure inline for ≤5 increments
**User Story**: US-002 | **Satisfies ACs**: AC-US2-06 | **Status**: [x] completed
**Model**: opus
**Test Plan**: Given `plugins/specweave/skills/team-merge/SKILL.md` lines ~81-92 always spawn a `sw-closer` subagent regardless of increment count → When the section is updated to run closure inline when merging ≤5 increments and only spawn the subagent for larger merges → Then `grep -c "inline closure\|≤ 5\|<= 5\|fewer than.*increment" team-merge/SKILL.md` returns ≥ 1

---

## Wave 3 — P2 Quality Improvements

### T-047: Collapse code-reviewer fan-out from 8 reviewers to 3 in SKILL.md
**User Story**: US-002 | **Satisfies ACs**: AC-US2-03, AC-US2-04 | **Status**: [x] completed
**Model**: opus
**Test Plan**: Given `plugins/specweave/skills/code-reviewer/SKILL.md` documents 8 parallel specialists and a 10-haiku validator fan-out → When the file is edited to reduce to 3 reviewers (security, logic, performance), replace haiku fan-out with inline self-critique, and add `--full-fanout` opt-in flag → Then `grep -c "independent-finding-validator\|haiku.*validator" SKILL.md` returns 0 and `grep -c "security.*logic.*performance\|3 reviewer" SKILL.md` returns ≥ 1

---

### T-048: Remove per-task model hints from do SKILL.md; use xhigh default
**User Story**: US-002 | **Satisfies ACs**: AC-US2-07 | **Status**: [x] completed
**Model**: opus
**Test Plan**: Given `plugins/specweave/skills/do/SKILL.md` line ~158 contains per-task model hints (haiku/sonnet/opus) → When those hints are removed and replaced with a single `xhigh` effort tier reference → Then `grep -c "haiku\|sonnet.*per.task\|per.task.*model" do/SKILL.md` returns 0 and `grep -c "xhigh" do/SKILL.md` returns ≥ 1

---

### T-049: Remove --simple mode and add --simple-compat alias in auto SKILL.md
**User Story**: US-005 | **Satisfies ACs**: AC-US5-02 | **Status**: [x] completed
**Model**: opus
**Test Plan**: Given `plugins/specweave/skills/auto/SKILL.md` lines ~47-57 have `--simple` as a default path → When the default is removed, a `--simple-compat` alias is added with a deprecation warning note, and a "Native Auto Mode" section is added → Then `grep -c "\\-\\-simple-compat" auto/SKILL.md` returns ≥ 1 and `grep -c "\\-\\-simple.*default\|default.*\\-\\-simple" auto/SKILL.md` returns 0

---

### T-050: Remove state-marker STEP 0 from pm SKILL.md and interview-state markers
**User Story**: US-005 | **Satisfies ACs**: AC-US5-03, AC-US5-05 | **Status**: [x] completed
**Model**: opus
**Test Plan**: Given `plugins/specweave/skills/pm/SKILL.md` lines ~18-34 contain a STEP 0 that writes a skill-chain state-marker file and lines ~79-96 reference `interview-*.json` state files → When both sections are removed (STEP 0 deleted, interview state managed in memory only) → Then `grep -c "skill-chain.*json\|interview.*json\|STEP 0" pm/SKILL.md` returns 0

---

### T-051: Remove state-marker STEP 0 from architect SKILL.md
**User Story**: US-005 | **Satisfies ACs**: AC-US5-03 | **Status**: [x] completed
**Model**: opus
**Test Plan**: Given `plugins/specweave/skills/architect/SKILL.md` lines ~9-24 contain a STEP 0 that writes a skill-chain state-marker file → When that section is removed → Then `grep -c "skill-chain.*json\|STEP 0.*state\|write.*marker" architect/SKILL.md` returns 0

---

### T-052 [RED]: Write failing tests for pretooluse-guard.ts TaskGet-based rewrite
**User Story**: US-005 | **Satisfies ACs**: AC-US5-03 | **Status**: [x] completed
**Model**: opus
**Test Plan**: Given `src/core/hooks/pretooluse-guard.ts` reads filesystem marker files to determine guard state → When tests in `src/core/hooks/pretooluse-guard.test.ts` assert that the guard succeeds (allows tool use) when no filesystem markers exist AND `TaskGet` returns the expected planner state, and the tests are run against the unmodified guard → Then the "no filesystem markers" test case FAILS (red)

---

### T-053 [GREEN]: Rewrite pretooluse-guard.ts to use TaskGet-based state with filesystem fallback
**User Story**: US-005 | **Satisfies ACs**: AC-US5-03 | **Status**: [x] completed
**Model**: opus
**Test Plan**: Given failing tests from T-052 → When `src/core/hooks/pretooluse-guard.ts` is rewritten to check TaskGet first, fall back to filesystem markers if TaskGet returns nothing (dual-read transition period), and tolerate absence of both gracefully → Then all guard tests pass (green) including the no-marker case

---

### T-054: Lower grill confidence threshold from 70 to 50 in SKILL.md; read from config
**User Story**: US-005 | **Satisfies ACs**: AC-US5-04 | **Status**: [x] completed
**Model**: opus
**Test Plan**: Given `plugins/specweave/skills/grill/SKILL.md` lines ~156-173 hardcode a confidence threshold of 70 → When the value is changed to 50 and the prose references `quality.grillConfidenceThreshold` as the config override → Then `grep -c "70.*threshold\|threshold.*70" grill/SKILL.md` returns 0 and `grep -c "50\|grillConfidenceThreshold" grill/SKILL.md` returns ≥ 2

---

### T-055: Raise code-review fix-loop cap from 3 to 5 in done SKILL.md
**User Story**: US-005 | **Satisfies ACs**: AC-US5-07 | **Status**: [x] completed
**Model**: opus
**Test Plan**: Given `plugins/specweave/skills/done/SKILL.md` lines ~58-67 cap the code-review fix loop at 3 iterations → When the cap is changed to 5 → Then `grep -c "max.*3.*iteration\|3.*iteration.*max\|cap.*3" done/SKILL.md` returns 0 and `grep -c "5.*iteration\|cap.*5" done/SKILL.md` returns ≥ 1

---

### T-056: Raise token budgets 3x in pm and brainstorm SKILL.md; reference config
**User Story**: US-005 | **Satisfies ACs**: AC-US5-08 | **Status**: [x] completed
**Model**: opus
**Test Plan**: Given `plugins/specweave/skills/pm/SKILL.md` lines ~163-168 hardcode 400/500/600 token budgets and `brainstorm/SKILL.md` lines ~508-524 have similar values → When each hardcoded value is multiplied by 3 (→ 1200/1500/1800) and prose references `quality.tokenBudgets` config key → Then `grep -c ": 400\|: 500\|: 600" pm/SKILL.md brainstorm/SKILL.md` returns 0

---

### T-057: Remove active-phase forbidden-list from team-lead SKILL.md
**User Story**: US-005 | **Satisfies ACs**: AC-US5-09 | **Status**: [x] completed
**Model**: opus
**Test Plan**: Given `plugins/specweave/skills/team-lead/SKILL.md` lines ~863-888 contain a "forbidden-list" of closure skills that cannot be loaded during the active phase → When that section is removed → Then `grep -c "forbidden.*list\|forbidden-list\|no closure.*active" team-lead/SKILL.md` returns 0

---

### T-058: Raise heartbeat stuck-detection thresholds in team-lead SKILL.md
**User Story**: US-005 | **Satisfies ACs**: AC-US5-06 | **Status**: [x] completed
**Model**: opus
**Test Plan**: Given `plugins/specweave/skills/team-lead/SKILL.md` lines ~928-979 set no-progress window at 2min and total-stuck at 10min → When both values are raised (2min → 5min no-progress; 10min → 20min total-stuck) and surrounding prose explains the 4.7 long-horizon rationale → Then `grep -c "2.*min.*progress\|progress.*2.*min" team-lead/SKILL.md` returns 0 and `grep -c "5.*min\|20.*min" team-lead/SKILL.md` returns ≥ 2

---

### T-059: Add tool-use-rationale block to judge-llm SKILL.md
**User Story**: US-010 | **Satisfies ACs**: AC-US10-01 | **Status**: [x] completed
**Model**: opus
**Test Plan**: Given `plugins/specweave/skills/judge-llm/SKILL.md` allowed-tools line is not followed by a rationale block → When a `## Tool-Use Rationale` or `tool-use-rationale:` block is added after the `allowed-tools` line explaining when each tool (Read/Grep/Glob/Bash) is called → Then `grep -c "tool-use-rationale\|Tool-Use Rationale" judge-llm/SKILL.md` returns ≥ 1

---

### T-060: Add tool-use-rationale blocks to 8 additional core skills
**User Story**: US-010 | **Satisfies ACs**: AC-US10-02 | **Status**: [x] completed
**Model**: opus
**Test Plan**: Given `plugins/specweave/skills/{grill,code-reviewer,do,pm,architect,done,team-lead,increment}/SKILL.md` have no `tool-use-rationale` block → When each file is edited to add the block after the `allowed-tools` line explaining when each declared tool is invoked → Then `grep -rn "tool-use-rationale\|Tool-Use Rationale" plugins/specweave/skills/{grill,code-reviewer,do,pm,architect,done,team-lead,increment}/SKILL.md` returns ≥ 8 matches (one per file)

---

### T-061 [RED]: Write failing tests for skill-lint.ts tool-use-rationale enforcement
**User Story**: US-010 | **Satisfies ACs**: AC-US10-03 | **Status**: [x] completed
**Model**: opus
**Test Plan**: Given `plugins/specweave/.lint/skill-lint.ts` does not exist → When tests assert that linting a SKILL.md with `allowed-tools` but no `tool-use-rationale` returns a lint error, and linting one with both returns success → Then both assertions FAIL (red)

---

### T-062 [GREEN]: Implement skill-lint.ts to enforce tool-use-rationale presence
**User Story**: US-010 | **Satisfies ACs**: AC-US10-03 | **Status**: [x] completed
**Model**: opus
**Test Plan**: Given failing tests from T-061 → When `plugins/specweave/.lint/skill-lint.ts` is created to parse SKILL.md frontmatter, detect `allowed-tools`, and error if no `tool-use-rationale` block follows → Then both lint tests pass (green)

---

### T-063: Update skill-authoring-guide.md with "Documenting Tool Use" section
**User Story**: US-010 | **Satisfies ACs**: AC-US10-04 | **Status**: [x] completed
**Model**: opus
**Test Plan**: Given `.specweave/docs/internal/specs/skill-authoring-guide.md` has no "Documenting Tool Use" section → When the section is added with a before/after example showing a SKILL.md without and with `tool-use-rationale` → Then `grep -c "Documenting Tool Use" skill-authoring-guide.md` returns ≥ 1 and the file contains "before:" and "after:" examples

---

### T-064: Create effort-levels.md documenting xhigh default and max opt-in
**User Story**: US-011 | **Satisfies ACs**: AC-US11-01 | **Status**: [x] completed
**Model**: opus
**Test Plan**: Given `.specweave/docs/internal/specs/effort-levels.md` does not exist → When the file is created documenting: `xhigh` as default for planning/implementation/review, `high` for short-and-sweet skills, `max` opt-in via `--effort max` with warning → Then the file exists, `grep -c "xhigh" effort-levels.md` returns ≥ 3, and `grep -c "max.*warning\|warning.*max\|overthinking" effort-levels.md` returns ≥ 1

---

### T-065: Add effort-level "Model Configuration" section to judge-llm, grill, and code-reviewer SKILL.md
**User Story**: US-011 | **Satisfies ACs**: AC-US11-02, AC-US11-03 | **Status**: [x] completed
**Model**: opus
**Test Plan**: Given `plugins/specweave/skills/{judge-llm,grill,code-reviewer}/SKILL.md` have no "Model Configuration" section documenting effort level → When each is edited to add a section declaring `xhigh` as default and `--effort max` as opt-in → Then `grep -c "Model Configuration" judge-llm/SKILL.md grill/SKILL.md code-reviewer/SKILL.md` returns 3

---

### T-066: Update increment SKILL.md line 4 to document effort-level expectation
**User Story**: US-011 | **Satisfies ACs**: AC-US11-04 | **Status**: [x] completed
**Model**: opus
**Test Plan**: Given `plugins/specweave/skills/increment/SKILL.md` line 4 shows `model: opus` with no effort-level context → When the line or adjacent section is updated to reference `xhigh` effort and the 4.7 rationale → Then `grep -c "xhigh" increment/SKILL.md` returns ≥ 1

---

### T-067 [RED]: Write failing test for dispatcher.ts --effort flag parsing
**User Story**: US-011 | **Satisfies ACs**: AC-US11-05 | **Status**: [x] completed
**Model**: opus
**Test Plan**: Given `src/cli/dispatcher.ts` does not parse `--effort <level>` → When a unit test asserts that parsing `["--effort", "xhigh"]` sets `options.effort = "xhigh"` and parsing `["--effort", "invalid"]` returns a validation error → Then both assertions FAIL (red)

---

### T-068 [GREEN]: Implement --effort flag parsing and propagation in dispatcher.ts
**User Story**: US-011 | **Satisfies ACs**: AC-US11-05 | **Status**: [x] completed
**Model**: opus
**Test Plan**: Given failing tests from T-067 → When `src/cli/dispatcher.ts` is edited to declare `--effort` with allowed values `low|medium|high|xhigh|max` and propagate into skill invocation options → Then both unit tests pass (green)

---

### T-069: Add "Native Auto Mode" section and advisory to auto SKILL.md
**User Story**: US-012 | **Satisfies ACs**: AC-US12-01, AC-US12-02 | **Status**: [x] completed
**Model**: opus
**Test Plan**: Given `plugins/specweave/skills/auto/SKILL.md` has no "Native Auto Mode" section → When the section is added documenting Shift+Tab native auto mode, when `sw:auto` is preferred (increment-aware gates, external sync), and the one-time advisory message → Then `grep -c "Native Auto Mode\|Shift+Tab" auto/SKILL.md` returns ≥ 2

---

### T-070 [RED]: Write failing tests for auto.ts --respect-native and --force-sw-auto flags
**User Story**: US-012 | **Satisfies ACs**: AC-US12-03 | **Status**: [x] completed
**Model**: opus
**Test Plan**: Given `src/cli/commands/auto.ts` does not parse `--respect-native` or `--force-sw-auto` → When tests assert that parsing `["--respect-native"]` sets `options.respectNative = true` (default true) and `["--force-sw-auto"]` sets `options.forceSw = true` → Then both FAIL (red)

---

### T-071 [GREEN]: Implement --respect-native and --force-sw-auto flags in auto.ts
**User Story**: US-012 | **Satisfies ACs**: AC-US12-03 | **Status**: [x] completed
**Model**: opus
**Test Plan**: Given failing tests from T-070 → When `src/cli/commands/auto.ts` is edited to parse both flags with `--respect-native` defaulting to true on Claude Code → Then unit tests pass (green)

---

### T-072: Create auto-mode-decision-tree.md
**User Story**: US-012 | **Satisfies ACs**: AC-US12-04 | **Status**: [x] completed
**Model**: opus
**Test Plan**: Given `.specweave/docs/internal/specs/auto-mode-decision-tree.md` does not exist → When the file is created with a decision tree or matrix documenting when to use native Shift+Tab auto vs `sw:auto` (with concrete examples: "increment-aware gates → sw:auto", "simple exploration → native") → Then the file exists, `grep -c "Shift+Tab\|sw:auto" auto-mode-decision-tree.md` returns ≥ 4, and at least 3 concrete example scenarios are present

---

### T-073: Verify auto-status and cancel-auto commands are unaffected
**User Story**: US-012 | **Satisfies ACs**: AC-US12-05 | **Status**: [x] completed
**Model**: opus
**Test Plan**: Given `plugins/specweave/skills/auto-status/SKILL.md` and the cancel-auto equivalent exist as first-class commands → When `grep -rn "auto-status\|cancel-auto" plugins/specweave/skills/auto/SKILL.md plugins/specweave/skills/auto-status/SKILL.md` is run → Then both commands are still referenced and no deprecation notice has been added to auto-status or cancel-auto SKILL.md files

---

## Wave 4 — P3 Consolidation & UX

### T-074: Create multi-project SKILL.md consolidating github and ado multi-project skills
**User Story**: US-007 | **Satisfies ACs**: AC-US7-02 | **Status**: [x] completed
**Model**: opus
**Test Plan**: Given `plugins/specweave/skills/multi-project/SKILL.md` does not exist → When the file is created with `--tool github|ado|jira` flag support, merging logic from `github-multi-project` and `ado-multi-project` and adding JIRA support → Then the file exists, `grep -c "\-\-tool" multi-project/SKILL.md` returns ≥ 3 (one per tool value), and JIRA is covered in at least one section

---

### T-075: Deprecate github-multi-project and ado-multi-project SKILL.md with alias redirects
**User Story**: US-007 | **Satisfies ACs**: AC-US7-02 | **Status**: [x] completed
**Model**: opus
**Test Plan**: Given `plugins/specweave/skills/github-multi-project/SKILL.md` and `ado-multi-project/SKILL.md` have no deprecation notice → When each is edited to add `[DEPRECATED]` prefix and migration note (`github-multi-project` → `sw:multi-project --tool github`; `ado-multi-project` → `sw:multi-project --tool ado`) → Then `grep -c "\[DEPRECATED\]" github-multi-project/SKILL.md ado-multi-project/SKILL.md` returns 2

---

### T-076: Add marketplace.json alias entries for multi-project deprecated skills
**User Story**: US-007 | **Satisfies ACs**: AC-US7-07 | **Status**: [x] completed
**Model**: opus
**Test Plan**: Given `plugins/specweave/marketplace.json` has no alias entries for `github-multi-project` or `ado-multi-project` → When alias entries are added routing both to `sw:multi-project --tool github` and `sw:multi-project --tool ado` respectively → Then `jq '[.skills[] | select(.alias != null and (.name | test("multi-project")))] | length' marketplace.json` returns ≥ 2

---

### T-077: Fold team-build preset logic into team-lead --preset; deprecate team-build SKILL.md
**User Story**: US-007 | **Satisfies ACs**: AC-US7-04 | **Status**: [x] completed
**Model**: opus
**Test Plan**: Given `plugins/specweave/skills/team-build/SKILL.md` contains full preset logic and `team-lead/SKILL.md` has no `--preset` flag → When `team-lead/SKILL.md` is updated with a `--preset <name>` section containing the folded logic, and `team-build/SKILL.md` is reduced to a thin alias that prints a deprecation warning and calls `sw:team-lead --preset` → Then `wc -l team-build/SKILL.md` returns < 30 and `grep -c "\-\-preset" team-lead/SKILL.md` returns ≥ 2

---

### T-078: Mark plan SKILL.md as deprecated for standalone use; add --regenerate-plan to increment
**User Story**: US-007 | **Satisfies ACs**: AC-US7-05 | **Status**: [x] completed
**Model**: opus
**Test Plan**: Given `plugins/specweave/skills/plan/SKILL.md` operates as a standalone planning skill → When the file is edited to mark it as deprecated for standalone use (regenerate-only mode via `sw:increment --regenerate-plan`) and the migration note is added → Then `grep -c "\[DEPRECATED\].*standalone\|regenerate-plan" plan/SKILL.md` returns ≥ 1 and `grep -c "\-\-regenerate-plan" plugins/specweave/skills/increment/SKILL.md` returns ≥ 1

---

### T-079: Simplify close-all SKILL.md from ~200 lines to ~40 lines
**User Story**: US-007 | **Satisfies ACs**: AC-US7-06 | **Status**: [x] completed
**Model**: opus
**Test Plan**: Given `plugins/specweave/skills/close-all/SKILL.md` is ~200 lines and implements per-increment closure logic directly → When the file is rewritten to ~40 lines containing only the batch-discovery loop and delegating per-increment closure to `sw:done` → Then `wc -l close-all/SKILL.md` returns ≤ 60 and `grep -c "sw:done\|delegate.*done" close-all/SKILL.md` returns ≥ 1

---

### T-080 [RED]: Write failing tests for resource-base.ts shared validator module
**User Story**: US-007 | **Satisfies ACs**: AC-US7-03 | **Status**: [x] completed
**Model**: opus
**Test Plan**: Given `src/core/validators/resource-base.ts` does not exist → When tests in `src/core/validators/resource-base.test.ts` assert that a concrete subclass (e.g., GitHubResourceValidator) inherits base methods and the interface is compatible with jira/ado validators → Then the assertions FAIL (red)

---

### T-081 [GREEN]: Implement resource-base.ts shared validator module
**User Story**: US-007 | **Satisfies ACs**: AC-US7-03 | **Status**: [x] completed
**Model**: opus
**Test Plan**: Given failing tests from T-080 → When `src/core/validators/resource-base.ts` is created with a shared abstract base class or interface containing common validation methods → Then all resource-base tests pass (green)

---

## Wave 5 — P4 Telemetry, Benchmarks & Release

### T-082 [RED]: Write failing tests for cache-metrics.ts
**User Story**: US-003 | **Satisfies ACs**: AC-US3-06, NFR-4.3 | **Status**: [x] completed
**Model**: opus
**Test Plan**: Given `src/core/telemetry/cache-metrics.ts` does not exist → When tests assert that `recordCacheHit(skillName, tokens)` increments a counter and `getCacheHitRate(skillName)` returns the hit rate as a number 0-1 → Then both assertions FAIL (red)

---

### T-083 [GREEN]: Implement cache-metrics.ts telemetry module
**User Story**: US-003 | **Satisfies ACs**: AC-US3-06, NFR-4.3 | **Status**: [x] completed
**Model**: opus
**Test Plan**: Given failing tests from T-082 → When `src/core/telemetry/cache-metrics.ts` is created with `recordCacheHit`, `getCacheHitRate`, and a `clearMetrics` helper → Then all cache-metrics tests pass (green)

---

### T-084: Add --cache-stats section to analytics SKILL.md
**User Story**: US-003 | **Satisfies ACs**: AC-US3-06 | **Status**: [x] completed
**Model**: opus
**Test Plan**: Given `plugins/specweave/skills/analytics/SKILL.md` has no `--cache-stats` section → When the section is added documenting cache hit rate output format and the `analytics.cacheMetrics.enabled` config knob → Then `grep -c "\-\-cache-stats" analytics/SKILL.md` returns ≥ 1

---

### T-085: Create agent-spawn-count benchmark
**User Story**: US-002, US-004 | **Satisfies ACs**: NFR-4.4 | **Status**: [x] completed
**Model**: opus
**Test Plan**: Given `test/benchmarks/agent-spawn-count.bench.ts` does not exist → When the file is created measuring agent spawn count on a baseline 5-task increment (using fixtures from T-086) and asserting the post-0669 count is ≤ 50% of the pre-0669 baseline → Then the file exists and running `npx vitest bench` picks up and executes the benchmark

---

### T-086: Create baseline-increment fixture for benchmarking
**User Story**: US-002, US-004 | **Satisfies ACs**: NFR-4.4 | **Status**: [x] completed
**Model**: opus
**Test Plan**: Given `test/fixtures/baseline-increment/` does not exist → When the directory is created with a canonical 5-task increment fixture (spec.md, plan.md, tasks.md, metadata.json matching the standard format) → Then `ls test/fixtures/baseline-increment/*.md` returns at least 3 files and each file conforms to the expected schema

---

### T-087: Create follow-up-audits.md listing 20 non-priority skills
**User Story**: US-001, US-006 | **Satisfies ACs**: NFR-3.1 | **Status**: [x] completed
**Model**: opus
**Test Plan**: Given `.specweave/docs/internal/specs/follow-up-audits.md` does not exist → When the file is created listing all 20 non-priority skills (sw:lsp, sw:qa, sw:npm, sw:release-*, sw:ado-*, sw:jira-*, sw:docs-*, sw:umbrella, sw:discrepancies, sw:skill-gen, sw:image, sw:video, sw:remotion) with brief audit notes for each → Then the file exists and `grep -c "sw:" follow-up-audits.md` returns ≥ 20

---

### T-088: Update CHANGELOG.md with 0669 / v1.1.0 entry
**User Story**: US-001, US-005, US-006 | **Satisfies ACs**: NFR-3.2 | **Status**: [x] completed
**Model**: opus
**Test Plan**: Given `CHANGELOG.md` has no entry for the 0669 / v1.1.0 release → When an entry is added at the top with an "Opus 4.7 Alignment" heading, calling out fixed extended-thinking removal, `--simple` deprecation, state markers removal, and linking to `opus-47-migration.md` → Then `grep -c "Opus 4.7 Alignment\|v1.1.0\|0669" CHANGELOG.md` returns ≥ 3

---

### T-089: Update README.md "Upgrading" section with 0669 migration pointer
**User Story**: US-001, US-005 | **Satisfies ACs**: NFR-3.3 | **Status**: [x] completed
**Model**: opus
**Test Plan**: Given `README.md` has no "Upgrading" section referencing 0669 → When a section is added or updated referencing `opus-47-migration.md` and listing the 3 P0 fixes → Then `grep -c "opus-47-migration\|Upgrading\|P0" README.md` returns ≥ 2

---

### T-090: Final NFR audit — verify all NFR-4 CI checks pass
**User Story**: US-001, US-002, US-006, US-007 | **Satisfies ACs**: NFR-4.1, NFR-4.2, NFR-4.3 | **Status**: [x] completed
**Model**: opus
**Test Plan**: Given all Wave 1–5 tasks are complete → When the following checks are run: (a) `skill-lint` CI grep confirms zero retired phrases; (b) a skill-count script reports non-deprecated skill count ≤ 40; (c) `sw:analytics --cache-stats` on a canary increment shows cache hit rate ≥ 40% → Then all three checks pass without error
