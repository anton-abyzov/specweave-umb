# 0855 — Fix SSE notifications: token-gate exemption for EventSource stream path

**Status**: active
**Related**: 0836 (X-Studio-Token gate), 0838 (SSE diagnose/source-origin), 0850 (studio install feedback)

## Problem Statement

Skill Studio users stopped receiving live toast notifications for skill update / decision
events. The bell count still ticks (via a 5-minute fetch-polling fallback) but **no toast
ever appears** — the live `EventSource onmessage -> window "studio:toast" CustomEvent ->
ToastProvider` path never fires. User report: *"I never get a notification anymore."*

## Root Cause

Increment 0836 added a per-process `X-Studio-Token` gate to the eval-server router
(`repositories/anton-abyzov/vskill/src/eval-server/router.ts`, `tokenGate()`). Every
`/api/*` request must carry an `X-Studio-Token` HTTP **header**. The exemption list is
ONLY:

- non-`/api` paths (static / SPA shell)
- `OPTIONS` preflight
- `/api/health`
- `/api/oauth/github/callback`
- `/api/oauth/github/desktop-complete`

The notification stream `GET /api/v1/skills/stream` is **not** exempt. The client opens it
with the browser `EventSource` API:

```
// src/eval-ui/src/hooks/useSkillUpdates.ts:640
const url = `${streamBase}?skills=${encodeURIComponent(csvForSubscribe)}`;
// :740
es = new EventSource(url);
```

`EventSource` **cannot set custom request headers** — it is a fixed GET with no header
control. The token is injected by `StudioTokenBridge`
(`src/eval-ui/src/contexts/StudioTokenBridge.ts`), which monkey-patches `globalThis.fetch`
**only**. `EventSource` does not use `fetch`, so the stream request reaches the router
**without** `X-Studio-Token` and is 401'd before it can be proxied upstream to the
platform UpdateHub. The live toast path is severed; only the polling fallback survives.

Verbatim gate (router.ts `tokenGate`, ~lines 157-211):

```ts
// Non-/api paths are static / SPA shell — never gated.
if (!pathname.startsWith("/api/")) return true;
if ((req.method || "GET").toUpperCase() === "OPTIONS") return true;
if (pathname === "/api/health") return true;
if (pathname === "/api/oauth/github/callback") return true;
if (pathname === "/api/oauth/github/desktop-complete") return true;

const supplied = readHeader(req, "x-studio-token");
const expected = getStudioToken();
if (tokensEqual(supplied, expected)) return true;
// ... 401, warn log (path + method only)
```

## Why not just blanket-exempt /stream

0836's gate is a security boundary: it stops a DNS-rebinding attack or *any* random
localhost browser tab from reaching the bearer-injecting platform proxy
(`/api/v1/account/*`, `/api/v1/private/*` inject a GitHub bearer Rust-side). Blanket-
exempting `/api/v1/skills/stream` would re-open a hole for any localhost tab to open the
stream. We must preserve the security property: **only a caller that already knows the
per-process token may open the stream.** The fix delivers the token via the one channel
`EventSource` *can* carry — a query param — validated with the same timing-safe compare.

## User Stories

### US-001 — Live toast notification on skill update/decision event
As a Skill Studio user, when a skill update or decision event fires upstream, I want a
toast to pop in the studio in real time (not just a silent bell increment), so I know
something happened without waiting up to 5 minutes for the polling fallback.

**Acceptance Criteria**
- **AC-US1-01**: `GET /api/v1/skills/stream?studioToken=<valid>` PASSES the token gate
  (not 401) and is forwarded to the platform proxy.
- **AC-US1-02**: The client `EventSource` URL for the notification stream includes
  `?studioToken=<current-token>` so the browser-side `EventSource` (which cannot set
  headers) authenticates the gate.
- **AC-US1-03**: An end-to-end SSE open against the eval-server returns `200` with
  `content-type: text/event-stream` (NOT 401) when the valid token is supplied as a
  query param.

### US-002 — Exemption must not weaken 0836's security boundary
As the platform owner, I require the new query-param exemption to preserve 0836's
guarantee: an unknown caller still cannot open the stream, and the token is never
logged or leaked upstream.

**Acceptance Criteria**
- **AC-US2-01**: `GET /api/v1/skills/stream` with a **missing** `studioToken` (and no
  header) is still 401.
- **AC-US2-02**: `GET /api/v1/skills/stream?studioToken=<wrong>` (wrong value, any length)
  is still 401.
- **AC-US2-03**: The query-param token is validated with the SAME timing-safe compare
  (`tokensEqual`) already used for the header — no `===` fast-path leak.
- **AC-US2-04**: The `studioToken` query param is STRIPPED from `req.url` before the
  request is proxied upstream, so it never reaches verified-skill.com.
- **AC-US2-05**: The rejection warn log (router.ts ~line 207) NEVER contains the token
  value (neither the supplied param nor the expected token).
- **AC-US2-06**: The query-param exemption applies ONLY to GET requests on the known
  EventSource stream path(s); a POST or a non-stream `/api/*` path with `?studioToken=`
  is NOT exempted by this mechanism.
