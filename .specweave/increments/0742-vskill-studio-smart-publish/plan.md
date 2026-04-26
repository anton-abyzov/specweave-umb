# Implementation Plan: vskill Studio Smart Publish (MVP): dirty-state pill + AI-commit publish drawer

## Overview

Add a two-layer feature to vskill studio so that authors can edit → review → ship a `SKILL.md` change without leaving the app. The **backend layer** (`src/eval-server/`) wraps the local `git` and `gh` CLIs behind path-safe REST endpoints that scope every operation to the resolved skill directory. The **frontend layer** (`src/eval-ui/src/`) extends the existing `SkillInfo` shape with a `gitStatus` field, slots a `GitStatusPill` next to `VersionBadge` on the detail header, adds a `Publish` button next to `Save` in `EditorPanel`, and ships a `PublishDrawer` that mirrors `OpsDrawer` and adapts its primary action to one of three modes — `push` (repo with remote), `create-via-gh` (repo without remote, `gh` available + authenticated), or `attach-remote-and-push` (repo without remote, no `gh`, polls `api.github.com`). All git/`gh` invocations use `child_process.execFile` with array args, and every skill path is resolved through the existing `resolveSkillDir` + `assertContained` guard so neither a hostile request nor a typo can escape the skill directory.

## ADR References

- **ADR 0688-01 — SSE Over WebSocket for Scope-Transfer Progress Streaming** — establishes SSE as the default transport for short-lived progress streams in the studio. The new `/git-publish` and `/git-commit-message` endpoints follow the same `initSSE` / `sendSSE` / `sendSSEDone` helpers from `sse-helpers.ts` that this ADR canonicalized.
- **ADR 0734-02 — SSE for Short-Lived Install Progress** — extends the SSE pattern to child-process-driven progress and is the closest precedent for streaming staged shell-command progress (`staging` → `committing` → `pushing`) back to the UI. We follow its event-name convention (`progress` / `error` / `done`).
- **ADR 0119 — Git Integration Strategy** and **ADR 0120 — GitHub Integration Approach** — establish the umbrella's default of preferring local CLIs (`git`, `gh`) over libgit2 / Octokit bindings for short-lived author-time operations. This increment continues that pattern; no new dependency is added.

No new ADR is required: the architecture composes existing accepted patterns (CLI-via-`execFile`, SSE for short-lived progress, `assertContained` path guard, provider/model SSE invocation from `improve-routes.ts`).

## Architecture

```
┌───────────────────────── Studio (browser) ─────────────────────────┐
│                                                                    │
│  DetailHeader                          EditorPanel                 │
│  ┌──────────────────────────────┐      ┌────────────────────────┐  │
│  │ name [VersionBadge]          │      │ AI Edit | Regenerate   │  │
│  │           [GitStatusPill]    │      │      [Save] [Publish↑] │  │
│  └──────────────────────────────┘      └────────┬───────────────┘  │
│                                                  │ click           │
│  useGitStatus  ◄──── CONTENT_SAVED               ▼                  │
│       │                                  ┌─────────────────────┐    │
│       │  GET /git-status                 │   PublishDrawer     │    │
│       └────────────────────────────────► │  mode = push |      │    │
│                                          │  create-via-gh |    │    │
│                                          │  attach-remote...   │    │
│                                          └──┬──────────────────┘    │
│                                             │                       │
│                            POST /git-diff   │ POST /git-commit-msg  │
│                            POST /git-publish│ (SSE)                 │
│                                             ▼                       │
└─────────────────────────────────────────────┬───────────────────────┘
                                              │ HTTP / SSE
┌─────────────────────────────────────────────▼───────────────────────┐
│                         eval-server (Node)                          │
│                                                                     │
│   git-routes.ts ──► resolveSkillDir + assertContained               │
│                ──► git-status.ts   (execFile git -C <skillDir> ...) │
│                ──► gh-detect.ts    (execFile gh auth status)        │
│                ──► improve-routes provider/model SSE → AI commit    │
│                                                                     │
└─────────────────────────────────────────────────────────────────────┘
                          │ child_process.execFile (no shell)
                          ▼
              ┌──────────┐  ┌──────────┐
              │   git    │  │   gh     │   (user's local CLIs)
              └──────────┘  └──────────┘
```

The core invariant: **the browser never sees a token, never receives a raw filesystem path it didn't already know, and every server-side path traversal is blocked by `assertContained`.**

