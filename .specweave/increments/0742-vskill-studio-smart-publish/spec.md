---
increment: 0742-vskill-studio-smart-publish
title: "vskill Studio Smart Publish (MVP): dirty-state pill + AI-commit publish drawer"
type: feature
priority: P2
status: planned
created: 2026-04-26
structure: user-stories
test_mode: TDD
coverage_target: 90
---

# Feature: vskill Studio Smart Publish (MVP): dirty-state pill + AI-commit publish drawer

## Overview

The vskill studio's Save button persists `SKILL.md` edits to disk but provides no UI signal that changes are uncommitted, and no path to share them via git/GitHub. Authors must drop to the terminal to commit and push, and the friction is even worse when the folder isn't on GitHub yet.

This increment adds three things:

1. A **dirty-state status pill** on the skill header (amber `● uncommitted`, blue `↑N` ahead) so authors never close the studio thinking work was shared when it was only saved to disk.
2. A **Publish** button next to Save that opens a drawer with a scoped diff preview and an AI-generated commit message produced by the user's currently-selected provider/model.
3. **Two publish paths** that handle the common cases in one click each:
   - **Path A** — repo with remote: `git add <skillDir>` → `git commit` → `git push`.
   - **Path B** — repo without remote: if `gh` CLI is installed and authenticated, `gh repo create … --source=. --push`; otherwise open `github.com/new` prefilled in a new tab while the drawer polls `api.github.com` for repo creation, then auto-attaches the remote and pushes.

Outcome: edit → review → ship happens inside the studio, without leaving the app.

## User Stories

### US-001: Dirty-state surfacing on the skill header (P1)
**Project**: vskill

**As a** skill author editing in vskill studio
**I want** a visible signal on the skill header that my saved-but-uncommitted edits haven't been published
**So that** I never close the studio thinking my work is shared when it's only on disk

**Acceptance Criteria**:
- [ ] **AC-US1-01**: A `GitStatusPill` component is slotted next to `VersionBadge` in `DetailHeader.tsx:151-178`, using inline-style design tokens that match `VersionBadge.tsx:27-60` (no Tailwind, no new design system).
- [ ] **AC-US1-02**: When `gitStatus.isRepo && gitStatus.dirty` is true, the pill renders an amber `● uncommitted` variant; when `gitStatus.isRepo && !dirty && ahead > 0`, it renders a blue `↑N` variant (where N is the ahead count); when `gitStatus.isRepo && !dirty && ahead === 0`, the pill is hidden; when `!gitStatus.isRepo` (folder is not a git repo), the pill is hidden.
- [ ] **AC-US1-03**: Hovering the pill shows a tooltip with the changed-file count and the current branch name (e.g. `2 files changed on main`); the tooltip text updates whenever `gitStatus` refreshes.
- [ ] **AC-US1-04**: After every successful `saveContent()` in `WorkspaceContext.tsx:223`, `useGitStatus` refetches `GET /api/skills/:plugin/:skill/git-status` so the pill flips to amber within one render cycle of the save completing — no polling, refresh is event-driven via the `CONTENT_SAVED` event.

---

### US-002: One-click Publish for repos with a remote (P1)
**Project**: vskill

**As a** skill author with a folder that's a git repo and has a remote
**I want** to commit and push from the studio without leaving the app
**So that** the round-trip from edit to shared state is one button instead of a terminal context switch

