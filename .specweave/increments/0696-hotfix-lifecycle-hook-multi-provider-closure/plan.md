# Implementation Plan: Hotfix LifecycleHookDispatcher multi-provider closure

**Increment**: 0696-hotfix-lifecycle-hook-multi-provider-closure
**Type**: hotfix | **Priority**: P1 | **Project**: specweave

---

## 1. Scope

Targeted, minimum-diff fix across exactly two production files plus tests:

1. `repositories/anton-abyzov/specweave/src/sync/sync-coordinator.ts`
   - Add `externalLinks.jira.epicKey` (and `externalLinks.ado.workItemId`) as fallback key sources in `closeJiraIssuesForUserStories` / `closeAdoWorkItemsForUserStories`.
   - Propagate per-US errors into `result.errors` (stop swallowing at the per-US catch block).
   - Emit a clear warning line when a provider is enabled but no key can be resolved.

2. `repositories/anton-abyzov/specweave/src/core/hooks/LifecycleHookDispatcher.ts`
   - Forward the full `SyncResult.errors[]` from `syncIncrementClosure()` into `result.syncErrors` (currently only outer throws make it).
   - Ensure `logError('onIncrementDone:closure', ...)` writes the complete error (provider + increment id) to `.specweave/logs/hooks.log`; the writer must be exception-safe.

No refactor of control flow. No renames. No config-shape changes. Backwards compatible.

---

## 2. Architecture

### 2.1 Current flow (broken for JIRA-epic-only increments)

```
CLI: specweave complete <id> --yes
  → IncrementCompleter.complete()
    → LifecycleHookDispatcher.onIncrementDone(incrementId, projectRoot)
      Step 1: LivingDocsSync.syncIncrement(id)
        → chains to GitHubFeatureSync (closes GH issues + creates feature spec)
      Step 2: SyncCoordinator.syncIncrementClosure()
        → gate checks (canUpdateExternalItems, autoSyncOnCompletion)
        → if githubEnabled: SKIP (handled by step 1)
        → if jiraEnabled:  closeJiraIssuesForUserStories(config)
            loops user stories, reads us.external_tools.jira.key
            ── BUG ── never reads externalLinks.jira.epicKey from increment metadata
            returns 0 silently, logs nothing user-visible
        → if adoEnabled:   closeAdoWorkItemsForUserStories(config)
            same shape ── same silent-zero bug for ADO-epic-only increments
      Step 3: drain retry queue
```

### 2.2 Fixed flow (minimal change)

```
closeJiraIssuesForUserStories(config):
  userStories = loadUserStoriesForIncrement()
  keys = collectJiraKeys(userStories, metadata)          ← refactor key resolution
    sources, in order:
      1. per-US  us.external_tools.jira.key
      2. per-US  us.external_id
      3. metadata.jira.issue
      4. metadata.externalLinks.jira.epicKey            ← NEW fallback
    dedup keys
  if keys.length === 0 AND jiraEnabled:
    logger.warn('⚠️  JIRA enabled but no issue key resolvable for increment — skipping closure')
    result.errors.push(WARN_NO_KEY_MSG)                 ← NEW: surface the gap
    return 0
  for key in keys:
    try { transition to targetStatus; closedCount++ }
    catch (err) {
      result.errors.push(`JIRA ${key}: ${err.message}`) ← NEW: propagate per-US error
      logger.error(...)
    }
  return closedCount
```

Symmetric change for ADO via `externalLinks.ado.workItemId`.

### 2.3 Dispatcher wiring (forward errors up)

```
LifecycleHookDispatcher.onIncrementDone.syncClosure():
  try {
    const closureResult = await coordinator.syncIncrementClosure()
    result.syncSuccess.push('Closure sync completed')
    if (closureResult.errors?.length) {                  ← NEW
      result.syncErrors.push(...closureResult.errors)
      LifecycleHookDispatcher.logError(
        'onIncrementDone:closure',
        new AggregateError(closureResult.errors, 'Provider closure errors')
      )
    }
  } catch (error) {
    result.syncErrors.push(`Closure sync failed: ${error.message}`)
    LifecycleHookDispatcher.logError('onIncrementDone:closure', error)
  }
```

---

## 3. Key Design Decisions

### 3.1 Where does the epic-key fallback live?

**Decision**: Inside `SyncCoordinator.closeJiraIssuesForUserStories` / `closeAdoWorkItemsForUserStories`, NOT in the dispatcher.

**Rationale**: Keeps the dispatcher dumb and keeps provider-specific lookup in one place. Makes unit testing straightforward. Matches the existing pattern of `metadataJiraKey` fallback already present at `sync-coordinator.ts:171-186`.

