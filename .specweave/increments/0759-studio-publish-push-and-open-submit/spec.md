---
increment: 0759-studio-publish-push-and-open-submit
title: 'Studio: Publish (push + open pre-filled submit page)'
type: feature
priority: P1
status: completed
created: 2026-04-26T00:00:00.000Z
structure: user-stories
test_mode: TDD
coverage_target: 90
---

# Feature: Studio: Publish (push + open pre-filled submit page)

## Overview

Minimum viable "publish to GitHub, then open verified-skill.com pre-filled" flow.

Today a skill author editing in `vskill studio` must drop to a terminal to run `git push`, then navigate manually to verified-skill.com. This increment closes that loop with a single Publish button in EditorPanel: it spawns a real `git push` subprocess, normalizes the remote URL, and opens `https://verified-skill.com/submit?repo=<encodedUrl>` in a new tab. The platform side pre-fills the URL input on arrival.

**Phase 1 (initial scope, shipped in vskill@0.5.129):** push only already-committed changes; no commit composition.

**Phase 5 follow-up (shipped in vskill@0.5.132):** when the working tree is dirty, the Publish button now opens a small drawer that auto-generates a commit message via the user's already-configured studio LLM provider (claude-cli / openai / openrouter / etc. — same one used by AI Edit and Improve). The user can edit the suggestion, then click "Commit & Push" — server runs `git add -A && git commit -m "<msg>" && git push`. On clean trees the original push-only flow is unchanged.

Still deferred to full 0742: dirty-state pill on the header, repo creation via `gh` CLI, no-remote attach flow, SSE streaming.

---

## User Stories

### US-006: Sidebar dirty indicator for skills with uncommitted changes (P1, Phase 6)
**Project**: vskill

**As a** skill author working in the studio
**I want** an at-a-glance amber dot next to any skill in the sidebar whose directory has uncommitted git changes
**So that** I can see which authored skills need to be published before I context-switch and forget

**Acceptance Criteria**:
- [x] **AC-US6-01**: Given the workspace has uncommitted changes inside a skill's directory, when the sidebar renders, then a small amber dot is visible immediately to the left of that skill's version badge with `aria-label="Uncommitted changes"` and a tooltip explaining the publish flow.
- [x] **AC-US6-02**: Given a skill's directory has no uncommitted changes, when the sidebar renders, then no dirty dot is shown for that skill.
- [x] **AC-US6-03**: A new lightweight `GET /api/git/status` endpoint runs `git status --porcelain` (argv-only, no shell:true) and returns `{ paths: string[] }` with the porcelain prefix already stripped. Non-git workspaces and git errors → `{ paths: [] }` with HTTP 200 (fail-soft).
- [x] **AC-US6-04**: A pure helper `getDirtySkillIds(skills, dirtyPaths, workspaceRoot)` resolves dirty paths to skill IDs. Handles: skill dir == workspace root (any dirty path → dirty), sibling-prefix collisions (`foo` vs `foobar`), porcelain status prefixes, and skill dirs outside the workspace root (defensively ignored).
- [x] **AC-US6-05**: `useDirtySkills(skills, workspaceRoot)` hook polls `/api/git/status` every 5 s by default (configurable), re-fires immediately on `studio:content-saved` events, and returns a `Set<string>` of dirty `<plugin>/<skill>` IDs. Network/API errors are coerced to an empty set (fail-silent).
- [x] **AC-US6-06**: The dirty set is plumbed end-to-end: `App.tsx` calls the hook, passes `dirtySkillIds` to `<Sidebar>`, which threads it through `<SectionList>` and `<PluginGroup>` to each `<SkillRow>`. The `<SkillRow>` `dirty` prop is optional and backward-compatible (legacy callers omit it; the dot stays hidden).
- [x] **AC-US6-07**: When the user reverts the dirty edits, the dot disappears within one poll cycle (≤ 5 s). Verified live against the greet-anton repo: dot appeared on dirty tree, disappeared after `git checkout`.

---

### US-005: AI-assisted commit message + commit/push for dirty trees (P1, Phase 5)
**Project**: vskill

