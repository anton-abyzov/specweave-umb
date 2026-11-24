---
id: 0875-studio-publish-rebase-and-model
---

# Plan: Studio Publish — Rebase, Default Model, Subdir skillPath

## Approach

Three independent, low-blast-radius bug fixes in `repositories/anton-abyzov/vskill`,
each TDD (RED → GREEN) with focused tests, no shared state between them.

### WS1 — Non-fast-forward auto-reconcile (server)
`src/eval-server/git-routes.ts` · `makePostGitPublishHandler`:
- Detect non-fast-forward rejection (`isNonFastForward`, regex over stderr+stdout).
- `git pull --rebase --autostash origin <branch>` then retry `git push`; set
  `reconciled: true` on clean success.
- On rebase conflict: collect conflicted paths (`git diff --diff-filter=U`, with
  `parseConflictFilesFromPull` fallback), `git rebase --abort` (best-effort), return
  structured 200 conflict JSON. Skip detached HEAD.

### WS2 — Active default model (UI)
`src/eval-ui/src/components/PublishDrawer.tsx` + `api.ts`:
- Resolve active provider/model from `useAgentCatalog` (same source as the header
  `AgentModelPicker`), prefer it over config props for `gitCommitMessage`, fall back
  to props pre-load. Display "Using <displayName>" (`data-testid=publish-ai-model`)
  in AI mode. Surface conflict response inline; append "(reconciled with remote)".

### WS3 — Subdir skillPath (UI)
`src/eval-ui/src/pages/workspace/EditorPanel.tsx`:
- Resolve the active skill's `skillPath` from `useStudio().state.skills` and forward
  to `PublishButton`; `undefined` for root-level/not-found preserves existing behavior.

## Testing

- Server: `src/eval-server/__tests__/git-routes.test.ts` (17 tests).
- UI: `PublishDrawerActiveModel.test.tsx` (4) + `EditorPanel.publishSkillPath.test.tsx` (4).
- All green; builds clean. Released as desktop 1.0.58 + 1.0.59.

## Rollout

Committed (`c941e4b`, `7e281c1`/`680e996`), pushed, released via signed/notarized DMGs;
auto-update manifest live at `verified-skill.com/desktop/latest.json` = 1.0.59.
