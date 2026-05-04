---
increment: 0822-vskill-clone-skill-fork
title: vskill clone — skill/plugin fork (clone-as-author)
type: feature
priority: P1
status: completed
created: 2026-05-01T00:00:00.000Z
structure: user-stories
test_mode: TDD
coverage_target: 90
---

# Feature: vskill clone — skill/plugin fork (clone-as-author)

## Problem Statement

When a user installs a skill from someone else's plugin (e.g., `sw/ado-mapper`) and wants to make it their own — tweak the prompt, add references, change behavior, host under their own GitHub — there is no supported path. They have to manually copy files across three possible source locations (project `.claude/skills/`, personal `~/.claude/skills/`, plugin cache `~/.claude/plugins/cache/...`), find every place that needs renaming, and hope they did not break a cross-skill reference. Every barrier between "this is almost what I want" and "now it's mine" loses contributors. This increment introduces `vskill clone <source>` — a CLI-only command that deep-copies any installed skill (or an entire plugin) into one of three target shapes (standalone skill, addition to an existing user-owned plugin, or a fresh new plugin), rewrites authorship while preserving provenance, and optionally scaffolds a GitHub repo. The implementation reuses existing primitives (`copyOwnSkillFiltered`, `writeProvenance`, `applyForkMetadata` extension to `installer/frontmatter.ts`) and adds no new dependencies.

## User Stories

### US-001: Clone a single skill to a standalone path (P1)
**Project**: vskill

**As a** vskill user who has installed a skill I want to fork
**I want** to run `vskill clone <name> --target standalone --path <dir>` and have the skill copied to a brand-new directory with my authorship applied
**So that** I can tweak it independently without affecting the original install

**Acceptance Criteria**:
- [x] **AC-US1-01**: `vskill clone <name>` resolves the source by searching the three known locations in order: project `.claude/skills/`, personal `~/.claude/skills/`, plugin cache `~/.claude/plugins/cache/`. When multiple matches exist, the CLI prompts the user to disambiguate (or honors `--source project|personal|cache`).
- [x] **AC-US1-02**: The cloned `SKILL.md` frontmatter has `name` rewritten to `<namespace>/<skill>` (namespace defaults to a slugified `--author`, which defaults to `git config user.name`), `author` updated to the new author, and `version` reset to `1.0.0`. Unknown frontmatter fields are preserved.
- [x] **AC-US1-03**: All non-`SKILL.md` files (`agents/`, `scripts/`, `references/`, any subdirectory contents) are deep-copied verbatim to the target.
- [x] **AC-US1-04**: A read-only reference scan reports cross-skill references (`` `sw:foo` ``, `Skill({ skill: "sw:foo" })`, `/sw:foo`) and literal occurrences of the OLD skill name in prose. The scan does NOT auto-rewrite — output is appended to the success summary so the user can decide.

---

### US-002: Clone a skill into an existing user-owned plugin (P1)
**Project**: vskill

**As a** plugin maintainer who already owns a plugin
**I want** to clone a foreign skill directly into my plugin via `--target plugin --plugin <name>`
**So that** the skill becomes part of my plugin without manual manifest editing

**Acceptance Criteria**:
- [x] **AC-US2-01**: `vskill clone <source> --target plugin --plugin <name>` copies the skill into the existing plugin's `skills/` directory and updates the plugin's `.claude-plugin/plugin.json` to register the new skill.
- [x] **AC-US2-02**: The plugin manifest update is atomic via two-phase commit — both the skill copy and the manifest update succeed together, or both roll back. Failure to write `plugin.json` removes the partially copied skill before exiting with an error.
- [x] **AC-US2-03**: A malformed plugin manifest at the target is detected and the command aborts with a clear error BEFORE any files are copied (no partial state on the target plugin).

---

### US-003: Clone to a fresh new plugin with optional GitHub scaffold (P1)
**Project**: vskill

**As a** user who wants to publish a forked skill under my own brand
**I want** `vskill clone <source> --target new-plugin --plugin-name <n> --path <dir>` to scaffold a complete plugin (manifest + `skills/` + the cloned skill) and optionally create a GitHub repo
**So that** I have a publishable starting point in one command

**Acceptance Criteria**:
- [x] **AC-US3-01**: `--target new-plugin --plugin-name <n> --path <dir>` scaffolds a fresh plugin directory containing `.claude-plugin/plugin.json` (with the new plugin name) and a `skills/<skill>/` subtree containing the cloned skill.
- [x] **AC-US3-02**: When `--github` is passed, an injectable `runGh` adapter is invoked to run `gh repo create` and an initial commit/push. If `gh` is unavailable or fails with `ENOENT`, the command gracefully skips the GitHub step, prints a clear notice, and still reports success on the local-disk artifacts.
- [x] **AC-US3-03**: GitHub scaffolding only runs AFTER all on-disk files are committed (atomic rename complete) — never on partial state.

