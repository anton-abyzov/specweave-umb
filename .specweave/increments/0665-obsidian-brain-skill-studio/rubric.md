---
increment: 0665-obsidian-brain-skill-studio
title: "Obsidian Brain Skill + Skill Studio Agent-Aware Extension"
generated: "2026-04-14"
source: sw-planner
version: "1.0"
status: pending
---

# Quality Contract: 0665-obsidian-brain-skill-studio

> Review and customize criteria (change severity, add/remove) before implementation begins.
> Blocking criteria must pass before `/sw:done` can close this increment.

---

## WS1: Obsidian Brain Skill

### R-001: SKILL.md exists and is under 500 lines [blocking]
- **Source**: AC-US1-01
- **Evaluator**: sw:grill
- **Verify**: File `plugins/personal/skills/obsidian-brain/SKILL.md` exists; `wc -l SKILL.md` < 500; frontmatter contains `description` and `allowed-tools: [Read, Write, Glob, Grep, Bash, CronCreate]`
- **Threshold**: All three conditions pass
- **Result**: [ ] PENDING

### R-002: Parametric config block — no hardcoded paths [blocking]
- **Source**: AC-US1-02, AC-US1-06
- **Evaluator**: sw:grill
- **Verify**: SKILL.md config block defines all 7 parameters as placeholders; `grep -rn "personal-docs\|/Users/\|/home/" obsidian-brain/` returns zero matches across all files
- **Threshold**: Zero hardcoded personal paths anywhere in the plugin directory
- **Result**: [ ] PENDING

### R-003: All 4 reference files created with correct content [blocking]
- **Source**: AC-US1-03
- **Evaluator**: sw:grill
- **Verify**: `references/vault-schema.md`, `routing-rules.md`, `wiki-format.md`, `cron-setup.md` all exist; vault-schema covers 3-layer architecture; routing-rules has parametric table; wiki-format covers all 5 frontmatter types; cron-setup documents CronCreate config
- **Threshold**: All 4 files exist with substantive content (>10 lines each)
- **Result**: [ ] PENDING

### R-004: All 3 shell scripts syntactically valid and functionally correct [blocking]
- **Source**: AC-US1-04
- **Evaluator**: sw:grill
- **Verify**: `bash -n detect-changes.sh && bash -n update-index.sh && bash -n lint-check.sh` all pass; scripts use POSIX-compatible syntax; each script's described behavior matches implementation
- **Threshold**: All 3 syntax checks pass; no bashisms detected
- **Result**: [ ] PENDING

### R-005: evals.json covers all 3 operations + credential detection [blocking]
- **Source**: AC-US1-05
- **Evaluator**: sw:grill
- **Verify**: `evals/evals.json` contains ≥5 test cases; all three operations (ingest, query, lint) have at least one test case; credential detection has a dedicated test case; each test case has `operation`, `input`, `expected_behavior` fields
- **Threshold**: ≥5 test cases, all 3 operations covered, credential case present
- **Result**: [ ] PENDING

### R-006: Ingest operation — wiki page creation and PARA routing [blocking]
- **Source**: AC-US2-01, AC-US2-02, AC-US2-05
- **Evaluator**: sw:grill
- **Verify**: SKILL.md ingest section describes: reading inbox, creating wiki pages with correct frontmatter (type/title/wikilinks), updating index.md, routing originals to PARA folder; source files are read-then-moved, never modified
- **Threshold**: All 5 behaviors documented clearly enough to execute without ambiguity
- **Result**: [ ] PENDING

### R-007: Ingest log entry format correct [blocking]
- **Source**: AC-US2-03
- **Evaluator**: sw:grill
- **Verify**: SKILL.md documents log format `YYYY-MM-DD HH:MM | PREFIX | page | details`; all 4 prefixes (`+page`, `~page`, `>ingest`, `@link`) are defined with their meaning
- **Threshold**: Format and all 4 prefixes documented
- **Result**: [ ] PENDING

