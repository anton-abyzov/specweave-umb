# Tasks: specweave get CLI command

## Summary

| Category | Count |
|----------|-------|
| Total tasks | 13 |
| Completed | 0 |
| Remaining | 13 |

---

### T-001: Source Parser — unit tests (RED)
**User Story**: US-001 | **Satisfies ACs**: AC-US1-01, AC-US1-02, AC-US1-03, AC-US1-04, AC-US1-05 | **Status**: [ ] pending
**Test**: Given `owner/repo`, HTTPS, SSH, local path, and non-GitHub URL inputs → When `parseSource()` runs → Then correct `ParsedSource` discriminated union is returned for each case
**File**: `src/cli/helpers/get/source-parser.test.ts`

---

### T-002: Source Parser — implementation (GREEN)
**User Story**: US-001 | **Satisfies ACs**: AC-US1-01, AC-US1-02, AC-US1-03, AC-US1-04, AC-US1-05 | **Status**: [ ] pending
**Test**: All T-001 tests pass
**File**: `src/cli/helpers/get/source-parser.ts`

Parsing rules:
- `git@github.com:org/repo.git` → `{ type: "github", owner, repo, cloneUrl: ssh-passthrough }`
- `https://github.com/org/repo[.git]` → `{ type: "github", owner, repo, cloneUrl: https-passthrough }`
- `https://other-host.com/org/repo` → `{ type: "git", owner, repo, cloneUrl }`
- `owner/repo` shorthand → `{ type: "github", owner, repo, cloneUrl: "https://github.com/owner/repo.git" }`
- `./path` or `/path` → `{ type: "local", absolutePath: resolved }`

Strip trailing `.git` from repo name. Strip trailing `/` from paths.

---

### T-003: Clone Helper — unit tests (RED)
**User Story**: US-002 | **Satisfies ACs**: AC-US2-01, AC-US2-03, AC-US2-04, AC-US2-05 | **Status**: [ ] pending
**Test**: Given mocked `execFileNoThrow` → When `cloneRepo()` is called with existing dir / new dir / auth failure / branch option → Then correct `CloneResult` is returned and git args are correct
**File**: `src/cli/helpers/get/clone-repo.test.ts`

---

### T-004: Clone Helper — implementation (GREEN)
**User Story**: US-002 | **Satisfies ACs**: AC-US2-01, AC-US2-03, AC-US2-04, AC-US2-05 | **Status**: [ ] pending
**Test**: All T-003 tests pass
**File**: `src/cli/helpers/get/clone-repo.ts`

```typescript
interface CloneResult { cloned: boolean; repoPath: string; skippedReason?: string; }
async function cloneRepo(source: ParsedSource, targetDir: string, options?: { branch?: string }): Promise<CloneResult>
```

- If `targetDir/.git` exists → return `{ cloned: false, skippedReason: "already exists" }`
- `mkdir -p` parent dir
- `execFileNoThrow('git', ['clone', cloneUrl, repoName, ...(branch ? ['--branch', branch] : [])], { cwd: parentDir })`
- On auth error (exitCode !== 0): detect stderr patterns (`Permission denied`, `Authentication failed`, `Repository not found`) and throw with helpful message

---

### T-005: Register Helper — unit tests (RED)
**User Story**: US-003 | **Satisfies ACs**: AC-US3-01, AC-US3-02, AC-US3-03, AC-US3-04, AC-US3-05 | **Status**: [ ] pending
**Test**: Given mocked `persistUmbrellaConfig` and fs → When `registerRepo()` is called → Then config.json gets correct entry, prefix defaults to 3-char uppercase, role is set, duplicate is detected
**File**: `src/cli/helpers/get/register-repo.test.ts`

---

### T-006: Register Helper — implementation (GREEN)
**User Story**: US-003 | **Satisfies ACs**: AC-US3-01, AC-US3-02, AC-US3-03, AC-US3-04, AC-US3-05 | **Status**: [ ] pending
**Test**: All T-005 tests pass
**File**: `src/cli/helpers/get/register-repo.ts`

```typescript
interface RegisterResult { registered: boolean; alreadyRegistered: boolean; }
async function registerRepo(projectRoot: string, owner: string, repoName: string, repoPath: string, options?: { prefix?: string; role?: string }): Promise<RegisterResult>
```

