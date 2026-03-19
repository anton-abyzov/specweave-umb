---
increment: 0612-reduce-github-api-calls
---

# Architecture: Reduce GitHub API Calls (Phase 1)

## Approach

Six surgical fixes to the existing GitHub sync pipeline. No new architecture — session caches, guard inversions, one GraphQL combined fetch, and shared state between sync passes.

## Files

| File | Changes |
|------|---------|
| `plugins/specweave/lib/integrations/github/duplicate-detector.ts` | Label cache, Phase 3 guard inversion |
| `plugins/specweave/lib/integrations/github/github-feature-sync.ts` | Milestone cache, label cache, merged fetch |
| `plugins/specweave/lib/integrations/github/github-client-v2.ts` | `getIssueWithLastComment()`, `skipDuplicateCheck` param |
| `src/cli/commands/sync-progress.ts` | AC sync dedup — share issue state |
| Test files for each source file |

## Key Decisions

1. **Session caches (not persistent)** — simple Maps cleared on process exit. No file I/O, no corruption risk.
2. **GraphQL for reads only** — `getIssueWithLastComment()` uses `gh api graphql`. Writes stay as REST via `gh` CLI.
3. **Phase 3 opt-in** — inverted guard from skip-if-set to run-if-set. Single-process syncs don't need verification.
4. **Shared label cache as exported utility** — both `duplicate-detector.ts` and `github-feature-sync.ts` use the same module-level cache.
