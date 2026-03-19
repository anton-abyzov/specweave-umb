# Implementation Plan: Cross-Process Rate Limit Coordination

## Overview

Add cross-process coordination for GitHub API rate limit. 4 new/modified modules, no architecture change to existing sync.

## Key Files

| File | Action | Purpose |
|------|--------|---------|
| `src/sync/github-rate-limit-budget.ts` | NEW | Shared rate-limit state file module |
| `src/sync/github-reconciler.ts` | MODIFY | Add file-based lock, check budget |
| `plugins/specweave/lib/integrations/github/github-client-v2.ts` | MODIFY | Check budget before every API call |
| `plugins/specweave/lib/integrations/github/label-cache.ts` | MODIFY | Persist to disk |
| `plugins/specweave/lib/integrations/github/github-feature-sync.ts` | MODIFY | Skip dup detection for linked issues |

## State Files

```
.specweave/state/
├── github-rate-limit.json    # {remaining, limit, resetAt, lastChecked}
├── reconciler.lock           # {pid, startedAt}
└── github-label-cache.json   # {repo: {labels: [...], cachedAt}}
```
