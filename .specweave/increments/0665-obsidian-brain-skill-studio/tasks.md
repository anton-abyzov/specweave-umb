---
increment: 0665-obsidian-brain-skill-studio
title: "Obsidian Brain Skill + Skill Studio Agent-Aware Extension"
status: active
test_mode: TDD
---

# Tasks: 0665-obsidian-brain-skill-studio

## WS1: Obsidian Brain Skill
_Location: `repositories/anton-abyzov/vskill/plugins/personal/skills/obsidian-brain/`_
_WS1 is fully parallelizable with WS2. Within WS1: T-001 through T-005 build SKILL.md incrementally; T-006 and T-007 are independent of SKILL.md tasks; T-008 requires T-001–T-007 complete._

---

### T-001: SKILL.md Scaffold + Parametric Config Block
**User Story**: US-001 | **Satisfies ACs**: AC-US1-01, AC-US1-02, AC-US1-06
**Status**: [x] Completed
**Test**: Given `obsidian-brain/` directory does not exist → When SKILL.md is created → Then file is under 500 lines; frontmatter includes `description` and `allowed-tools: [Read, Write, Glob, Grep, Bash, CronCreate]`; a parametric config block declares `vault_path`, `para_folders`, `wiki_dir`, `inbox_dir`, `log_file`, `index_file`, `credentials_folder` as user-configured placeholders; `grep -rn "personal-docs\|/Users/\|/home/" SKILL.md` returns zero matches

---

### T-002: SKILL.md Ingest Operation with Credential Guard
**User Story**: US-002 | **Satisfies ACs**: AC-US2-01, AC-US2-02, AC-US2-03, AC-US2-04, AC-US2-05
**Status**: [x] Completed
**Test**: Given SKILL.md scaffold exists → When the ingest section is written → Then procedure describes reading `inbox_dir`, creating/updating wiki pages with correct frontmatter (`type`, `title`, wikilinks), updating `index.md`, appending log entries with format `YYYY-MM-DD HH:MM | PREFIX | page | details` (prefixes: `+page`, `~page`, `>ingest`, `@link`), routing originals to PARA folder; credential detection block covers API key patterns, `password:`, `token:`, `secret:`, AWS/GCP patterns — on match: stop ingestion, route file to `credentials_folder`, log `!cred` warning, never create wiki page; source files described as read-then-moved only (never written in place)

---

### T-003: SKILL.md Query Synthesis Operation
**User Story**: US-003 | **Satisfies ACs**: AC-US3-01, AC-US3-02, AC-US3-03
**Status**: [x] Completed
**Test**: Given SKILL.md has ingest section → When query operation section is added → Then procedure reads `index.md` to identify relevant pages, reads those pages using Read/Glob/Grep, synthesizes answer with wikilink citations (`[[page-name]]`); optional synthesis page filing is documented (type: synthesis, correct frontmatter, cross-refs, `?query` log prefix); section explicitly states no Obsidian app or CLI dependency — filesystem tools only

---

### T-004: SKILL.md Vault Lint Health Check Operation
**User Story**: US-004 | **Satisfies ACs**: AC-US4-01, AC-US4-02, AC-US4-03, AC-US4-04
**Status**: [x] Completed
**Test**: Given SKILL.md has query section → When lint section is added → Then checks covered: orphan wiki pages (in wiki/ but absent from index), missing concept pages (mentioned but not created), missing cross-references between related pages, inbox backlog exceeding threshold (default: 10); procedure delegates deterministic checks to `scripts/lint-check.sh` and semantic checks to LLM analysis; report categorized by severity (error/warning/info) with actionable fix suggestions per finding; log entries use `!lint` prefix with findings summary

---

### T-005: SKILL.md Scheduled Operation + CronCreate Documentation
**User Story**: US-005 | **Satisfies ACs**: AC-US5-01, AC-US5-02, AC-US5-03, AC-US5-04
**Status**: [x] Completed
**Test**: Given SKILL.md has all three operations → When scheduled operation section is added → Then CronCreate 4x/day setup is documented with configurable interval; pre-flight check covers vault path accessibility, inbox file count, last-run timestamp check to prevent duplicate processing; every run logs start, operations performed, and completion status to `log_file`; errors use `!error` prefix; run priority order: ingest first (if inbox has files) → lint (if threshold exceeded or weekly cadence) → index rebuild

---

### T-006: Reference Files (vault-schema, routing-rules, wiki-format, cron-setup)
**User Story**: US-001 | **Satisfies ACs**: AC-US1-03
**Status**: [x] Completed
**Test**: Given SKILL.md references 4 companion files → When all are created in `references/` → Then: `vault-schema.md` documents the 3-layer architecture (PARA folders + wiki layer + raw/inbox); `routing-rules.md` contains a parametric PARA routing table with no hardcoded personal paths; `wiki-format.md` covers all 5 frontmatter types (entity, concept, source, synthesis, map), slugified naming, YYYY-MM-DD prefix for sources, and wikilink conventions; `cron-setup.md` documents CronCreate configuration and pre-flight checks; `grep -rn "personal-docs\|/Users/\|/home/" references/` returns zero matches

---

### T-007: Shell Scripts (detect-changes, update-index, lint-check)
**User Story**: US-001 | **Satisfies ACs**: AC-US1-04
**Status**: [x] Completed
**Test**: Given `scripts/` directory is created → When three scripts are written → Then: all three pass `bash -n <script>` (syntax check); `detect-changes.sh` outputs inbox file count and lists recently modified files; `update-index.sh` reads wiki page frontmatter and regenerates `wiki/index.md`; `lint-check.sh` outputs orphan page list, missing cross-ref count, and inbox backlog count vs threshold; all scripts use POSIX-compatible syntax (no bashisms, no GNU-only flags)

