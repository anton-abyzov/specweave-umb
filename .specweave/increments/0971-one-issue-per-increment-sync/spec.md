# 0971 Tracker sync: one issue per increment from the ledger

## Problem

The 3.0 docs say `specweave sync push` keeps one GitHub issue, Jira issue or Azure DevOps work item per increment. The code still runs the 2.x model: it reads user stories and `spec.md` checkboxes, never `ledger.jsonl`, so a 3.0 increment's issue shows "_No user stories defined_", no AC progress and a link to a `tasks.md` that doesn't exist. `specweave complete` can also update trackers through the living-docs path without any close flag. About 22,400 lines carry this, with two client layers for Jira and ADO. Assessment: `~/Projects/github/studio-research-notes/tracker-integrations-2026-10-20/assessment.md`.

Trackers are a secondary feature (user decision, October 20, 2026). Start this only when someone uses tracker sync on 3.0 increments, except T-01, which fixes a rule violation.

## Scope

In: the issue body and state built from `spec.md` and `ledger.jsonl`; idempotent push for GitHub, Jira and ADO; a real `--dry-run`; migration of per-user-story links; deleting per-story sync, the ADO hierarchy, frontmatter link writes, sync push's living-docs step and dead hook code; Jira/ADO end-to-end tests with mocked HTTP; docs that match.
Out: two-way sync (pull stays report-only, `--create-increments` unchanged); new providers; any landing-page promotion of trackers; running against real trackers in tests or CI.

## Acceptance Criteria

- [ ] AC-01: `specweave complete` calls no tracker unless a `hooks.post_increment_done.close_*` flag is set. A test with a legacy spec (user stories, `externalLinks`, `livingDocs: 'onDone'`) asserts zero tracker client calls.
- [ ] AC-02: `sync push` builds the issue from `spec.md` and `ledger.jsonl`: title, summary, AC checklist with each AC's state folded from the ledger, and a link to `spec.md`; no `tasks.md` link and no user-story section. Works for a 3.0 increment with no user stories.
- [ ] AC-03: Re-running push updates the same issue or work item on GitHub, Jira and ADO, never a duplicate. Tracker state changes only on push or the close-on-complete flag.
- [ ] AC-04: `sync push --dry-run` prints, per provider, the title, a body diff and the state change, and makes no mutating call (asserted in tests).
- [ ] AC-05: An increment with per-story links (`externalLinks`, user-story `external_tools`, Jira keys, ADO IDs) migrates to one increment-level link without creating an issue: keep the increment link if present, else adopt the first story link. The next real push leaves one pointer comment on each other per-story issue. Fixtures cover every link shape.
- [ ] AC-06: One client per provider. Per-story sync, frontmatter link writes, the ADO epic/feature hierarchy, sync push's living-docs step and `LifecycleHookDispatcher.onTaskCompleted` are deleted; net deletion is at least 3,000 lines.
- [ ] AC-07: Jira and ADO each have a push, re-push and close suite with mocked HTTP comparable to GitHub's; `npm run test:unit` passes; `docs-site/docs/guides/github-sync.md`, `jira-ado-sync.md` and `docs-site/docs/reference/sync-cli.md` match the behavior.

## Approach

Fold AC state with the existing ledger reader in `src/core/tasks/`, render one body template shared by all providers, and keep provider differences to create, update, close and status mapping (`src/sync/status-mapper.ts`). Remove the living-docs call from `src/cli/commands/sync-progress.ts` and the `syncToExternalTools` call from the onDone living-docs path. Keep `src/integrations/{jira,ado}` or the plugin-lib copies, whichever the remaining callers use, and delete the other.

## Decisions

### Defaulted

- D-01: Pull stays report-only; this increment does not add two-way sync.
- D-02: Per-story issues are never closed or edited by the migration beyond one pointer comment.
- D-03: Tests use mocked HTTP only; no `specweave sync push` against real trackers.

## Open questions

- Keep the per-story pointer comment, or migrate silently? Recommended: one comment, so people watching those issues find the increment issue.

## Tasks

### T-01 Stop the complete-time tracker path
- AC: AC-01 | Files: src/core/hooks/LifecycleHookDispatcher.ts, src/core/living-docs/living-docs-sync.ts | Test: tests/unit/core/hooks (new legacy-spec case)

### T-02 Ledger-driven issue title and body
- AC: AC-02 | Files: src/sync/external-issue-auto-creator.ts, src/core/ac-progress-sync.ts | Test: tests/unit/sync body snapshot for a 3.0 increment

### T-03 Idempotent push per provider
- AC: AC-03 | Files: src/sync/, src/cli/commands/sync-progress.ts | Test: tests/unit/sync re-push cases for GitHub, Jira, ADO

### T-04 Real dry-run diff
- AC: AC-04 | Files: src/cli/commands/sync-progress.ts | Test: tests/unit/sync dry-run asserts no mutating calls

### T-05 Per-story link migration
- AC: AC-05 | Files: src/sync/pr-linker.ts, src/sync/frontmatter-updater.ts, new migration module | Test: fixtures for every link shape

### T-06 Delete per-story code and duplicate clients
- AC: AC-06 | Files: src/sync/, src/integrations/, plugins/specweave/lib/integrations/ | Test: npm run test:unit, npx tsc --noEmit -p .

### T-07 Jira and ADO end-to-end suites and docs
- AC: AC-07 | Files: tests/unit/sync, docs-site/docs/guides/, docs-site/docs/reference/sync-cli.md | Test: npm run test:unit, cd docs-site && npm run build

### T-08 Verify and close 0971
- AC: all | Files: none | Test: specweave verify, fresh-context review, specweave complete
