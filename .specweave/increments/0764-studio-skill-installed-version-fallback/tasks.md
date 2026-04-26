# 0764 — Tasks

### T-001: Backend — frontmatter + contentHash fallback in versions enrichment
**User Story**: US-001 / US-002
**Satisfies ACs**: AC-US1-01, AC-US1-02, AC-US1-03, AC-US1-04, AC-US2-01, AC-US2-02
**Status**: [x] completed
**Test Plan (Given/When/Then)**:
- Given a skill without a lockfile entry but with `version: 1.0.2` in `SKILL.md`,
  When `/api/skills/:plugin/:skill/versions` is called,
  Then row `1.0.2` returns `isInstalled: true` and others return `false`.
- Given a skill without a lockfile entry and without frontmatter version, but its on-disk SKILL.md sha256 matches the platform `contentHash` of `1.0.0`,
  When the endpoint is called,
  Then row `1.0.0` returns `isInstalled: true`.
- Given a lockfile entry for `1.0.1` AND frontmatter `1.0.2`,
  When the endpoint is called,
  Then row `1.0.1` (lockfile) wins.

### T-002: Vitest unit test covering the four AC paths
**User Story**: US-001
**Satisfies ACs**: AC-US1-01..04
**Status**: [x] completed
**Test Plan**: New file `src/eval-server/__tests__/api-routes.versions-isinstalled.test.ts`. Mock lockfile + fs (or extract a pure helper `pickInstalledVersion(versions, { lockfileVersion, frontmatterVersion, onDiskHash })` and unit-test that — preferable for isolation).

### T-003: Data — add `version: 1.0.3` to `.claude/skills/scout/SKILL.md`
**User Story**: US-003
**Satisfies ACs**: AC-US3-01
**Status**: [x] completed
**Test Plan**: Read the file after edit, confirm the frontmatter contains `version: 1.0.3` between the `---` fences and the rest of the file is unchanged.

### T-004: Build, test, publish vskill `0.5.131`
**User Story**: shipping
**Status**: [x] completed
**Test Plan**: `npm run build && npm run build:eval-ui && npx vitest run src/eval-server/__tests__/api-routes.versions-isinstalled.test.ts`. Bump `package.json` to `0.5.131`. `npm publish`. Wait for npm CDN to settle, then `npx -y vskill@0.5.131 --version` returns `0.5.131`.

### T-005: Verify in studio (preview tools)
**User Story**: US-001/2/3
**Status**: [x] completed
**Test Plan**: Start `npx -y vskill@0.5.131 studio` against the vskill repo root, navigate to `/#/skills/.claude/scout`, confirm: (a) header chip reads `v1.0.3` non-italic, (b) the `1.0.3` row has the `installed` badge + larger dot, (c) the "Update to 1.0.3" button is NOT shown (because we're already on latest).