### R-008: Credential detection — halt, route, log, never wiki [blocking]
- **Source**: AC-US2-04
- **Evaluator**: sw:grill
- **Verify**: SKILL.md credential detection covers API key patterns, `password:`, `token:`, `secret:`, AWS/GCP patterns; procedure halts ingestion, routes to `credentials_folder`, logs `!cred` warning; explicit instruction to never create wiki page from credential content
- **Threshold**: All 4 detection patterns listed; all 3 response actions documented
- **Result**: [ ] PENDING

### R-009: Query operation — index-driven synthesis with citations [blocking]
- **Source**: AC-US3-01, AC-US3-02, AC-US3-03
- **Evaluator**: sw:grill
- **Verify**: Query section describes index.md → relevant pages → synthesis with wikilink citations; optional synthesis page filing documented (type: synthesis, frontmatter, cross-refs, `?query` log); explicit filesystem-only statement (no Obsidian CLI)
- **Threshold**: All 3 ACs clearly addressed in the section
- **Result**: [ ] PENDING

### R-010: Lint checks — all 4 categories covered [blocking]
- **Source**: AC-US4-01, AC-US4-02
- **Evaluator**: sw:grill
- **Verify**: Lint section covers: orphan pages, missing concept pages, missing cross-references, inbox backlog threshold (default: 10); procedure uses `lint-check.sh` for deterministic + LLM for semantic checks
- **Threshold**: All 4 check types documented; script/LLM split explicit
- **Result**: [ ] PENDING

### R-011: Lint report severity categorization and log format [blocking]
- **Source**: AC-US4-03, AC-US4-04
- **Evaluator**: sw:grill
- **Verify**: SKILL.md lint report format has error/warning/info severity tiers with actionable fix suggestions; log entries use `!lint` prefix with findings summary
- **Threshold**: Three severity tiers defined; `!lint` prefix documented
- **Result**: [ ] PENDING

### R-012: Scheduled operation — CronCreate 4x/day with pre-flight and logging [blocking]
- **Source**: AC-US5-01, AC-US5-02, AC-US5-03, AC-US5-04
- **Evaluator**: sw:grill
- **Verify**: Scheduled section documents CronCreate 4x/day setup; pre-flight covers vault accessibility, inbox count, last-run timestamp; every run logs start/operations/completion; errors use `!error`; priority order: ingest → lint → index rebuild
- **Threshold**: All 4 AC behaviors present and unambiguous
- **Result**: [ ] PENDING

---

## WS2: Skill Studio Agent-Aware Extension

### R-013: filterAgentsByFeatures returns correct subset [blocking]
- **Source**: AC-US6-01
- **Evaluator**: sw:grill
- **Verify**: `filterAgentsByFeatures({ slashCommands: true })` returns only agents matching flag; multi-flag filter returns intersection; unit tests pass
- **Threshold**: Unit tests green; no false positives/negatives in filter logic
- **Result**: [ ] PENDING

### R-014: getAgentCreationProfile returns full profile [blocking]
- **Source**: AC-US6-02, AC-US6-03
- **Evaluator**: sw:grill
- **Verify**: Profile contains non-empty `stripFields`, non-empty `addGuidance`, and `featureSupport` snapshot; unknown agentId returns `undefined`; unit tests pass
- **Threshold**: All three profile fields present; undefined case handled
- **Result**: [ ] PENDING

### R-015: Claude path unchanged when no targetAgents [blocking]
- **Source**: AC-US7-01
- **Evaluator**: sw:grill
- **Verify**: POST `/api/skills/generate` with no `targetAgents` produces prompt string identical to unmodified `BODY_SYSTEM_PROMPT`; unit test asserts string equality
- **Threshold**: String equality assertion passes
- **Result**: [ ] PENDING

### R-016: Non-Claude agents trigger constraint section injection [blocking]
- **Source**: AC-US7-02, AC-US7-03
- **Evaluator**: sw:grill
- **Verify**: `targetAgents: ["cursor"]` appends `## Target Agent Constraints` section to prompt; section contains feature-derived constraints (no slash commands, no hooks, no MCP for Cursor); section is appended to existing prompt, not a separate template
- **Threshold**: Constraint section present; derived from featureSupport flags (not hardcoded)
- **Result**: [ ] PENDING

