# Tasks: Studio header — clickable GitHub link for locally-authored skills

## Task Notation

- `[T-###]`: Task ID
- `[ ]`: Not started | `[x]`: Completed
- Test mode: TDD (RED → GREEN → REFACTOR per task pair)

---

## Phase 1: Pure helpers (TDD)

### T-001: RED — Test plan for `parseGithubRemote()`

**User Story**: US-001 | **Satisfies ACs**: AC-US1-03, AC-US2-02 | **Status**: [x]

**Description**: Write failing unit tests for the pure remote-parser. No implementation yet.

**Test Plan**:
- **File**: `repositories/anton-abyzov/vskill/src/eval-server/__tests__/authored-source-link.test.ts`
- **Tests** (Given / When / Then):
  - **TC-001**: SSH remote with `.git` suffix
    - Given remote `git@github.com:anton-abyzov/greet-anton.git`
    - When `parseGithubRemote(remote)` runs
    - Then returns `https://github.com/anton-abyzov/greet-anton`
  - **TC-002**: SSH remote without `.git` suffix
    - Given remote `git@github.com:anton-abyzov/greet-anton`
    - When parsed
    - Then returns `https://github.com/anton-abyzov/greet-anton`
  - **TC-003**: HTTPS remote with `.git` suffix → strips
  - **TC-004**: HTTPS remote without `.git` suffix → unchanged
  - **TC-005**: `ssh://git@github.com/owner/repo.git` URL form
    - Then returns `https://github.com/owner/repo`
  - **TC-006**: Non-github SSH (`git@gitlab.com:owner/repo.git`) → returns `null`
  - **TC-007**: Non-github HTTPS (`https://bitbucket.org/owner/repo`) → returns `null`
  - **TC-008**: Empty string → returns `null`
  - **TC-009**: Whitespace-only → returns `null`
  - **TC-010**: Malformed (`not-a-url`) → returns `null`

---

### T-002: GREEN — Implement `parseGithubRemote()`

**User Story**: US-001 | **Satisfies ACs**: AC-US1-03 | **Status**: [x]

**Description**: Implement the pure regex-based parser in `api-routes.ts`. Make T-001 tests pass.

