---
increment: 0838-sse-diagnose-source-origin-updates
title: 'Plan: SSE diagnose mode + source-origin update tracking'
type: plan
---

# Plan: SSE diagnose mode + source-origin update tracking

## Approach

Three orthogonal threads, each scoped to a single layer, sequenced so the
diagnostic surface lands first (so we can verify the other two with our own
tooling):

1. **Diagnostic surface** (US-001, US-004) — `console.debug` flag,
   eval-server proxy logging, bell tooltip status text + pip. Pure additive
   client-side work; no network contracts change. Lands first so the rest
   of the increment can be verified with the diagnostic tool we just shipped.
2. **Visibility queue** (US-003) — bounded `localStorage` FIFO, replay on
   `visibilitychange`, dedupe against `seenEventIds`. Pure client-side; no
   network contracts. Lands second because it makes the toast pipeline
   end-to-end testable for backgrounded windows — needed to validate the
   source-origin path manually.
3. **Source-origin tracking + telemetry** (US-002, US-005) — extends
   `resolveSubscriptionIds` with a registry-lookup option, adds
   `?include=source-origin` to `/api/v1/skills/updates`, adds new
   `/api/v1/studio/telemetry/sse` Worker route. Lands last because it
   touches platform contracts and benefits from the diagnostic surface for
   verification.

Test stack: Vitest 1.x (unit/integration) for `useSkillUpdates`,
`resolveSubscriptionIds`, the toast queue, and `UpdateBell`; Playwright 1.x
(E2E) for the source-origin publish→toast scenario through the running
eval-server proxy + verified-skill.com staging.

## Files to modify

### vskill (eval-ui)
- `repositories/anton-abyzov/vskill/src/eval-ui/src/hooks/useSkillUpdates.ts`
  - Add `[sse]` `console.debug` block gated on `VSKILL_DEBUG_SSE` (read from
    `import.meta.env.VITE_VSKILL_DEBUG_SSE` or
    `new URLSearchParams(window.location.search).get("debugSse") === "1"`).
  - Add visibility-queue module integration in the `onMessage` handler:
    when `document.visibilityState === "hidden"`, enqueue toast payload
    instead of dispatching.
  - Add `visibilitychange → "visible"` listener that drains the queue at
    250ms intervals via `studio:toast` CustomEvent dispatches; deduplicate
    against `updateStore.hasSeen(eventId)`.
  - Add telemetry hook: dedupe-by-(event,session) `fetch("/api/v1/studio/telemetry/sse", ...)`
    on `connected`, `fallback`, `reconnect-scheduled`, `gone` transitions.
  - Pass an extended `trackingSkillIds` list that includes source-origin
    skills with a registry twin (resolved by the helper below).
- `repositories/anton-abyzov/vskill/src/eval-ui/src/utils/resolveSubscriptionIds.ts`
  - Add `includeSourceOriginMatches?: boolean` option.
  - When set, accept `InstalledSkillEntry & { origin?: "installed" | "source"; author?: string; localVersion?: string }`.
  - Source-origin entries are filtered out of the immediate return as
    today, but a parallel async `lookupSourceOriginIds(entries): Promise<ResolvedSubscriptionId[]>`
    helper hits `/api/v1/skills/lookup-by-name` with `[{name, author}, ...]`
    and returns the resolved uuid/slug pairs (cached in-memory for the
    session).
  - The hook calls the async helper from a `useEffect` and merges the
    resolved IDs into the SSE filter on next render.
- `repositories/anton-abyzov/vskill/src/eval-ui/src/StudioContext.tsx`
  - Pass source-origin skills (with `author`, `version`) into
    `useSkillUpdates`'s new `sourceOriginSkills` option, alongside the
    existing `skillIds`/`trackingSkillIds`.
- `repositories/anton-abyzov/vskill/src/eval-ui/src/components/UpdateBell.tsx`
  - Add status pip (`<span data-testid="update-bell-status-pip">`) anchored
    bottom-right of the icon, color from `status` prop on `useStudio()`.
  - Append `Live updates: <state>` to tooltip via `aria-describedby` linked
    to a hidden `<span data-testid="update-bell-status-text">`.
  - Debounce (500ms) `aria-live="polite"` announcements on status change.
- `repositories/anton-abyzov/vskill/src/eval-ui/src/utils/toastQueue.ts` **(new)**
  - `enqueue(entry)`, `drain(): Entry[]`, `peek(): Entry[]`, `clear()`.
  - localStorage-backed FIFO with `STORAGE_KEY = "vskill:toast-queue"`,
    `MAX_ENTRIES = 10`, `STALE_AFTER_MS = 30 * 60 * 1000`.
  - SSR-safe: returns no-op when `typeof window === "undefined"`.