**As a** skill author with uncommitted changes
**I want** the Publish button to open a drawer that suggests a commit message and lets me edit + commit + push in one click
**So that** I don't have to switch to a terminal to compose a commit message and run git commit before publishing

**Acceptance Criteria**:
- [x] **AC-US5-01**: Given the working tree is dirty, when the user clicks Publish, then a drawer opens with a textarea pre-populated by an AI-generated commit message; `api.gitDiff()` is the dirty-detection probe.
- [x] **AC-US5-02**: Given the drawer mounts, when it auto-fires `api.gitCommitMessage()`, then the request body includes the studio-configured `provider` and `model` (read from `useConfig()`); server reuses the existing `createLlmClient({provider, model})` infrastructure (same path as AI Edit / Improve / Generate).
- [x] **AC-US5-03**: Given the textarea is populated, when the user edits the message, then the textarea reflects the new value (controlled component, not read-only).
- [x] **AC-US5-04**: Given the user clicks "Commit & Push" with a non-empty message, then `api.gitPublish({ commitMessage })` is invoked; server runs `git add -A` then `git commit -m "<msg>"` then `git push` with argv-array safety (no shell interpolation, no `shell:true`).
- [x] **AC-US5-05**: Given the commit/push succeeds, then `window.open` opens `https://verified-skill.com/submit?repo=<canonical>` with `noopener,noreferrer`, a success toast fires (short SHA + branch), and the drawer closes via `onClose`.
- [x] **AC-US5-06**: Given the commit/push fails (rejected push, hook failure, network error), then an error toast fires with stderr summary; `window.open` is NOT called and the drawer stays open so the user can adjust and retry.
- [x] **AC-US5-07**: Given the textarea is empty (or whitespace only), when the user views the drawer, then the "Commit & Push" button is disabled.
- [x] **AC-US5-08**: Given the user clicks Cancel, then `onClose` fires immediately; `api.gitPublish` is never called.
- [x] **AC-US5-09**: Given the user clicks Regenerate, then `api.gitCommitMessage` re-fires and the textarea content is replaced with the new suggestion.
- [x] **AC-US5-10**: Given the diff sent to the LLM exceeds 10K characters, when the prompt is constructed, then it is truncated with a "(truncated…)" note prepended; the full diff is never sent.
- [x] **AC-US5-11**: Given the working tree is clean, when the user clicks Publish, then today's push-only flow runs unchanged (no drawer, no `git add`, no `git commit`).
- [x] **AC-US5-12**: Given `commitMessage` is provided to `/api/git/publish` but the working tree is clean, then the server skips `git add`/`git commit` (a stray message is a no-op) and just runs `git push`.

---

### US-001: Publish button in studio EditorPanel (P1)
**Project**: vskill

**As a** skill author working in the studio editor
**I want** a Publish button next to Save in the editor header
**So that** I can push my committed changes to GitHub without leaving the editor

**Acceptance Criteria**:
- [x] **AC-US1-01**: Given the workspace has a git remote configured (`hasRemote === true`), when EditorPanel renders, then a Publish button appears in the header next to the Save button.
- [x] **AC-US1-02**: Given the workspace has no git remote (`hasRemote === false`), when EditorPanel renders, then the Publish button is not rendered (not merely hidden — element absent from DOM).
- [x] **AC-US1-03**: Given the Publish button is visible, when the user clicks it and the POST /git-publish request is in-flight, then the button is disabled and shows a loading indicator until the response is received.
- [x] **AC-US1-04**: Given the workspace mounts, when `useGitRemote` fires `GET /git-remote`, then the hook stores `{ remoteUrl, branch, hasRemote }` in local state and EditorPanel reads from that state to control button visibility.
- [x] **AC-US1-05**: Given `GET /git-remote` returns `hasRemote: false` or the request fails (network error / git error), when EditorPanel renders, then no Publish button is shown (fail-silent, no error UI for this case).

---

### US-002: POST /git-publish and GET /git-remote eval-server routes (P1)
**Project**: vskill

**As a** skill author who clicked Publish
**I want** the studio to run a real `git push` using my workspace credentials
**So that** my committed changes reach GitHub without terminal access

