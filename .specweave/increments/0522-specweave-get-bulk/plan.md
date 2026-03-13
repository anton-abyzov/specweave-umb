# Plan: `specweave get` Bulk Cloning

## Architecture

Wire existing infrastructure into `specweave get`. No new systems — only integration.

## Files Changed

| File | Change |
|---|---|
| `src/cli/helpers/init/github-repo-cloning.ts` | Add `export` to `fetchGitHubRepos()` |
| `src/cli/helpers/get/bulk-get.ts` | NEW — auth, source parsing, repo list builder |
| `src/cli/commands/get.ts` | Bulk detection at top + `_handleBulkGet()` |
| `bin/specweave.js` | Add 5 new options to `get` command |
| `plugins/specweave/skills/get/SKILL.md` | Add bulk examples |

## Existing Infrastructure Reused (unchanged)

- `src/core/background/job-launcher.ts` → `launchCloneJob()`
- `src/cli/workers/clone-worker.ts` → background sequential clone
- `src/cli/helpers/selection-strategy.ts` → `matchByGlob()`, `matchByRegex()`
- `src/cli/helpers/init/types.ts` → `REPO_FETCH_LIMITS`

## Bulk Detection Logic

In `parseBulkSource(source, { all, pattern })`:
- `"org/*"` → bulk, org=org, pattern=null
- `"org/prefix-*"` → bulk, org=org, pattern=prefix-*
- `"org"` + `--all` → bulk, org=org, pattern=null
- `"org"` + `--all` + `--pattern "svc-*"` → bulk, org=org, pattern=svc-*
- `"org/repo"` (no glob, no `--all`) → null (single-repo path)

## Flow

```
specweave get "acme-corp/service-*"
→ parseBulkSource() → { org, pattern }
→ getAuthToken() → GH_TOKEN || gh auth token
→ fetchGitHubRepos(org, token, limit)
→ matchByGlob(repos, pattern) + filter archived/forks
→ launchCloneJob({ projectPath, repositories })
→ "Found N repos. Job started. Monitor: specweave jobs"
```

## Testing Strategy

- TDD: tests first, then implementation
- `tests/unit/cli/helpers/get/bulk-get.test.ts` — unit tests for all 3 helpers
- `tests/unit/cli/commands/get-bulk.test.ts` — integration for bulk + regression for single-repo