### vskill (eval-server)
- `repositories/anton-abyzov/vskill/src/eval-server/platform-proxy.ts`
  - Existing `randomUUID` import is already present; reuse for
    `requestId`. Echo `X-Request-Id` on response headers.
  - Add `proxy.sse.start{requestId, upstreamUrl}` and
    `proxy.sse.end{requestId, status, durationMs}` `console.log` lines on
    `text/event-stream` paths only, gated on
    `process.env.VSKILL_DEBUG_SSE === "1"`.

### vskill-platform (Next.js + CF Worker)
- `repositories/anton-abyzov/vskill-platform/src/app/api/v1/skills/updates/route.ts`
  - Accept new `?include=source-origin` query param.
  - When set, accept request body shape:
    `{ sourceOrigin: [{name, author, version}, ...] }` in addition to the
    existing installed-skill payload.
  - For each source-origin entry, look up the registry skill by
    case-insensitive name + exact author (Prisma:
    `prisma.skill.findFirst({ where: { name: { equals: name, mode: "insensitive" }, author: { equals: author } } })`).
    Match → produce the same response shape as installed-skill results.
    No match → silently exclude.
  - When source-origin and installed entries collide on `name`, the
    installed entry wins (preserves existing semantics).
- `repositories/anton-abyzov/vskill-platform/src/app/api/v1/skills/lookup-by-name/route.ts` **(new)**
  - `POST` body: `{ entries: [{name, author}, ...] }` (max 50 entries).
  - Returns `{ results: [{name, author, uuid?, slug?}, ...] }`.
  - Pure read; no auth required; respects existing per-IP rate limits.
- `repositories/anton-abyzov/vskill-platform/src/app/api/v1/studio/telemetry/sse/route.ts` **(new)**
  - `POST` body validated as
    `{ event: "connected"|"fallback"|"reconnect-scheduled"|"gone-frame-received", sessionId: string, sourceTier: "platform-proxy"|"direct-browser"|"tauri-native", timestamp: number, durationSinceOpenMs?: number }`.
  - Writes one row to `STUDIO_SSE_TELEMETRY` Cloudflare Analytics Engine
    binding via `env.STUDIO_SSE_TELEMETRY.writeDataPoint({...})`.
  - All errors swallowed; returns `204 No Content` always.
- `repositories/anton-abyzov/vskill-platform/wrangler.toml` (or equivalent)
  - Add Analytics Engine binding `STUDIO_SSE_TELEMETRY` (deferred to T-013
    if not already present).

### Tests (new files)
- `repositories/anton-abyzov/vskill/src/eval-ui/src/utils/__tests__/toastQueue.test.ts`
- `repositories/anton-abyzov/vskill/src/eval-ui/src/utils/__tests__/resolveSubscriptionIds.source-origin.test.ts`
- `repositories/anton-abyzov/vskill/src/eval-ui/src/hooks/__tests__/useSkillUpdates.visibility-queue.test.ts`
- `repositories/anton-abyzov/vskill/src/eval-ui/src/hooks/__tests__/useSkillUpdates.telemetry.test.ts`
- `repositories/anton-abyzov/vskill/src/eval-ui/src/components/__tests__/UpdateBell.status-pip.test.tsx`
- `repositories/anton-abyzov/vskill/src/eval-server/__tests__/platform-proxy-debug-log.test.ts`
- `repositories/anton-abyzov/vskill-platform/src/app/api/v1/skills/updates/__tests__/source-origin.test.ts`
- `repositories/anton-abyzov/vskill-platform/src/app/api/v1/skills/lookup-by-name/__tests__/route.test.ts`
- `repositories/anton-abyzov/vskill-platform/src/app/api/v1/studio/telemetry/sse/__tests__/route.test.ts`
- `repositories/anton-abyzov/vskill/e2e/source-origin-update-toast.spec.ts` (Playwright)

## Architecture Decisions

### ADR-001: Visibility queue uses localStorage with per-window in-memory dedupe

**Decision**: Persist the toast queue to `localStorage` (key `vskill:toast-queue`),
not `sessionStorage`. Each Studio window keeps an in-memory `Set<eventId>`
of "already replayed in this tab" so cross-window contention does not cause
the same toast to fire twice.

**Rationale**:
- `localStorage` survives a tab reload, so a user who refreshes a
  backgrounded window still sees pending toasts.
- `sessionStorage` would scope cleanly per tab but loses entries on reload —
  not the durability semantics the user expects.
- Multi-window collision (same toast queued in two tabs simultaneously) is
  the only downside; addressed by the per-window in-memory dedupe set
  keyed on `eventId`.
- The `seenEventIds` set in `useSkillUpdates` already provides this
  dedupe layer for live events; we extend it to cover replayed events.

