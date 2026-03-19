# Architecture Plan: Init Async Clone Jobs

## Decision: Replace sync cloning with launchCloneJob threshold routing

### Context

`specweave init` currently uses `cloneReposIntoWorkspace()` — a synchronous loop of `execFileNoThrowSync('git', ['clone', ...])` calls that blocks the entire init flow. The existing background job system (`launchCloneJob()` + `clone-worker.ts`) is production-proven via `specweave get` and `triggerGitHubRepoCloning()`. This increment wires init into that same system with a repo-count threshold to decide foreground vs background execution.

### Architecture

```
User input → promptRepoUrls() → ParsedRepo[]
                                      ↓
                         mapParsedReposToCloneOptions()
                                      ↓
                   CloneLaunchOptions.repositories[]
                                      ↓
                         repos.length <= 3?
                         /              \
                       yes               no
                        ↓                 ↓
         launchCloneJob(fg:true)   launchCloneJob(bg:false)
                        ↓                 ↓
         runForegroundClone()      clone-worker.ts (detached)
                        ↓                 ↓
         set umbrellaDiscovery    init completes immediately
         from results              worker updates config later
                        ↓
            init config write
         (includes childRepos)
```

### Component Changes

#### 1. `src/cli/helpers/init/repo-connect.ts` — Modify

**Add constant**:
```typescript
export const FOREGROUND_CLONE_THRESHOLD = 3;
```

**Add mapping function**:
```typescript
export function mapParsedReposToCloneOptions(
  repos: ParsedRepo[]
): Array<{ owner: string; name: string; path: string; cloneUrl: string }> {
  return repos.map(r => ({
    owner: r.org,
    name: r.name,
    path: `repositories/${r.org}/${r.name}`,
    cloneUrl: r.cloneUrl,
  }));
}
```

The mapping is trivial: `ParsedRepo.org` → `owner`, construct `path` from org+name pattern.

**Add foreground clone runner**:
```typescript
export async function runForegroundClone(
  projectPath: string,
  jobId: string,
  repos: Array<{ owner: string; name: string; path: string; cloneUrl: string }>
): Promise<RepoConnectResult>
```

This function:
- Iterates repos sequentially
- Uses `execFileNoThrow` (async) for each `git clone` — NOT `execFileNoThrowSync` (satisfies AC-US1-05)
- Updates job progress via `getJobManager(projectPath).updateProgress()`
- On completion: calls `jobManager.completeJob()` or `jobManager.completeJobWithWarnings()`
- Returns `RepoConnectResult` with per-repo success/failure for init to consume

**Remove**: `cloneReposIntoWorkspace()` — the only caller is `init.ts` line 365, which this increment replaces. No other callers exist (verified via grep — remaining references are test files and re-exports).

#### 2. `src/cli/commands/init.ts` — Modify (lines 349-379)

**Replace the clone block** (lines 362-373):

Before:
```typescript
const repos = await promptRepoUrls(language);
if (repos.length > 0) {
  const result = cloneReposIntoWorkspace(targetDir, repos);
  console.log(chalk.green(`\n   ✓ Cloned ${result.totalCloned} repo(s)`));
  // ...
  umbrellaDiscovery = scanUmbrellaRepos(targetDir);
}
```

After:
```typescript
const repos = await promptRepoUrls(language);
if (repos.length > 0) {
  const mapped = mapParsedReposToCloneOptions(repos);

  if (repos.length <= FOREGROUND_CLONE_THRESHOLD) {
    // Foreground: blocking clone for small batches
    const { job } = await launchCloneJob({
      projectPath: targetDir,
      repositories: mapped,
      foreground: true,
    });
    const cloneResult = await runForegroundClone(targetDir, job.id, mapped);
    console.log(chalk.green(`\n   ✓ Cloned ${cloneResult.totalCloned} repo(s)`));
    if (cloneResult.totalFailed > 0) {
      console.log(chalk.yellow(`   ⚠ ${cloneResult.totalFailed} repo(s) failed to clone`));
    }
    // Build umbrella discovery from successful clones
    // (replaces scanUmbrellaRepos re-scan — AC-US1-06)
    const clonedRepos = cloneResult.repos.filter(r => r.success);
    if (clonedRepos.length > 0) {
      umbrellaDiscovery = {
        isUmbrella: true,
        repositoriesDir: path.join(targetDir, 'repositories'),
        orgs: [...new Set(clonedRepos.map(r => r.org))],
        repos: clonedRepos.map(r => ({
          org: r.org,
          name: r.name,
          path: r.path,
          hasGit: true,
        })),
        totalRepoCount: clonedRepos.length,
      };
    }
  } else {
    // Background: non-blocking clone for large batches
    const result = await launchCloneJob({
      projectPath: targetDir,
      repositories: mapped,
    });
    if (!result.skippedPreFlight) {
      console.log(chalk.green(`   ✓ Clone job started in background (Job ID: ${result.job.id})`));
      console.log(chalk.cyan('   Check progress: specweave jobs'));
    }
    // umbrellaDiscovery stays null → config writes umbrella.enabled
    // with empty childRepos; clone-worker populates them on completion
  }
}
```

