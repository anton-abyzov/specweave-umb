---
increment: 0548-skill-gen-autoinstall-dedup-docs
generated: 2026-03-16
---

# Tasks: Skill-Gen Auto-Install, Dedup, Docs

## Stream A — Auto-Install Skill-Creator

### T-001: Create `skill-creator-installer.ts` with `ensureSkillCreator()`
**User Story**: US-001 | **Satisfies ACs**: AC-US1-01, AC-US1-02, AC-US1-03
**Status**: [x] completed
**Test**: Given a new module `src/cli/helpers/init/skill-creator-installer.ts` → When `ensureSkillCreator(projectRoot)` is called with no skill-creator present and `claude` CLI available → Then it runs `claude install-skill <url>` and returns `{ installed: true, skipped: false }`; when skill-creator already exists it returns `{ installed: false, skipped: true }` without spawning any process; when `claude` CLI is missing it returns `{ installed: false, error: 'claude CLI not found' }` without throwing

---

### T-002: Write unit tests for `ensureSkillCreator()`
**User Story**: US-001 | **Satisfies ACs**: AC-US1-01, AC-US1-02, AC-US1-03
**Status**: [x] completed
**Test**: Given `tests/unit/init/skill-creator-installer.test.ts` covers all branches → When: skill-creator exists (skip), symlink treated as existing (skip), claude CLI missing (warn+skip), install success (installed: true), install failure (warn+non-blocking), 30s timeout exceeded (warn+non-blocking) → Then all cases pass and coverage on `skill-creator-installer.ts` reaches 95%

---

### T-003: Wire `ensureSkillCreator()` into `init.ts`
**User Story**: US-001 | **Satisfies ACs**: AC-US1-01, AC-US1-02, AC-US1-03
**Status**: [x] completed
**Test**: Given `init.ts` calls `ensureSkillCreator()` after `installAllPlugins()` → When init runs on a project without `.claude/skills/skill-creator/SKILL.md` → Then `ensureSkillCreator()` is invoked once; when install fails → Then a warning is logged but `init()` still resolves successfully without throwing

---

### T-004: Wire `ensureSkillCreator()` into `update-instructions.ts`
**User Story**: US-001 | **Satisfies ACs**: AC-US1-04
**Status**: [x] completed
**Test**: Given `update-instructions.ts` calls `ensureSkillCreator()` at end of function → When `.claude/skills/skill-creator/SKILL.md` is absent → Then `ensureSkillCreator()` is invoked and its warning (on failure) is logged; when skill-creator is already present → Then installation is silently skipped and no process is spawned

---

### T-005: Update `SKILL.md` skill-gen Step 4 for local-first lookup
**User Story**: US-001 | **Satisfies ACs**: AC-US1-05
**Status**: [x] completed
**Test**: Given `plugins/specweave/skills/skill-gen/SKILL.md` Step 4 is updated → When `.claude/skills/skill-creator/SKILL.md` exists locally → Then `SKILL_CREATOR_PATH` is set to that local path without executing the global find; when absent locally → Then it falls back to the `~/.claude/plugins/cache/claude-plugins-official/skill-creator` glob path

---

## Stream B — Deduplication Awareness

### T-006: Create `rule-collector.ts` with `collectExistingRules()`
**User Story**: US-002 | **Satisfies ACs**: AC-US2-01, AC-US2-03, AC-US2-05
**Status**: [x] completed
**Test**: Given `src/core/skill-gen/rule-collector.ts` implements `collectExistingRules(projectRoot)` → When called on a project with CLAUDE.md, .cursorrules, and two skill SKILL.md files → Then returned `content` includes all four files with `--- file: <path> ---` headers and `fileCount` equals 4; when total chars exceed 40K (10K tokens) → Then content is truncated to the hard cap; when all rule files are absent → Then `content` is empty string and `fileCount` is 0

---

### T-007: Write unit tests for `RuleCollector`
**User Story**: US-002 | **Satisfies ACs**: AC-US2-01, AC-US2-03, AC-US2-05
**Status**: [x] completed
**Test**: Given `tests/unit/skill-gen/rule-collector.test.ts` covers all branches → When: no rule files (empty project), single large file hitting per-file 2K-token cap, combined files hitting 10K-token global cap, empty (0-byte) file skipped, security-filtered filenames (`.env`, `credentials.json`, `secret.key`) excluded, `.cursor/rules/*.mdc` globbed correctly → Then all assertions pass and branch coverage on rule-collector.ts reaches 95%

---

### T-008: Inject `RuleCollector` into `SignalCollector` and update `buildPrompt()`
**User Story**: US-002 | **Satisfies ACs**: AC-US2-01, AC-US2-02, AC-US2-03
**Status**: [x] completed
**Test**: Given `signal-collector.ts` gains an optional `existingRules` parameter in `buildPrompt()` and calls `ruleCollector.collectExistingRules()` inside `detectPatternsLLM()` → When existing rules are non-empty → Then the built prompt contains an `<existing-rules>` block with the instruction not to duplicate them; when existing rules are empty → Then no `<existing-rules>` block appears and the prompt matches the baseline format exactly

---

### T-009: Add slug-level dedup guard in `SKILL.md`
**User Story**: US-002 | **Satisfies ACs**: AC-US2-04
**Status**: [x] completed
**Test**: Given `plugins/specweave/skills/skill-gen/SKILL.md` Step 5 checks for an existing skill directory before delegating to skill-creator → When `.claude/skills/${PATTERN_SLUG}/SKILL.md` already exists → Then the step logs "Skill '${PATTERN_SLUG}' already exists -- skipping" and exits without calling skill-creator; when the directory does not exist → Then skill-creator is invoked normally

---

## Stream C — Documentation

### T-010: Rewrite `skill-generation.md` to reflect LLM-based architecture
**User Story**: US-003 | **Satisfies ACs**: AC-US3-01, AC-US3-02, AC-US3-03, AC-US3-04
**Status**: [x] Completed
**Test**: Given `docs-site/docs/skills/extensible/skill-generation.md` is fully rewritten → When a developer reads it → Then the page contains: (1) a Prerequisites section covering living docs, LLM config, and skill-creator auto-install; (2) a How It Works section describing LLM-based detection with dynamic categories and file-based confidence scoring; (3) a `--seed` command example explaining it solves the cold start problem; (4) a walkthrough using an Express+React+Zod project through the full init→seed→detect→suggest→generate→eval flow; (5) no references to keyword matching or hardcoded category lists

---

### T-011: Update README.md skill-gen section
**User Story**: US-003 | **Satisfies ACs**: AC-US3-05
**Status**: [x] Completed
**Test**: Given `README.md` skill-gen section is updated → When a reader scans the section → Then it contains 3-4 sentences describing LLM-based skill generation, mentions zero-friction first run via auto-install, and includes a link to the full `skill-generation.md` docs page
