# Implementation Plan: External Integration Health Check & Smart Linking

## Overview

This increment wires together existing SpecWeave modules into a cohesive integration pipeline. No new services or external APIs are needed — the work is primarily integration and CLI wiring. The four user stories map to four independent integration points that can be implemented in parallel.

## Architecture

### Components Modified

1. **`src/cli/commands/sync-setup.ts`** — Add health check call after successful setup
2. **`src/cli/commands/sync-health.ts`** (NEW) — Standalone health check CLI command
3. **`src/core/config/types.ts`** — Add `includeExternalKey` to `GitConfig`
4. **`src/core/cicd/branch-utils.ts`** (NEW) — Branch name builder with external key support
5. **`src/sync/pr-linker.ts`** — Already complete, no changes needed
6. **PR creation flow** — Wire `linkPrToExternalTickets()` call after PR creation

### Components Reused (No Changes)

- `src/sync/integration-health-check.ts` — All health check functions
- `src/integrations/jira/jira-client.ts` → `addRemoteLink()`
- `plugins/specweave-ado/lib/ado-client.ts` → `addHyperlink()`
- `src/sync/pr-linker.ts` → `resolveExternalBranchPrefix()`, `linkPrToExternalTickets()`

### Data Flow

```
sync-setup completes → health check for configured provider → display results
                                                                    ↓
                                                        sync-health (on-demand)

PR creation → metadata.json external refs → pr-linker → JIRA addRemoteLink / ADO addHyperlink
                                                ↓
                                    branch-utils builds name with ticket key
```

## Technology Stack

- **Language**: TypeScript (ESM, `.js` extensions in imports)
- **Testing**: Vitest with `vi.hoisted()` + `vi.mock()` for ESM mocking
- **CLI**: Commander.js (existing CLI framework)

## Architecture Decisions

- **AD-1: Health checks after setup, not during** — Running health checks after `setupIssueTracker()` returns keeps the setup flow clean. If health checks fail, setup still succeeds (credentials are saved) but user gets immediate feedback about what to fix.
- **AD-2: `includeExternalKey` defaults to false** — Opt-in to avoid surprising existing users with changed branch names. Can be enabled per-project.
- **AD-3: Non-blocking PR linking** — Link failures are logged but never block PR creation or increment closure. External tool availability shouldn't gate the dev workflow.
- **AD-4: Reuse existing `resolveExternalBranchPrefix()`** — This function already extracts JIRA keys and ADO IDs from metadata. No need to duplicate logic.

## Implementation Phases

### Phase 1: Health Check Wiring (US-001, US-004)
- Wire health checks into sync-setup completion
- Create standalone sync-health CLI command with --json support
- Add tests

### Phase 2: Branch Naming (US-002)
- Extend GitConfig with `includeExternalKey`
- Create branch name builder utility
- Integrate with PR-based closure flow
- Add tests

### Phase 3: Auto PR Linking (US-003)
- Wire `linkPrToExternalTickets()` into PR creation flow
- Ensure non-blocking error handling
- Add tests

## Testing Strategy

- **Unit tests**: Each new function tested in isolation with mocked dependencies
- **Integration**: Verify CLI commands produce correct output and exit codes
- **Mocking**: All external API calls (JIRA, ADO, GitHub) mocked — no real API calls in tests
- **Coverage target**: 90% (per increment config)

## Technical Challenges

### Challenge 1: Finding the PR creation integration point
**Solution**: Locate where PR URLs are written to `metadata.json.prRefs` — that's where `linkPrToExternalTickets()` should be called
**Risk**: Low — the PR creation flow is well-defined in the codebase