## Backend Modules

All modules live in `repositories/anton-abyzov/vskill/src/eval-server/`. Imports follow the `.js` extension convention required by `--moduleResolution nodenext`.

### `git-status.ts` (NEW)

Module shape (single exported function plus the response type):

```ts
import { execFile } from "node:child_process";
import { promisify } from "node:util";
const execFileP = promisify(execFile);

export interface GitFile {
  path: string;          // relative to skillDir
  status: string;        // raw two-letter porcelain code, e.g. " M", "??", "A "
}

export interface GitStatus {
  isRepo: boolean;
  dirty: boolean;
  hasRemote: boolean;
  remoteUrl: string | null;
  branch: string | null;
  ahead: number;
  files: GitFile[];
  repoRoot: string | null;     // toplevel from `git rev-parse --show-toplevel`
}

export async function inspectSkillRepo(skillDir: string): Promise<GitStatus>;
```

Implementation outline:

1. `git -C <skillDir> rev-parse --is-inside-work-tree` — non-zero exit ⇒ `{ isRepo: false, ... }` returned with all other fields zero/null.
2. `git -C <skillDir> rev-parse --show-toplevel` — `repoRoot`.
3. `git -C <skillDir> rev-parse --abbrev-ref HEAD` — `branch` (may be `HEAD` for detached, returned verbatim).
4. `git -C <skillDir> remote get-url origin` — non-zero exit ⇒ `hasRemote = false`, otherwise capture `remoteUrl`.
5. `git -C <skillDir> status --porcelain -- <skillDir>` — scoped status; populates `files[]` and `dirty` (true if list is non-empty).
6. `git -C <skillDir> rev-list --count @{u}..HEAD` — ahead count; if no upstream, `ahead = 0` (do not throw).

All six calls are `execFile('git', [...args])` — no `exec`, no shell. Errors bubble up as a normal rejected promise; the route handler converts them to `{ ok: false, error }` JSON.

### `gh-detect.ts` (NEW)

```ts
export interface GhStatus {
  available: boolean;       // `gh --version` succeeded
  authenticated: boolean;   // `gh auth status` succeeded
  user: string | null;      // parsed from `gh auth status` output
}

export async function detectGh(): Promise<GhStatus>;
```

Implementation:

1. `execFile('gh', ['--version'])` — non-zero exit or ENOENT ⇒ `{ available: false, authenticated: false, user: null }`.
2. `execFile('gh', ['auth', 'status', '--show-token=false'])` — non-zero exit ⇒ `{ available: true, authenticated: false, user: null }`. The flag is mandatory: even though the redirected stdout doesn't ordinarily carry the token, `--show-token=false` makes the contract explicit and is forward-compatible with any future `gh` change. **The token itself MUST NEVER appear in logs, response payloads, or error messages — see NFR-005.**
3. Parse the `Logged in to github.com as <username>` line defensively. Different `gh` versions vary the prose slightly; we look for a `as ([\w.-]+)` capture group on a line containing `github.com`. If parsing fails, `user = null` but `authenticated = true` (the auth check still succeeded).

### `git-routes.ts` (NEW)

Registers four endpoints on the existing `Router`:

| Method | Path | Body | Response |
|---|---|---|---|
| `GET`  | `/api/skills/:plugin/:skill/git-status` | — | `{ ok: true, gitStatus: GitStatus, gh: GhStatus }` |
| `POST` | `/api/skills/:plugin/:skill/git-diff` | `{}` | `{ ok: true, diff: string }` (text diff scoped to skillDir) |
| `POST` | `/api/skills/:plugin/:skill/git-commit-message?sse` | `{ provider: ProviderName, model: string, instruction?: string }` | SSE stream — `progress` events with token chunks, terminating `done` with the final message |
| `POST` | `/api/skills/:plugin/:skill/git-publish?sse` | `{ message: string, mode: 'push' \| 'create-via-gh' \| 'attach-remote-and-push', visibility?: 'public' \| 'private', remoteUrl?: string }` | SSE stream — `progress` events for each stage, terminating `done` with `{ commitSha, branch, remoteUrl }` |

All four handlers begin with the same prelude:

```ts
const skillDir = resolveSkillDir(root, params.plugin, params.skill);
// resolveSkillDir already calls assertContained internally — directory traversal is blocked.
```

`/git-diff` runs `git -C <skillDir> diff -- <skillDir>` (scoped — never `git diff` raw, never `-A`). The result is returned as plain text in a JSON envelope to keep the existing `fetchJson` helper usable.