**Acceptance Criteria**:
- [x] **AC-US2-01**: Given a valid workspace path, when `GET /git-remote` is called, then eval-server runs `git remote get-url origin` and `git rev-parse --abbrev-ref HEAD` and returns `{ remoteUrl: string, branch: string, hasRemote: true }`.
- [x] **AC-US2-02**: Given the workspace has no git remote, when `GET /git-remote` is called, then eval-server returns `{ remoteUrl: null, branch: string, hasRemote: false }` (HTTP 200, not a 4xx).
- [x] **AC-US2-03**: Given a valid workspace with at least one commit, when `POST /git-publish` is called, then eval-server spawns `git push` via `child_process.spawn` using an argv array (NOT shell-string interpolation), captures stdout and stderr, and returns `{ success: true, commitSha, branch, remoteUrl, stdout, stderr }` on exit code 0.
- [x] **AC-US2-04**: Given `git push` exits with a non-zero code (e.g. rejected push, auth failure), when `POST /git-publish` is called, then eval-server returns HTTP 500 with `{ success: false, stdout, stderr }` and the full stderr is included.
- [x] **AC-US2-05**: Given the `git push` subprocess does not exit within 60 seconds (configurable via `GIT_PUBLISH_TIMEOUT_MS` env var), when the timeout fires, then the subprocess is killed, eval-server returns HTTP 500 with `{ success: false, stderr: "timeout" }`.
- [x] **AC-US2-06**: Given any request to `/git-publish` or `/git-remote`, when the routes are registered, then the workspace `root` path is bound once at factory time via `registerGitRoutes(router, root)` — it is never accepted as a per-request parameter, eliminating path-traversal at the architectural level. Additionally, both endpoints enforce a loopback IP guard and an Origin header CSRF guard to prevent cross-site or external invocation.

---

### US-003: Success flow — open verified-skill.com pre-filled (P1)
**Project**: vskill

**As a** skill author whose publish succeeded
**I want** my browser to automatically open verified-skill.com/submit pre-filled with my repo URL
**So that** I can submit or discover my skill with one click

**Acceptance Criteria**:
- [x] **AC-US3-01**: Given `POST /git-publish` returns `{ success: true }`, when the response is received, then the UI calls `window.open('https://verified-skill.com/submit?repo=' + encodeURIComponent(httpsUrl), '_blank', 'noopener,noreferrer')` exactly once.
- [x] **AC-US3-02**: Given the remote URL is SSH-format (`git@github.com:owner/repo.git`), when building the `?repo=` param, then the URL is normalized to `https://github.com/owner/repo` (trailing `.git` stripped, `git@github.com:` → `https://github.com/`).
- [x] **AC-US3-03**: Given the remote URL is already HTTPS (`https://github.com/owner/repo.git`), when building the `?repo=` param, then the URL is normalized to `https://github.com/owner/repo` (trailing `.git` stripped, scheme/host unchanged).
- [x] **AC-US3-04**: Given a successful publish, when the browser tab is opened, then a success toast is shown with the commit SHA (short, 7 chars), branch name, and the text "Opening verified-skill.com…".
- [x] **AC-US3-05**: Given `POST /git-publish` returns `{ success: false }` or the request fails (network error / 5xx), when the response is received, then the Publish button is re-enabled, a dismissible error toast is shown with a summary of stderr (first 200 chars), and `window.open` is NOT called.

---

### US-004: /submit page pre-fills repo URL from query param (P1)
**Project**: vskill-platform

**As a** skill author arriving at verified-skill.com/submit from the studio
**I want** the repo URL input to be pre-filled with my repo
**So that** I only need to click Discover without retyping the URL