**Import changes**:
- Add: `import { launchCloneJob } from '../../core/background/job-launcher.js';`
- Add to init helpers import: `mapParsedReposToCloneOptions`, `runForegroundClone`, `FOREGROUND_CLONE_THRESHOLD`
- Remove from init helpers import: `cloneReposIntoWorkspace`
- `execFileNoThrowSync` stays — still used for `git init` / `git add` / `git commit` (lines 384-389)
- `scanUmbrellaRepos` stays imported — still used for `continueExisting` flows and non-clone paths

**Remove**: The `scanUmbrellaRepos(targetDir)` re-scan call at line 372 (inside the clone-repos branch only).

#### 3. `src/cli/helpers/init/index.ts` — Modify exports

- Add exports: `mapParsedReposToCloneOptions`, `runForegroundClone`, `FOREGROUND_CLONE_THRESHOLD`
- Remove export: `cloneReposIntoWorkspace`

#### 4. No changes to these files

- `src/core/background/job-launcher.ts` — `launchCloneJob()` already supports `foreground: true`
- `src/cli/workers/clone-worker.ts` — Background worker unchanged
- `src/cli/commands/get.ts` — Uses its own clone path, not affected
- `src/cli/helpers/init/github-repo-cloning.ts` — Already uses `launchCloneJob()`, not affected

### Config Timing (FR-003)

**Problem**: Background jobs update `config.json` asynchronously — init must ensure umbrella mode is enabled before the clone completes.

**Solution**: Already handled by existing init code (lines 434-440):
```typescript
} else if (!config.umbrella?.enabled) {
  config.umbrella = { enabled: true, projectName: finalProjectName, childRepos: [] };
}
```

When `umbrellaDiscovery` is null (background mode), init writes `umbrella.enabled: true` with empty `childRepos[]`. The clone-worker populates `childRepos` on completion (clone-worker.ts lines 264-310). No new code needed.

For foreground mode, `umbrellaDiscovery` is built from clone results (see init.ts changes above), so init writes the full config in one pass.

### Trade-off: Inline clone vs shared utility

**Considered**: Extracting `cloneRepository()` from `clone-worker.ts` into a shared module.

**Rejected**: The clone-worker is a standalone script designed for detached execution. Its `cloneRepository()` uses `spawn` with pipes for stderr capture — overkill for a simple foreground clone of 1-3 repos. The foreground handler uses `execFileNoThrow` (async, already in the codebase) for simplicity. Both approaches call `git clone` — no behavioral divergence.

### Trade-off: Threshold value

**3 repos** chosen because:
- 1-3 repos typically clone in < 30s (acceptable interactive delay)
- 4+ repos may take minutes (unacceptable for blocking init)
- Matches UX expectation: small workspace = instant, org-wide = background
- Named constant (`FOREGROUND_CLONE_THRESHOLD`) makes it easy to tune later

### Test Impact

Files requiring updates:
- `tests/unit/cli/helpers/init/repo-connect.test.ts` — Add tests for `mapParsedReposToCloneOptions`, `runForegroundClone`, `FOREGROUND_CLONE_THRESHOLD`; remove `cloneReposIntoWorkspace` tests
- `tests/unit/cli/commands/init.test.ts` — Mock `launchCloneJob` + `runForegroundClone` instead of `cloneReposIntoWorkspace`
- `tests/unit/cli/commands/init-multirepo.test.ts` — Update multi-repo clone assertions for new function signatures
- `tests/unit/cli/commands/init-config-validation.test.ts` — May need mock updates for changed imports
- `tests/unit/cli/commands/init-path-resolution.test.ts` — May reference old function name

### Risk Assessment

| Risk | Mitigation |
|------|------------|
| Foreground clone skips worker-level umbrella config write | Foreground handler builds `umbrellaDiscovery` from results; init writes config centrally |
| Breaking `specweave get` | No shared code modified — `get` has its own clone path |
| Job manager import in init | Already imports `LivingDocsUserInputs` from background types (line 52) — precedent exists |
| Test instability from async switch | Keep `vi.mock` on `launchCloneJob` and `execFileNoThrow` — no real git operations in tests |