`/git-commit-message?sse` reuses the provider/model SSE pattern from `improve-routes.ts:21`: same `initSSE` / `sendSSE` / `sendSSEDone` helpers from `sse-helpers.ts`, same `createLlmClient` from `../eval/llm.js`, same `{provider, model}` body shape. The system+user prompts are described in §"AI Commit-Message Prompt" below.

`/git-publish?sse` is a switch on `mode`:

- `mode === 'push'`:
  1. `progress { phase: 'staging' }` → `git -C <skillDir> add -- <skillDir>`
  2. `progress { phase: 'committing' }` → `git -C <skillDir> commit -m <message>`
  3. `progress { phase: 'pushing' }` → `git -C <skillDir> push`
  4. `done { commitSha, branch, remoteUrl }` (capture sha from `git rev-parse HEAD` post-commit)

- `mode === 'create-via-gh'`:
  Pre-validate `body.visibility` is exactly `'public'` or `'private'` (reject otherwise — we never pass a user-supplied flag through to `gh`). Reject if `gh-detect` reports `!authenticated`. Read the frontmatter `description` from `<skillDir>/SKILL.md`, truncate to ≤120 chars.
  1. `progress { phase: 'creating' }` → `execFile('gh', ['repo', 'create', skillFolderName, '--' + visibility, '--source=' + repoRoot, '--push', '--description=' + truncatedDescription])`. `gh` itself runs `git init` if needed, attaches origin, and pushes — one shell call.
  2. `done { remoteUrl }` (re-run `inspectSkillRepo` post-call to capture the now-attached origin URL).

- `mode === 'attach-remote-and-push'`:
  Validate `body.remoteUrl` matches `^https://github\.com/[\w.-]+/[\w.-]+(\.git)?$`.
  1. `progress { phase: 'linking' }` → `git -C <repoRoot> remote add origin <url>` (use `repoRoot` from `inspectSkillRepo`, NOT `skillDir`, since `remote add` is a repo-level op).
  2. `progress { phase: 'pushing' }` → `git -C <repoRoot> push -u origin <branch>` (branch from `inspectSkillRepo`).
  3. `done { remoteUrl }`.

Stage-progress events keep the UI honest about long-running pushes; the SSE heartbeat from `withHeartbeat` (already used in `improve-routes.ts`) prevents intermediate proxies from idling out the connection.

### `router.ts` (MOD)

No code change to `router.ts` itself. The new routes are wired by adding one import + one call in `eval-server.ts:24,94`:

```ts
import { registerGitRoutes } from "./git-routes.js";
// ...
registerImproveRoutes(router, root);
registerGitRoutes(router, root);
```

### `api-routes.ts` (MOD)

The `GET /api/skills/:plugin/:skill` detail handler (the one consumed by `WorkspaceContext` on mount) is augmented to call `inspectSkillRepo(skillDir)` and embed the result in the response under `gitStatus`. The cost is bounded — six `execFile` calls per detail load — so we add a 5-second in-memory cache keyed by `skillDir` to avoid re-running the six `git` calls on rapid back-to-back detail loads (the user double-clicking a sidebar row, for example). The cache is invalidated whenever `applyImprovement` succeeds or `/git-publish` reports `done`. The cache lives in `git-status.ts` to keep the route handler thin.

The response shape becomes:

```ts
{
  ...existingSkillInfoFields,
  gitStatus: GitStatus | null,   // null when inspectSkillRepo throws (defensive)
  gh: GhStatus,
}
```

The legacy `/api/skills` list endpoint (line 1671) is **not** changed — git status is fetched per-skill on demand by the frontend, never for the whole sidebar.

## Frontend Modules

All paths are under `repositories/anton-abyzov/vskill/src/eval-ui/src/`.

### `types.ts` (MOD)

Extend `SkillInfo` (currently at line 119) with the matching shape:

```ts
export interface GitFile { path: string; status: string }
export interface GitStatus {
  isRepo: boolean;
  dirty: boolean;
  hasRemote: boolean;
  remoteUrl: string | null;
  branch: string | null;
  ahead: number;
  files: GitFile[];
  repoRoot: string | null;
}
export interface GhStatus {
  available: boolean;
  authenticated: boolean;
  user: string | null;
}

export interface SkillInfo {
  // ... existing fields ...
  gitStatus?: GitStatus | null;
  gh?: GhStatus;
}
```

