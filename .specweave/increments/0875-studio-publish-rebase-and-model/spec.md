---
id: 0875-studio-publish-rebase-and-model
title: >-
  Studio publish: auto-reconcile non-fast-forward pushes + show/use default
  model + subdir skillPath
status: completed
type: feature
priority: P1
repos:
  - repositories/anton-abyzov/vskill
requirementsSource: >-
  User-reported Skill Studio publish-drawer bugs (screenshots + explicit 'fix
  the publish button' direction). Direct bug-fix increment — see
  .specweave/state/interview-0875-studio-publish-rebase-and-model.json for
  coverage.
---

# Studio Publish: Rebase, Default Model, and Subdir skillPath

## Problem Statement

The Skill Studio (desktop) publish drawer had three user-reported failures when
publishing a skill to a Git remote:

1. **Non-fast-forward push** — when `origin/<branch>` had moved ahead, `git push`
   aborted with a raw `non-fast-forward` / `[rejected]` / `fetch first` error that
   was dumped into the error toast. The user was stuck with no recovery path.
2. **Generate-with-AI used the wrong model** — the "Generate with AI" commit-message
   button used the (possibly stale) config props instead of the studio's actually
   selected default model shown in the header picker, and never displayed which
   model was writing the message.
3. **Publish from the Edit tab failed for subdirectory skills** — publishing a skill
   that lives under `skills/<name>/` submitted with no `skillPath`, so the registry
   looked at the repo root and failed with "SKILL.md not found in the repository".

## Requirements Source

This is a direct bug-fix increment driven by user screenshots and explicit
"fix the publish button" direction. There was no upfront written spec; the
requirements are the three reproducible failures above. Coverage is documented in
`.specweave/state/interview-0875-studio-publish-rebase-and-model.json`.

## User Stories

### US-001: Auto-reconcile a non-fast-forward publish push

As a Skill Studio user publishing to a shared remote, when the remote has moved
ahead, I want the publish to transparently rebase my commit onto the latest remote
and retry the push, so a clean divergence resolves without me touching the terminal —
and when there is a real conflict, I want a clear, actionable message instead of a
raw git error.

**Acceptance Criteria:**

- [x] **AC-US1-01**: On a non-fast-forward push rejection (`non-fast-forward`,
  `[rejected]`, `fetch first`, or `Updates were rejected`), the publish handler runs
  `git pull --rebase --autostash origin <branch>` and retries `git push`. On a clean
  rebase the retried push succeeds and the response sets `reconciled: true`.
- [x] **AC-US1-02**: When the rebase conflicts, the handler collects the conflicted
  file paths (`git diff --name-only --diff-filter=U`, with a stdout-parse fallback),
  runs `git rebase --abort` (best-effort) to restore a clean tree, and returns
  HTTP 200 with `{ success: false, conflict: true, reason: "rebase_conflict",
  conflictedFiles, error }` listing the conflicted files.
- [x] **AC-US1-03**: The PublishDrawer surfaces the conflict response inline
  (listing the conflicted files) rather than via the generic error toast, and shows
  "(reconciled with remote)" in the success message when `reconciled` is set. The
  detached-HEAD edge case (branch == "HEAD") is skipped — no rebase attempted.

### US-002: Generate-with-AI uses and displays the studio's selected default model

As a Skill Studio user, when I click "Generate with AI" for a commit message, I want
it to use the same default model I selected in the header picker, and to show me which
model is writing the message, so the result matches my expectation.

**Acceptance Criteria:**

- [x] **AC-US2-01**: PublishDrawer resolves the active model/provider from
  `useAgentCatalog` (`catalog.activeAgent` + `catalog.activeModel`, with the
  human-readable name from the active agent's matching model `displayName`) — the
  SAME source as the header `AgentModelPicker` — and passes it to
  `api.gitCommitMessage`, preferring it over the possibly-stale config props.
- [x] **AC-US2-02**: When the catalog has not loaded yet, PublishDrawer falls back to
  the `provider`/`model` config props so generation never breaks.
- [x] **AC-US2-03**: In AI mode, PublishDrawer displays which model writes the message
  ("Using <displayName>", `data-testid="publish-ai-model"`).

### US-003: Publish from the Edit tab sends skillPath for subdir skills

As a Skill Studio user editing a skill that lives in a subdirectory, when I publish
from the Edit tab, I want the repo-relative `SKILL.md` path forwarded so the registry
finds my skill instead of failing with "SKILL.md not found in the repository".

**Acceptance Criteria:**

- [x] **AC-US3-01**: EditorPanel resolves the active skill's repo-relative `skillPath`
  (e.g. `skills/greet-anton/SKILL.md`) from `useStudio().state.skills` (matching on
  `plugin` + `skill`) — the same source RightPanel/DetailHeader use — and forwards it
  to `PublishButton` via the `skillPath` prop.
- [x] **AC-US3-02**: When the active skill has no resolvable `skillPath` (e.g. a
  root-level skill or not found in studio state), `skillPath` is `undefined` and the
  existing root-level publish behavior is preserved (no regression).

## Out of Scope

- Interactive conflict resolution UI (manual pull/resolve is the documented path).
- Changes to the registry submit/website flow itself.
- Model selection logic in the header picker (reused as-is, not modified).
