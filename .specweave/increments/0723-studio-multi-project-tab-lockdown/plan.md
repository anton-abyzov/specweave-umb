# Implementation Plan: Studio Multi-Project Tab Lockdown

**Increment**: 0723-studio-multi-project-tab-lockdown
**Project**: vskill-platform
**Branch**: `feat/0723-studio-tab-lockdown` in `repositories/anton-abyzov/vskill-platform`
**Related ADR**: [0723-01-workspace-fingerprint-coordination.md](../../docs/internal/architecture/adr/0723-01-workspace-fingerprint-coordination.md)

---

## Architecture Overview

Each Studio tab captures a **workspace fingerprint** at load time. When the underlying workspace process changes (a new `vskill studio` invocation in a different folder, a process restart, etc.), every other tab detects it within ~1 second, enters a non-dismissable **lockdown** state, and refuses to send mutations. The server independently rejects mutations whose fingerprint header is stale via HTTP 409 (defence-in-depth).

```
┌─────────── Tab A (loaded for ~/alpha) ───────────┐
│  initialFingerprint = "a4f9c2d1"                 │
│  authFetch sends X-Workspace-Fingerprint: a4f9.. │
└─────────────────┬────────────────────────────────┘
                  │ BroadcastChannel("vskill-studio")
                  ↓
┌─────────── Tab B (just opened for ~/beta) ───────┐
│  fetches /api/v1/studio/workspace-info           │
│  → { fingerprint: "b7e3a8f2", root, repoUrl }    │
│  broadcasts { type: "workspace-checked" }        │
└─────────────────┬────────────────────────────────┘
                  ↓ Tab A receives broadcast
                  ↓ → re-fetches /workspace-info
                  ↓ → sees b7e3a8f2 ≠ a4f9c2d1
                  ↓ → triggers LOCKDOWN
                  ↓ → fires telemetry
                  ↓ → renders ProjectChangedModal

┌─────────── Server (next API route) ──────────────┐
│  on every mutating studio/* request:             │
│   if header "X-Workspace-Fingerprint" present    │
│      and != current fingerprint                  │
│   → 409 { code: "WORKSPACE_FINGERPRINT_MISMATCH" │
│           current, was }                         │
└──────────────────────────────────────────────────┘
```

**Fingerprint construction** (server-side, derived once per process boot):

```ts
const BOOT_ID = randomUUID();                              // module-load constant
const ROOT = path.resolve(process.env.STUDIO_WORKSPACE_ROOT ?? process.cwd());
const FINGERPRINT = sha256(`${BOOT_ID}:${ROOT}`).slice(0, 12);
```

Same root + same process → same fingerprint. Restart Studio (even on the same root) → new BOOT_ID → new fingerprint → all open tabs lock. This is correct: a restart implies state may have changed.

---

## Server-Side Design

### `src/lib/workspace-fingerprint.ts` (NEW)

