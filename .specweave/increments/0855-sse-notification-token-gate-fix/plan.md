# 0855 — Technical Plan

## Files touched (vskill repo: repositories/anton-abyzov/vskill)

| File | Change |
|------|--------|
| `src/eval-server/router.ts` | `tokenGate()` — add narrow query-param-token exemption for GET EventSource stream paths; strip `studioToken` from `req.url` before return; keep token out of logs |
| `src/eval-ui/src/contexts/StudioTokenBridge.ts` | Add `getStudioTokenForUrl()` getter exposing the resolved per-process token to non-fetch callers (EventSource) |
| `src/eval-ui/src/hooks/useSkillUpdates.ts` | Append `&studioToken=<token>` to the EventSource stream URL when a token is available |
| `src/eval-server/__tests__/router-token-gate.test.ts` | Add gate test cases: valid query token passes on /stream, wrong/missing still 401, token stripped from req.url, token not logged, POST/non-stream not exempted |
| `src/eval-server/__tests__/sse-stream-token-gate.test.ts` (new) | Integration: real eval-server, open SSE with `?studioToken=valid` → 200 `text/event-stream`; without/with wrong token → 401 |

## Design

### Server — `tokenGate()` (router.ts)

The gate runs inside `Router.handle()` (router.ts:72), which executes BEFORE the
eval-server dispatcher calls `shouldProxyToPlatform(req.url)` / `proxyToPlatform(req, res)`
(eval-server.ts:154-155). The proxy builds its upstream target from `req.url`
(platform-proxy.ts:282 `new URL(req.url, baseUrl)`), forwarding `target.search` verbatim.
Therefore mutating `req.url` inside `tokenGate` to drop `studioToken` is sufficient to
keep the token from leaking upstream — no change needed in platform-proxy.ts.

Known EventSource GET stream paths (from `grep new EventSource(` in src/eval-ui):
- `/api/v1/skills/stream` — the notification stream (DEFAULT_STREAM_BASE), the only
  EventSource that traverses the platform proxy and is token-gated. The other
  EventSource constructions (`/api/events`, `/api/studio/ops/stream`, and the SSE GETs in
  `api.ts`) are local eval-server routes; this fix also exempts them by GET+pathname so
  the same header-less EventSource limitation never silently 401s a local stream.

Algorithm added after the existing exemptions, before the header read:

```ts
const STREAM_GET_PATHS = new Set([
  "/api/v1/skills/stream",
  "/api/events",
  "/api/studio/ops/stream",
]);
// EventSource cannot set request headers, so the per-process token arrives as
// a ?studioToken=<t> query param. Validate it with the SAME timing-safe compare
// used for the header. Scope: GET only, known stream pathnames only.
if (method === "GET" && STREAM_GET_PATHS.has(pathname)) {
  const url = new URL(rawUrl, "http://127.0.0.1");
  const qpToken = url.searchParams.get("studioToken");
  if (qpToken && tokensEqual(qpToken, getStudioToken())) {
    // Strip the token BEFORE the request is proxied upstream so it never
    // reaches verified-skill.com. Mutate req.url in place — the proxy reads
    // req.url after the gate returns.
    url.searchParams.delete("studioToken");
    req.url = `${url.pathname}${url.search}`;
    return true;
  }
  // Optional defense-in-depth: also allow loopback remoteAddress. Primary
  // mechanism is the query token above; we do NOT loosen to non-loopback.
}
```

- The token value is NEVER passed to `console.warn`. The existing reject log already
  logs `method + pathname` only; the new code adds no token to any log line.
- Wrong / missing `studioToken` falls through to the existing header check, which fails
  → 401. (A wrong query token + no header = 401, preserving the boundary.)

### Client — StudioTokenBridge getter

`StudioTokenBridge.ts` resolves the per-process token from the injected
`<script id="__vskill_studio_token__">` tag (browser) or Tauri IPC. It already caches it
in `cachedToken`. Add a synchronous getter so EventSource (which can't await the patched
fetch) can read it:

```ts
/** Public accessor for non-fetch callers (e.g. EventSource URLs). */
export function getStudioTokenForUrl(): string | null {
  if (cachedToken) return cachedToken;
  const fromDom = readStudioTokenFromDom();
  if (fromDom) { cachedToken = fromDom; return fromDom; }
  return null;
}
```

(DOM read is synchronous and is the primary source in both browser and Tauri.)

### Client — useSkillUpdates EventSource URL

```ts
let url = `${streamBase}?skills=${encodeURIComponent(csvForSubscribe)}`;
const studioToken = getStudioTokenForUrl();
if (studioToken) url += `&studioToken=${encodeURIComponent(studioToken)}`;
es = new EventSource(url);
```

Token only appended when present; on verified-skill.com (no injected token) the URL is
unchanged, so the platform's cookie auth path is untouched.

## Test strategy (TDD: RED → GREEN → REFACTOR)

1. RED — extend router-token-gate.test.ts with the 6 AC cases; add new integration test.
2. GREEN — implement the gate change + client changes.
3. REFACTOR — dedupe the URL parse already done at the top of tokenGate (reuse `pathname`
   instead of re-parsing where possible).
4. Run `npx vitest run src/eval-server` (scoped). Report counts.

## Risks / mitigations

- **Token leak to upstream** → stripped from `req.url` before proxy reads it (AC-US2-04).
- **Token in logs** → no log line ever receives the token (AC-US2-05); test asserts it.
- **Widening the gate hole** → exemption is GET-only AND limited to an allowlist of known
  stream pathnames AND requires a valid timing-safe-compared token (AC-US2-06).