---

### US-004: Whole-plugin clone — bulk-clone all skills under a new namespace (P2)
**Project**: vskill

**As a** user who wants to fork an entire plugin (multiple skills) under my own namespace
**I want** to run `vskill clone --plugin <name> --namespace <ns>` (no `<source>` arg) and have every skill in that plugin cloned under one new namespace
**So that** I do not have to clone each skill one by one

**Acceptance Criteria**:
- [x] **AC-US4-01**: `--plugin <name>` without a `<source>` argument enumerates every skill in the named plugin and clones each under the single `--namespace`.
- [x] **AC-US4-02**: Before any write occurs, the CLI prints a confirmation listing of all skills that will be cloned and prompts the user to proceed (or aborts cleanly).
- [x] **AC-US4-03**: If any individual skill in the bulk operation fails, all already-cloned skills in the same run are rolled back so the target ends in a clean (no-partial) state.

---

### US-005: Provenance tracking via `.vskill-meta.json` (P1)
**Project**: vskill

**As a** maintainer of a forked skill
**I want** the clone to record where it came from (and the chain if I fork a fork)
**So that** future maintainers (or I) can trace lineage back to the original source

**Acceptance Criteria**:
- [x] **AC-US5-01**: Every successful clone writes a `.vskill-meta.json` (extending the existing `Provenance` type per ADR 0688-02) containing `forkedFrom: { source, version, clonedAt }` where `source` is the original full skill name (e.g., `sw/ado-mapper`), `version` is the source version at clone time, and `clonedAt` is an ISO-8601 timestamp.
- [x] **AC-US5-02**: When the source itself was previously a fork (i.e., already had a `.vskill-meta.json` with its own `forkedFrom`), the new clone preserves the chain by setting `forkChain[]` to the prior `forkChain` plus the source's namespace, and sets `originalSource` to the deepest known ancestor.
- [x] **AC-US5-03**: Existing `Provenance` fields written by other vskill flows are preserved (no field is dropped) when the type is extended with `forkedFrom`, `originalSource`, `forkChain`.

---

### US-006: Atomicity — failed clone leaves no partial state (P1)
**Project**: vskill

**As a** user running `vskill clone`
**I want** any failure (validation error, write error, manifest error) to leave no half-cloned files behind
**So that** I can re-run the command without manually cleaning up

**Acceptance Criteria**:
- [x] **AC-US6-01**: All file writes go to `<target>.tmp` first; only after every step succeeds (copy, frontmatter rewrite, provenance write, validation, optional manifest update) does the command perform an atomic rename to `<target>`. On any failure, `<target>.tmp` is removed and no partial state remains.
- [x] **AC-US6-02**: Re-running `vskill clone` with the same arguments against an existing target is a no-op error by default (clear "target exists" message). With `--force`, the existing target is overwritten — but only after the new clone is fully staged in `.tmp`, so a failure during overwrite still does not corrupt the existing target.
- [x] **AC-US6-03**: Permission-denied on the target directory produces a clear, actionable error and leaves no partial state (no `.tmp` directory left behind).

## Functional Requirements

### FR-001: CLI command surface
The `clone` command is registered in `src/index.ts` (Commander wiring) with the following flags:
- `<source>` (positional, optional when `--plugin` is used alone): skill identifier (`ado-mapper` or `sw/ado-mapper`)
- `--target standalone|plugin|new-plugin` (interactive prompt if omitted)
- `--path <dir>` (for `standalone` or `new-plugin`)
- `--plugin <name>` (for `--target plugin`, OR for whole-plugin clone)
- `--plugin-name <name>` (for `--target new-plugin`)
- `--author <name>` (default: `git config user.name`)
- `--namespace <ns>` (default: slugified `--author`)
- `--github` (scaffold GitHub repo, only valid with `--target new-plugin`)
- `--force` (overwrite existing target)
- `--source project|personal|cache` (auto-detect; prompt if ambiguous)
- `--dry-run` (print planned actions without writing)

### FR-002: Source resolution
A `skill-locator` module resolves `<source>` across three known locations in deterministic order: project `.claude/skills/`, personal `~/.claude/skills/`, plugin cache `~/.claude/plugins/cache/`. Multiple matches → interactive prompt or `--source` override.

