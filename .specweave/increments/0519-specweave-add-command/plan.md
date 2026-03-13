# Architecture Plan: specweave get CLI command

## Overview

A new top-level CLI command `specweave get <source>` that clones an existing git repository into a SpecWeave umbrella workspace and registers it in the umbrella config. Decomposed into four modules following the existing `src/cli/helpers/` + `src/cli/commands/` pattern.

## Architecture Decisions

### AD-1: Modular Helper Pattern (not monolithic command)

Split logic into three focused helpers under `src/cli/helpers/get/`:

```
src/cli/helpers/get/
  source-parser.ts   -- Pure function: string -> ParsedSource
  clone-repo.ts      -- Side-effect: git clone orchestration
  register-repo.ts   -- Side-effect: config.json mutation

src/cli/commands/
  get.ts             -- Orchestrator: parse -> clone -> register -> init
```

**Rationale**: Matches the established `src/cli/helpers/init/` pattern (github-repo-cloning, bitbucket-repo-cloning, ado-repo-cloning). Each helper is independently testable. The command file is a thin orchestrator.

**Alternative considered**: Single file. Rejected -- the source parser is pure logic with 5+ input formats, worth isolating for unit testing without filesystem/process mocking.

### AD-2: Reuse existing utilities, no new abstractions

| Need | Reuse | Notes |
|------|-------|-------|
| Git clone | `execFileNoThrow('git', ['clone', ...])` | Same pattern as clone-worker.ts |
| Remote detection | `detectRepository()` from git-utils.ts | For local path sources |
| URL parsing | `parseGitRemoteUrl()` from git-utils.ts | Partial reuse for SSH/HTTPS detection |
| Config registration | `persistUmbrellaConfig()` from umbrella-detector.ts | Handles dedup-safe merge by id |
| Config types | `ChildRepoConfig`, `UmbrellaConfig` from config/types.ts | Existing interfaces |

**No new dependencies**. No new abstractions. Direct reuse of battle-tested utilities.

### AD-3: Registration via `persistUmbrellaConfig()` + prefix patch

`persistUmbrellaConfig()` handles the merge-by-id deduplication pattern (umbrella-detector.ts). It does not handle `prefix` or `role` fields. Registration will:

1. Call `persistUmbrellaConfig()` for the dedup-safe base entry
2. Read-modify-write to patch `prefix` and `role` onto the entry

This mirrors exactly what `addRepoToUmbrella()` in umbrella-migrator.ts does (lines 696-719).

### AD-4: Command registration in bin/specweave.js

Register as a top-level command (not a subcommand of `migrate-to-umbrella`), placed just before the migrate-to-umbrella block. Uses the same lazy-import pattern:

```javascript
program
  .command('get <source>')
  .description('Clone and register an existing repository into the workspace')
  .option('--branch <branch>', 'Clone a specific branch')
  .option('--prefix <prefix>', 'User story prefix (default: first 3 chars uppercase)')
  .option('--role <role>', 'Repository role (frontend, backend, etc.)')
  .option('--no-init', 'Skip specweave init on cloned repo')
  .option('--yes', 'Skip confirmation prompts')
  .action(async (source, opts) => {
    const { getCommand } = await import('../dist/src/cli/commands/get.js');
    await getCommand(source, opts);
  });
```

### AD-5: No background worker

Unlike the multi-repo clone in init (clone-worker.ts), `specweave get` clones a single repository. No background job, no progress file, no job manager. Just inline `execFileNoThrow('git', ['clone', ...])` with stdout/stderr forwarding.

## Component Design

### 1. source-parser.ts

Pure function with zero side effects.

```
Input:  string (user's <source> argument)
Output: ParsedSource
```

```typescript
type SourceType = 'github' | 'git' | 'local';

interface ParsedSource {
  type: SourceType;
  owner: string;       // org/user for remote, extracted from git remote for local
  repo: string;        // repo name (no .git suffix)
  cloneUrl?: string;   // full clone URL (undefined for local)
  absolutePath?: string; // resolved absolute path (only for local)
}
```

Parsing rules (ordered by specificity):

| Input pattern | Type | Clone URL |
|---|---|---|
| `git@host:org/repo.git` | github/git | passthrough (SSH) |
| `https://github.com/org/repo[.git]` | github | passthrough (HTTPS) |
| `https://other-host.com/org/repo` | git | passthrough |
| `owner/repo` (no protocol, no dots except in names) | github | `https://github.com/owner/repo.git` |
| `./path` or `/path` or `../path` | local | n/a |

