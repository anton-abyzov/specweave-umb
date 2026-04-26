# 0765 — Tasks

### T-001: Resolver — plugin-aware lookup + cache key
**User Story**: US-001
**Satisfies ACs**: AC-US1-01, AC-US1-02, AC-US1-03
**Status**: [x] completed
**Test Plan**:
- Given a lockfile entry `greet-anton → github:anton-abyzov/greet-anton` AND a source-tree skill at `<root>/skills/greet-anton/SKILL.md`,
  When `resolveSkillApiName("greet-anton", ".claude", root)` is called,
  Then it returns `anton-abyzov/greet-anton/greet-anton` (lockfile wins).
- Given the same setup,
  When `resolveSkillApiName("greet-anton", "vskill", root)` is called (authoring view),
  Then it returns `<vskill-remote-owner>/<vskill-remote-repo>/greet-anton` (source-tree wins).
- Given two consecutive calls with different plugins for the same skill,
  Then both results are cached independently (no cross-plugin contamination).

### T-002: api-routes — thread plugin through the wrapper
**User Story**: US-001
**Satisfies ACs**: AC-US1-04
**Status**: [x] completed
**Test Plan**: Update both `/api/skills/:plugin/:skill/versions` and `/.../versions/diff` handlers to pass `params.plugin`. Existing version-routes tests still pass (`vitest run src/eval-server/__tests__/version-routes.test.ts` — current pre-existing failures stay at 3, no new failures).

### T-003: Update — rewrite SKILL.md frontmatter when newVersion ≠ on-disk version
**User Story**: US-002
**Satisfies ACs**: AC-US2-01, AC-US2-02, AC-US2-03
**Status**: [x] completed
**Test Plan**:
- Given a SKILL.md on disk with `version: "1.0.2"` and the resolver computes `newVersion = "1.0.3"`,
  When the update post-install rewrite step runs,
  Then the file ends with `version: "1.0.3"` and the lockfile entry `version` field is `"1.0.3"`.

### T-004: BDD unit tests for both fixes
**User Story**: US-001 + US-002
**Status**: [x] completed
**Test Plan**: New `skill-name-resolver.plugin-aware.test.ts` (4 cases) + new `update.frontmatter-bump.test.ts` (2 cases — bump path, no-op when already at target).

### T-005: Build, test, publish vskill@0.5.132
**User Story**: shipping
**Status**: [x] completed
**Test Plan**: `npm run build && npm run build:eval-ui && npx vitest run src/eval-server/__tests__ src/commands/__tests__`. Bump `package.json` to `0.5.132`. `npm publish`. Wait for npm CDN, then `npx -y vskill@0.5.132 --version` returns `0.5.132`.

### T-006: Sub-agent smoke verification
**User Story**: US-001 + US-002
**Status**: [x] completed
**Test Plan**: Spawn a sub-agent to: kill all old vskill studios, `npx -y vskill@0.5.132 studio` against the umbrella root, hit the API endpoints for `.claude/scout` (regression check), `.claude/greet-anton` (4 versions, badge on 1.0.2), POST update on greet-anton, re-fetch `.claude/greet-anton/versions` (badge moves to 1.0.3), and `cat .claude/skills/greet-anton/SKILL.md` to confirm frontmatter says `version: "1.0.3"`. Report concise pass/fail per AC.