### FR-003: Frontmatter rewrite (regex, house style)
`installer/frontmatter.ts` is extended with one new exported `applyForkMetadata(content, { name, author, version, forkedFrom })` function that rewrites only the listed fields in the YAML frontmatter via regex (matching the existing module's house style — NOT gray-matter). All unknown fields are preserved. The function is idempotent on rerun against already-forked content.

### FR-004: Two-phase commit on plugin manifest
For `--target plugin`, both the new skill subtree and the updated `plugin.json` are staged in `.tmp` siblings, then atomically renamed in sequence. Failure on the manifest write rolls back the skill copy.

### FR-005: GitHub scaffold injection
The github-scaffold module accepts an injectable `runGh` adapter for testability. The default adapter shells out to `gh`; the test fake records arguments and can throw `ENOENT` to verify graceful skip.

### FR-006: Reference-only scan
The `reference-scanner` module is read-only. It detects cross-skill reference patterns (`` `sw:foo` ``, `Skill({ skill: "sw:foo" })`, `/sw:foo`) and literal old-skill-name occurrences, but never rewrites anything. Output appears in the success summary so the user can decide what (if anything) to change manually.

## Success Criteria

- `node dist/bin.js clone --help` succeeds and is asserted in `.github/workflows/ci.yml` (CI smoke gate).
- All 9 source × target combinations (3 source locations × 3 target shapes) pass integration tests using `mkdtemp` + `HOME` override.
- `applyForkMetadata` unit tests cover: preservation of unknown frontmatter fields, idempotence on rerun, and graceful handling of malformed frontmatter.
- Atomicity tests prove that a forced manifest-write failure rolls back the skill copy (no partial state on disk).
- Chained-fork integration test (depth 2) produces a `.vskill-meta.json` with the correct `forkChain[]` and `originalSource`.
- github-scaffold tests with the fake `runGh` verify both the success path (correct argv passed) and the graceful-skip path (`ENOENT` does not fail the overall clone).
- Unit + integration coverage ≥ 90% for new modules under `src/clone/`.
- Existing commands (`install`, `list`, etc.) continue to work — full `npm test` passes with no regressions.

## Out of Scope

- **Lockfile entry for cloned skills.** Cloned skills are user-owned (not registry-installed). Adding them to the lockfile would blur `vskill outdated` semantics for forks. Excluded by design.
- **Studio UI "Fork" button.** The eval-server has no Fork button today; deferred to a follow-up increment. This increment is CLI-only.
- **Registry publish flow.** Forked skills go to local disk and optionally a GitHub repo. Publishing to verified-skill.com is a separate concern.
- **Automatic cross-skill reference rewriting.** Cross-skill refs point to OTHER skills, not to the cloned skill — silently substituting them would break dependencies. The scanner reports only.
- **chmod / executable-bit preservation.** Skills are plain text; no current skill depends on the executable bit, and existing copy helpers do not preserve mode.

## Dependencies

- Existing module: `src/installer/frontmatter.ts` — extended with `applyForkMetadata()`.
- Existing module: `src/studio/lib/scope-transfer.ts` + `src/shared/copy-plugin-filtered.ts` — reused for filtered recursive directory copy.
- Existing module: `src/studio/lib/provenance.ts` — `writeProvenance` / `readProvenance` reused; the `Provenance` type in `src/studio/types.ts` is extended.
- Existing pattern: `src/commands/add.ts` line 838+ — rollback pattern reused for two-phase commit.
- External CLI (optional, for `--github`): `gh` (GitHub CLI). Gracefully skipped if absent.
- No new npm dependencies.

## Test Plan Reference

The Planner will produce Given/When/Then BDD scenarios in tasks.md against the layers defined in plan.md:

| Layer | Coverage |
|---|---|
| Unit (Vitest, `vi.hoisted` style) | skill-locator across 3 source locations; `applyForkMetadata` (preservation, idempotence, malformed input); reference-scanner (3 patterns, no false positives in code blocks); target-router branches |
| Integration (mkdtemp + HOME override) | 9 source × target combos; skill with `agents/*.md` subdir; collision when target already has `.vskill-meta.json`; chained fork (depth 2); permission-denied target; malformed plugin manifest at target |
| Manifest atomicity | Failure-injected `plugin.json` write rolls back skill copy |
| github-scaffold | Fake `runGh` — success path argv assertion + `ENOENT` graceful-skip path |
| CLI smoke (CI) | `node dist/bin.js clone --help` assertion in `.github/workflows/ci.yml` |
