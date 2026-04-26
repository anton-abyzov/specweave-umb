---
increment: 0743-vskill-source-link-provenance
title: "vskill source-link provenance"
created: 2026-04-26
test_mode: TDD
---

# Implementation Tasks

All work happens in `repositories/anton-abyzov/vskill/`. RED → GREEN → REFACTOR per layer.

---

## Layer 2 (server resolver) — smallest blast radius first

### T-001: RED — invert legacy-fallback expectation in skill-metadata-source-link test
**User Story**: US-002 | **Satisfies ACs**: AC-US2-01 | **Status**: [x] completed
**Test Plan (Given/When/Then)**:
- Given a lockfile entry with `source: github:anton-abyzov/greet-anton` and no `sourceSkillPath`
- When `buildSkillMetadata(skillDir, "installed", root)` runs
- Then `md.skillPath` is `null` (was `"SKILL.md"` — this assertion change is the RED step)

Edit `src/eval-server/__tests__/skill-metadata-source-link.test.ts` — change line 99 expectation to `expect(md.skillPath).toBeNull()`. Run `npx vitest run skill-metadata-source-link` and confirm the test fails.

### T-002: GREEN — drop "SKILL.md" default in resolveSourceLink legacy branch
**User Story**: US-002 | **Satisfies ACs**: AC-US2-01, AC-US2-02, AC-US2-03 | **Status**: [x] completed
**Test Plan (Given/When/Then)**:
- Given the test from T-001 (failing)
- When `resolveSourceLink` returns `skillPath: entry.sourceSkillPath ?? null` (was `?? "SKILL.md"`)
- Then T-001 passes; the explicit-field test (lines 102-124) still passes; the authored-skill test (lines 126-137) still passes

Edit `src/eval-server/api-routes.ts:799` — replace `?? "SKILL.md"` with `?? null`. Run the test file and confirm GREEN.

---

## Layer 3 (frontend) — depends on Layer 2 contract

### T-003: RED — invert homepage-fallback regression test in DetailHeader.source-link
**User Story**: US-003 | **Satisfies ACs**: AC-US3-01 | **Status**: [x] completed
**Test Plan (Given/When/Then)**:
- Given `SkillInfo` with `repoUrl: null`, `skillPath: null`, `homepage: "https://github.com/anton-abyzov/easychamp-mcp"`
- When `DetailHeader` renders the byline
- Then a `source-file-copy` chip is rendered (was: a `source-file-link` anchor with the wrong href)

Edit `src/eval-ui/src/components/__tests__/DetailHeader.source-link.test.tsx:133-147` — invert the assertion: expect `source-file-copy` to be present and `source-file-link` to be absent. Update the test name to reflect the new contract ("renders copy-chip when only homepage is present, not a misleading anchor"). Run `npx vitest run DetailHeader.source-link` and confirm RED.

### T-004: GREEN — DetailHeader stops passing homepage to SourceFileLink
**User Story**: US-003 | **Satisfies ACs**: AC-US3-01, AC-US3-02, AC-US3-03 | **Status**: [x] completed
**Test Plan (Given/When/Then)**:
- Given the test from T-003 (failing) plus the existing positive tests at lines 79-92, 103-119
- When `DetailHeader.tsx:201` is changed from `repoUrl={skill.repoUrl ?? skill.homepage ?? null}` to `repoUrl={skill.repoUrl ?? null}` (only the SourceFileLink line; AuthorLink at line 199 unchanged)
- Then T-003 passes; positive tests still pass (AC-US3-02 + AC-US3-03 verified)

Edit `src/eval-ui/src/components/DetailHeader.tsx:201`. Run the test file and confirm GREEN.

---

## Layer 1 (CLI install) — biggest change, last

### T-005: RED — direct-repo install lockfile-write test
**User Story**: US-001 | **Satisfies ACs**: AC-US1-01, AC-US1-02 | **Status**: [x] completed
**Test Plan (Given/When/Then)**:
- Given a mocked `installOneGitHubSkill` returning a `SkillInstallResult` carrying `sourceSkillPath: "plugins/sw/skills/greet-anton/SKILL.md"`
- When the direct-repo install lockfile-write block (`add.ts:2086-2103`) runs
- Then the persisted lockfile entry has `sourceRepoUrl: "https://github.com/anton-abyzov/vskill"` AND `sourceSkillPath: "plugins/sw/skills/greet-anton/SKILL.md"`