### R-017: /api/skills/generate accepts targetAgents parameter [blocking]
- **Source**: AC-US7-04
- **Evaluator**: sw:grill
- **Verify**: `GenerateSkillRequest` interface includes `targetAgents?: string[]`; endpoint processes the field and triggers agent-aware augmentation; unit/integration test passes
- **Threshold**: Interface updated; endpoint behavior verified by test
- **Result**: [ ] PENDING

### R-018: GET /api/agents/installed returns all 49 agents with installed flag [blocking]
- **Source**: AC-US8-01, AC-US8-02
- **Evaluator**: sw:grill
- **Verify**: Endpoint returns array of length 49; each entry has `id`, `displayName`, `featureSupport`, `isUniversal`, `installed: boolean`; non-detected agents appear with `installed: false` (not omitted); response has `suggested` field
- **Threshold**: Length 49; no agent omitted; all required fields present
- **Result**: [ ] PENDING

### R-019: target-agents frontmatter parsed correctly [blocking]
- **Source**: AC-US8-03
- **Evaluator**: sw:grill
- **Verify**: `frontmatter.ts` parses `target-agents: claude-code, cursor` as `targetAgents: ["claude-code", "cursor"]`; round-trip parse/serialize maintains order; unit tests pass
- **Threshold**: Parsing correct; unit tests green
- **Result**: [ ] PENDING

### R-020: canonical.ts install filtered by target-agents [blocking]
- **Source**: AC-US8-04
- **Evaluator**: sw:grill
- **Verify**: Install with `targetAgents: ["claude-code", "cursor"]` on 3 detected agents installs to exactly 2 directories; absent `targetAgents` installs to all detected (existing behavior); unit tests cover both cases
- **Threshold**: Filtering correct; no regression on existing install path
- **Result**: [ ] PENDING

### R-021: AgentSelector renders grouped checkboxes with feature indicators [blocking]
- **Source**: AC-US9-01, AC-US9-02
- **Evaluator**: sw:grill
- **Verify**: Component renders agents in two groups (universal/non-universal); each row shows 4 feature indicators (slash commands, hooks, MCP, custom system prompt) with visual distinction; installed agents visually differentiated; checkbox onChange fires with correct ID array
- **Threshold**: Component tests green; all 4 indicators rendered per agent
- **Result**: [ ] PENDING

### R-022: CreateSkillPage wires targetAgents to generation API [blocking]
- **Source**: AC-US9-03, AC-US9-04
- **Evaluator**: sw:grill
- **Verify**: Form submission passes `targetAgents` to POST endpoint; generated SKILL.md contains `target-agents` frontmatter; agent list populated from `/api/agents/installed`; component tests pass
- **Threshold**: End-to-end data flow verified by component tests
- **Result**: [ ] PENDING

---

## Infrastructure Criteria

### R-023: WS2 unit test coverage ≥ 95% on new/modified files [blocking]
- **Source**: spec.md coverage_target: 90 (elevating WS2 to 95% per TDD mode)
- **Evaluator**: vitest --coverage
- **Verify**: `npx vitest run --coverage` reports ≥95% line/branch coverage on agents-registry.ts, skill-create-routes.ts, api-routes.ts, frontmatter.ts, canonical.ts
- **Threshold**: 95% coverage on all 5 modified TypeScript files
- **Result**: [ ] PENDING

### R-024: WS1 evals pass baseline (≥4 of 5 test cases pass) [blocking]
- **Source**: spec.md Success Criteria
- **Evaluator**: vskill eval
- **Verify**: Run evals against evals.json; at least 4 of 5 test cases produce expected behavior
- **Threshold**: 4/5 eval pass rate
- **Result**: [ ] PENDING

### R-025: No new npm dependencies introduced [blocking]
- **Source**: plan.md "No new npm dependencies"
- **Evaluator**: sw:grill
- **Verify**: `git diff package.json` shows no new entries in `dependencies` or `devDependencies` for vskill
- **Threshold**: Zero new dependencies added
- **Result**: [ ] PENDING

### R-026: Independent LLM evaluation [advisory]
- **Source**: Standard closure gate
- **Evaluator**: sw:judge-llm
- **Verify**: sw:judge-llm reviews implementation against spec.md acceptance criteria
- **Threshold**: No critical findings; advisory findings addressed or documented
- **Result**: [ ] PENDING