**Acceptance Criteria**:
- [x] **AC-US4-01**: Given the page loads with `?repo=https://github.com/owner/repo`, when the component mounts, then the URL `<input>` is pre-filled with `https://github.com/owner/repo`.
- [x] **AC-US4-02**: Given the `?repo=` param is absent or empty, when the component mounts, then the URL `<input>` is empty (existing behavior unchanged).
- [x] **AC-US4-03**: Given the `?repo=` param contains a value that does NOT match `GITHUB_REPO_VALIDATION_RE`, when the component mounts, then the URL `<input>` is left empty and no error UI is shown (silent drop).
- [x] **AC-US4-04**: Given the URL input has been pre-filled from the query param, when the user edits the input field manually, then the field behaves as normal (not locked to the param value).
- [x] **AC-US4-05**: Given the page is pre-filled from `?repo=`, when the component mounts, then the form is NOT auto-submitted — the user must click Discover/Submit themselves.

---

## Functional Requirements

### FR-001: eval-server git routes module
A new file `src/eval-server/git-routes.ts` (in the vskill repo) exposes two Express routes. Routes are mounted in the existing eval-server main entry. Both routes require a workspace path (resolved via existing `WorkspaceContext` / request header pattern already used by eval-server).

### FR-002: Subprocess security
`git push` and `git remote get-url origin` are spawned via `child_process.spawn` with an explicit argv array. Shell-string interpolation is forbidden. The workspace `root` path is bound once at route-registration time (`registerGitRoutes(router, root)`) — it is not accepted per-request, which eliminates path traversal by construction. Both routes also enforce: (1) loopback IP guard (`req.socket.remoteAddress`), and (2) Origin header CSRF guard rejecting any non-localhost Origin.

### FR-003: `useGitRemote` hook
A new React hook `eval-ui/src/hooks/useGitRemote.ts` calls `GET /git-remote` once on workspace mount. Returns `{ remoteUrl, branch, hasRemote, loading, error }`. EditorPanel consumes this hook to control Publish button visibility.

### FR-004: URL normalization utility
A pure function (testable, no side effects) converts any GitHub remote URL (SSH or HTTPS, with or without `.git` suffix) to a canonical `https://github.com/owner/repo` form. Used by the click handler before building `window.open` URL.

### FR-005: Platform query-param pre-fill
`src/app/submit/page.tsx` reads `?repo=` from the query string (via `window.location.search` in the client-side useEffect, or `useSearchParams()` from `next/navigation` — either approach is valid for a Client Component). The value is validated against the existing `GITHUB_REPO_VALIDATION_RE` before being written into input state. The component remains a Client Component (`'use client'`) if it is not already.

*Implementation note*: The code uses `window.location.search` inside a `useEffect` which avoids the Suspense boundary requirement of `useSearchParams()` while being functionally equivalent for a client-side-only read. Both approaches are spec-compliant.

---

## Out of Scope

The following are deferred to increment 0742:

- Dirty-state status pill in DetailHeader
- AI-generated commit messages
- Repo creation via `gh` CLI for repos without a remote
- No-remote attach flow (connecting a new remote from the UI)
- SSE streaming of git push output
- Auto-submit on the platform side
- Push progress / output streaming to the UI

---

## Edge Cases

| Scenario | Expected Behavior |
|---|---|
| No commits to push (`Everything up-to-date`) | `git push` exits 0 — still open submit page (URL matters, not whether commits were transferred) |
| Non-fast-forward (rejected push) | Error toast with stderr, no browser open |
| SSH remote URL | Normalized to HTTPS before building `?repo=` param |
| Malformed `?repo=` on platform | Input left empty, no error UI |
| Concurrent Publish clicks | Button disabled while in-flight; only one request in flight at a time |
| Network failure during /git-publish | 5xx / fetch error → error toast, button re-enabled |
| /git-remote request fails | Publish button not shown (fail-silent) |

---

## Dependencies

- Node.js `child_process.spawn` (stdlib, no new deps)
- `useSearchParams` from `next/navigation` (already available in Next.js 15)
- `GITHUB_REPO_VALIDATION_RE` — existing constant in vskill-platform
- `apiFetch` / fetch wrapper in `eval-ui/src/lib/api.ts`
- Existing workspace path allowlist in eval-server
- Existing `/submit` page flow at verified-skill.com (OAuth, discover, submit — unchanged)

---

## Success Criteria