**Acceptance Criteria**:
- [ ] **AC-US2-01**: A `Publish` button is rendered next to `Save` in `EditorPanel.tsx:370`, visible when `gitStatus.isRepo && (dirty || ahead > 0 || !hasRemote)`. When `!gitStatus.isRepo`, the button is disabled and shows a tooltip explaining `git init` is coming in a follow-up increment.
- [ ] **AC-US2-02**: Clicking `Publish` opens `PublishDrawer` (420px right, `createPortal`, esc-close — mirrors `OpsDrawer.tsx`). The drawer header shows the repo root path, the current branch, and the resolved remote URL (e.g. `Repo: ~/Projects/TestLab • branch: main • origin → github.com/anton/testlab`).
- [ ] **AC-US2-03**: The drawer renders a diff preview produced by `POST /api/skills/:plugin/:skill/git-diff`, which executes `git diff -- <skillDir>`. The preview includes ONLY changes inside the skill directory — unrelated tracked changes elsewhere in the parent repo MUST NOT appear, even if the parent repo is dirty.
- [ ] **AC-US2-04**: On drawer open, the drawer auto-streams an AI commit message via `POST /api/skills/:plugin/:skill/git-commit-message?sse`, using the `{provider, model}` shape from `SkillImprovePanel.tsx:72` with whatever `useAgentCatalog()` reports as the active selection from the top-right `AgentModelPicker`. The message is one line, ≤72 chars, no body, no emoji, no AI/Claude/Anthropic references.
- [ ] **AC-US2-05**: The streamed message lands in an editable textarea; the user can edit it freely, and a `Regenerate` button restarts the SSE stream with the same provider/model. When `useAgentCatalog` switches the active model mid-drawer, the next `Regenerate` uses the new selection.
- [ ] **AC-US2-06**: Clicking `Commit & Push` calls `POST /api/skills/:plugin/:skill/git-publish?sse` with `{message, mode: 'push'}`, which runs `git add <skillDir>` → `git commit -m <message>` → `git push` (each step via `child_process.execFile`, no shell). On success, a `studio:toast` CustomEvent fires naming the commit short-SHA and remote branch, the drawer closes, the dirty-state pill clears, and `useGitStatus` refetches.

---

### US-003: One-click Publish to GitHub for repos without a remote (P1)
**Project**: vskill

**As a** skill author with a folder that's a git repo but has never been pushed to GitHub
**I want** a "Create on GitHub" button that creates the repo, attaches the remote, and pushes for me
**So that** I don't have to memorize `git remote add` syntax or hunt for the right fields on the GitHub new-repo form

**Acceptance Criteria**:
- [ ] **AC-US3-01**: When `gitStatus.isRepo && !hasRemote`, the drawer's primary button reads `Create on GitHub & Push` (gh available + authenticated) or `Create on GitHub` (gh missing or unauthenticated). `gh` availability and auth state come from `GET /api/skills/:plugin/:skill/git-status` (the response embeds `gh: {available, authenticated, user}` produced by `gh-detect.ts` running `gh auth status --show-token=false` — the token MUST NEVER appear in logs, response payloads, or error messages).
- [ ] **AC-US3-02**: When `gh` is available and authenticated, clicking `Create on GitHub & Push` calls `POST /git-publish?sse` with `mode: 'create-via-gh'`, `visibility: 'public'|'private'` (drawer radio, default public), and the AI-generated message. The server runs `gh repo create <skill-name> --<visibility> --source=<repoRoot> --push --description="<frontmatter description, ≤120 chars>"` via `execFile`. On success, the toast names the new repo URL, the drawer closes, the pill clears, and `gitStatus.hasRemote` flips to true.
- [ ] **AC-US3-03**: When `gh` is missing or unauthenticated, clicking `Create on GitHub` opens `https://github.com/new?name=<urlencoded skill folder name>&description=<urlencoded frontmatter description>&visibility=<public|private>` in a new browser tab. Simultaneously, the drawer begins polling `GET https://api.github.com/repos/<owner>/<skill-name>` every 2 seconds for up to 60 seconds (≤30 requests, well under the 60/hr unauthenticated rate limit). `<owner>` is derived from `gh auth status` if `gh` is installed-but-unauthenticated; otherwise the drawer shows an `Owner` text input the user fills before the poll starts.
- [ ] **AC-US3-04**: When the poll receives a 200 response within 60 seconds, the drawer immediately calls `POST /git-publish?sse` with `mode: 'attach-remote-and-push'` and `remoteUrl: 'https://github.com/<owner>/<name>.git'`. The server runs `git remote add origin <url>` → `git push -u origin <branch>` via `execFile`. On success, the toast names the new repo URL, the drawer closes, and the pill clears.
- [ ] **AC-US3-05**: When the poll exceeds 60 seconds without a 200 response, the drawer transitions to a fallback state showing a `Paste your repo URL` text input with a `Push` button. Submitting the URL triggers the same `mode: 'attach-remote-and-push'` server flow as AC-US3-04. The user can also click `Cancel` to abort without leaving the studio in an inconsistent state.