**Alternatives considered**:
- `sessionStorage` only: rejected — loses entries on reload.
- IndexedDB: rejected — overkill for 10 entries; adds async overhead to a
  hot path.
- Service Worker queue: rejected — Studio is not a PWA; out of scope.

### ADR-002: Source-origin match key is name + author

**Decision**: Match source-origin skills to registry skills by
case-insensitive `name` + exact `author` (both pulled from `SKILL.md`
frontmatter). No SHA-based matching.

**Rationale**:
- Source-origin skills are local working copies; their content hash
  diverges from the registry by definition (uncommitted edits, dev-only
  scaffolding, draft prompts). Hash matching would produce zero matches in
  the common case.
- `name + author` is the canonical identity used by the registry
  (`prisma.skill` has a unique constraint approximating this). Skills
  without an `author` field in frontmatter are excluded — same fail-safe
  as today's `slug.length > 0` check.
- Case-insensitive `name` mirrors how Studio search treats names; exact
  `author` prevents typo collisions across distinct authors with similar
  handles.

**Alternatives considered**:
- `name + version`: rejected — version mismatch is the whole point of
  "update available", so matching on it is circular.
- Content SHA: rejected — see above.
- `name + repo URL`: rejected — source-origin skills often lack a
  `sourceRepoUrl` in their local frontmatter.

### ADR-003: Telemetry endpoint lives in vskill-platform (not a dedicated Worker)

**Decision**: The new telemetry route lives at
`vskill-platform/src/app/api/v1/studio/telemetry/sse/route.ts`, served by
the same Cloudflare Worker as the rest of the platform. Writes go to a
Cloudflare Analytics Engine binding (`STUDIO_SSE_TELEMETRY`) added to the
existing `wrangler.toml`.

**Rationale**:
- Reuses the existing Worker deploy pipeline; no new wrangler config or
  CI surface.
- Analytics Engine is purpose-built for high-volume, low-cost append-only
  metrics — exactly the shape of telemetry pings (4 events × N sessions /
  day).
- A dedicated Worker would mean a separate deploy, separate observability,
  separate auth surface — all overhead for what is effectively a logging
  endpoint.
- Failure isolation: telemetry writes are wrapped in try/catch, never
  block the SSE path. Even if the Analytics Engine binding errors, the
  user-visible Studio is unaffected.

**Alternatives considered**:
- Dedicated Worker (e.g. `studio-telemetry-worker`): rejected — adds CI
  surface for no benefit.
- Existing Sentry / Datadog: rejected — fleet-level SSE health is not
  error-shaped (most events are normal lifecycle transitions); analytics
  storage is a better fit.
- KV writes: rejected — Analytics Engine is purpose-built for this; KV
  has write-rate limits this would exceed at scale.

## Out of Scope

- **Tauri auto-updater**: The native macOS auto-updater path is a separate
  concern with its own threat model (code signing, update server,
  rollback). Tracked in a separate increment.
- **Cloudflare Worker SSE producer**: The producer at
  `vskill-platform/src/app/api/v1/skills/stream/route.ts` is healthy per
  the researcher run. We forward events verbatim and do not modify the
  fan-out logic.
- **Update dropdown body redesign**: The dropdown rows, copy, and layout
  are unchanged. Only the bell anchor (status pip) and tooltip are
  modified.
- **Native macOS notifications**: Only in-app `studio:toast` is in scope.
  OS-level notifications would require Tauri permissions and are deferred.
- **PII in telemetry**: We deliberately do NOT send skill IDs, user IDs,
  or URLs. Adding identification would require a separate privacy review.

## Test stack

- **Vitest 1.x** with `vi.useFakeTimers()` for the visibility-queue
  scheduling tests, `vi.hoisted()` + `vi.mock()` for mocking the
  EventSource constructor, and `@testing-library/react` for the
  `UpdateBell.status-pip.test.tsx` rendering assertions.
- **Playwright 1.x** for the E2E scenario:
  1. Start `vskill studio` against a fixture project containing one
     source-origin skill matching a registry twin in staging.
  2. Open Studio in a Chromium context.
  3. Trigger a publish via the staging registry (pre-canned publish
     event).
  4. Assert the `studio:toast` CustomEvent fires within 5s (with the
     window foregrounded) AND assert the bell counter increments.
  5. Repeat with `page.evaluate(() => Object.defineProperty(document, "visibilityState", {value: "hidden"}))`
     and assert the queue persists; on visibility flip, assert replay.
- **Coverage targets**: 90% line/branch on new modules
  (`toastQueue.ts`, `resolveSubscriptionIds.ts` source-origin paths,
  `UpdateBell.tsx` status pip branch). 100% AC scenario coverage in
  Playwright (one E2E spec per AC where it makes sense; collated where
  not).