Add tests under `src/commands/__tests__/add.lockfile-source-link.test.ts` (new file). Use `lockfile.test.ts` fixtures for the assertion shape. Run RED.

### T-006: RED — single-skill legacy lockfile-write test
**User Story**: US-001 | **Satisfies ACs**: AC-US1-03 | **Status**: [x] completed
**Test Plan (Given/When/Then)**:
- Given `installSingleSkillLegacy` invoked with `--skill foo`, deriving `skillSubpath = "skills/foo/SKILL.md"`
- When the lockfile write at `add.ts:2716-2730` runs
- Then the entry has `sourceRepoUrl: "https://github.com/owner/repo"` AND `sourceSkillPath: "skills/foo/SKILL.md"`

Add to the same new test file. Run RED.

### T-007: GREEN — extend SkillInstallResult + thread sourceSkillPath
**User Story**: US-001 | **Satisfies ACs**: AC-US1-01, AC-US1-02, AC-US1-03 | **Status**: [x] completed
**Test Plan (Given/When/Then)**:
- Given T-005 + T-006 failing
- When (a) `SkillInstallResult` gains `sourceSkillPath?: string`; (b) `installOneGitHubSkill` sets it from its `path` parameter; (c) caller at `add.ts:2078` passes `skill.path` through; (d) lockfile writes at lines 2090-2099 and 2720-2728 add `sourceRepoUrl` + `sourceSkillPath` fields
- Then T-005 + T-006 pass; existing add tests still pass

Edit `src/commands/add.ts`. Run RED tests + full add suite, confirm GREEN.

---

## REFACTOR + verification

### T-008: Run full vskill test suite
**User Story**: All | **Satisfies ACs**: All | **Status**: [x] completed
**Test Plan**: `cd repositories/anton-abyzov/vskill && npm test` returns 0 with all tests green.

### T-009: Build vskill
**User Story**: US-004 | **Satisfies ACs**: AC-US4-01 | **Status**: [x] completed
**Test Plan**: `npm run build` produces `dist/index.js` and `dist/eval-ui/` without TypeScript errors.

### T-010: End-to-end — reinstall greet-anton from local build
**User Story**: US-004 | **Satisfies ACs**: AC-US4-01 | **Status**: [x] completed
**Test Plan (Given/When/Then)**:
- Given `TestLab/greet-anton/` removed
- When `node /…/vskill/dist/index.js add anton-abyzov/vskill/greet-anton --yes` runs
- Then `TestLab/greet-anton/vskill.lock` contains both `sourceRepoUrl` and `sourceSkillPath`

### T-011: End-to-end — studio anchor opens correct GitHub file
**User Story**: US-004 | **Satisfies ACs**: AC-US4-02 | **Status**: [x] completed
**Test Plan (Given/When/Then)**:
- Given the local studio is running (`node /…/vskill/dist/index.js studio`, port 3136)
- When I navigate to `http://localhost:3136/#/skills/TestLab/greet-anton` and inspect the SKILL.md anchor
- Then the href contains the actual `sourceSkillPath` (not just `/blob/HEAD/SKILL.md`) and HTTP-fetches HTTP 200 (or visibly opens the file in a browser)

Verify via Bash `curl -sI` against the resolved href.

### T-012: End-to-end — legacy entry shows copy-chip
**User Story**: US-004 | **Satisfies ACs**: AC-US4-03 | **Status**: [x] completed
**Test Plan (Given/When/Then)**:
- Given a lockfile entry seeded with `source: github:owner/repo` only (no sourceSkillPath)
- When the studio renders the detail header
- Then `source-file-copy` chip is visible (no `source-file-link` anchor)

### T-013: Patch-bump + npm publish vskill
**User Story**: US-004 | **Satisfies ACs**: AC-US4-02 | **Status**: [x] completed (v0.5.124, vskill commit 7897f27)
**Test Plan**: `npm version patch && npm publish` succeeds; install via `npx vskill@latest` resolves the new version.
