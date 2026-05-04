---
increment: 0822-vskill-clone-skill-fork
title: "vskill clone — skill/plugin fork (clone-as-author)"
status: planned
---

# Tasks: vskill clone — skill/plugin fork (clone-as-author)

## Dependency Order

- **T-001** must complete before T-002 onward (types contract — all other tasks depend on the shared type definitions)
- **T-002 → T-010** are sequential within the backend agent (each module builds on the previous)
- **T-011 → T-015** can run in parallel with T-002 → T-010 once T-001 is done (testing agent works alongside backend)

---

## Phase 1 — Shared Types

### T-001: Add `src/clone/types.ts`; extend `Provenance` in `src/studio/types.ts` with fork fields
**User Story**: US-005
**AC**: AC-US5-01, AC-US5-02, AC-US5-03
**Status**: [x] completed
**Owner**: shared-types

**Test Plan**:
Given `src/studio/types.ts` exports a `Provenance` interface with existing fields
When `forkedFrom`, `originalSource`, and `forkChain` optional fields are added to the interface
Then TypeScript compilation succeeds, existing consumers (provenance.ts, scope-transfer.ts) have no type errors, and all three new fields appear in the exported interface

---

## Phase 2 — Core Modules

### T-002: `src/clone/skill-locator.ts` — discover skill across project/personal/cache
**User Story**: US-001
**AC**: AC-US1-01
**Status**: [x] completed
**Owner**: backend

**Test Plan**:
Given a skill identifier `sw/ado-mapper` and HOME set to a temp dir with `.claude/skills/sw/ado-mapper/SKILL.md` present
When `locateSkill("sw/ado-mapper", { cwd, home })` is called
Then it returns the personal location match; given the same skill exists in both project `.claude/skills/` and personal `~/.claude/skills/`, the module returns both matches so the caller can prompt for disambiguation

---

### T-003: Extend `src/installer/frontmatter.ts` with `applyForkMetadata()`
**User Story**: US-001
**AC**: AC-US1-02
**Status**: [x] completed
**Owner**: backend

**Test Plan**:
Given a `SKILL.md` string with `name: sw/ado-mapper`, `author: Original Author`, `version: 2.1.0`, and an unknown field `custom-tag: yes`
When `applyForkMetadata(content, { name: "anton/ado-mapper", author: "Anton", version: "1.0.0", forkedFrom: "sw/ado-mapper" })` is called
Then the returned string has `name: anton/ado-mapper`, `author: Anton`, `version: 1.0.0`, and `custom-tag: yes` is preserved verbatim

---

### T-004: `src/clone/provenance-fork.ts` — wrap `writeProvenance` with fork merging logic
**User Story**: US-005
**AC**: AC-US5-01, AC-US5-02
**Status**: [x] completed
**Owner**: backend

**Test Plan**:
Given a target `.tmp` directory and a source skill that has an existing `.vskill-meta.json` with `forkedFrom: { source: "original/skill", version: "1.0.0", clonedAt: "2026-01-01T00:00:00Z" }`
When `writeForkProvenance(tmpDir, { source: "sw/ado-mapper", version: "2.1.0", clonedAt: now }, existingMeta)` is called
Then `.vskill-meta.json` in tmpDir contains `forkedFrom` pointing to `sw/ado-mapper`, `originalSource` set to `original/skill`, and `forkChain` array containing `"original/skill"`

---

### T-005: `src/clone/reference-scanner.ts` — read-only cross-skill ref report
**User Story**: US-001
**AC**: AC-US1-04
**Status**: [x] completed
**Owner**: backend

**Test Plan**:
Given a SKILL.md body containing `` `sw:foo` ``, `Skill({ skill: "sw:bar" })`, `/sw:baz`, a literal occurrence of the old skill name in prose, and a code block that also contains `/sw:qux` (inside triple-backtick fence)
When `scanReferences(content, { oldSkillName: "ado-mapper" })` is called
Then it returns matches for the three patterns and the prose occurrence, but does NOT return the match inside the code block as a false positive, and no file is written or modified

