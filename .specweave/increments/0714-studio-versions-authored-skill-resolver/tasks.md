# Tasks: Studio Versions: resolve owner/repo for authored skills

## Notation
- `[T-NN]` task id, `[ ]` not started, `[x]` done
- Each task lists the AC(s) it satisfies and a BDD test plan.

## Phase 1 — RED (failing tests first)

### T-01: Write parser unit tests for `parseGitHubRemoteUrl`
**AC**: AC-US1-01, AC-US1-03
**Status**: [x] Done
**File**: `repositories/anton-abyzov/vskill/src/eval-server/__tests__/resolveSkillApiName.test.ts` (new)
**Test Plan**:
- **TC-01a**: Given `https://github.com/anton-abyzov/vskill.git`, When parsed, Then returns `{ owner: "anton-abyzov", repo: "vskill" }`.
- **TC-01b**: Given `https://github.com/anton-abyzov/vskill` (no `.git`), When parsed, Then returns `{ owner: "anton-abyzov", repo: "vskill" }`.
- **TC-01c**: Given `git@github.com:anton-abyzov/vskill.git`, When parsed, Then returns `{ owner: "anton-abyzov", repo: "vskill" }`.
- **TC-01d**: Given `ssh://git@github.com/anton-abyzov/vskill.git`, When parsed, Then returns `{ owner: "anton-abyzov", repo: "vskill" }`.
- **TC-01e**: Given `https://gitlab.com/x/y.git`, When parsed, Then returns `null`.
- **TC-01f**: Given `""` or `undefined`, When parsed, Then returns `null`.

### T-02: Write `findAuthoredSkillDir` unit tests
**AC**: AC-US1-01, AC-US3-02
**Status**: [x] Done
**File**: same test file as T-01
**Test Plan**:
- **TC-02a**: Given a temp tree `plugins/mobile/skills/appstore/SKILL.md`, When called with `"appstore"`, Then returns absolute path to `plugins/mobile/skills/appstore`.
- **TC-02b**: Given two matching plugins (`plugins/a/skills/dup/SKILL.md`, `plugins/b/skills/dup/SKILL.md`), When called with `"dup"`, Then returns the `a/` path (lexicographic first).
- **TC-02c**: Given no match, When called with `"missing"`, Then returns `null`.

### T-03: Write `resolveSkillApiName` integration tests (authored path)
**AC**: AC-US1-01, AC-US1-04, AC-US3-01, AC-US3-02, AC-US3-03
**Status**: [x] Done
**File**: same test file as T-01
**Test Plan**:
- **TC-03a**: Given a lockfile entry for `installed-skill` with source `github:foo/bar#abc`, When resolveSkillApiName is called, Then returns `foo/bar/installed-skill` AND zero git shell-outs were issued.
- **TC-03b**: Given no lockfile entry and an authored skill at `plugins/mobile/skills/appstore/SKILL.md` with mocked git remote `https://github.com/anton-abyzov/vskill.git`, When resolveSkillApiName is called, Then returns `anton-abyzov/vskill/appstore`.
- **TC-03c**: Same as TC-03b, When called twice, Then `git config --get remote.origin.url` was invoked exactly once (cache hit second time).
- **TC-03d**: Given no lockfile entry and no authored SKILL.md anywhere, When resolveSkillApiName is called, Then returns the bare skill name (preserves backward compat).
- **TC-03e**: Given an authored skill but git execFile rejects (no git on PATH), When resolveSkillApiName is called, Then returns the bare skill name.

## Phase 2 — GREEN (minimum implementation)

### T-04: Implement `parseGitHubRemoteUrl`
**AC**: AC-US1-01
**Status**: [x] Done
**File**: `repositories/anton-abyzov/vskill/src/eval-server/skill-name-resolver.ts` (new)
**Test Plan**: T-01 passes.

### T-05: Implement `findAuthoredSkillDir`
**AC**: AC-US1-01, AC-US3-02
**Status**: [x] Done
**File**: same as T-04
**Test Plan**: T-02 passes.

### T-06: Implement `readGitOriginOwnerRepo` (execFile + parser)
**AC**: AC-US1-01, AC-US1-03
**Status**: [x] Done
**File**: same as T-04
**Test Plan**: covered by T-03b, T-03e via `vi.mock("node:child_process")`.

### T-07: Wire fallback into `resolveSkillApiName` with cache
**AC**: AC-US1-01, AC-US1-04, AC-US2-02, AC-US3-01, AC-US3-02
**Status**: [x] Done
**File**: `repositories/anton-abyzov/vskill/src/eval-server/api-routes.ts` (edit) + import from T-04 module
**Test Plan**: T-03a..e pass. Plus all existing `api-routes` tests still green.

## Phase 3 — Proxy verification + REFACTOR

### T-08: Confirm proxy routes return correct envelope
**AC**: AC-US1-02, AC-US2-01
**Status**: [x] Done
**Test Plan**:
- **TC-08a**: Given an authored skill resolves to `owner/repo/skill`, When `GET /api/skills/mobile/appstore/versions` is invoked with the upstream platform stubbed to return `{ versions: [{version:"1.0.1"},{version:"1.0.0"}], count: 2 }`, Then the proxy responds 200 with `{ versions: [...], count: 2, source: "platform" }` (envelope unchanged from existing 0707 contract).
- **TC-08b**: Same but `from=1.0.0&to=1.0.1` on `/versions/diff` reaches the platform diff endpoint with the hierarchical path.

### T-09: Manual verification in Skill Studio
**AC**: AC-US1-02 (success criteria)
**Status**: [x] Done
**Steps**:
1. `cd repositories/anton-abyzov/vskill && npm run build && npm link` (or restart running studio).
2. Open `localhost:3162/?panel=tests#/skills/mobile/appstore` → Versions tab.
3. Expect 2 versions (1.0.1, 1.0.0) listed.
4. Open obsidian-brain → expect 6 versions.
**Test Plan**: visual confirmation; record in increment notes.

### T-10: Run full test suite + lint
**AC**: AC-US3-03
**Status**: [x] Done
**Steps**: `cd repositories/anton-abyzov/vskill && npx vitest run && npx tsc --noEmit`. Zero failures.

## Phase 4 — Closure

### T-11: Sync living docs and run /sw:done
**AC**: (process)
**Status**: [x] Done
**Steps**: `specweave sync-living-docs 0714-studio-versions-authored-skill-resolver` then invoke `/sw:done 0714`.