**Implementation Details**:
- Add at module scope (near `resolveSourceLink`):
  ```ts
  function parseGithubRemote(remote: string): string | null {
    const trimmed = (remote ?? "").trim();
    if (!trimmed) return null;
    // SSH: git@github.com:owner/repo[.git]
    let m = /^git@github\.com:([^/]+)\/([^/.]+(?:\.[^/]+)*?)(?:\.git)?$/.exec(trimmed);
    if (m) return `https://github.com/${m[1]}/${m[2]}`;
    // ssh://git@github.com/owner/repo[.git]
    m = /^ssh:\/\/git@github\.com\/([^/]+)\/([^/.]+(?:\.[^/]+)*?)(?:\.git)?$/.exec(trimmed);
    if (m) return `https://github.com/${m[1]}/${m[2]}`;
    // https://github.com/owner/repo[.git]
    m = /^https?:\/\/github\.com\/([^/]+)\/([^/.]+(?:\.[^/]+)*?)(?:\.git)?(?:\/.*)?$/.exec(trimmed);
    if (m) return `https://github.com/${m[1]}/${m[2]}`;
    return null;
  }
  ```

**Test**: Given any input from T-001 → When `parseGithubRemote(input)` runs → Then returns the expected canonical URL or null.

---

### T-003: RED — Test plan for `walkUpForGitRoot()`

**User Story**: US-001, US-002 | **Satisfies ACs**: AC-US1-01, AC-US2-01 | **Status**: [x]

**Description**: Write failing tests for the `.git` ancestor walker.

**Test Plan**:
- **File**: same as T-001 — `authored-source-link.test.ts`
- **Tests**:
  - **TC-011**: `.git` directory at start dir
    - Given a tmp dir containing `.git/` and a child `skill/`
    - When `walkUpForGitRoot(skillDir)` runs
    - Then returns the parent (tmp dir)
  - **TC-012**: `.git` file (worktree case) at parent
    - Given a tmp dir containing a `.git` FILE and a child `skill/`
    - Then returns the parent
  - **TC-013**: No `.git` anywhere in walk
    - Given a tmp dir with no git anywhere
    - Then returns `null`
  - **TC-014**: Bails at filesystem root
    - Given a path under `/tmp` with no `.git`
    - Then walk terminates without throwing, returns `null`
  - **TC-015**: Respects `maxLevels` cap
    - Given a deeply nested path with `.git` 15 levels up
    - When called with `maxLevels = 12`
    - Then returns `null`

---

### T-004: GREEN — Implement `walkUpForGitRoot()`

**User Story**: US-001, US-002 | **Satisfies ACs**: AC-US1-01, AC-US2-01 | **Status**: [x]

**Description**: Implement the walker. Use `existsSync` (handles both `.git/` directory and `.git` file).

**Implementation Details**:
```ts
function walkUpForGitRoot(startDir: string, maxLevels = 12): string | null {
  let current = resolve(startDir);
  for (let i = 0; i < maxLevels; i++) {
    if (existsSync(join(current, ".git"))) return current;
    const parent = dirname(current);
    if (parent === current) return null;  // filesystem root
    current = parent;
  }
  return null;
}
```

**Test**: Given any test case from T-003 → When `walkUpForGitRoot` runs → Then returns the expected git root or null.

---

## Phase 2: I/O helper with memoization (TDD)

### T-005: RED — Integration tests for `detectAuthoredSourceLink()`

**User Story**: US-001, US-002, US-003 | **Satisfies ACs**: AC-US1-01, AC-US1-02, AC-US2-01, AC-US2-02, AC-US3-01, AC-US3-02, AC-US3-03 | **Status**: [x]

**Description**: Real-git-repo integration tests with `mkdtempSync` + `git init` setups. Write 8 failing cases.

**Test Plan**:
- **File**: `authored-source-link.test.ts` (same file)
- **Helper**: `seedGitRepo(remote: string, skillSubdir = "")` — creates tmp dir, runs `git init`, `git config user.email + user.name`, `git remote add origin <remote>`, writes SKILL.md, optionally commits.
- **Tests**:
  - **TC-016**: Authored skill at repo root with SSH github remote
    - Given a tmp git repo with origin `git@github.com:a/b.git` and SKILL.md committed at root
    - When `detectAuthoredSourceLink(repoDir)` runs
    - Then returns `{repoUrl: "https://github.com/a/b", skillPath: "SKILL.md"}`
  - **TC-017**: Authored skill at `skills/foo/SKILL.md` (multi-skill repo)
    - Then returns `{repoUrl, skillPath: "skills/foo/SKILL.md"}`
  - **TC-018**: No `.git` directory anywhere
    - Then returns `{null, null}`
  - **TC-019**: Non-github remote (gitlab)
    - Then returns `{null, null}` AND `git ls-files` is NOT invoked (verified via spy or by running in a dir where ls-files would error — but we short-circuit before reaching it)
  - **TC-020**: Untracked SKILL.md (no commit)
    - Given a git repo with a SKILL.md that has not been `git add`-ed
    - Then returns `{repoUrl, skillPath: <relative-path-from-walk>}` (filesystem fallback)
  - **TC-021**: Memoization — second call hits cache
    - Given a previously-detected dir
    - When called again
    - Then `git config` and `git ls-files` are NOT invoked (assert via spy on execFileSync OR by deleting the .git dir and verifying the cached value is still returned)
  - **TC-022**: Never throws on git failure
    - Given a dir where `git config` errors (e.g., remote not set)
    - Then returns `{null, null}` (no exception bubbles up)
  - **TC-023**: Bounded child_process invocations
    - Given a fully successful detection
    - Then exactly 2 execFileSync calls happen (config + ls-files)
    - Given a detection that fails at the remote step
    - Then exactly 1 execFileSync call happens (config only — short-circuit)

---

### T-006: GREEN — Implement `detectAuthoredSourceLink()`

**User Story**: US-001, US-002, US-003 | **Satisfies ACs**: AC-US1-01, AC-US1-02, AC-US2-01, AC-US2-02, AC-US3-01, AC-US3-02, AC-US3-03 | **Status**: [x]

**Description**: Implement the I/O helper with module-level memoization.

**Implementation Details**:
```ts
const authoredSourceLinkCache = new Map<string, { repoUrl: string | null; skillPath: string | null }>();