- Read `config.json`, check for existing entry by id → return `alreadyRegistered: true` if found
- Build `ChildRepoConfig` entry with `id`, `path`, `name`, `prefix` (default: first 3 chars uppercase), `role`
- Call `persistUmbrellaConfig()` for dedup-safe merge
- Post-patch `prefix` and `role` via read-modify-write (mirrors `addRepoToUmbrella()` pattern)

---

### T-007: Get Command — unit tests (RED)
**User Story**: US-004 | **Satisfies ACs**: AC-US4-01, AC-US4-02, AC-US4-03, AC-US4-04, AC-US4-05 | **Status**: [ ] pending
**Test**: Given mocked helpers + config → When `getCommand()` is called with various option combinations → Then correct helpers are called in order, `--no-init` skips init, `--yes` skips prompts, local path skips clone
**File**: `src/cli/commands/get.test.ts`

---

### T-008: Get Command — implementation (GREEN)
**User Story**: US-004 | **Satisfies ACs**: AC-US4-01, AC-US4-02, AC-US4-03, AC-US4-04, AC-US4-05 | **Status**: [ ] pending
**Test**: All T-007 tests pass
**File**: `src/cli/commands/get.ts`

Orchestration flow:
1. Check `.specweave/config.json` exists → error if not found
2. Read `umbrella.enabled` from config
3. `parseSource(source)` → `ParsedSource`
4. For `local` type: validate path + `.git` exists, `detectRepository()` for owner/repo
5. Determine `targetDir` (`repositories/{owner}/{repo}/` in umbrella, `./{repo}/` outside)
6. Clone if remote source (skip if dir + `.git` exists)
7. Register in umbrella config if `umbrella.enabled`
8. Run `execFileNoThrow('specweave', ['init', '.'], { cwd: targetDir })` unless `--no-init`
9. Print summary

---

### T-009: Register command in bin/specweave.js
**User Story**: US-004 | **Satisfies ACs**: AC-US4-01 | **Status**: [ ] pending
**Test**: Given `bin/specweave.js` → When `specweave get --help` is run → Then the `add` command appears with correct options
**File**: `bin/specweave.js`

Add before the `migrate-to-umbrella` block:
```javascript
program
  .command('get <source>')
  .description('Clone and register an existing repository into the workspace')
  .option('--branch <branch>', 'Clone a specific branch')
  .option('--prefix <prefix>', 'User story prefix (default: first 3 chars uppercase)')
  .option('--role <role>', 'Repository role (frontend, backend, mobile, infra, shared)')
  .option('--no-init', 'Skip specweave init on cloned repo')
  .option('--yes', 'Skip confirmation prompts')
  .action(async (source, opts) => {
    const { getCommand } = await import('../dist/src/cli/commands/get.js');
    await addCommand(source, opts);
  });
```

---

### T-010: sw:get Skill — SKILL.md
**User Story**: US-005 | **Satisfies ACs**: AC-US5-01, AC-US5-02, AC-US5-03 | **Status**: [ ] pending
**Test**: Given SKILL.md → When `description` is parsed → Then it contains trigger phrases and explicit negative patterns
**File**: `plugins/specweave/skills/get/SKILL.md`

Triggers: "add repo", "clone repo", "add github repo to umbrella", "register this repo", "add owner/repo", "clone and register"
Negative: "add a feature", "add a task", "add a story", "add an increment" (→ sw:increment)

Skill body: extract source from user message, infer `--prefix`/`--role`/`--branch` if mentioned, run `specweave get <source> [...flags]`

---

### T-011: Run full test suite
**User Story**: US-001–US-004 | **Satisfies ACs**: all | **Status**: [ ] pending
**Test**: `npx vitest run` in `repositories/anton-abyzov/specweave/` → all new tests pass, no regressions
**File**: test suite

---

### T-012: Build and verify CLI
**User Story**: US-004 | **Satisfies ACs**: AC-US4-01 | **Status**: [ ] pending
**Test**: `npm run build` succeeds → `specweave get --help` shows the command
**File**: built dist/

---

### T-013: Refactor pass (/simplify)
**User Story**: US-001–US-005 | **Satisfies ACs**: all | **Status**: [ ] pending
**Test**: `/simplify` review — no duplication, no dead code, all edge cases handled
**Notes**: Run after all tests pass; clean up any temporary scaffolding