The `?` keeps the change backward-compatible with cached responses and with tests that build `SkillInfo` literals.

### `components/GitStatusPill.tsx` (NEW)

```ts
export interface GitStatusPillProps {
  gitStatus: GitStatus | null | undefined;
  "data-testid"?: string;
}
```

Render rules (mirrors `VersionBadge.tsx:27-60` for tokens):

| Condition | Output |
|---|---|
| `!gitStatus \|\| !gitStatus.isRepo` | `null` (nothing rendered) |
| `gitStatus.dirty` | amber chip — `● uncommitted` |
| `!dirty && ahead > 0` | blue chip — `↑{ahead}` |
| `!dirty && ahead === 0` | `null` (nothing rendered) |

Style tokens: same `inline-flex` / `border 1px solid var(--border)` / `borderRadius 4` / `fontFamily var(--font-mono)` / `fontSize 12` / `tabular-nums` shape used by `VersionBadge`. The amber variant uses `var(--amber-9, #b8860b)` for the dot and `var(--amber-12)` for text on `var(--amber-3)` background; the blue variant uses analogous `--blue-*` tokens. Title attribute carries the rich tooltip from AC-US1-03 (e.g. `2 files changed on main`).

Slot location in `DetailHeader.tsx:151-178`: inside the same row-2 flex container that holds the `<h2>` name and `<span data-testid="detail-header-version">VersionBadge</span>`, immediately after the version badge, with `gap: 8` between them.

### `components/PublishDrawer.tsx` (NEW)

```ts
export interface PublishDrawerProps {
  open: boolean;
  onClose: () => void;
  plugin: string;
  skill: string;
  gitStatus: GitStatus;
  gh: GhStatus;
  // From WorkspaceContext / useAgentCatalog — passed in to keep the drawer pure.
  provider: ProviderName;
  model: string;
}
```

Mode resolution (computed at render time from props):

```ts
type Mode = 'push' | 'create-via-gh' | 'attach-remote-and-push';

function computeMode(g: GitStatus, gh: GhStatus): Mode {
  if (g.hasRemote) return 'push';
  if (gh.available && gh.authenticated) return 'create-via-gh';
  return 'attach-remote-and-push';
}
```