For `github` type, both SSH and HTTPS URLs from github.com are typed as `github`. Non-GitHub git URLs are typed as `git`. The owner/repo are extracted by regex from the URL. For local paths, `path.resolve()` produces the absolute path.

Edge cases handled:
- Trailing `.git` stripped when deriving repo name
- Trailing `/` stripped from paths
- Dots and hyphens in owner/repo names

### 2. clone-repo.ts

Orchestrates git clone with idempotency.

```typescript
interface CloneOptions {
  branch?: string;
}

interface CloneResult {
  cloned: boolean;      // true if clone happened, false if skipped
  repoPath: string;     // absolute path to the cloned repo
  skippedReason?: string; // "already exists" etc.
}

async function cloneRepo(
  source: ParsedSource,
  targetDir: string,
  options?: CloneOptions
): Promise<CloneResult>
```

Logic flow:

```
1. Check if targetDir/.git exists
   YES -> return { cloned: false, skippedReason: "already exists" }
2. mkdir -p parent directory
3. Build args: ['clone', cloneUrl, repoName]
   if (branch) args.push('--branch', branch)
4. execFileNoThrow('git', args, { cwd: parentDir })
5. If exitCode !== 0:
   - Check stderr for auth-related patterns
   - Throw with helpful message (suggest gh auth login / SSH key setup)
6. Return { cloned: true, repoPath: targetDir }
```

Auth error detection patterns (from stderr):
- `Permission denied (publickey)` -- SSH key issue
- `Authentication failed` -- HTTPS credential issue
- `Repository not found` -- private repo + no auth
- `Could not resolve host` -- network issue

### 3. register-repo.ts

Handles umbrella config registration.

```typescript
interface RegisterOptions {
  prefix?: string;
  role?: string;
}

interface RegisterResult {
  registered: boolean;
  alreadyRegistered: boolean;
}

async function registerRepo(
  projectRoot: string,
  owner: string,
  repoName: string,
  repoPath: string,     // relative path from projectRoot
  options?: RegisterOptions
): Promise<RegisterResult>
```

Logic flow:

```
1. Read config.json
2. Check umbrella.childRepos for existing entry by id (=repoName)
   YES -> return { registered: false, alreadyRegistered: true }
3. Build ChildRepoConfig entry:
   - id: repoName
   - path: repoPath (relative, e.g., "repositories/org/repo")
   - name: repoName
   - prefix: options.prefix || repoName.substring(0,3).toUpperCase()
   - role: options.role (if provided)
4. Call persistUmbrellaConfig() with the new entry
5. Patch prefix/role via read-modify-write (persistUmbrellaConfig doesn't handle these)
6. Return { registered: true, alreadyRegistered: false }
```

### 4. add.ts (Command Orchestrator)

Thin orchestrator that ties the helpers together.

```typescript
interface AddOptions {
  branch?: string;
  prefix?: string;
  role?: string;
  init?: boolean;   // default true, --no-init sets to false
  yes?: boolean;
}

async function addCommand(source: string, options: AddOptions): Promise<void>
```

Logic flow:

```
1. Detect SpecWeave project (check .specweave/config.json exists)
   NOT FOUND -> error "Not a SpecWeave project. Run specweave init first."

2. Read config to check umbrella.enabled
   isUmbrella = config.umbrella?.enabled === true

3. Parse source via parseSource(source)

4. Determine target directory:
   if (source.type === 'local'):
     - Validate path exists: fs.existsSync(absolutePath)
     - Validate .git exists: fs.existsSync(path.join(absolutePath, '.git'))
     - Use detectRepository() to extract owner/repo
     - targetDir = absolutePath (no clone needed)
   else (remote):
     if (isUmbrella):
       targetDir = path.join(projectRoot, 'repositories', source.owner, source.repo)
     else:
       targetDir = path.join(projectRoot, source.repo)

5. Clone (skip for local):
   if (source.type !== 'local'):
     result = await cloneRepo(source, targetDir, { branch: options.branch })
     Print clone status

6. Register in umbrella config (only if umbrella workspace):
   if (isUmbrella):
     relPath = path.relative(projectRoot, targetDir)
     result = await registerRepo(projectRoot, owner, repo, relPath, {
       prefix: options.prefix,
       role: options.role,
     })
     Print registration status

7. Run specweave init (if not --no-init):
   if (options.init !== false):
     execFileNoThrow('specweave', ['init', '.'], { cwd: targetDir })
     Print init status

8. Print summary
```