- Skill author can click Publish in studio → git push completes → browser opens `https://verified-skill.com/submit?repo=<url>` with the input pre-filled.
- Zero new external npm dependencies added.
- Unit test coverage ≥ 90% for URL normalizer, subprocess wrapper, and query-param pre-fill logic.
- Playwright E2E: fixture repo with a remote → Publish click → `window.open` called with correct `?repo=` param.
- No regression to the existing Save flow or submit page behavior.

---

### US-007: Manual version-bump controls + save refresh + no-jump enforcement (P1, Phase 7)
**Project**: vskill

**As a** skill author
**I want** to bump major / minor / patch by exactly +1 from the editor toolbar AND have the version refresh everywhere immediately after Save AND be blocked from accidentally jumping versions
**So that** I can maintain meaningful semver across releases without typing YAML and without surprises at publish time

**Acceptance Criteria** (all completed in vskill@0.5.139):
- [x] **AC-US7-01**: Three buttons "+patch / +minor / +major" appear next to Save in EditorPanel toolbar (read-only skills hide them). Each button's tooltip previews the resulting version (e.g. "Bump patch: 1.0.5 → 1.0.6").
- [x] **AC-US7-02**: Clicking +patch increments patch by 1 and writes the new SKILL.md content via `setFrontmatterVersion`. Clicking +minor increments minor by 1 and resets patch to 0. Clicking +major increments major by 1 and resets minor + patch to 0.
- [x] **AC-US7-03**: Save validates the version transition via `validateVersionTransition(from, to)`. Allowed transitions: identical, patch+1, minor+1 with patch=0, major+1 with minor=patch=0. Decreases are rejected. Anything else surfaces an error toast and Save is blocked.
- [x] **AC-US7-04**: After a successful save, EditorPanel dispatches a `studio:content-saved` CustomEvent. App.tsx listens and calls `refreshSkills()` so the sidebar version badge, header breadcrumb, and dirty indicator all reflect the freshly-saved frontmatter.
- [x] **AC-US7-05**: Helpers `bumpVersion(current, kind)` and `validateVersionTransition(from, to)` are pure functions with full test coverage (19 tests). `setFrontmatterVersion(content, v)` is idempotent — same version returns identical bytes.
- [x] **AC-US7-06**: Default 1.0.0 (source="default") no longer renders italic in `<VersionBadge>`. Italics remain only for genuinely-inherited versions ("registry" / "plugin"). Tooltip "No version declared" preserved on hover for discoverability.

---

### US-008: Stamp version into local + platform skill content (P1, Phase 8)
**Project**: vskill / vskill-platform

**As a** skill consumer
**I want** every skill — local install or platform-served — to carry an explicit `version:` line in its SKILL.md frontmatter
**So that** the studio never falls back to the default placeholder and the version provenance is unambiguous

**Acceptance Criteria** (all completed):
- [x] **AC-US8-01** (B1, vskill@0.5.140): New `vskill stamp-versions` CLI walks default scopes (`~/.claude/skills/`, `~/.claude/plugins/cache/`) and injects `version: "1.0.0"` into any SKILL.md frontmatter that lacks a version. Defaults to dry-run; `--write` applies. Idempotent. Refuses to walk paths outside `$HOME` as a safety check. Verified: 61/63 of Anton's local skills were stamped on first run; 0/63 changes on re-run.
- [x] **AC-US8-02** (A, platform): `publish.ts` calls `injectVersionIfMissing(skillMdContent, newVersion)` after newVersion is finalized so every new `SkillVersion.content` row carries a `version:` line. Idempotent — author-declared frontmatter is byte-preserved (does not disturb contentHash dedup).
- [x] **AC-US8-03** (A, platform): `scripts/backfill-version-stamps.ts` walks all SkillVersion rows, injects `version: <row.version>` into stored content where missing, and recomputes contentHash. Tested with 5 cases (idempotent re-run, null content, error per row, dry-run vs write). Production run is opt-in via `npx tsx scripts/backfill-version-stamps.ts --write`.

---

### US-009: OAuth redirect preserves ?repo= query string (P1, Phase 8)
**Project**: vskill-platform

