# 0761 — Tasks

## US-001: Resolver source-tree probe

### T-001: RED — failing test for `<root>/skills/<skill>` resolution
**User Story**: US-001 | **AC**: AC-US1-01, AC-US1-05 | **Status**: [x] completed
**Test Plan**: Given a tmp `<root>` containing `skills/foo/SKILL.md` and a stubbed git remote `https://github.com/acme/myrepo.git`, when `resolveSkillApiName('foo', root)` is called with no lockfile entry, then it returns `acme/myrepo/foo` (currently returns `foo`).

### T-002: GREEN — add `findAuthoredSourceTreeSkillDir` + wire into resolver
**User Story**: US-001 | **AC**: AC-US1-01, AC-US1-02 | **Status**: [x] completed
**Test Plan**: T-001 turns green. Existing `skill-name-resolver.test.ts` cases stay green.

### T-003: precedence test — lockfile beats source-tree
**User Story**: US-001 | **AC**: AC-US1-03 | **Status**: [x] completed
**Test Plan**: Given a lockfile entry pointing at `marketplace owner=x repo=y` AND a source-tree skill at `<root>/skills/foo`, then `resolveSkillApiName('foo', root)` returns `x/y/foo` (lockfile wins).

### T-004: precedence test — source-tree beats plugins/* walk
**User Story**: US-001 | **AC**: AC-US1-04 | **Status**: [x] completed
**Test Plan**: Given a source-tree skill `<root>/skills/foo` AND a plugins-tree skill `<root>/plugins/personal/skills/foo`, then `resolveSkillApiName('foo', root)` returns the source-tree's owner/repo (canonical author location wins).

## US-002: VersionHistoryPanel tier label

### T-005: RED — failing UI test asserting "Trusted Publisher"
**User Story**: US-002 | **AC**: AC-US2-01 | **Status**: [x] completed
**Test Plan**: Given a `VersionHistoryPanel` render with `versions = [{ certTier: 'CERTIFIED', ... }]`, when the timeline renders, then the badge text contains `"Trusted Publisher"` (currently `"CERTIFIED"`).

### T-006: GREEN — import + apply `formatTierLabel`
**User Story**: US-002 | **AC**: AC-US2-01, AC-US2-04 | **Status**: [x] completed
**Test Plan**: T-005 green. CERT_COLORS unchanged.

### T-007: unknown-tier passthrough test
**User Story**: US-002 | **AC**: AC-US2-02 | **Status**: [x] completed
**Test Plan**: Given `certTier: 'EXPERIMENTAL'`, then badge text is `"EXPERIMENTAL"` (raw).

## US-003: 503 retry

### T-008: RED — failing test on `checkSkillUpdates` retrying 503
**User Story**: US-003 | **AC**: AC-US3-01 | **Status**: [x] completed
**Test Plan**: Given fetch sequence `[503, 200 with {results:[{name:'a',version:'1.0.0',…}]}]`, when `api.checkSkillUpdates(['a'])` is called, then the second response's results are returned and fetch is called twice.

### T-009: GREEN — add `fetchWith5xxRetry` helper + wire it
**User Story**: US-003 | **AC**: AC-US3-01, AC-US3-04, AC-US3-05 | **Status**: [x] completed
**Test Plan**: T-008 green. Apply to `checkSkillUpdates` and `resolveInstalledSkillIds`. Successful first response: fetch called exactly once.

### T-010: 4xx-no-retry test
**User Story**: US-003 | **AC**: AC-US3-02 | **Status**: [x] completed
**Test Plan**: Given fetch sequence `[404]`, when `checkSkillUpdates(['a'])` is called, then result is `[]` and fetch is called exactly once.

### T-011: thrown-error-no-retry test
**User Story**: US-003 | **AC**: AC-US3-03 | **Status**: [x] completed
**Test Plan**: Given `fetch` throws on first call, when `checkSkillUpdates(['a'])` is called, then result is `[]` and fetch is called exactly once.

## US-004: UpdateBell wording

### T-012: RED — failing test for "Also installed under …" wording
**User Story**: US-004 | **AC**: AC-US4-01 | **Status**: [x] completed
**Test Plan**: Given a studio context whose current agent is "Claude Code" AND an update with `installLocations: [{agentLabel:'Claude Code', …}, {agentLabel:'Codex CLI', …}]`, when the bell entry is clicked AND the skill row is missing from the sidebar (forced via mocked skills=[]), then the toast text contains `"Also installed under Codex CLI"` and does NOT contain `"switch to"`.

### T-013: GREEN — branch toast wording on installLocations + currentAgent
**User Story**: US-004 | **AC**: AC-US4-01, AC-US4-02 | **Status**: [x] completed
**Test Plan**: T-012 green. Add a sibling test: when current agent is "Claude Code" AND installLocations is `[{agentLabel:'Codex CLI'}]` only, toast keeps the legacy `"Skill installed under Codex CLI — switch to Codex CLI to view details"`.

### T-014: pluralisation test (≥ 2 other locations)
**User Story**: US-004 | **AC**: AC-US4-01 | **Status**: [x] completed
**Test Plan**: Given current agent "Claude Code" AND installLocations `[{agentLabel:'Claude Code'},{agentLabel:'Codex CLI'},{agentLabel:'Cursor'}]`, then toast text is `"Also installed under 2 other locations"`.

## Verification

### T-015: Run targeted vitest suites
**Status**: [x] completed
**Test Plan**: `npx vitest run src/eval-server/__tests__/skill-name-resolver src/eval-ui/src/pages/workspace src/eval-ui/src/api.test src/eval-ui/src/components/__tests__/UpdateBell` — all pass.

### T-016: Manual studio verification
**Status**: [x] completed
**Test Plan**: After rebuild, hit `http://localhost:3162/api/skills/vskill/greet-anton/versions` and confirm only `1.0.1` is returned. Reload the studio Versions tab and confirm badge text reads `Trusted Publisher`. Click an update from the bell with greet-anton multi-installed and confirm toast wording.