### 5. SKILL.md (sw:get skill)

Located at `plugins/specweave/skills/get/SKILL.md`.

Key fields:
- `name`: "get"
- `description`: Triggers on "add repo", "clone repo", "add github repo to umbrella", "register this repo"
- `activation`: Manual/keyword. Must NOT activate on "add a feature" or "add a task"
- Body: Instructions to extract source from user message and run `specweave get <source>` with appropriate flags

Negative activation patterns explicitly listed to prevent false positives:
- "add a feature" -> sw:increment
- "add a task" -> direct task creation
- "add a story" -> sw:increment
- "add an increment" -> sw:increment

## Data Flow

```
User: specweave get org/repo --prefix BE --role backend
                    |
                    v
            +---------------+
            | source-parser |  parseSource("org/repo")
            +-------+-------+  -> { type: "github", owner: "org", repo: "repo",
                    |             cloneUrl: "https://github.com/org/repo.git" }
                    v
            +---------------+
            |  clone-repo   |  cloneRepo(source, "repositories/org/repo")
            +-------+-------+  -> { cloned: true, repoPath: "..." }
                    |
                    v
            +----------------+
            | register-repo  |  registerRepo(root, "org", "repo", "repositories/org/repo",
            +-------+--------+    { prefix: "BE", role: "backend" })
                    |             -> { registered: true }
                    v
            +----------------+
            | specweave init |  execFileNoThrow("specweave", ["init", "."], { cwd })
            +----------------+
```

## Edge Cases Matrix

| Scenario | Clone | Register | Init | Notes |
|---|---|---|---|---|
| Fresh clone + umbrella | YES | YES | YES | Happy path |
| Repo dir exists, not registered | SKIP | YES | YES | AC-US4-05 |
| Repo dir exists + registered | SKIP | SKIP | SKIP | Full idempotency |
| Local path, umbrella | SKIP | YES | YES | AC-US4-03 |
| Non-umbrella workspace | YES | SKIP | optional | AC-US2-02 |
| Git auth failure | ERROR | SKIP | SKIP | AC-US2-05 |
| Not a SpecWeave project | ERROR | n/a | n/a | Guard at top |
| Local path not exists | ERROR | n/a | n/a | Edge case |
| Local path no .git | ERROR | n/a | n/a | Edge case |

## File Inventory

### New Files

| File | Purpose | Lines (est.) |
|---|---|---|
| `src/cli/helpers/get/source-parser.ts` | Parse source argument | ~80 |
| `src/cli/helpers/get/clone-repo.ts` | Git clone orchestration | ~90 |
| `src/cli/helpers/get/register-repo.ts` | Umbrella config registration | ~70 |
| `src/cli/commands/get.ts` | Command orchestrator | ~120 |
| `plugins/specweave/skills/get/SKILL.md` | Skill definition | ~50 |

### Modified Files

| File | Change |
|---|---|
| `bin/specweave.js` | Add `program.command('get <source>')` block (~15 lines) |

## Dependencies

```
get.ts
  |- source-parser.ts (parseSource)
  |- clone-repo.ts (cloneRepo)
  |   \- execFileNoThrow (from utils/)
  |- register-repo.ts (registerRepo)
  |   \- persistUmbrellaConfig (from core/living-docs/)
  |- detectRepository (from utils/git-utils)
  \- chalk (for output)
```

No new npm dependencies. All imports use `.js` extensions per ESM/nodenext requirement.

## Testing Strategy

- **source-parser.ts**: Pure unit tests -- 7+ test cases covering all URL formats and edge cases. No mocking needed.
- **clone-repo.ts**: Unit tests with `execFileNoThrow` mocked via `vi.mock()`. Test idempotency (dir exists), auth failure messages, branch flag.
- **register-repo.ts**: Unit tests with `fs` and `persistUmbrellaConfig` mocked. Test dedup, prefix defaults, role assignment.
- **add.ts**: Integration-style unit tests with all helpers mocked. Test the orchestration logic and edge case matrix above.

## Risks and Mitigations

| Risk | Mitigation |
|---|---|
| `persistUmbrellaConfig` changes its interface | Import is already stable (used by clone-worker, migrate-to-umbrella). Pin to current signature. |
| `specweave init` subprocess fails | Non-fatal. Print warning, command still succeeds. |
| Windows path separators in `repoPath` | Use `path.join()` and `path.relative()` consistently. Normalize to `/` before writing to config. |