---

### T-006: `src/clone/target-router.ts` — `writeStandalone`, `writeToPlugin`, `writeNewPlugin`
**User Story**: US-001, US-002, US-003
**AC**: AC-US1-03, AC-US2-01, AC-US2-02, AC-US2-03, AC-US3-01
**Status**: [x] completed
**Owner**: backend

**Test Plan**:
Given a staged `.tmp` skill directory and `--target plugin --plugin my-plugin` where `my-plugin/.claude-plugin/plugin.json` is valid
When `writeToPlugin(tmpSkillDir, pluginDir, skillName)` is called
Then the skill files are copied into `plugins/skills/<skillName>/`, `plugin.json` is updated to register the skill, and if an error is injected on the `plugin.json` write, the partially copied skill directory is removed (no partial state)

---

### T-007: `src/clone/github-scaffold.ts` with injectable `runGh`; graceful skip
**User Story**: US-003
**AC**: AC-US3-02, AC-US3-03
**Status**: [x] completed
**Owner**: backend

**Test Plan**:
Given a committed (atomic rename complete) new-plugin directory and `--github` flag with an injectable `runGh` that records its arguments
When `scaffoldGitHub({ pluginDir, repoName, runGh })` is called
Then `runGh` receives `["repo", "create", repoName, "--public"]` and the initial commit/push argv; when the same function is called with a `runGh` that throws `{ code: "ENOENT" }`, the function resolves successfully with a `skipped: true` result and no exception propagates

---

### T-008: `src/commands/clone.ts` orchestrator
**User Story**: US-006
**AC**: AC-US6-01, AC-US6-02, AC-US6-03
**Status**: [x] completed
**Owner**: backend

**Test Plan**:
Given `vskill clone sw/ado-mapper --target standalone --path /tmp/cloned-ado --author Anton --namespace anton` with all source files present
When the orchestrator runs validate → copy to `.tmp` → rewrite frontmatter → write provenance → validate cloned → atomic rename
Then the final directory exists at `/tmp/cloned-ado`, `.tmp` is gone, and `.vskill-meta.json` is present; when an error is injected at the frontmatter-rewrite step, `/tmp/cloned-ado.tmp` is cleaned up and `/tmp/cloned-ado` does not exist

---

### T-009: Register `clone` in `src/index.ts` with all flags + interactive prompts
**User Story**: US-001
**AC**: AC-US1-01
**Status**: [x] completed
**Owner**: backend

**Test Plan**:
Given `node dist/bin.js clone --help` is executed
When the built binary runs
Then the help output lists all flags: `--target`, `--path`, `--plugin`, `--plugin-name`, `--author`, `--namespace`, `--github`, `--force`, `--source`, `--dry-run`, and the command description matches the feature intent

---

### T-010: Whole-plugin clone path (`--plugin <name>` without `<source>`)
**User Story**: US-004
**AC**: AC-US4-01, AC-US4-02, AC-US4-03
**Status**: [x] completed
**Owner**: backend

**Test Plan**:
Given a plugin `test-plugin` with three skills (`skill-a`, `skill-b`, `skill-c`) and `--plugin test-plugin --namespace myns --target standalone --path /tmp/bulk`
When `vskill clone --plugin test-plugin --namespace myns` is executed
Then the CLI prints a confirmation listing all three skills before any write; after confirmation, all three are cloned under `myns/`; if an error is injected on `skill-b`, `skill-a` is rolled back and `skill-c` is never attempted, leaving `/tmp/bulk` empty

---

## Phase 3 — Tests

### T-011: Unit tests for skill-locator, provenance-fork, reference-scanner (mocked fs)
**User Story**: US-001, US-005
**AC**: AC-US1-01, AC-US1-04, AC-US5-01, AC-US5-02
**Status**: [x] completed — skill-locator (15) + provenance-fork (11) + reference-scanner (15) = 41 tests pass
**Owner**: testing