### 3.2 One key or many?

**Decision**: Collect ALL candidate keys (from all four sources), dedup, iterate.

**Rationale**: If a user story has its own JIRA key AND the increment has an `epicKey`, we want to close the story AND the epic. Dedup avoids double-closing when they happen to reference the same key.

### 3.3 Warning vs hard error on unresolvable keys

**Decision**: Warning line in stdout + entry in `result.errors`. Hook still returns success overall (other providers may have succeeded).

**Rationale**: A misconfigured increment shouldn't block closure of the other providers. CI consumers can fail the build by asserting `result.syncErrors.length === 0` if desired.

### 3.4 Don't rename the config flag

**Decision**: Keep `close_github_issue`, `close_external_issue`, `close_jira_issue` as-is. They already OR together correctly.

**Rationale**: Renaming would break existing user configs. Documentation update is a follow-up.

---

## 4. Test Strategy

- **Unit tests** (`src/sync/__tests__/sync-coordinator.closure.test.ts`):
  - `closeJiraIssuesForUserStories falls back to externalLinks.jira.epicKey when no US/metadata key present`
  - `closeJiraIssuesForUserStories pushes per-US errors into result.errors`
  - `closeJiraIssuesForUserStories skips already-Done issues idempotently`
  - `closeAdoWorkItemsForUserStories falls back to externalLinks.ado.workItemId`
  - `syncIncrementClosure returns errors from both providers even when one throws`

- **Integration tests** (`src/core/hooks/__tests__/lifecycle-hook-dispatcher.closure.test.ts`):
  - `onIncrementDone invokes jiraClient.updateIssue and adoClient.updateWorkItem once each when both configured`
  - `onIncrementDone forwards closureResult.errors into result.syncErrors`
  - `onIncrementDone writes provider errors to .specweave/logs/hooks.log`
  - `onIncrementDone survives JIRA failure and still closes ADO`
  - `onIncrementDone reproduces SWE2E-861 scenario: externalLinks.jira.epicKey only, closure fires`

- **Strict TDD**: All new tests MUST be red on HEAD before any production code change (AC-US5-01). Verified by committing test file first and running `npx vitest run` in `repositories/anton-abyzov/specweave/` — build must fail.

- **Manual smoke test** (post-merge, pre-close):
  1. Close `0673-submission-dedup-cleanup-at-scale` (or whatever is next to close) with umbrella config as-is.
  2. Assert JIRA epic and ADO work item both auto-close from a single `specweave complete` run, with stdout lines matching AC-US1-04 and AC-US2-03.

---

## 5. Risks

| Risk | Mitigation |
|------|------------|
| Epic fallback closes the wrong key for increments where `externalLinks.jira.epicKey` is stale | Pre-check: `jiraClient.getIssue(key)` returns 404 → log and skip, don't throw. Matches existing behavior at `sync-coordinator.ts:199-202`. |
| Per-US error propagation breaks an existing test that relied on silent failure | Grep for `result.errors` assertions in `sync-coordinator.*.test.ts` and update expectations deliberately. Failing tests from this change are expected signal. |
| `.specweave/logs/hooks.log` writer throws on locked-file / read-only FS | Wrap log writer in try/catch with stderr fallback (AC-US3-03 requires it). |
| Dedup logic collides with case-insensitive JIRA keys | JIRA keys are case-sensitive by convention; normalize via `.trim()` only, not `.toLowerCase()`. |

---

## 6. Files Touched (Final List)

**Production**
- `repositories/anton-abyzov/specweave/src/sync/sync-coordinator.ts` (~40 lines changed / added)
- `repositories/anton-abyzov/specweave/src/core/hooks/LifecycleHookDispatcher.ts` (~15 lines added)

**Tests (new)**
- `repositories/anton-abyzov/specweave/src/sync/__tests__/sync-coordinator.closure.test.ts`
- `repositories/anton-abyzov/specweave/src/core/hooks/__tests__/lifecycle-hook-dispatcher.closure.test.ts`

**Docs**
- Update code comment block at `LifecycleHookDispatcher.ts:252-257` to reflect the corrected behavior.

---

## 7. Release

- Patch bump on `specweave` CLI (e.g., `v1.0.xxx` → `v1.0.xxx+1`).
- Changelog entry:
  > Hotfix: `specweave complete` now reliably closes JIRA epics and ADO work items referenced only via `externalLinks.*`, not only via per-user-story frontmatter. Per-provider closure errors now surface in `result.syncErrors` and `.specweave/logs/hooks.log`.
- No migration required.