---

### T-008: Evals (evals/evals.json)
**User Story**: US-001 | **Satisfies ACs**: AC-US1-05
**Status**: [x] Completed
**Test**: Given SKILL.md and all supporting files are complete → When `evals/evals.json` is created → Then it contains ≥5 test cases: (1) clean text file ingest → wiki page with correct frontmatter created, (2) file with `password: abc123` → routed to `credentials_folder`, no wiki page, `!cred` log entry, (3) query on sample vault → answer with ≥1 wikilink citation, (4) vault with orphan page → lint reports error-severity finding, (5) scheduled run with empty inbox → skips ingest, logs completion; each case has `operation`, `input`, and `expected_behavior` fields

---

## WS2: Skill Studio Agent-Aware Extension
_Location: `repositories/anton-abyzov/vskill/src/`_
_WS2 is fully parallelizable with WS1. Within WS2: T-009 precedes T-010 and T-011; T-012 is independent; T-013 precedes T-014._

---

### T-009: agents-registry.ts — filterAgentsByFeatures + getAgentCreationProfile
**User Story**: US-006 | **Satisfies ACs**: AC-US6-01, AC-US6-02, AC-US6-03
**Status**: [x] Completed
**Test**: Given `agents-registry.ts` has 49 agent definitions with `FeatureSupport` → When Vitest unit tests run → Then: `filterAgentsByFeatures({ slashCommands: true })` returns only agents where `featureSupport.slashCommands === true`; `filterAgentsByFeatures({ slashCommands: true, hooks: true })` matches agents satisfying BOTH flags; `getAgentCreationProfile("cursor")` returns `AgentCreationProfile` with non-empty `stripFields`, non-empty `addGuidance`, and `featureSupport` matching Cursor's registry entry; `getAgentCreationProfile("unknown-agent")` returns `undefined`

---

### T-010: skill-create-routes.ts — Agent-Aware Prompt Augmentation
**User Story**: US-007 | **Satisfies ACs**: AC-US7-01, AC-US7-02, AC-US7-03, AC-US7-04
**Status**: [x] Completed
**Test**: Given `BODY_SYSTEM_PROMPT` exists in `skill-create-routes.ts` and `GenerateSkillRequest` interface exists → When Vitest unit tests exercise prompt-building logic → Then: request with no `targetAgents` produces prompt string equal to unmodified `BODY_SYSTEM_PROMPT`; request with `targetAgents: ["cursor"]` produces prompt containing `## Target Agent Constraints` section appended (not a separate template); cursor section includes "Do NOT reference slash commands" and "Do NOT include hook examples"; request with `targetAgents: ["claude-code"]` does NOT append constraint section; constraint text is derived from `getAgentCreationProfile()` feature flags, not hardcoded agent names

---

### T-011: api-routes.ts — GET /api/agents/installed Endpoint
**User Story**: US-008 | **Satisfies ACs**: AC-US8-01, AC-US8-02
**Status**: [x] Completed
**Test**: Given `api-routes.ts` uses an existing custom HTTP router → When Vitest tests mock `detectInstalledAgents()` and invoke `GET /api/agents/installed` → Then response body has `agents` array of length 49; each entry contains `id`, `displayName`, `featureSupport`, `isUniversal`, `installed: boolean`; agents returned by `detectInstalledAgents()` mock have `installed: true`; agents not detected have `installed: false` (present in array, not omitted); response has `suggested` string field

---

### T-012: frontmatter.ts + canonical.ts — target-agents Field Support
**User Story**: US-008 | **Satisfies ACs**: AC-US8-03, AC-US8-04
**Status**: [x] Completed
**Test**: Given `frontmatter.ts` parses SKILL.md YAML frontmatter → When Vitest tests parse a SKILL.md containing `target-agents: claude-code, cursor` → Then parsed result includes `targetAgents: ["claude-code", "cursor"]` as a string array; when `canonical.ts` install logic runs with `targetAgents: ["claude-code", "cursor"]` against 3 detected agents (claude-code, cursor, cline) → Then install executes for claude-code and cursor only; when `targetAgents` is absent → Then canonical.ts installs to all detected agents (existing behavior unchanged, no regression)

---

### T-013: AgentSelector.tsx — Checkbox Group with Feature Indicators
**User Story**: US-009 | **Satisfies ACs**: AC-US9-01, AC-US9-02
**Status**: [x] Completed
**Test**: Given mock agent data from `GET /api/agents/installed` → When Vitest/React Testing Library renders `AgentSelector` with mock props → Then checkboxes render for all agents grouped as "Universal Agents" (`isUniversal: true`) and a second group; each agent row shows 4 feature indicators (slash commands, hooks, MCP, custom system prompt) — visually distinct for supported vs unsupported; agents with `installed: true` have a visual badge/border distinguishing them from `installed: false`; toggling a checkbox fires `onChange(selectedIds: string[])` with the updated selection

---

### T-014: CreateSkillPage.tsx + useCreateSkill.ts — Wire Agent Selection
**User Story**: US-009 | **Satisfies ACs**: AC-US9-03, AC-US9-04
**Status**: [x] Completed
**Test**: Given `AgentSelector.tsx` is complete and API endpoint is available → When Vitest component tests render `CreateSkillPage` with mocked API responses → Then `AgentSelector` is rendered in the form; selecting agents updates local form state; on form submit, `useCreateSkill` sends `targetAgents: string[]` in the POST `/api/skills/generate` body; generated SKILL.md stream contains `target-agents: <selected-ids>` in its YAML frontmatter; agent list is loaded from `GET /api/agents/installed` (not hardcoded)