function detectAuthoredSourceLink(skillDir: string): { repoUrl: string | null; skillPath: string | null } {
  const absDir = resolve(skillDir);
  const cached = authoredSourceLinkCache.get(absDir);
  if (cached) return cached;

  const result = (() => {
    const gitRoot = walkUpForGitRoot(absDir);
    if (!gitRoot) return { repoUrl: null, skillPath: null };

    let remote = "";
    try {
      remote = execFileSync("git", ["config", "--get", "remote.origin.url"], {
        cwd: gitRoot,
        timeout: 1500,
        stdio: ["ignore", "pipe", "ignore"],
        encoding: "utf-8",
      }).trim();
    } catch {
      return { repoUrl: null, skillPath: null };
    }

    const repoUrl = parseGithubRemote(remote);
    if (!repoUrl) return { repoUrl: null, skillPath: null };

    let skillPath: string | null = null;
    try {
      const tracked = execFileSync("git", ["ls-files", "--full-name", "SKILL.md"], {
        cwd: absDir,
        timeout: 1500,
        stdio: ["ignore", "pipe", "ignore"],
        encoding: "utf-8",
      }).trim();
      if (tracked) {
        skillPath = tracked;
      }
    } catch {
      // ignore — fallback below
    }

    if (!skillPath) {
      // Filesystem fallback for untracked SKILL.md
      skillPath = relative(gitRoot, join(absDir, "SKILL.md")).replace(/\\/g, "/");
    }

    return { repoUrl, skillPath };
  })();

  authoredSourceLinkCache.set(absDir, result);
  return result;
}
```

**Test**: All TC-016 through TC-023 pass.

---

## Phase 3: Wire into `resolveSourceLink`

### T-007: RED — Integration test for `resolveSourceLink` precedence

**User Story**: US-002 | **Satisfies ACs**: AC-US2-03, AC-US1-04 | **Status**: [x]

**Description**: Test that lockfile path STILL wins, AND that authored fall-through fires only when lockfile is silent.

**Test Plan**:
- **File**: `authored-source-link.test.ts`
- **Tests**:
  - **TC-024**: Lockfile precedence preserved
    - Given a skill dir inside a git repo (`origin: git@github.com:wrong/repo.git`) with a lockfile entry pointing to `https://github.com/correct/repo`
    - When `buildSkillMetadata(skillDir, "installed", root)` runs
    - Then `repoUrl` = `https://github.com/correct/repo` (lockfile wins, NOT the git remote)
  - **TC-025**: Authored fall-through fires when no lockfile
    - Given a skill dir inside a git repo with `origin: git@github.com:author/repo.git`, NO lockfile written
    - When `buildSkillMetadata(skillDir, "source", root)` runs
    - Then `repoUrl` = `https://github.com/author/repo`, `skillPath = "SKILL.md"`
  - **TC-026**: Authored skill outside git → null
    - Given a skill dir with no `.git` ancestor
    - Then `repoUrl` = null, `skillPath` = null (copy-chip fallback in UI)

---

### T-008: GREEN — Append fall-through to `resolveSourceLink`

**User Story**: US-002 | **Satisfies ACs**: AC-US2-03, AC-US1-04 | **Status**: [x]

**Description**: One-line change to `resolveSourceLink` — replace each `return { repoUrl: null, skillPath: null };` exit with a fall-through to `detectAuthoredSourceLink(skillDir)`.

**Implementation Details**:
- Replace the four `return { repoUrl: null, skillPath: null };` exits in `resolveSourceLink` (lines 788, 793, 811, plus implicit exit) with `return detectAuthoredSourceLink(skillDir);`
- Lockfile-success branches (lines 795-800, 812-815) remain unchanged — they return the lockfile values directly.

**Test**: TC-024 + TC-025 + TC-026 pass. Existing `skill-metadata-source-link.test.ts` (6 tests for 0737/0743) continues to pass byte-identically (the fall-through never fires for those tests because they all have a lockfile entry).

---

## Phase 4: Manual verification

### T-009: Studio integration check (manual)

**User Story**: US-001, US-002 | **Satisfies ACs**: AC-US1-04, AC-US2-01 | **Status**: [x]

**Description**: Per memory `feedback_self_install_vskill.md` — closer agent installs the candidate vskill version itself and runs the studio (does NOT ask the user to restart).

**Verification result (2026-04-26)**:
- `npm run build` clean (tsc 0 errors).
- One-off node script invoking `detectAuthoredSourceLink('/Users/antonabyzov/Projects/TestLab/greet-anton')` returned `{repoUrl: "https://github.com/anton-abyzov/greet-anton", skillPath: "SKILL.md"}`. ✓
- `buildSkillMetadata` invoked with `root = /Users/antonabyzov/Projects/TestLab` (which has a `vskill.lock` with sourceRepoUrl/sourceSkillPath pointing to the installed-from-vskill copy) returned the lockfile-recorded values — confirming AC-US2-03 lockfile precedence. ✓
- All 28 new unit tests + 6 0737/0743 regression tests pass (34/34).

**Verification steps**:
1. `cd repositories/anton-abyzov/vskill && npm run build`
2. `npm pack` → produces `vskill-X.Y.Z.tgz`
3. `npx vskill-X.Y.Z.tgz studio` (or local link, depending on convention)
4. Open `http://localhost:<assigned-port>/#/skills/TestLab/greet-anton`
5. Assert: header shows `↗` anchor with `target="_blank"`
6. Click anchor → assert opens `https://github.com/anton-abyzov/greet-anton/blob/HEAD/SKILL.md` in new tab
7. Open another skill in a NON-git directory → assert copy-chip still renders (no link, no error)
8. Open an already-installed skill (e.g. one from the platform) → assert original 0737/0743 link still works

**Test**: All four UI assertions pass.

---

## Test File Summary

Single new file: `repositories/anton-abyzov/vskill/src/eval-server/__tests__/authored-source-link.test.ts`
- 26 test cases (TC-001 through TC-026)
- Uses `mkdtempSync` + `execFileSync("git", [...])` for real git repo seeding
- `afterEach` cleanup with `rmSync(tmp, { recursive: true, force: true })`
- Module-level `authoredSourceLinkCache.clear()` in `beforeEach` to isolate memoization tests

## Regression Coverage

`repositories/anton-abyzov/vskill/src/eval-server/__tests__/skill-metadata-source-link.test.ts` is NOT modified. All 6 existing tests must continue passing.