## Non-Functional Requirements

### NFR-001: Path safety
All skill paths MUST be resolved through the existing `resolveSkillDir` + `assertContained` guard in `skill-resolver.ts:15`. New routes MUST NOT accept raw filesystem paths from the client.

### NFR-002: Subprocess safety
All git and `gh` invocations MUST use `child_process.execFile` with array arguments — never `exec`, never shell strings, never user-supplied arguments interpolated into a command string.

### NFR-003: Commit scope
`git add` MUST always be scoped to `<skillDir>` (e.g. `git add -- <skillDir>`). Use of `git add -A`, `git add .`, or any unscoped form is forbidden — parent-repo changes outside the skill directory MUST NEVER be committed by this feature.

### NFR-004: Diff scope
`git diff` MUST always be scoped via `git diff -- <skillDir>` so that the AI prompt and drawer preview see only the skill's own changes, not unrelated parent-repo work.

### NFR-005: Token hygiene
The `gh-detect` helper MUST always pass `--show-token=false` to `gh auth status`. The detected username MAY be returned to the client; the OAuth token or any auth header MUST NEVER be logged, returned in API responses, or included in error payloads.

### NFR-006: URL parameter encoding
The skill name and frontmatter description used to build `https://github.com/new?...` MUST be URL-encoded via `encodeURIComponent`. Frontmatter description is truncated to ≤120 chars before encoding.

### NFR-007: Test coverage
Unit ≥95%, integration ≥90%, E2E covers 100% of AC scenarios across all three publish modes (`push`, `create-via-gh`, `attach-remote-and-push` including the 60s timeout fallback).

## Success Criteria

- A skill author can edit `SKILL.md` in the studio and see an amber dirty-state pill on the header within one render cycle of clicking Save.
- For a repo with a remote, clicking `Publish` → `Commit & Push` lands the change on the remote in one drawer interaction with an AI-generated commit message.
- For a repo without a remote and `gh` authenticated, clicking `Create on GitHub & Push` creates the GitHub repo, attaches the remote, and pushes in one drawer interaction.
- For a repo without a remote and no `gh`, clicking `Create on GitHub` prefills the GitHub form, polls for creation, and auto-attaches+pushes — the user clicks once in the studio and once on GitHub.
- Across all paths: parent-repo changes outside the skill directory are never swept into the commit, the `gh` token never leaves the server, and the dirty-state pill clears after a successful publish.

## Out of Scope (deferred to follow-up increments)

- `git init` for non-repo folders (current behavior: Publish disabled with explanatory tooltip).
- Upstream-drift indicator (`↓N` arrow) and pull action.
- Version-bump detection → tag and GitHub release creation.
- Symlinked / Copied install-method warnings on the drawer.
- Background `git fetch` for drift awareness.
- OAuth-based GitHub authentication (the feature relies on the user's existing `gh` auth or browser tab today).

## Dependencies

- Increment `0670-skill-builder-universal` MUST close before this increment activates (this increment is queued at `status: planned`).
- Reuses existing modules — does not require new dependencies:
  - `src/eval-server/skill-resolver.ts:15` — `resolveSkillDir` + `assertContained`
  - `src/eval-server/improve-routes.ts:21` — provider/model SSE pattern
  - `src/eval-ui/src/components/OpsDrawer.tsx` — drawer skeleton
  - `src/eval-ui/src/components/VersionBadge.tsx:27-60` — badge style tokens
  - `src/eval-ui/src/hooks/useAgentCatalog.ts` — active provider/model selection
  - `src/eval-ui/src/App.tsx:240-254` + `studio:toast` CustomEvent — toast bridge
- External CLIs: `git` (required), `gh` (optional — feature degrades gracefully when missing).