Sections (top-to-bottom, mirroring `OpsDrawer.tsx`'s skeleton — `createPortal`, 420px right, esc-close):

1. **Header strip** — `Repo: <repoRoot> • branch: <branch> • origin → <remoteUrl>` (the `origin` segment is hidden when `!hasRemote`). For `attach-remote-and-push`, also renders an `Owner` text input (default value: `gh.user ?? ''`) and a `public | private` radio.

2. **Diff preview** — fetches `POST /git-diff` once on mount; renders the unified diff in a fixed-height scroll container with monospace font. Empty diff (e.g. only an untracked file) shows a fallback "No tracked changes — new files only" with the file list from `gitStatus.files`.

3. **Commit message** — `<textarea>` with the streamed AI message. On mount, opens the `git-commit-message?sse` SSE stream, accumulates `progress` event payloads into the textarea via `setState`. A `Regenerate` button aborts the current stream (via `AbortController`) and reopens it with the same `{provider, model}` from props — re-reading the latest from `useAgentCatalog` is the parent's job, so the drawer never goes stale on its own. Edits to the textarea cancel any in-flight stream.

4. **Footer** — the action button label switches by mode:
   - `push` ⇒ `Commit & Push`
   - `create-via-gh` ⇒ `Create on GitHub & Push`
   - `attach-remote-and-push` ⇒ `Create on GitHub` (opens the prefilled `/new` tab, then enters poll state)

The poll state for `attach-remote-and-push`:

```
state machine:
  idle  ──[click Create on GitHub]──►  polling
  polling ──[200 within 60s]────────►  pushing
  polling ──[60s elapsed]───────────►  paste-url
  paste-url ──[user pastes + Push]──►  pushing
  pushing ──[done event]────────────►  closed (drawer.onClose + toast + pill clears)
  any state ──[Cancel]──────────────►  closed (no side effect on the repo)
```

Polling implementation: `setInterval(2000)` calls `fetch('https://api.github.com/repos/<owner>/<name>')` directly from the browser (CORS-allowed for the public read, no auth needed for the existence check). On status 200, clear the interval and POST `/git-publish?sse` with `mode: 'attach-remote-and-push'` and `remoteUrl: 'https://github.com/<owner>/<name>.git'`.

### `hooks/useGitStatus.ts` (NEW)

```ts
export function useGitStatus(plugin: string, skill: string): {
  gitStatus: GitStatus | null;
  gh: GhStatus | null;
  refresh: () => void;
};
```

- Fetches `GET /api/skills/:plugin/:skill/git-status` on mount.
- Subscribes to a `CONTENT_SAVED` event surfaced by `WorkspaceContext` (see below) and refetches on each emission.
- No polling — refresh is event-driven.
- Exposes a manual `refresh()` so the drawer can refetch on `done`.

### `pages/workspace/EditorPanel.tsx` (MOD)

Insert a `Publish` button immediately after the Save button at line 370. Visibility:

```ts
const showPublish = gitStatus?.isRepo && (gitStatus.dirty || gitStatus.ahead > 0 || !gitStatus.hasRemote);
const disablePublish = !gitStatus?.isRepo;
```

When `disablePublish`, render the button with `disabled` and a `title="Initialize this folder as a git repo first — git init support is coming in a follow-up increment."` tooltip. Clicking when enabled sets a local `publishOpen` state that opens `<PublishDrawer />`.

### `pages/workspace/WorkspaceContext.tsx` (MOD)

After `dispatch({ type: "CONTENT_SAVED" })` at line 227, also `window.dispatchEvent(new CustomEvent('studio:content-saved', { detail: { plugin, skill } }))`. `useGitStatus` subscribes to this event for its event-driven refresh. Using a global `CustomEvent` (rather than threading a callback through context) keeps `useGitStatus` decoupled from `WorkspaceContext` — same pattern the codebase already uses for `studio:toast` (App.tsx:240-254).

### `api.ts` (MOD)

Add four wrappers next to `applyImprovement` at line 449:

```ts
getGitStatus(plugin: string, skill: string): Promise<{ ok: boolean; gitStatus: GitStatus; gh: GhStatus }> {
  return fetchJson(`/api/skills/${plugin}/${skill}/git-status`);
},

getGitDiff(plugin: string, skill: string): Promise<{ ok: boolean; diff: string }> {
  return fetchJson(`/api/skills/${plugin}/${skill}/git-diff`, { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: '{}' });
},

// SSE — streams via fetch + AbortController, not fetchJson.
streamCommitMessage(plugin, skill, body, onProgress, onDone, onError, signal): void { ... }
streamPublish(plugin, skill, body, onProgress, onDone, onError, signal): void { ... }
```

The two SSE wrappers follow the same `fetch → res.body.getReader → TextDecoder → buffer split on \n\n` pattern that `SkillImprovePanel.tsx:65-89` already uses; we extract that into a small shared helper in `sse.ts` if duplication is meaningful (judgment call during implementation — the pattern is small enough that inlining is also fine).

## Sequence Diagrams

### Path A — repo with remote → click Publish → Commit & Push

```
User      Studio (browser)              eval-server                  git
 │             │                              │                       │
 │ click Save  │                              │                       │
 │────────────►│                              │                       │
 │             │ POST /apply-improvement      │                       │
 │             │─────────────────────────────►│                       │
 │             │                              │ writeFileSync         │
 │             │ ◄────────────────────────────│ ok                    │
 │             │ dispatch CONTENT_SAVED       │                       │
 │             │ (CustomEvent: studio:        │                       │
 │             │  content-saved)              │                       │
 │             │                              │                       │
 │             │ useGitStatus.refresh()       │                       │
 │             │ GET /git-status              │                       │
 │             │─────────────────────────────►│  inspectSkillRepo     │
 │             │                              │ ─────────────────────►│
 │             │                              │ ◄────────────── dirty │
 │             │ ◄────────────────────────────│ {dirty:true,...}      │
 │             │ amber pill renders           │                       │
 │             │                              │                       │
 │ click Publish                              │                       │
 │────────────►│ open PublishDrawer mode=push │                       │
 │             │ POST /git-diff               │                       │
 │             │─────────────────────────────►│ git diff -- <skillDir>│
 │             │                              │ ─────────────────────►│
 │             │ ◄────── diff ────────────────│                       │
 │             │ POST /git-commit-message?sse │                       │
 │             │─────────────────────────────►│ LLM stream            │
 │             │ ◄── progress (chunks) ───────│                       │
 │             │ ◄── done (final message)─────│                       │
 │             │ textarea populated           │                       │
 │             │                              │                       │
 │ click Commit & Push                        │                       │
 │────────────►│ POST /git-publish?sse        │                       │
 │             │  mode=push                   │                       │
 │             │─────────────────────────────►│ git add -- <skillDir> │
 │             │                              │ ─────────────────────►│
 │             │ ◄── progress staging ────────│                       │
 │             │                              │ git commit -m <msg>   │
 │             │                              │ ─────────────────────►│
 │             │ ◄── progress committing ─────│                       │
 │             │                              │ git push              │
 │             │                              │ ─────────────────────►│
 │             │ ◄── progress pushing ────────│                       │
 │             │ ◄── done {sha,branch,remote}─│                       │
 │             │ studio:toast (sha + branch)  │                       │
 │             │ drawer.close()               │                       │
 │             │ useGitStatus.refresh()       │                       │
 │             │ → pill clears                │                       │
```

### Path B — repo without remote, `gh` available + authenticated

Same prelude up to drawer open; mode resolves to `create-via-gh` (gitStatus.hasRemote=false, gh.available=true, gh.authenticated=true). The drawer renders the `public/private` radio in the header strip. On click `Create on GitHub & Push`:

```
Studio (browser)              eval-server                          gh CLI               GitHub
      │                             │                                 │                    │
      │ POST /git-publish?sse       │                                 │                    │
      │ mode=create-via-gh,         │                                 │                    │
      │ visibility=public           │                                 │                    │
      │────────────────────────────►│ read SKILL.md frontmatter desc  │                    │
      │                             │ truncate ≤120 chars             │                    │
      │                             │ gh repo create <name> --public  │                    │
      │                             │   --source=<repoRoot>           │                    │
      │                             │   --push --description=...      │                    │
      │                             │ ───────────────────────────────►│ create repo        │
      │                             │                                 │ ──────────────────►│
      │                             │                                 │ ◄────── created ───│
      │                             │                                 │ git init / origin  │
      │                             │                                 │ add / push (one shot)
      │ ◄── progress creating ──────│                                 │                    │
      │                             │ inspectSkillRepo (re-read)      │                    │
      │ ◄── done {remoteUrl} ───────│                                 │                    │
      │ toast + close + pill clears │                                 │                    │
```

Critical: `gh repo create … --source=<repoRoot> --push` does the equivalent of `git init` (if needed), `git remote add origin`, and `git push -u origin <branch>` in a single CLI call — that's why this path is genuinely one click on the studio side.

### Path C — repo without remote, no `gh`

```
Studio (browser)                eval-server          GitHub web UI         api.github.com
      │                                │                 │                       │
      │ click Create on GitHub         │                 │                       │
      │ window.open(/new?name=...)─────────────────────► │ form prefilled        │
      │                                │                 │                       │
      │ setInterval(2000) GET /repos/<owner>/<name> ─────────────────────────────►│
      │ ◄── 404 ─────────────────────────────────────────────────────────────────│
      │ ... (repeat) ...                                                          │
      │                                │                 │ user clicks Create    │
      │                                │                 │ ──── creates repo ───►│
      │ ◄── 200 ─────────────────────────────────────────────────────────────────│
      │ clearInterval                  │                 │                       │
      │ POST /git-publish?sse          │                 │                       │
      │ mode=attach-remote-and-push,   │                 │                       │
      │ remoteUrl=https://github.com/  │                 │                       │
      │   <owner>/<name>.git           │                 │                       │
      │───────────────────────────────►│                 │                       │
      │                                │ git remote add origin <url>             │
      │ ◄── progress linking ──────────│                 │                       │
      │                                │ git push -u origin <branch>             │
      │ ◄── progress pushing ──────────│                 │                       │
      │ ◄── done {remoteUrl} ──────────│                 │                       │
      │ toast + close + pill clears    │                 │                       │
      │                                │                 │                       │
      │ (timeout fallback if no 200 in 60s):              │                       │
      │   drawer transitions to paste-url state           │                       │
      │   user pastes <repoUrl> + clicks Push             │                       │
      │   same /git-publish call as above                 │                       │
```

The 60-second window with 2-second polling = at most 30 unauthenticated `api.github.com` requests, well under the 60-per-hour-per-IP unauthenticated rate limit.

## AI Commit-Message Prompt

Reuses the provider/model SSE wiring from `improve-routes.ts:21-67` — same `createLlmClient`, same `initSSE`/`sendSSE`/`sendSSEDone`, same `{provider, model}` body shape that `SkillImprovePanel.tsx:72` constructs.

System prompt:

```
You write conventional git commit messages from a diff. Output exactly one
line, ≤72 characters. No body. No emoji. No "🤖". No "Co-Authored-By".
No mention of AI, Claude, Anthropic, GPT, or any model name. Use the
imperative mood ("add", "fix", "update"). Do not wrap the line in quotes
or backticks. Output the message and nothing else.
```

User payload:

```
Skill: <plugin>:<skill>
Version: <oldFrontmatterVersion> → <newFrontmatterVersion>   (omit line if no version delta)

Diff (scoped to skill directory):
<git diff -- <skillDir>>
```

Provider/model: whatever `useAgentCatalog().activeAgent`/`.activeModel` reports (already used by `AiEditBar.tsx`). The drawer reads these from props; the parent (`EditorPanel`) reads them from the same `useAgentCatalog` hook the existing AI Edit bar uses, so the user's top-right model picker is the single source of truth.

## Security

- **Subprocess**: every git/`gh` call is `execFile('git'|'gh', [...args])` with array args. No `exec`, no `spawn` with `shell: true`, no string concatenation, no template literals interpolating user input into a command string. (NFR-002)
- **Path containment**: every route uses `resolveSkillDir(root, plugin, skill)` which calls `assertContained` internally. The `repoRoot` returned by `git rev-parse --show-toplevel` is an output, not an input — we never accept a raw path from the client. (NFR-001)
- **Add scope**: `git add -- <skillDir>` always. Never `-A`, never `.`, never unscoped. (NFR-003)
- **Diff scope**: `git diff -- <skillDir>` always. Never raw `git diff`. (NFR-004)
- **AI prompt**: sees only the scoped diff, never the full repo content or any path outside the skill directory.
- **gh token**: `gh auth status --show-token=false` always. The token MUST NEVER appear in stdout we capture, in our logs, in any HTTP response, or in error messages. The username is the only identity field we expose. (NFR-005)
- **GitHub URL params**: `encodeURIComponent` on the skill name and the truncated frontmatter description before string-concatenation into the `/new` URL. Description is truncated to ≤120 chars before encoding. (NFR-006)
- **Remote URL validation**: the `attach-remote-and-push` endpoint validates `remoteUrl` against `^https://github\.com/[\w.-]+/[\w.-]+(\.git)?$` before passing to `git remote add`.
- **Visibility validation**: `body.visibility` must be exactly `'public'` or `'private'` — anything else is rejected with 400 before any `gh` invocation.
- **Polling**: the 30-request budget per drawer-open is well under the unauthenticated `api.github.com` rate limit (60/hr/IP).
- **Auth**: no interactive auth in this feature. We rely entirely on the user's existing `git` credential helper and `gh` auth.

## Test Strategy

| File | Test Type | Test File |
|---|---|---|
| `git-status.ts` | unit | `src/eval-server/__tests__/git-status.test.ts` |
| `gh-detect.ts` | unit | `src/eval-server/__tests__/gh-detect.test.ts` |
| `git-routes.ts` | unit | `src/eval-server/__tests__/git-routes.test.ts` |
| `api-routes.ts` augment | unit | `src/eval-server/__tests__/api-routes.git-status.test.ts` (new) |
| `GitStatusPill.tsx` | component | `src/eval-ui/src/components/__tests__/GitStatusPill.test.tsx` |
| `PublishDrawer.tsx` | component | `src/eval-ui/src/components/__tests__/PublishDrawer.test.tsx` |
| `useGitStatus.ts` | unit | `src/eval-ui/src/hooks/__tests__/useGitStatus.test.tsx` |
| `EditorPanel.tsx` Publish button | component | extend `src/eval-ui/src/pages/workspace/__tests__/EditorPanel.test.tsx` |

**Unit-test child-process mocking pattern** (Vitest):

```ts
import { vi } from "vitest";
const { execFileMock } = vi.hoisted(() => ({ execFileMock: vi.fn() }));
vi.mock("node:child_process", () => ({ execFile: execFileMock }));
// In tests: execFileMock.mockImplementation((cmd, args, cb) => cb(null, { stdout, stderr }));
```

The same pattern is already used by other `src/eval-server/__tests__/*.test.ts` files — we follow it verbatim for consistency.

**Integration tests** — two fixtures under `src/eval-server/__tests__/fixtures/`:

1. `repo-with-bare-remote/` — a parent git repo + bare remote on disk + a skill subdirectory inside the parent, plus extra unrelated dirty changes outside the skill subdirectory. Asserts:
   - `inspectSkillRepo(skillDir)` reports `dirty: true` for the skill changes.
   - `POST /git-publish` with `mode: 'push'` lands the commit on the bare remote.
   - The bare remote's commit is **scoped** — it does not include the unrelated dirty changes outside the skill directory.
   - Re-running the same flow after the remote has the commit is idempotent (no error on a clean second run).

2. `repo-no-remote/` — a parent git repo with no `origin` configured + MSW intercepting `https://api.github.com/repos/<owner>/<name>`. Asserts the `attach-remote-and-push` flow attaches origin and pushes.

**E2E** — `repositories/anton-abyzov/vskill/e2e/studio-publish-drawer.spec.ts`. Three scenarios using Playwright + `npx vskill@<dev-version> studio` against the three fixtures:

1. **Path A** — open studio → edit SKILL.md → Save → assert amber pill → click Publish → drawer renders with diff + streamed AI message → click Regenerate → assert new message → click Commit & Push → assert toast + pill clears + bare remote `git log` shows the commit.
2. **Path B** — same flow but `mode=create-via-gh`. Mocks `gh` via a shim on `PATH` that records its arguments and creates the repo on a local fake "GitHub" server.
3. **Path C** — same flow but `mode=attach-remote-and-push`. Mocks `api.github.com` with MSW; the test programmatically flips the mock from 404 to 200 mid-poll and asserts the drawer auto-pushes. A second sub-scenario keeps the mock at 404 for the full 60s and asserts the paste-url fallback appears.

**Coverage targets** (from CLAUDE.md): unit ≥ 95%, integration ≥ 90%, E2E covers 100% of AC scenarios across all three publish modes (NFR-007).

## Dependencies & Risks

**Dependencies**:
- Increment `0670-skill-builder-universal` MUST close before this increment activates. The increment is created at `status: planned` and only flips to `active` once 0670 closes.
- `git` CLI (required — every modern dev environment has it; we error out cleanly with a friendly message if `git --version` itself fails).
- `gh` CLI (optional — feature degrades to the browser-tab + polling path when missing, never errors).
- No new npm dependencies. No new ADR.

**Risks**:

1. **`gh auth status` output format may change across versions.** Mitigation: parse defensively with a permissive regex and accept "authenticated but username unparseable" as a valid state. Tests cover three known output formats from `gh` 2.40, 2.45, 2.50.
2. **`https://github.com/new` query-param contract is empirically observed, not formally documented.** Mitigation: this is a human-facing pre-fill — if GitHub ever drops the params, the form just opens blank and the user fills it manually. The polling mechanism still detects the repo by name and proceeds. We won't break, only degrade.
3. **`api.github.com` unauthenticated rate limit is 60/hr/IP** — a single drawer open can use up to 30 of those. A user opening the drawer twice within 30 minutes from the same IP is well under the limit. A user with a CI runner sharing the IP could plausibly hit it; in practice this is a developer-machine-only scenario and the fallback paste-url state covers it cleanly.
4. **`gh repo create --source=<dir> --push` requires the dir to already be a git repo** with at least one commit. The drawer's `gitStatus.isRepo` precondition (which gates `Publish` visibility) covers this. We add a server-side defensive re-check: if the skill repo has zero commits, the route returns 400 with "Initialize this folder as a git repo first" before invoking `gh`.
5. **Network/SSE stalls during long pushes**. Mitigation: reuse the existing `withHeartbeat` from `sse-helpers.ts` that already handles this for `/improve` — same heartbeat keeps proxies from idling out the connection.

## Rollout

- Single-commit feature, behind no flag — the MVP scope is small and self-contained, and every code path is gated by the existing `gitStatus.isRepo` precondition. There's no flag to gate because the feature is invisible (no pill, no Publish button) on folders that aren't git repos.
- Standard `/sw:npm` flow when this increment closes: commit → tag → npm publish → GitHub Release → push. No multi-stage rollout, no canary, no kill switch needed — the feature is purely additive on the studio surface.
- Backward compat: extending `SkillInfo` with optional `gitStatus`/`gh` is non-breaking; older cached responses still parse fine and the UI renders the no-pill / no-button fallback.
