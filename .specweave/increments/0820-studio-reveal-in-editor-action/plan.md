# Implementation Plan: Studio Reveal in Editor action

## Overview

Add a single `POST /api/skills/reveal-in-editor` endpoint to the eval-server that resolves the user's preferred editor and spawns it on a skill path. Wire the three sidebar context-menu actions (Open / Reveal in Editor / Edit) to the endpoint. Replace the stale `editPlaceholder` toast string with real success/failure copy.

## Architecture

### Components

- **`src/eval-server/utils/resolve-editor.ts`** *(new)* — Pure helper. `resolveEditorCommand(target, env, platform, which)` returns `{ command, args }`. Pure means no I/O on import; the `which`, `env`, and `platform` args are injectable for deterministic tests. A `defaultWhich` is exported with a process-lifetime cache.
- **`src/eval-server/api-routes.ts`** *(edit)* — Registers `router.post("/api/skills/reveal-in-editor", …)`. Body `{ plugin, skill, file? }`. Validates inputs, resolves the dir via `scanSkillInstallLocations`, derives the spawn target (`dir` or `join(dir, file)`), calls `resolveEditorCommand`, and `spawn`s detached/unref'd.
- **`src/eval-ui/src/api.ts`** *(edit)* — Adds `revealInEditor(plugin, skill, file?)` to the exported `api` object. Pattern matches `setConfig` (`fetchJson` + JSON body).
- **`src/eval-ui/src/hooks/useContextMenuState.ts`** *(edit)* — Splits the collapsed `case "open" | "reveal" | "edit":` placeholder into three branches that call `api.revealInEditor` and dispatch toasts based on response/error.
- **`src/eval-ui/src/strings.ts`** *(edit)* — Removes `actions.editPlaceholder`. Adds 4 new entries to `toasts`: `openingInEditor`, `noEditor`, `openFailed`, `skillNotFound`.

### API Contract

```http
POST /api/skills/reveal-in-editor
Content-Type: application/json

{ "plugin": "<plugin-or-empty-for-personal>", "skill": "<skill-name>", "file": "SKILL.md" }
```

**200**: `{ "ok": true, "command": "code", "args": ["--reuse-window", "/abs/path/to/SKILL.md"] }`
**400 invalid_body**: missing/blank `plugin` or `skill`.
**400 invalid_file**: `file` contains `/`, `\`, or `..` segments (or empty string).
**404 skill_not_found**: `(plugin, skill)` resolved to no install location.
**404 file_not_found**: `file` is a clean basename but absent on disk.
**500 no_editor**: every editor candidate failed to resolve (no `$VISUAL`/`$EDITOR`, `code`/`cursor` not on PATH, OS default missing).
**500 spawn_failed**: `spawn` errored (e.g. dir deleted between resolve and spawn).

### Editor Resolution

```
$VISUAL  →  $EDITOR  →  code (PATH)  →  cursor (PATH)
                                            ↓
                          darwin: open <path>
                          linux:  xdg-open <path>
                          win32:  cmd /c start "" <path>
```

`$VISUAL` and `$EDITOR` are split on whitespace. The first token is the command, remaining tokens are flags, and the resolved path is **always appended last** so flag-injection cannot displace it.

### Security Decisions

- **Server re-resolves the dir** from `(plugin, skill)`. The client cannot supply an arbitrary path — the only attack surface is the choice of `(plugin, skill)`, which `scanSkillInstallLocations` already restricts to known install roots with traversal defenses.
- **`file` is basename-validated**: rejects on `/`, `\`, `..`-as-segment, or empty string.
- **`existsSync` check** on the final path before spawn — distinguishes "skill malformed (no SKILL.md)" from "spawn failed for some other reason."
- **`spawn` with argv array** (no shell). The resolved path is the last argv element so a malicious `$VISUAL` cannot put it in a flag position.

## Technology Stack

- **Language**: TypeScript (existing).
- **Server framework**: existing custom router (`src/eval-server/router.ts`).
- **Process spawn**: `node:child_process` `spawn` (async, detached, unref).
- **Testing**: Vitest with `vi.hoisted()` + `vi.mock()`.

**Architecture Decisions**:
- **Why `(plugin, skill)` instead of accepting `dir`?** Trusting client-supplied paths lets a malicious localhost page open arbitrary files in the user's editor. Re-resolving server-side makes the attack surface = the existing scope-resolver, which is already hardened.
- **Why detached/unref'd spawn?** The endpoint must return immediately. Editors typically take 100ms-2s to render; blocking on stdout would tie up the request thread.
- **Why route `edit` to the same flow as `reveal` for now?** The original `editPlaceholder` promised inline editing "lands with 0675" — that increment never happened. Routing `edit` externally is a strict improvement over a stub toast, and keeps the menu functional while inline-editing is deferred.

## Implementation Phases

### Phase 1: Server foundations
- T-001: Create `resolve-editor.ts` with deterministic, injected-dep tests.
- T-002: Add the new POST route + body validation.

### Phase 2: UI wiring
- T-003: Add `api.revealInEditor` method.
- T-004: Replace the collapsed switch branch in `useContextMenuState.ts` with three real branches; add toast strings; remove placeholder.

### Phase 3: Test extension
- T-005: Extend the existing useContextMenuState test with assertions for fetch payload and toast dispatch in each of the three branches plus error paths.

## Testing Strategy

TDD red→green per `.specweave/config.json` `testing.defaultTestMode: "TDD"`:

1. Write `resolve-editor.test.ts` covering each rung of the resolution ladder + flag-handling + platform fallback.
2. Write `reveal-in-editor.test.ts` mocking `scanSkillInstallLocations`, `resolveEditorCommand`, and `child_process.spawn`. Assert handler returns the right `sendJson` payload for each AC scenario.
3. Extend `useContextMenuState.test.ts` to mock `fetch` and assert correct payload + toast dispatch for `open`, `reveal`, `edit`, plus 404/500/network-failure paths.
4. After green tests, run the full vitest suite to ensure no regression elsewhere.
5. Manual smoke per the verification section of the spec — start studio, right-click each origin type, exercise each menu item.

## Technical Challenges

### Challenge 1: Editor resolution must be deterministic in tests
**Solution**: `resolveEditorCommand` accepts `env`, `platform`, and `which` as parameters. Tests pin them; production calls use `process.env`, `process.platform`, and the cached `defaultWhich`.
**Risk**: defaults silently mask test bugs. Mitigation: every test passes its own `which` and `env` — no test relies on defaults.

### Challenge 2: Spawn errors are async
**Solution**: `spawn(cmd, args, opts)` reports `ENOENT` etc. via an `'error'` event on the returned ChildProcess. The route handler awaits the *spawn* (not the editor exiting) using a tiny Promise wrapper that resolves on the `'spawn'` event and rejects on `'error'`. Detached + unref means we don't wait for the editor to close.
**Risk**: race between `child.unref()` and an immediate spawn error. Mitigation: attach the `'error'` listener before `unref`, resolve the promise inside the `'spawn'` handler.

### Challenge 3: Plugin-cache scope skills have a different dir layout
**Solution**: `scanSkillInstallLocations` already abstracts this — it returns validated dirs across project / personal / plugin scopes with the precedence used by `/api/skills/updates`. We pick the first (highest-precedence) install.
**Risk**: a skill present only in plugin-cache might require a read-only edit. Mitigation: out of scope; opening a read-only file in an editor is acceptable Studio behavior (matches what VSCode does for cache files).