**As a** skill author who arrives at /submit?repo=… from the studio Publish flow without being signed in
**I want** the GitHub OAuth round-trip to land me back at /submit?repo=…
**So that** the URL input is still pre-filled after I authenticate (instead of empty)

**Acceptance Criteria** (completed in platform deploy `d7ddde7a`):
- [x] **AC-US9-01**: When `authState === "unauthenticated"` on `/submit`, the "Login with GitHub" link constructs its `?redirect=` from the current `window.location.search`, so the destination after auth is `/submit?repo=<encoded>` not just `/submit`. The OAuth init route's open-redirect guard still passes (encoded URL has no literal `://`).
- [x] **AC-US9-02**: After the GitHub callback restores the user session and follows the cookie-stored redirect, the submit page mounts with `?repo=…` intact and `getPrefillRepo` populates the URL input automatically.


---

### US-010: Sleek PublishDrawer redesign (P1, Phase 9)
**Project**: vskill

**As a** skill author opening the publish drawer
**I want** a centered modal with explicit "Write yourself / Generate with AI" mode toggle and inline error blocks
**So that** the surface looks like a real product and the AI doesn't auto-fire when I just want to type a message

**Acceptance Criteria** (shipped in vskill@0.5.142):
- [x] **AC-US10-01**: Modal renders centered via `position: fixed; inset: 0; flex` (not bottom-right corner). 520 px wide, max-height 80 vh, hairline 1 px borders + dramatic shadow.
- [x] **AC-US10-02**: Backdrop dim `rgba(0,0,0,0.55)` + `backdrop-filter: blur(6px)`. Backdrop click dismisses (unless a publish is in flight). Modal entry animation: 180 ms opacity + 4 px translateY; respects `prefers-reduced-motion`.
- [x] **AC-US10-03**: Segmented mode control with two segments: `Write yourself` (default) and `Generate with AI`. Active segment fills with `--bg-subtle`. Manual mode never auto-fires AI — fixes the previous surprise-side-effect on mount.
- [x] **AC-US10-04**: AI mode click → fires `api.gitCommitMessage`. AI generation failure renders an inline alert block (NOT a transient toast) with role="alert" + a "Retry" link. Block stays visible until the user retries or switches mode.
- [x] **AC-US10-05**: Publish/push failure renders a separate inline alert block (`data-testid="publish-error-push"`) below the textarea — drawer stays open so the user can fix the message and retry. Toast still fires for accessibility.
- [x] **AC-US10-06**: Footer left-aligns Regenerate (AI mode only); right-aligns Cancel + Commit & Push. Backward-compatible: existing tests pass via `defaultMode="ai"` opt-in.

---

### US-011: Pending-state metadata (state + age) in submission responses (P1, Phase 9)
**Project**: vskill-platform

**As a** user re-submitting a skill that's still being processed
**I want** the "Already pending" badge to show *which* scan stage and how long ago I submitted
**So that** I understand whether to wait or take action — no opaque badges

**Acceptance Criteria** (deployed to verified-skill.com Worker version `11b25234`):
- [x] **AC-US11-01**: `upsertSubmission` returns `{ kind: "pending", id, state, submittedAt?, ageSeconds? }` when an existing Submission exists and is in PENDING_STATES. The `submittedAt` and `ageSeconds` fields are populated from `Submission.createdAt` (Date) — additive contract, older callers and test mocks that omit createdAt see the original `{kind, id, state}` shape.
- [x] **AC-US11-02**: `POST /api/v1/submissions` forwards the metadata into the response's `skipped[]` array as `{ skillName, reason, state?, submittedAt?, ageSeconds? }`.
- [x] **AC-US11-03**: Submit page renders the rich badge: `Pending: tier 1 scan · 3m ago` (instead of opaque `Already pending`). Falls back to `Already pending` when the platform omits the new fields. Tooltip explains the in-flight semantics + that the next submit after publish picks up latest commits automatically.
- [x] **AC-US11-04**: All 128 platform unit tests pass (publish-rescan + publish-degraded-data fixtures pre-stamped with `version:` to acknowledge the Phase 8 stamping behavior).
