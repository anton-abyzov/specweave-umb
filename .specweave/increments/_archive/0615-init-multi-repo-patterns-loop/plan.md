# Implementation Plan: Init Multi-Repo Patterns and Add-More Loop

## Overview

Modify 2 files in the specweave CLI to wire existing `get` command infrastructure into the `init` flow. No new dependencies or architectural changes — pure reuse of existing functions.

## Architecture

### Approach: Reuse `bulk-get.ts` in `repo-connect.ts`

The `specweave get` command already has `parseBulkSource()` for detecting glob patterns and `buildBulkRepoList()` for resolving them against GitHub API. We import these into `repo-connect.ts` and add a loop wrapper.

### Components Modified

1. **`repo-connect.ts`** — Add `promptRepoUrlsLoop()` function that:
   - Wraps the existing input prompt in a do-while loop
   - Parses each token: `parseBulkSource()` for bulk detection, `parseRepoInput()` for individual repos
   - Dispatches bulk tokens to `buildBulkRepoList()` → `launchCloneJob()` (background)
   - Dispatches individual repos to `runForegroundClone()` (≤3) or `launchCloneJob()` (>3)
   - Shows "Do you want to add more?" confirm after each round
   - Returns cumulative results + job IDs

2. **`init.ts`** — Replace the `promptRepoUrls()` + inline clone block with a single `promptRepoUrlsLoop()` call

### Data Flow

```
User input: "org-a/* my-org/my-repo org-b/svc-*"
  │
  ├── Token "org-a/*" → parseBulkSource() → BulkSource{org:"org-a", pattern:null}
  │     → getAuthToken() → buildBulkRepoList("org-a", token, null) → BulkRepoEntry[]
  │     → launchCloneJob(entries) → background job
  │
  ├── Token "my-org/my-repo" → parseBulkSource() → null (not bulk)
  │     → parseRepoInput() → ParsedRepo
  │     → mapParsedReposToCloneOptions() → runForegroundClone()
  │
  └── Token "org-b/svc-*" → parseBulkSource() → BulkSource{org:"org-b", pattern:"svc-*"}
        → getAuthToken() → buildBulkRepoList("org-b", token, "svc-*") → BulkRepoEntry[]
        → launchCloneJob(entries) → background job
```

## Technology Stack

- **Existing**: TypeScript, @inquirer/prompts (confirm), minimatch (via selection-strategy.ts)
- **No new dependencies**

## Testing Strategy

- Unit tests with mocked inquirer prompts and mocked GitHub API calls
- Test files: `src/cli/helpers/init/__tests__/repo-connect.test.ts`
- Coverage: loop behavior, bulk detection, mixed input routing, i18n strings