**Test Plan**:
Given `vi.hoisted` mocks for `fs/promises` and `path` utilities
When skill-locator is tested for all three source locations (project, personal, cache), provenance-fork is tested for first-fork and chained-fork cases, and reference-scanner is tested for all three patterns plus code-block false positive guard
Then all unit assertions pass with no real disk I/O and coverage for the new modules reaches >= 90%

---

### T-012: Unit tests for `applyForkMetadata` (preservation, idempotence, malformed)
**User Story**: US-001
**AC**: AC-US1-02
**Status**: [x] completed — 14 tests pass
**Owner**: testing

**Test Plan**:
Given three test fixtures: a well-formed SKILL.md with unknown fields, an already-forked SKILL.md (idempotence check), and a SKILL.md with malformed/missing YAML frontmatter delimiter
When `applyForkMetadata` is called on each fixture with the same metadata arguments
Then unknown fields are preserved in fixture 1, the output equals the input for fixture 2 (idempotent), and fixture 3 returns a clear error (does not silently corrupt the file)

---

### T-013: Integration tests — 9 source x target combos using mkdtemp + HOME override
**User Story**: US-001, US-002, US-003
**AC**: AC-US1-01, AC-US1-02, AC-US1-03, AC-US1-04, AC-US2-01, AC-US2-02, AC-US2-03, AC-US3-01
**Status**: [x] completed — 9 combo tests + 4 edge-case tests (collision, --force, malformed manifest, dry-run) pass
**Owner**: testing

**Test Plan**:
Given a temp directory created with `mkdtemp`, HOME overridden to the temp dir, and skill fixtures from `e2e/fixtures/skills/lint-markdown-files` and `e2e/fixtures/test-plugin/skills/test-skill`
When each of the 9 combinations (project/personal/cache source x standalone/plugin/new-plugin target) is exercised via the orchestrator
Then all 9 produce the correct output directory structure, correct frontmatter rewrite, valid `.vskill-meta.json`, and reference-scan output in the summary; the malformed-plugin-manifest case aborts before any copy; the collision case (target already exists) aborts with a "target exists" error unless `--force` is passed

---

### T-014: Integration tests for atomicity — rollback, permission-denied, chained fork
**User Story**: US-006, US-005
**AC**: AC-US6-01, AC-US6-02, AC-US6-03, AC-US5-02
**Status**: [x] completed — 4 atomicity tests pass (chained fork, read-only target, plugin-manifest rollback, frontmatter-failure cleanup)
**Owner**: testing

**Test Plan**:
Given a mkdtemp workspace and an error-injecting wrapper around `fs.rename` that throws on the `plugin.json` rename
When `writeToPlugin` runs and the manifest rename fails
Then no skill files remain in the plugin directory; given a target directory with `mode 0o444` (read-only), the orchestrator exits with a permission-denied error and no `.tmp` artifact remains; given a source skill whose `.vskill-meta.json` already has a `forkChain`, the cloned output's `.vskill-meta.json` has `forkChain` extended by one entry and `originalSource` set to the deepest ancestor

---

### T-015: github-scaffold tests with fake `runGh`; CLI smoke in `ci.yml`
**User Story**: US-003
**AC**: AC-US3-02
**Status**: [x] completed — 10 unit tests + ci.yml smoke step added
**Owner**: testing

**Test Plan**:
Given a fake `runGh` that records all invocations and returns successfully
When `scaffoldGitHub` is called with `repoName: "anton-ado-tools"` and the fake adapter
Then the recorded argv includes `repo create` with the correct name and `--public`; given the same call with a fake that throws `{ code: "ENOENT" }`, the function resolves with `skipped: true`; given `.github/workflows/ci.yml` is updated to include `node dist/bin.js clone --help`, the CI step is present and the command exits 0 in the build environment