Module-level boot ID + helpers. The cache strategy is the load-bearing decision: the existing `workspaceInfoCache` continues to cache only the slow git lookup (`repoUrl`); the fingerprint itself is recomputed on every call (it's a single sha256 of a 36-char UUID + a path — sub-microsecond).

```ts
import { randomUUID, createHash } from "node:crypto";
import path from "node:path";
import type { NextRequest } from "next/server";

// Module-load constant — survives for the lifetime of the Node process.
// A process restart (any reason) → new BOOT_ID → all tabs lock.
const BOOT_ID = randomUUID();

export function getWorkspaceFingerprint(root: string): string {
  const resolved = path.resolve(root);
  return createHash("sha256").update(`${BOOT_ID}:${resolved}`).digest("hex").slice(0, 12);
}

export class WorkspaceMismatchError extends Error {
  readonly current: string;
  readonly was: string;
  constructor(current: string, was: string) {
    super("WORKSPACE_FINGERPRINT_MISMATCH");
    this.name = "WorkspaceMismatchError";
    this.current = current;
    this.was = was;
  }
}

// Returns the server's current fingerprint when the header is absent (back-compat
// for non-Studio clients) or matches. Throws WorkspaceMismatchError when the
// header is present and differs.
export function assertWorkspaceFingerprint(
  request: NextRequest,
  currentRoot: string,
): string {
  const current = getWorkspaceFingerprint(currentRoot);
  const sent = request.headers.get("x-workspace-fingerprint");
  if (sent && sent !== current) {
    throw new WorkspaceMismatchError(current, sent);
  }
  return current;
}
```

### `src/app/api/v1/studio/workspace-info/route.ts` (EDIT)

Extend the response with `fingerprint` and `root`. The cache only stores the slow git lookup result (the existing behaviour is preserved); the fingerprint is recomputed on every request because it's cheap and must reflect real-time process state.

```ts
// Response shape: { repoUrl: string | null, fingerprint: string | null, root: string | null }
// repoUrl: cached per-root (slow git lookup)
// fingerprint: not cached (cheap; tied to process lifetime)
// root: returned as-is for client display in lockdown modal
```

If `getStudioWorkspaceRoot()` returns null (no env var, no cwd), all three fields are null and lockdown infra stays inert.

### `src/app/api/v1/studio/telemetry/[kind]/route.ts` (EDIT)

Three changes:

1. Add `"lockdown"` to the `KINDS` tuple with its own Zod schema:
   ```ts
   const lockdownSchema = z.object({
     reason: z.enum(["broadcast", "visibility", "focus", "api-409"]),
     originalFingerprint: z.string().length(12),
     newFingerprint: z.string().length(12),
     ts: z.number().int().positive(),
   });
   ```
2. Call `assertWorkspaceFingerprint(req, getStudioWorkspaceRoot()!)` near the top of the handler. On `WorkspaceMismatchError`, respond `409 { code: "WORKSPACE_FINGERPRINT_MISMATCH", current, was }`.
3. After the existing DB write, when `kind === "lockdown"`, also write to the `STUDIO_LOCKDOWN_AE` Analytics Engine binding:
   ```ts
   env.STUDIO_LOCKDOWN_AE.writeDataPoint({
     blobs: ["lockdown", parsed.data.reason],
     doubles: [Date.now()],
   });
   ```
   (`env` accessed via `getCloudflareContext()` — the existing CF binding pattern in this repo.)

The fingerprint assert runs **before** the rate-limit check is irrelevant because the check is fast and must apply regardless. Order: parse params → fingerprint assert → rate-limit → JSON parse → schema validate → DB write → AE write → 204.

The `lockdown` kind specifically MUST NOT enforce the fingerprint header (the whole point is that it's the locked tab telling the server it's locked) — bypass for that one kind only.

### `wrangler.jsonc` (EDIT)

Add to `analytics_engine_datasets` (the array currently contains only `UPDATE_METRICS_AE`):

```jsonc
"analytics_engine_datasets": [
  // 0708: scanner / DO / delivery / queue metrics sink (AC-US1-07, NFR-007).
  { "binding": "UPDATE_METRICS_AE", "dataset": "skill_update_metrics" },
  // 0723: Studio lockdown trigger telemetry (AC-US6-03).
  { "binding": "STUDIO_LOCKDOWN_AE", "dataset": "studio_lockdown_events" }
]
```

Dimensions per event: `blob1 = "lockdown"` (kind tag, future-proofs against other studio events sharing the dataset), `blob2 = reason`, `double1 = ts`. Dashboard query: `SELECT count() FROM studio_lockdown_events WHERE blob1 = 'lockdown' GROUP BY blob2`.

---

## Client-Side Design

### `src/lib/lockdown-state.ts` (NEW)

A **module-level singleton**, deliberately not a React context. The reason: `authFetch` (a non-React module) needs to read `isLocked` and `initialFingerprint` synchronously per request. Bridging a context across a non-React module would require an awkward `setState` callback indirection. A singleton with a `Set<() => void>` subscriber list, consumed in React via `useSyncExternalStore`, is the React 18+ canonical pattern for this exact case.

```ts
type LockdownReason = "broadcast" | "visibility" | "focus" | "api-409";

interface State {
  initialFingerprint: string | null;
  originalRepoUrl: string | null;
  originalRoot: string | null;
  isLocked: boolean;
  lockReason: LockdownReason | null;
  currentFingerprint: string | null;
  currentRepoUrl: string | null;
  currentRoot: string | null;
}

const state: State = {
  initialFingerprint: null, originalRepoUrl: null, originalRoot: null,
  isLocked: false, lockReason: null,
  currentFingerprint: null, currentRepoUrl: null, currentRoot: null,
};

const subscribers = new Set<() => void>();

function notify() { for (const fn of subscribers) fn(); }

export function init(initial: { fingerprint: string; repoUrl: string | null; root: string }) {
  // Idempotent — only sets if not already initialised
  if (state.initialFingerprint !== null) return;
  state.initialFingerprint = initial.fingerprint;
  state.originalRepoUrl = initial.repoUrl;
  state.originalRoot = initial.root;
  notify();
}

export function setLocked(
  reason: LockdownReason,
  current: { fingerprint: string; repoUrl: string | null; root: string },
) {
  if (state.isLocked) return;  // first lock wins; subsequent triggers are no-ops
  state.isLocked = true;
  state.lockReason = reason;
  state.currentFingerprint = current.fingerprint;
  state.currentRepoUrl = current.repoUrl;
  state.currentRoot = current.root;
  notify();
}

export function subscribe(fn: () => void): () => void {
  subscribers.add(fn);
  return () => subscribers.delete(fn);
}

export function getSnapshot(): Readonly<State> { return state; }
export function getInitialFingerprint(): string | null { return state.initialFingerprint; }
export function isLocked(): boolean { return state.isLocked; }
```

Key invariants:
- **First lock wins** — once locked, subsequent triggers are silently dropped (prevents telemetry spam if multiple detection paths fire simultaneously).
- **`init` is idempotent** — a stray double-mount of `LockdownProvider` (e.g., during dev hot reload) does not reset the original fingerprint.
- **No `unlock` API** — the only way out of lockdown is a full page reload.

### `src/lib/lockdown-error.ts` (NEW)

```ts
export class LockdownError extends Error {
  readonly reason: string;
  constructor(reason: string) {
    super(`Studio is locked: ${reason}`);
    this.name = "LockdownError";
    this.reason = reason;
  }
}
```

Typed so existing try/catch sites can do `if (err instanceof LockdownError)` and present a non-network-error message.

### `src/lib/auth-fetch.ts` (EDIT)

Three additions, all narrow:

1. **Fingerprint header**: read `getInitialFingerprint()` once at the start; if non-null, add `X-Workspace-Fingerprint: <value>` to the outgoing headers.
2. **Pre-flight lockdown check**: if `isLocked()` AND method ∈ `{POST, PUT, PATCH, DELETE}`, throw `LockdownError("pre-flight")` before the network call.
3. **Post-response 409 handler**: if `response.status === 409`, parse the body; if `body.code === "WORKSPACE_FINGERPRINT_MISMATCH"`, fetch fresh `/workspace-info` to learn the new repoUrl/root, call `setLocked("api-409", fresh)`, then throw `LockdownError("api-409")`.

The 401-refresh logic is preserved unchanged — lockdown is layered on top.

```ts
export async function authFetch(input: RequestInfo | URL, init?: RequestInit): Promise<Response> {
  const method = (init?.method ?? "GET").toUpperCase();
  const isMutation = method === "POST" || method === "PUT" || method === "PATCH" || method === "DELETE";

  if (isLocked() && isMutation) {
    throw new LockdownError("pre-flight");
  }

  const fp = getInitialFingerprint();
  const headers = new Headers(init?.headers);
  if (fp) headers.set("X-Workspace-Fingerprint", fp);

  const response = await fetch(input, { credentials: "include", ...init, headers });

  if (response.status === 409) {
    const body = await response.clone().json().catch(() => null);
    if (body && (body as { code?: string }).code === "WORKSPACE_FINGERPRINT_MISMATCH") {
      // Refresh workspace info to get current repoUrl/root for the modal
      const fresh = await fetch("/api/v1/studio/workspace-info").then((r) => r.json()).catch(() => null);
      if (fresh && fresh.fingerprint) {
        setLocked("api-409", fresh);
      }
      throw new LockdownError("api-409");
    }
  }

  if (response.status !== 401) return response;

  const refreshed = await attemptRefresh();
  if (!refreshed) return response;

  return fetch(input, { credentials: "include", ...init, headers });
}
```

### `src/app/components/LockdownProvider.tsx` (NEW)

Client component, mounted in `layout.tsx` outside `LayoutShell` so the modal sits above nav/footer. Owns four side effects:

1. **Initial fetch on mount**: `GET /api/v1/studio/workspace-info` → `lockdown-state.init()`. If fetch fails or fingerprint is null, stays inert (graceful degradation per AC-US1-04).
2. **`BroadcastChannel("vskill-studio")` listener**: on `workspace-checked` message, re-fetch `/workspace-info` and compare. If mismatch → `setLocked("broadcast", fresh)`. The provider also broadcasts `workspace-checked` after its own initial fetch succeeds so other tabs notice it.
3. **`visibilitychange` and `focus` listeners**: when document becomes visible OR window gains focus, re-fetch `/workspace-info` and compare. If mismatch → `setLocked("visibility" | "focus", fresh)`.
4. **Lockdown trigger telemetry**: subscribes to `lockdown-state`. On the transition from `isLocked: false → true`, fire-and-forget `POST /api/v1/studio/telemetry/lockdown` with `{ reason, originalFingerprint, newFingerprint, ts }`. Uses fresh `fetch` (not `authFetch`) to bypass the pre-flight lockdown check since this is the lockdown event itself.

Renders `<ProjectChangedModal />` conditionally via `useSyncExternalStore` on the singleton.

```tsx
"use client";

import { useEffect, useSyncExternalStore } from "react";
import { init, setLocked, subscribe, getSnapshot } from "@/lib/lockdown-state";
import ProjectChangedModal from "./ProjectChangedModal";

export function useLockdown() {
  return useSyncExternalStore(subscribe, getSnapshot, getSnapshot);
}

async function fetchWorkspaceInfo(): Promise<{ fingerprint: string; repoUrl: string | null; root: string } | null> {
  try {
    const res = await fetch("/api/v1/studio/workspace-info");
    if (!res.ok) return null;
    const json = await res.json();
    if (!json.fingerprint || !json.root) return null;
    return { fingerprint: json.fingerprint, repoUrl: json.repoUrl, root: json.root };
  } catch {
    return null;
  }
}

export default function LockdownProvider({ children }: { children: React.ReactNode }) {
  const snapshot = useSyncExternalStore(subscribe, getSnapshot, getSnapshot);

  useEffect(() => {
    let cancelled = false;
    let channel: BroadcastChannel | null = null;
    let prevLocked = false;

    (async () => {
      const initial = await fetchWorkspaceInfo();
      if (cancelled || !initial) return;
      init(initial);

      // Establish coordination only when we have a fingerprint
      if (typeof BroadcastChannel !== "undefined") {
        channel = new BroadcastChannel("vskill-studio");
        channel.postMessage({ type: "workspace-checked" });
        channel.onmessage = async (e) => {
          if (e.data?.type === "workspace-checked") {
            const fresh = await fetchWorkspaceInfo();
            if (fresh && fresh.fingerprint !== initial.fingerprint) {
              setLocked("broadcast", fresh);
            }
          }
        };
      }
    })();

    const onVisibilityOrFocus = async (evt: Event) => {
      if (evt.type === "visibilitychange" && document.visibilityState !== "visible") return;
      const fresh = await fetchWorkspaceInfo();
      const initial = getSnapshot().initialFingerprint;
      if (fresh && initial && fresh.fingerprint !== initial) {
        setLocked(evt.type === "focus" ? "focus" : "visibility", fresh);
      }
    };
    document.addEventListener("visibilitychange", onVisibilityOrFocus);
    window.addEventListener("focus", onVisibilityOrFocus);

    // Telemetry on lock transition
    const unsub = subscribe(() => {
      const s = getSnapshot();
      if (s.isLocked && !prevLocked) {
        prevLocked = true;
        fetch("/api/v1/studio/telemetry/lockdown", {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({
            reason: s.lockReason,
            originalFingerprint: s.initialFingerprint,
            newFingerprint: s.currentFingerprint,
            ts: Date.now(),
          }),
        }).catch(() => {});
      }
    });

    return () => {
      cancelled = true;
      channel?.close();
      document.removeEventListener("visibilitychange", onVisibilityOrFocus);
      window.removeEventListener("focus", onVisibilityOrFocus);
      unsub();
    };
  }, []);

  return (
    <>
      {children}
      {snapshot.isLocked && <ProjectChangedModal />}
    </>
  );
}
```

### `src/app/components/ProjectChangedModal.tsx` (NEW)

Pure presentation. Reads from `useLockdown()` for original/current paths. See **UI Design Brief** below for visual spec.

### `src/app/layout.tsx` (EDIT)

Wrap `LayoutShell` (and its children) inside `LockdownProvider`. The modal then renders above all routed content automatically.

```tsx
<LockdownProvider>
  <LayoutShell nav={navContent} footer={footerContent}>
    {children}
  </LayoutShell>
</LockdownProvider>
```

`LockdownProvider` must be inside `Suspense` and inside `AuthProvider` so it doesn't disrupt those boundaries.

---

## UI Design Brief

(Output of the `frontend-design` skill engagement, captured here per AC-US5-08. The implementation in `ProjectChangedModal.tsx` follows this brief literally.)

### Aesthetic direction

Terminal lockdown — the modal reads as "the system has stopped" rather than "a popup is asking you something." Borrows the existing `error.tsx` terminal-block vocabulary verbatim so users perceive it as part of vskill, not an overlay library.

### Layout (visual hierarchy)

```
┌──────────────────────────────────────────────────────┐
│   [!]  PROJECT CHANGED                               │  ← header rail (~12% weight)
├──────────────────────────────────────────────────────┤
│                                                       │
│   $ vskill --status                                   │  ← terminal block (~70% weight)
│   ERR! workspace fingerprint mismatch                 │
│                                                       │
│   was: anton-abyzov/alpha                             │
│        /Users/anton/Projects/alpha                    │
│                                                       │
│   now: anton-abyzov/beta                              │
│        /Users/anton/Projects/beta                     │
│                                                       │
│   > This tab is locked. Unsaved changes here          │
│     are not persisted._                               │
│                                                       │
├──────────────────────────────────────────────────────┤
│  [ Reload as anton-abyzov/beta ]  [ Open original ↗ ] [ × Close tab ] │
│  Run `vskill studio` from /Users/anton/Projects/alpha │  ← hint, only under "Open"
└──────────────────────────────────────────────────────┘
```

### Color palette mapping

| Element | Token |
|---|---|
| Backdrop | `rgba(0,0,0,0.75)` + `backdrop-filter: blur(12px)` |
| Card shell | `var(--surface)` bg, `1px solid var(--border)`, 6px radius |
| Card outer shadow | `0 24px 60px rgba(0,0,0,0.45)` |
| Header rail bg | `var(--bg-subtle)` |
| Warning glyph `[!]` | `var(--accent-amber)` foreground, `1px solid var(--accent-amber)` box |
| Headline `PROJECT CHANGED` | `var(--text)`, mono, 0.875rem, letter-spacing 0.08em, uppercase |
| Terminal block bg | `var(--bg-code)` |
| `$ vskill --status` line | `var(--code-green)` |
| `ERR!` line | `var(--code-red)` |
| `was:` / `now:` labels | `var(--text-faint-terminal)` |
| `was:` value (stale) | `var(--code-red)` |
| `now:` value (live) | `var(--accent-amber)` |
| Body explainer (`>` prefix + cursor) | `#E6EDF3` (matches error.tsx body line literally) |
| Action rail bg | `var(--bg-subtle)` |
| Primary button | bg `var(--btn-bg)`, color `var(--btn-text)` |
| Secondary button | transparent bg, `1px solid var(--border)`, `var(--text)` |
| Tertiary button | transparent bg, `1px solid transparent` (border on hover), `var(--text-faint)` |
| Hint text | `var(--text-faint-terminal)`, mono 0.75rem |

No hard-coded colors anywhere except `rgba(0,0,0,0.75)` for the backdrop (intentionally theme-independent).

### Warning glyph

`[!]` rendered as bracketed exclamation in monospace, 0.875rem, `var(--accent-amber)` text with a 1px amber border on the inline-block span. Rejected `⚠` (cross-platform emoji rendering inconsistency) and `❗` (consumer-y). Bracketed ASCII reads as "log severity tag" — the right register for terminal aesthetic.

### Micro-copy

- Headline: **`PROJECT CHANGED`** (uppercase, letter-spaced)
- Terminal line 1: **`$ vskill --status`** (matches error.tsx)
- Terminal line 2: **`ERR! workspace fingerprint mismatch`**
- `was:` two-line: `was: <repo-short-name>` / `<originalRoot>` (root indented 2 spaces)
- `now:` two-line: `now: <repo-short-name>` / `<currentRoot>`
- Body line: **`> This tab is locked. Unsaved changes here are not persisted._`** (with blinking `terminal-cursor`)
- Primary button: **`Reload as <new-short-name>`**
- Secondary button: **`Open <original-short-name> ↗`**
- Hint under secondary: ``Run `vskill studio` from <originalRoot>``
- Tertiary button: **`× Close tab`**
- Tertiary fallback (if `window.close()` is blocked): inline below the row, `var(--text-faint)`: **`Browser blocked auto-close — close this tab manually.`**

`<repo-short-name>` derives from `repoUrl` via `normalizeGitHubRemote` then taking the last two path segments. If `repoUrl` is null, fall back to `path.basename(root)`.

### Action button affordances

- **Primary `Reload as <new>`**: `window.location.reload()`. Solid background. The recommended action — visually loudest.
- **Secondary `Open <original> ↗`**: `window.open(window.location.origin, "_blank", "noopener,noreferrer")`. Outlined. The hint text below clarifies why this works (a new Studio process needs to be started in the original folder).
- **Tertiary `× Close tab`**: `window.close()`. Borderless until hover. If `window.close()` returns silently and the tab is still alive after 250ms, the inline fallback message renders.

### Accessibility

- `role="alertdialog"` on card root
- `aria-modal="true"` on card root
- `aria-labelledby="lockdown-title"` (headline span has matching `id`)
- `aria-describedby="lockdown-desc"` (wraps body explainer)
- **Focus management**: on mount, `useEffect` calls `primaryButtonRef.current?.focus()`. The previously focused element is captured but never restored (no return path).
- **Focus trap**: `keydown` handler at card root listens for `Tab` and `Shift+Tab`. Cycles strictly within the three button refs. `Escape` is captured and `preventDefault`'d silently.
- **No backdrop click handler** at all (more honest than `e.stopPropagation` indirection).
- Screen reader: when `isLocked` flips true, `alertdialog` is announced; headline speaks first, then body.
- All three buttons are real `<button type="button">` elements.

### Responsive (below 540px viewport)

- Card max-width: `calc(100vw - 32px)`, padding reduces from `1.75rem` → `1.25rem`
- Header glyph + headline stay inline (one unit)
- Action rail switches `flex-direction: row` → `column`, gap `0.5rem`
- Buttons go full-width (`width: 100%`)
- Order on mobile: primary (top), secondary (middle), tertiary (bottom)
- Terminal block padding reduces `1.25rem 1.5rem` → `1rem 1rem`
- Long paths get `overflow-wrap: anywhere`

### Dark mode parity

Confirmed: every color is a CSS custom property already in `globals.css`. The card automatically inverts via the existing `[data-theme="dark"]` selector. No `prefers-color-scheme` checks needed. The only literal value (`rgba(0,0,0,0.75)` backdrop) is intentionally theme-independent.

---

## Files to Create / Modify

| Path | Change | LOC est. |
|---|---|---|
| `src/lib/workspace-fingerprint.ts` | NEW — `BOOT_ID` + `getWorkspaceFingerprint()` + `assertWorkspaceFingerprint()` + `WorkspaceMismatchError` | ~40 |
| `src/lib/lockdown-state.ts` | NEW — module-level singleton (`init`, `setLocked`, `subscribe`, `getSnapshot`, `getInitialFingerprint`, `isLocked`) | ~60 |
| `src/lib/lockdown-error.ts` | NEW — `LockdownError` typed class | ~10 |
| `src/lib/auth-fetch.ts` | EDIT — add fingerprint header + pre-flight lockdown check + 409 handler | +30 |
| `src/app/api/v1/studio/workspace-info/route.ts` | EDIT — extend response with `fingerprint` + `root`; cache only `repoUrl` | +10 |
| `src/app/api/v1/studio/telemetry/[kind]/route.ts` | EDIT — add `lockdown` kind + schema; call `assertWorkspaceFingerprint` (skip for `lockdown` kind itself); wire AE | +40 |
| `src/app/components/LockdownProvider.tsx` | NEW — client component (BroadcastChannel + visibility/focus + telemetry firing + `useLockdown` hook) | ~120 |
| `src/app/components/ProjectChangedModal.tsx` | NEW — pure presentation, designed via UI Design Brief | ~180 |
| `src/app/layout.tsx` | EDIT — wrap `LayoutShell` in `LockdownProvider` | +3 |
| `wrangler.jsonc` | EDIT — add `STUDIO_LOCKDOWN_AE` Analytics Engine binding | +2 |

**Existing utilities reused (do not re-create)**: `workspaceInfoCache`, `normalizeGitHubRemote`, `authFetch` (extended), CSS tokens in `globals.css`, modal overlay pattern from `ReportProblemModal`, terminal-block visual language from `error.tsx`.

**Schema unchanged**: `studioTelemetry` already accepts arbitrary `kind` strings — no Prisma migration.

---

## Risk Mitigations

| Risk | Mitigation |
|---|---|
| **`BroadcastChannel` not in Safari < 15.4** | Graceful degradation — `typeof BroadcastChannel !== "undefined"` check skips channel setup; visibility/focus polling still detects within 1s |
| **Server fingerprint cached across restarts** | Fingerprint is **never** cached. The existing `workspaceInfoCache` caches only `repoUrl` (the slow git lookup). Fingerprint is recomputed on every request — sub-microsecond cost |
| **Mid-process env-var changes** | Cache key is `root`; if `STUDIO_WORKSPACE_ROOT` flips, cache miss → fresh `repoUrl` lookup. Fingerprint recompute is automatic |
| **React 18 concurrent rendering** | `useSyncExternalStore` is the canonical primitive for the singleton subscription — handles tearing correctly |
| **Header pollutes HTTP cache** | `X-Workspace-Fingerprint` only sent on mutating verbs; no `Vary` header added to GETs. Cacheable GETs are unaffected |
| **Telemetry endpoint locks itself out** | The `lockdown` kind specifically bypasses `assertWorkspaceFingerprint` — the locked tab needs to be able to report its lockdown |
| **Multiple detection paths fire simultaneously** | `setLocked` short-circuits when already locked → first lock wins; no telemetry spam |
| **Stray hot-reload double-mount of `LockdownProvider`** | `init` is idempotent (early return if `initialFingerprint` already set) |
| **Focus restoration after unlock** | N/A — there is no unlock path. Reload is the only recovery, which discards the focus context anyway |
| **`window.close()` blocked by browser** | 250ms after-the-call check renders inline fallback message: "Browser blocked auto-close — close this tab manually." |

---

## Testing Strategy

### Unit (Vitest)
- `workspace-fingerprint.test.ts`:
  - `getWorkspaceFingerprint(root)` is deterministic within a process
  - Different `root` values → different fingerprints
  - Length is exactly 12 chars, hex-only
  - `assertWorkspaceFingerprint` returns current when header absent (back-compat)
  - `assertWorkspaceFingerprint` returns current when header matches
  - `assertWorkspaceFingerprint` throws `WorkspaceMismatchError` with `current` and `was` when header differs
- `lockdown-state.test.ts`:
  - `init` is idempotent (second call ignored)
  - `setLocked` sets `isLocked: true` and notifies subscribers
  - `setLocked` is no-op when already locked (first lock wins)
  - `subscribe` returns an unsubscribe function that detaches
  - `getSnapshot` returns the same object reference until state changes (for `useSyncExternalStore` correctness)
- `auth-fetch.test.ts`:
  - GET passes through unchanged
  - Mutating method when `isLocked()` → throws `LockdownError("pre-flight")` without network call
  - Mutating method when not locked → adds `X-Workspace-Fingerprint` header
  - 409 with `code: WORKSPACE_FINGERPRINT_MISMATCH` body → calls `setLocked("api-409", ...)` and throws
  - 409 with other code → returned as-is, no lockdown
  - 401 refresh path still works alongside lockdown layer

### Integration (Vitest, route handlers)
- `workspace-info/route.test.ts`:
  - Returns `{ repoUrl, fingerprint, root }` shape
  - Fingerprint is hex 12 chars
  - Repeated calls → same fingerprint within process
  - `repoUrl` is cached (second call doesn't re-exec git)
- `telemetry/[kind]/route.test.ts`:
  - `lockdown` kind accepts valid payload, returns 204
  - `lockdown` kind validates `reason` enum
  - Mismatched fingerprint header on `submit-click` → 409 with `code: WORKSPACE_FINGERPRINT_MISMATCH`, `current`, `was`
  - Missing fingerprint header → still accepted (back-compat)
  - `lockdown` kind specifically does NOT enforce the header (so locked tab can report)
  - AE binding called with `blobs: ["lockdown", reason]`, `doubles: [ts]` (mock the binding)

### E2E (Playwright, `studio-lockdown.spec.ts`)
- Modal renders when `isLocked` is true (mock `/workspace-info` to return mismatch on second call)
- Modal has `role="alertdialog"`, `aria-modal="true"`, `aria-labelledby`, `aria-describedby` attributes
- Pressing `Escape` does NOT close the modal
- Clicking the backdrop does NOT close the modal
- `Tab` cycles focus among the three action buttons; `Shift+Tab` reverses
- Initial focus is on the primary `Reload as ...` button
- All three buttons render with correct text
- Mobile viewport (< 540px): buttons stack vertically and go full-width
- Telemetry POST fires once when lockdown activates (verify via network intercept)

### Coverage targets
- Unit: 95%
- Integration: 90%
- E2E: 100% of AC scenarios

---

## ADR References

- **NEW**: [ADR 0723-01: Workspace fingerprint as single-tab coordination primitive](../../docs/internal/architecture/adr/0723-01-workspace-fingerprint-coordination.md) — documents the choice of server fingerprint + `BroadcastChannel` over alternatives (Durable Object + WebSocket, polling, server-sent events)

---

## Out of Scope (Explicit)

- Guarding non-Studio mutating endpoints (admin queue, problem-reports, auth refresh) — follow-up after this lands
- Cross-device coordination — naturally handled because each device hits its own local Studio process
- Persisting `originalRepoUrl` across reload — held in component state, not needed after reload
- Auto-recovery ("click to switch and continue") — reload is the only path forward
- Service-worker–based detection — overkill for local-only use case
