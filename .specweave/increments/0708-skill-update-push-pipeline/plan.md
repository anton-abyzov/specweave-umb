# Implementation Plan: Skill Update Push Pipeline (Scanner + UpdateHub DO + SSE + Studio UI)

> **Source of truth**: This plan implements the approved design captured in
> `~/.claude/plans/fluffy-foraging-popcorn.md`. Design decisions below are
> reproduced verbatim; rationale lives in the linked ADRs.

## Overview

verified-skill.com becomes the central authority for "is there a newer version
of this skill?" The platform runs one upstream GitHub SHA scanner (on the
existing Worker cron, bumped from hourly to every 10 minutes), fans out SHA
change events through a Durable Object hub, and serves them to Skill Studio
tabs over a filtered Server-Sent Events endpoint. Optional GitHub webhooks
give first-party repos ~1-second push latency. There is no separate long-running
CLI daemon in v1 — Skill Studio is the sole consumer.

This plan does NOT redesign anything — it translates the approved architecture
into file-level work. See
[fluffy-foraging-popcorn.md](file:~/.claude/plans/fluffy-foraging-popcorn.md)
for the full research / alternatives analysis.

## Architecture

```
           ┌─────────────────────────────────────────────┐
           │  Cloudflare Workers (verified-skill.com)    │
           │                                             │
Source     │  ┌───────────────┐   ┌──────────────────┐  │
 repos  ───┼─▶│ Scanner Task  │──▶│  Neon (Prisma)   │  │
 (GitHub)  │  │ (extends      │   │  Skill +         │  │
 webhook ──┼─▶│  cron cadence │   │  SkillVersion    │  │
           │  │  → every 10m) │   └──────────────────┘  │
           │  └───────┬───────┘            │            │
           │          │ on new SHA         │            │
           │          ▼                    │            │
           │  ┌──────────────────────────────────────┐ │
           │  │  UpdateHub Durable Object            │ │
           │  │  - shard-ready name: "UpdateHub-0"   │ │
           │  │  - hibernatable WebSocket API        │ │
           │  │  - Map<WebSocket, {filter:Set<id>}>  │ │
           │  │  - fanout(event, event.skillId ∈ f)  │ │
           │  └──────────────────────────────────────┘ │
           │          │                                 │
           │          │ DO stub (from Worker)           │
           │          ▼                                 │
           │  ┌────────────────────────┐  ┌──────────┐ │
           │  │ GET /api/v1/skills/    │  │ POST     │ │
           │  │     stream             │  │ /api/v1/ │ │
           │  │ (SSE + filter qs)      │  │ internal/│ │
           │  │                        │  │ skills/  │ │
           │  │ POST /api/v1/webhooks/ │  │ publish  │ │
           │  │     github             │  │ (HMAC)   │ │
           │  └────────────────────────┘  └──────────┘ │
           └─────────────────────────────────────────────┘
                          │
                          ▼
                  Skill Studio (useSkillUpdates hook)
                  - Update chips / bell / row indicator
                  - Toast on visibilityState === "visible"
                  - Auto-reconnect with backoff
```

### Components

- **Scanner** (`src/lib/skill-update/scanner.ts`, NEW) — iterates
  `Skill` rows with non-null `sourceRepoUrl`, calls
  `GET /repos/:owner/:repo/commits/:branch` with an If-None-Match ETag
  header, compares the returned SHA against `Skill.lastSeenSha`, inserts
  a new `SkillVersion` row when it differs, and publishes a
  `skill-update` event to the UpdateHub DO.
- **UpdateHub Durable Object** (`src/lib/skill-update/update-hub.ts`, NEW)
  — single DO class `UpdateHub` bound as `UPDATE_HUB`. One instance
  in v1 (`idFromName("UpdateHub-0")`, with the numeric suffix
  pre-wired for future sharding — see §Scaling Triggers). Holds all
  active client connections. Uses
  Cloudflare's **hibernatable WebSocket API** (`state.acceptWebSocket()`)
  so the DO unloads between events while keeping sockets alive. Maintains
  `Map<connId, { filter: Set<string> | null }>` in memory (cheap to
  rebuild on wake; not persisted).
- **Public SSE endpoint** (`src/app/api/v1/skills/stream/route.ts`, NEW)
  — opens an SSE `ReadableStream`, gets the DO stub, forwards the
  connection via `fetch()` with `Upgrade: websocket`, and proxies each
  JSON event the DO emits out to the client as SSE. Filter comes from
  either the `?skills=<csv>` URL param (small installs, <100 skills) or
  a server-side subscription keyed by session cookie (large installs,
  see `/subscribe` below). **Not paginated** — this is a live event
  stream, not a query result.
- **Subscription endpoint** (`src/app/api/v1/skills/stream/subscribe/route.ts`,
  NEW) — `POST` with JSON body `{skills: string[]}` (no limit, but
  we cap at 5000 server-side for safety). Stores the subscription
  under the caller's session cookie key in `SEARCH_CACHE_KV`
  (TTL 24h, refreshed on each stream connect). Response sets/refreshes
  a `sw-stream-session` cookie. `GET /api/v1/skills/stream` without a
  `?skills=` param reads the filter from this cookie-keyed entry.
  **Server-side authoritative**: the DO trusts whatever filter the
  stream endpoint forwards, which always comes from either the URL or
  the KV subscription — the client has no way to bypass or broaden it.
- **Webhook receiver**
  (`src/app/api/v1/webhooks/github/route.ts`, NEW) — verifies the
  GitHub `X-Hub-Signature-256` HMAC against
  `GITHUB_WEBHOOK_SECRET`, extracts `ref` + `after` SHA from the push
  payload, and invokes the scanner for that single repo (fast path).
- **Internal publish endpoint**
  (`src/app/api/v1/internal/skills/publish/route.ts`, NEW) — auth via
  existing `hasInternalAuth()` (`X-Internal-Key`), forwards the event
  body to the UpdateHub DO. Used by the scanner and (future) admin tools.
- **Studio UI** (in `vskill` repo, under `src/studio/`) — shared
  `useSkillUpdates()` React hook that opens **one** EventSource per
  tab (never more — a user with 500 installed skills still holds
  exactly one connection), applies the installed-skill filter, and
  emits React state updates consumed by `SkillRow`, `SidebarSection`,
  `TopRail.UpdateBell`, and `RightPanel.UpdateAction`. Falls back to
  5-min poll after 60s of no successful `open`. Gates toast notifications
  on `document.visibilityState === "visible"`. Exposes
  `isTrackedForUpdates(skillId): boolean` so the UI can render a dim
  "not tracked" affordance for skills with null `sourceRepoUrl` on the
  platform side.

### Data Model

Reuse existing `Skill` + `SkillVersion` models. Two new nullable columns
on `Skill` (no new tables in v1):

```prisma
model Skill {
  // ... existing fields ...

  /// Upstream source for the scanner. Null = not tracked.
  /// e.g., "https://github.com/anthropic-skills/frontend-design"
  sourceRepoUrl String?

  /// Branch the scanner tracks. Default main.
  sourceBranch  String? @default("main")

  /// Last git SHA observed on sourceBranch. Used for diff detection.
  lastSeenSha   String?

  /// When the scanner last ran against this skill.
  lastCheckedAt DateTime?

  /// Discovery resolver state — null = never attempted, "pending" =
  /// enqueued, "resolved" = sourceRepoUrl set by resolver, "unresolvable"
  /// = resolver gave up (may be user-registered later), "user-registered"
  /// = explicit opt-in via /skills/:id/register-tracking.
  resolutionState    String?
  resolutionAttempts Int       @default(0)
  resolutionLastAt   DateTime?

  @@index([sourceRepoUrl, lastCheckedAt(sort: Asc)])  // scanner work queue
  @@index([resolutionState, resolutionLastAt])        // discovery backoff queue
}
```

> **Column naming**: `lastCheckedAt` (not `lastScannedAt`) matches the
> spec's AC-US1-05. Stick with this name everywhere — in migrations,
> code, seed script, and logs. The `resolution*` columns support the
> discovery flow described in §Skill Discovery & Registration.

`SkillVersion` is unchanged — the scanner inserts rows exactly the same
way the existing submission pipeline does (shares `contentHash`, `gitSha`,
`diffSummary`, `versionBump` fields).

**New table `UpdateEvent`** — transactional outbox for the delivery
guarantee (see §Delivery Guarantee). Every path that inserts a
`SkillVersion` (scanner consumer, submission-processing consumer,
webhook-triggered scan) MUST insert a row here in the same
transaction.

```prisma
model UpdateEvent {
  /// ULID — sortable, URL-safe; also the SSE `id:` field.
  id          String   @id
  skillId     String
  skill       Skill    @relation(fields: [skillId], references: [id])
  versionId   String   // FK to the SkillVersion row written in the same txn
  payload     Json     // full SkillUpdateEvent shape — frozen at write time
  source      String   // "submission" | "scanner" | "webhook-scan" | "backfill"
  createdAt   DateTime @default(now())
  /// NULL = never delivered to DO. Set by internal publish or reconciler on success.
  publishedAt DateTime?
  /// Incremented by reconciler on each retry attempt.
  publishAttempts Int @default(0)
  lastAttemptErr  String?

  @@index([publishedAt, createdAt])  // reconciler work queue
  @@index([skillId, createdAt(sort: Desc)])
}
```

Retention: a daily prune job deletes `UpdateEvent` rows where
`publishedAt < NOW() - 7 days` to keep the table bounded. The DO's
replay log (5-min in-memory) is the fast path for client reconnects;
DB is the source of truth for the reconciler.

### API Contracts

#### `GET /api/v1/skills/stream`
**Purpose**: Public SSE feed of skill-update events. One connection per
Studio tab, not paginated, not batched — the server pushes exactly the
events the subscription filter matches, nothing more, nothing less.
**Query / filter resolution** (in precedence order):
1. `?skills=<skillId>[,<skillId>...]` — CSV of `Skill.id` values,
   URL-encoded. Hard limit: 2 KB URL, ≈100 skillIds. Suitable for
   typical users.
2. Omitted `skills` param + `sw-stream-session` cookie set → server
   reads the subscription from `SEARCH_CACHE_KV` under
   `stream-sub:<sessionId>`. Used by power users (>100 installed
   skills) who first POSTed to `/subscribe`.
3. Both missing → 400 `{"error":"filter_required"}`. There is no
   "subscribe to everything" mode on the public endpoint.

The filter is **server-side authoritative**: the stream endpoint
copies the filter into the WS upgrade URL to the DO; the DO trusts
only what the stream endpoint passes in; the client never sees or
manipulates the filter after the initial send.
**Response**: `Content-Type: text/event-stream`. Event format:
```
event: skill.updated
id: <UUID v4>
data: {"skillId":"uuid","name":"frontend-design","pluginName":"anthropic",
       "version":"1.4.0","previousVersion":"1.3.2","gitSha":"abc123",
       "contentHash":"sha256:...","diffSummary":"2 files changed",
       "publishedAt":"2026-04-24T16:00:00Z"}

: keepalive
```
Keepalive is a raw SSE comment (`: keepalive\n\n`) every 25s — not a
named event. Matches existing `submissions/stream` pattern and fits
under CF's 30s idle cap. No caller auth — event payload is public info.

#### `POST /api/v1/webhooks/github`
**Purpose**: Fast-path scanner trigger for first-party repos.
**Headers**:
- `X-Hub-Signature-256: sha256=<hmac-hex>` — GitHub-computed HMAC over raw
  body with `GITHUB_WEBHOOK_SECRET`.
- `X-GitHub-Event: push` (others → 200 ack, no-op).
**Body**: GitHub push-event payload. Relevant fields: `ref`, `after`,
`repository.full_name`.
**Response**: `200 {"ok":true,"processed":N}` where N = skills re-scanned.

#### `POST /api/v1/skills/stream/subscribe`
**Purpose**: Register a server-side subscription for users whose
installed-skill list exceeds the URL budget.
**Body**: `{"skills": ["<uuid>", ...]}` — up to 5000 entries
(server-side cap; exceeding returns 413).
**Response**: `200 {"ok": true, "count": N, "sessionId": "<uuid>"}`.
Sets a `sw-stream-session=<uuid>; HttpOnly; Secure; SameSite=Lax;
Max-Age=86400` cookie. The subscription is stored at
`stream-sub:<sessionId>` in `SEARCH_CACHE_KV` with a 24h TTL; each
subsequent `GET /api/v1/skills/stream` refreshes the TTL.

**Mutation semantics**: Client re-POSTs the full list whenever
installed-skill state changes (install, uninstall). This is idempotent
— the new list wholesale replaces the old one under the same session.
No incremental add/remove endpoint in v1; the list is short enough to
resend even at 5000 skills.

#### `POST /api/v1/internal/skills/publish`
**Purpose**: Internal-only skill-update event publisher.
**Headers**: `X-Internal-Key: <INTERNAL_BROADCAST_KEY>` (reuses existing secret).
**Body**: `{ eventId, type: "skill.updated", skillId, version, diffSummary?, publishedAt, ... }`.
The `eventId` is the `UpdateEvent.id` (ULID) used for DO-side
idempotency (P3 in §Delivery Guarantee). The DO skips fan-out if the
`eventId` is already in its replay log.
**Response**: `202 {"ok":true,"enqueued":true,"deduped":boolean}` —
fire-and-forget per AC-US3-04. The endpoint returns once the DO has
accepted (or deduped) the event; it does NOT wait for fan-out
completion.

## Design Decisions

| Decision | Chosen | Rationale |
|---|---|---|
| Transport to browser | **SSE** (`EventSource`) | Matches existing pattern in `submissions/stream/route.ts`; auto-reconnect built-in; one-way is sufficient. See `ADR-0708-02`. |
| Fan-out coordinator | **Hibernatable Durable Object** (single `UpdateHub-0` instance v1) | `event-bus.ts` is per-Worker-isolate — two tabs connecting to different edges never see each other's events. DO is the only CF primitive that holds cross-edge connection state. Hibernation drops idle CPU cost to zero. See `ADR-0708-01`. |
| Shard strategy | Single DO v1 named `UpdateHub-0`, shard-ready code path from day one | CF DOs handle thousands of concurrent WS per instance. 100 target skills × ~10 tabs each = 1000 connections. Code uses `shardForSkillId()` helper that returns 0 while `SHARD_COUNT=1`; flipping the var triggers the pre-designed N-shard topology (see §Scaling Triggers). |
| Scanner cadence | Extend existing cron `0 * * * *` → `*/10 * * * *` with minute-based dispatch (scanner only on minutes 0, 10, 20, 30, 40, 50) | 100 skills × 6 scans/hr = 600 GitHub requests/hr. Fine-grained PAT gives 5000/hr — 12% budget. Room to grow to ~800 tracked skills. |
| Webhook fast-path | Optional, first-party only | Anthropic repos we can't webhook. For our own, HMAC webhook cuts latency from ~5 min (next cron) to ~1s. |
| Schema changes | 4 new nullable `Skill` columns + 1 composite index, no new table | YAGNI: no join-table needed when `sourceRepoUrl` is 1:1 with a skill. If we later want multiple upstreams per skill we'll add `TrackedSkillSource` then. |
| Internal auth | Reuse `INTERNAL_BROADCAST_KEY` + `X-Internal-Key` | Already in prod; don't invent a second secret. |
| GitHub auth | Fine-grained PAT `GITHUB_TOKEN` in CF secrets — scopes: Contents (read) on public repos only | Same token the 0705 compare code uses. Rotation via `wrangler secret put`. |
| UI update strategy | EventSource-first; 5-min poll fallback only on 3 consecutive connect failures | Live feels live. Poll is the safety net for corp networks that block long-lived HTTP streams. |
| Toast gating | `document.visibilityState === "visible"` | User requirement: no toast if tab is backgrounded — the chip/bell indicators still update so the user sees it on return. |

## Skill Discovery & Registration

The seed script bootstraps ~100 curated skills, but the catalog must
keep growing as community skills land in user installs. We chose
**Option D — reactive resolver on `/check-updates` traffic — combined
with a light Option C opt-in UI for the unresolvable tail.** See the
"Skill discovery/registration flow" sequence diagram in
[architecture.md](./architecture.md).

### Why this option

| Concern | Outcome |
|---|---|
| Friction | Zero. User does nothing; the `/check-updates` calls the Studio already makes become the discovery signal. |
| Privacy | Neutral. `/check-updates` already carries the installed-skill list; no new telemetry. |
| Abuse | Low. Resolver only accepts URLs it can verify from metadata already in our DB (signed submission path). Explicit-opt-in is rate-limited per session. |
| Scale | 1000 users × 50 skills ≈ 50k discovery jobs, processed async via CF Queue with backoff — no scanner cron impact. |
| Coverage | ~80% via metadata inference; the tail gets an explicit "Register" button per skill. |

Options A–C considered and rejected:
- **Option A (manual seed only)** — long tail never reached. Rejected.
- **Option B (auto-discovery from all Studio telemetry)** — pushes too
  much trust onto the client + overlaps with what `/check-updates`
  already provides. Rejected as strictly dominated by D.
- **Option C (user per-skill opt-in)** — kept as the *fallback* branch
  for the unresolvable tail, not the primary path.

### Discovery infrastructure

1. **New CF Queue** `discovery-resolve` added to `wrangler.jsonc`
   alongside `submission-processing` and `eval-processing`.
   `max_batch_size: 10`, `max_batch_timeout: 3`, `max_concurrency: 5`,
   `max_retries: 2`, DLQ: `submission-dlq` (reuse existing).
2. **Enqueue helper**
   `src/lib/skill-update/discovery/enqueue.ts` — called by
   `check-updates` for any skill with `sourceRepoUrl === null` AND
   (`resolutionState === null` OR (`resolutionState === "unresolvable"`
   AND `resolutionLastAt` older than the backoff window)). Backoff:
   exponential — 1h, 6h, 24h, 72h, then stops auto-retrying (waits
   for user action).
3. **Resolver consumer**
   `src/lib/skill-update/discovery/resolver.ts` — queue consumer
   (registered in `scripts/build-worker-entry.ts`). For each job:
   fetches raw `SKILL.md` from the known `Skill.repoUrl`, parses
   frontmatter `repository:` field (plugin manifest as fallback),
   verifies the URL exists and serves a `SKILL.md` at the declared
   path. On success, `UPDATE Skill SET sourceRepoUrl, sourceBranch,
   resolutionState = "resolved"`. On failure, increments
   `resolutionAttempts` and sets `resolutionState = "unresolvable"`
   with the next retry gated by the backoff.
4. **Explicit opt-in endpoint**
   `src/app/api/v1/skills/[id]/register-tracking/route.ts` — `POST`
   with body `{repoUrl, branch}`. Rate-limited 10/hr per session via
   existing rate-limit middleware. Verifies the repo exists and
   contains a reachable `SKILL.md` whose content matches the current
   `Skill.contentHash` before writing. Sets `resolutionState = "user-registered"`.

### Check-updates response change (two fields)

`POST /api/v1/skills/check-updates` adds per-result:
```json
{
  "name": "...",
  "installed": "...",
  "latest": "...",
  "updateAvailable": false,
  "trackedForUpdates": true,       // new: sourceRepoUrl !== null
  "resolutionState": null          // new: for UI to hint "pending" / "unresolvable"
}
```
`trackedForUpdates` backs `isTrackedForUpdates()` in the Studio hook.
`resolutionState` lets the UI explain the state (tooltip "Trying to
register…" vs "Couldn't find source — click to register manually").

### Abuse controls

- **Resolver trust boundary**: the resolver only reads `Skill.repoUrl`
  (already in our signed submission DB). It does NOT accept
  client-supplied URLs for automatic registration.
- **Explicit opt-in verification**: `/register-tracking` MUST verify
  that the `SKILL.md` at the declared path hashes to the current
  `Skill.contentHash` before accepting — prevents users from
  registering random repos as the source for an unrelated skill.
- **Rate limit**: 10 register-tracking calls per session per hour,
  via existing `applyRateLimit` middleware.

## Scaling Triggers

The architecture is sized for v1 but designed so each growth step is a
**parameter change or single-dimension split**, not a rewrite. Document
the trigger and the action up front so we don't repaint the design
later.

| Dimension | v1 target | Trigger to act | Action (silent to users) |
|---|---|---|---|
| Tracked skills | 100 | 150 | No change — still well within cron budget. |
| Tracked skills | 200 | 400 | Bump cron from `*/10` to `*/5`. Doubles GitHub budget (1200/hr) — still 24% of 5k PAT. No code change. |
| Tracked skills | 500+ | sustained | **Shard-per-prefix DO routing.** See shard-key algorithm below. Scanner and stream endpoint both start hashing `Skill.id` into one of N shards; DO instances spun up lazily via `idFromName("UpdateHub-${shard}")`. Client stream endpoint opens N parallel WS to the DO shards that cover its filter and merges output. |
| Concurrent SSE clients | 100 | 500 | No change — single DO handles thousands. |
| Concurrent SSE clients | 1000 | 3000 sustained | Shard by `sessionId` hash (orthogonal to skill shard) — clients stick to one shard, publishers fan out to all. |
| Installed skills / user | 100 | 100 | Switch to `POST /subscribe` automatically in the hook (already designed). |
| Installed skills / user | 5000 | hard cap — reject higher with 413. Revisit if a real user hits it. |

### Shard-key algorithm (deferred to 500-skill trigger)

Goal: preserve locality (users filtering for skill X always hit the
same shard as the publisher of X) and make the mapping deterministic
across the scanner, stream endpoint, and DO without coordination.

```ts
function shardForSkillId(skillId: string, shardCount: number): number {
  // FNV-1a 32-bit — same algorithm already used in check-updates cache key
  let h = 0x811c9dc5 >>> 0;
  for (let i = 0; i < skillId.length; i++) {
    h = Math.imul(h ^ skillId.charCodeAt(i), 0x01000193) >>> 0;
  }
  return h % shardCount;
}

// DO binding: UPDATE_HUB.get(env.UPDATE_HUB.idFromName(`UpdateHub-${shardForSkillId(id, SHARD_COUNT)}`))
```

`SHARD_COUNT` lives in `wrangler.jsonc` as a Worker `var`, not a
secret, so it can be bumped via `wrangler deploy` without code change.
v1 value: `1` — all skills hash to shard 0, addressed via
`idFromName("UpdateHub-0")`. The shard-0-only v1 is already on the
sharded code path, eliminating a migration later.

### What changes when we actually shard

1. **Scanner** — already publishes via `shardForSkillId(event.skillId, env.SHARD_COUNT)`, so no code change; only `SHARD_COUNT` grows.
2. **Stream endpoint** — for each skillId in the filter, computes its
   shard; groups skills by shard; opens one WS per shard; multiplexes
   events onto the single SSE client connection.
3. **Internal publish endpoint** — same grouping as scanner.
4. **DOs** — no code change. Each DO instance is identical; sharding
   is a naming convention.

This keeps the code-change surface to (1) adding the hash helper, (2)
looping the existing single-shard code over a shard list. No schema
change, no client protocol change, no user-visible change.

## Durable Object Design

### Class: `UpdateHub`

```ts
export class UpdateHub implements DurableObject {
  private state: DurableObjectState;
  private sessions = new Map<WebSocket, { filter: Set<string> | null }>();

  constructor(state: DurableObjectState) {
    this.state = state;
    // Rehydrate in-memory filter map from hibernated sockets on wake
    for (const ws of this.state.getWebSockets()) {
      const meta = ws.deserializeAttachment() as { filter: string[] | null } | null;
      const filter = meta?.filter ? new Set(meta.filter) : null;
      this.sessions.set(ws, { filter });
    }
  }

  async fetch(req: Request): Promise<Response> {
    if (req.headers.get("Upgrade") === "websocket") {
      return this.handleWebSocketUpgrade(req);
    }
    if (new URL(req.url).pathname === "/publish") {
      return this.handlePublish(req);
    }
    return new Response("not found", { status: 404 });
  }

  private async handleWebSocketUpgrade(req: Request): Promise<Response> {
    // The stream endpoint resolves the filter (URL param or KV-backed
    // cookie subscription) and passes it here. The DO never parses
    // client input directly — filter is already authoritative by the
    // time it reaches this method.
    const url = new URL(req.url);
    const skills = url.searchParams.get("skills");
    const filter = skills
      ? new Set(skills.split(",").map(s => s.trim()).filter(Boolean))
      : null;  // null reserved for internal tooling; public stream always sets a filter

    const pair = new WebSocketPair();
    // acceptWebSocket triggers hibernation semantics — DO unloads while
    // the socket stays open; wakes on incoming message or broadcast.
    this.state.acceptWebSocket(pair[1]);
    pair[1].serializeAttachment({ filter: filter ? [...filter] : null });
    this.sessions.set(pair[1], { filter });

    return new Response(null, { status: 101, webSocket: pair[0] });
  }

  async webSocketClose(ws: WebSocket) {
    this.sessions.delete(ws);
  }

  async webSocketError(ws: WebSocket) {
    this.sessions.delete(ws);
  }

  private async handlePublish(req: Request): Promise<Response> {
    const event = await req.json<SkillUpdateEvent>();
    let delivered = 0;

    for (const [ws, meta] of this.sessions) {
      if (meta.filter && !meta.filter.has(event.skillId)) continue;
      try {
        ws.send(JSON.stringify({ type: "skill.updated", data: event }));
        delivered++;
      } catch {
        this.sessions.delete(ws);
      }
    }
    return Response.json({ ok: true, delivered });
  }
}
```

**Hibernation semantics**: `state.acceptWebSocket()` is the key API —
sockets accepted this way survive DO eviction. On any incoming message or
`fetch()` invocation the DO wakes, `getWebSockets()` returns the
already-open sockets, and we rebuild the in-memory filter map from their
serialized attachment. Cost: the DO bills only when awake (on publish or
client send) — essentially zero while 1000 clients idle.

**Connection filter map**: `Map<WebSocket, { filter: Set<string> | null }>`.
Filter values are `Skill.id` strings (UUIDs), matching the spec's
`skills=<csv>` query param at the public SSE boundary. The DO does not
need to know plugin/skill names — matching is strictly by `skillId`.

**Broadcast algorithm**: O(N) over connections per event. For 1000
connections at 5 events/min this is trivial. If we ever see CPU pressure,
the next step is not a larger DO — it's **sharding by skill**: hash
`pluginName:skillName` into `idFromName(shard_${i})`, with clients
connecting to the shard(s) matching their filter. Deferred until observed.

## Scanner Design

### Work queue

Every 10 min the cron calls `runSkillUpdateScan(env)`. Budget: 1000ms
Worker CPU + 600 GitHub requests. The scan pulls up to 100 `Skill` rows
with non-null `sourceRepoUrl`, ordered by `lastCheckedAt ASC NULLS FIRST`.
The composite index `[sourceRepoUrl, lastCheckedAt]` backs this.

```ts
export async function runSkillUpdateScan(env: Env): Promise<ScanReport> {
  const skills = await db.skill.findMany({
    where: { sourceRepoUrl: { not: null } },
    orderBy: { lastCheckedAt: "asc" },
    take: 100,
  });

  const report: ScanReport = { scanned: 0, changed: 0, errors: 0 };

  for (const skill of skills) {
    try {
      const etag = await env.SEARCH_CACHE_KV.get(`scanner-etag:${skill.id}`);
      const resp = await fetch(
        `https://api.github.com/repos/${parseOwnerRepo(skill.sourceRepoUrl!)}/commits/${skill.sourceBranch ?? "main"}`,
        {
          headers: {
            "Authorization": `Bearer ${env.GITHUB_TOKEN}`,
            "User-Agent": "verified-skill-scanner",
            ...(etag ? { "If-None-Match": etag } : {}),
          },
        },
      );

      report.scanned++;

      if (resp.status === 304) { continue; }                  // no change
      if (!resp.ok) { report.errors++; continue; }

      const commit = await resp.json();
      const newEtag = resp.headers.get("ETag");
      if (newEtag) await env.SEARCH_CACHE_KV.put(`scanner-etag:${skill.id}`, newEtag, { expirationTtl: 7 * 24 * 3600 });

      if (commit.sha === skill.lastSeenSha) {
        await db.skill.update({ where: { id: skill.id }, data: { lastCheckedAt: new Date() } });
        continue;
      }

      // Provenance suppression (0688 sidecar): skip scope-transfer / local promotions
      if (await isLocallyPromoted(skill)) {
        await db.skill.update({
          where: { id: skill.id },
          data: { lastSeenSha: commit.sha, lastCheckedAt: new Date() },
        });
        report.suppressedLocallyPromoted++;
        continue;
      }

      const newVersion = await createSkillVersionFromCommit(skill, commit, env);
      await db.skill.update({
        where: { id: skill.id },
        data: { lastSeenSha: commit.sha, lastCheckedAt: new Date(), currentVersion: newVersion.version },
      });

      // Transactional outbox write — SkillVersion + UpdateEvent in ONE txn.
      // (scanOneSkill() refactor — see §Delivery Guarantee for the full pattern.)
      const { event } = await db.$transaction(async (tx) => {
        await tx.skillVersion.create({ data: { ... newVersion ... } });
        await tx.skill.update({
          where: { id: skill.id },
          data: { lastSeenSha: commit.sha, lastCheckedAt: new Date(), currentVersion: newVersion.version },
        });
        const eventId = ulid();
        const payload = {
          type: "skill.updated", skillId: skill.id, name: skill.name,
          pluginName: skill.pluginName, version: newVersion.version,
          previousVersion: skill.currentVersion, gitSha: commit.sha,
          contentHash: newVersion.contentHash, diffSummary: newVersion.diffSummary,
          publishedAt: new Date().toISOString(),
        };
        const evt = await tx.updateEvent.create({
          data: { id: eventId, skillId: skill.id, versionId: newVersion.id,
                  source: "scanner", payload },
        });
        return { event: evt };
      });
      // Fire-and-forget publish AFTER commit — reconciler retries on failure.
      publishToUpdateHubWithEventId(env, event.payload, event.id)
        .then(() => db.updateEvent.update({ where: { id: event.id }, data: { publishedAt: new Date() } }))
        .catch(() => { /* reconciler picks up */ });
      report.changed++;
    } catch (err) {
      report.errors++;
      console.error(`[scanner] ${skill.name}`, err);
    }
  }

  return report;
}
```

### ETag caching

Per-skill ETag is stored in `SEARCH_CACHE_KV` with key
`scanner-etag:${skill.id}`, TTL 7 days. `If-None-Match` gets a 304 from
GitHub **and does not count against the rate limit**, cutting effective
budget usage to "changed skills only" (~single digits per hour once
steady-state).

### Rate-limit math

- Fine-grained PAT: 5000 req/hr.
- 100 tracked skills × 6 scans/hr = 600 req/hr worst case (no ETag).
- With ETag (steady state): 600 × ~2% change rate = ~12 full-response requests/hr.
- Webhook fast-path adds bursty spikes but each webhook = 1 scan = 1 API call.
- **Budget headroom**: ~88% unused. Tracked-skill ceiling ≈ 800 before hitting 50% budget.

### Provenance suppression (0688 integration)

`isLocallyPromoted(skill)` reads the 0688 provenance sidecar from the
shared store (same logic used by scope-transfer). If
`origin !== "upstream"` or the skill was promoted/scope-transferred, we
**update `lastSeenSha` silently** (so we don't re-fire on the next scan)
but **do not publish the event or cut a `SkillVersion` row**. Prevents the
scanner from spamming "update available" when the change is our own
in-platform mutation.

## SSE Protocol

### Event types

| Event | Frequency | Payload |
|---|---|---|
| `skill.updated` | On scanner detection | `{type, skillId, name, pluginName, version, previousVersion, gitSha, contentHash, diffSummary, publishedAt}` |
| (keepalive SSE comment) | Every 25s | `: keepalive\n\n` (not a named event) |

### Filter resolution (client perspective)

Typical flow (≤100 installed skills):
```
GET /api/v1/skills/stream?skills=<skillId1>,<skillId2>,...
Accept: text/event-stream
```

Power-user flow (>100 installed skills, URL too large):
```
POST /api/v1/skills/stream/subscribe
Content-Type: application/json
{"skills": ["<uuid>", ...]}           # full list, up to 5000
→ 200 + Set-Cookie: sw-stream-session=<uuid>; Max-Age=86400

GET /api/v1/skills/stream              # no ?skills= param
Cookie: sw-stream-session=<uuid>
Accept: text/event-stream
```

**Authority**: the SSE endpoint resolves the filter (URL first, then
cookie→KV fallback) server-side and forwards it to the DO via the
internal WS upgrade URL (`wss://internal/ws?skills=...`). The DO has
no concept of "unfiltered public stream" — filter-less WS upgrades are
rejected at the stream endpoint, never reaching the DO.

**Not paginated**: the stream is an event source, not a query result.
There is no `offset`, `cursor`, `page`, or `next` concept at any layer.
Missed events during a disconnect are reconciled via the
`GET /api/v1/skills/check-updates` fallback path on reconnect, which
already compares installed SHA against latest DB state.

### Keepalive

Server sends a raw `: keepalive\n\n` SSE comment every 25s (matches
existing `submissions/stream` behavior). Under CF's 30s idle timeout this
is the upper bound we can use safely.

### Auto-reconnect contract

`EventSource` reconnects by default with exponential backoff. Client-side
contract:
- Track `EventSource.readyState` and `ev.lastEventId` (the ULID of the
  most-recent received event; persisted to `localStorage`).
- On reconnect, the browser automatically sets the `Last-Event-ID`
  header from the last `id:` value seen. Server replays events from
  the DO log within the 5-min TTL; on miss, sends a synthetic
  `event: gone\n...` frame and the client falls back to
  `/api/v1/skills/check-updates` for full reconcile.
- After 60 seconds of no successful `open` (per AC-US5-05), fall back
  to 5-min poll against `/api/v1/skills/check-updates` until one
  successful open occurs.
- Filter changes (install/uninstall) close the current stream and open
  a new one with the updated `?skills=` query — no server-side filter
  mutation protocol needed.
- Client-side dedup: a `Set<string>` of recently-seen event IDs
  (capacity 500, FIFO eviction) drops duplicates on the rare
  replay-races-live-event window. Details in §Delivery Guarantee.

## Delivery Guarantee

**Goal**: every `SkillVersion` that lands in the DB results in a
`skill.updated` event delivered to every matching connected client,
even when a Worker isolate dies mid-publish, a DO wake races a
publish, or the client reconnects across a network blip. Target: 99%
of `SkillVersion` writes produce a delivered client event within 10s
P99 (see NFR below).

The design is a classic **transactional outbox + replay log +
idempotency key** stack, layered so each pattern recovers from a
different failure mode.

### Pattern 1 — Transactional Outbox (DB → DO reliability)

Every write path — scanner consumer, submission-processing consumer,
webhook-triggered scan — wraps the `SkillVersion` insert and the
`UpdateEvent` insert in a **single DB transaction**:

```ts
await db.$transaction(async (tx) => {
  const version = await tx.skillVersion.create({ data: { ... } });
  await tx.updateEvent.create({
    data: {
      id: ulid(),                      // "evt_01HXYZ..."
      skillId: skill.id,
      versionId: version.id,
      source: "scanner",               // or "submission" | "webhook-scan"
      payload: buildPayload(skill, version),
    },
  });
});
// Fire-and-forget publish AFTER commit. Success → publishedAt = NOW().
publishToUpdateHub(env, payload, { eventId }).catch(/* reconciler retries */);
```

If the process crashes between `COMMIT` and the `publishToUpdateHub`
call, the row is still in `UpdateEvent` with `publishedAt = NULL`, and
the reconciler picks it up.

**Reconciler** (`src/lib/skill-update/outbox-reconciler.ts`, runs
every 30s inside the existing cron). One job, not per-source:

```ts
async function reconcileOutbox(env: Env) {
  // Any event unpublished for >10s is our responsibility. 10s is the
  // happy-path publish budget; below that we'd race the normal path.
  const stuck = await db.updateEvent.findMany({
    where: {
      publishedAt: null,
      createdAt: { lt: new Date(Date.now() - 10_000) },
      publishAttempts: { lt: 10 },
    },
    orderBy: { createdAt: "asc" },
    take: 50,
  });
  for (const evt of stuck) {
    try {
      await publishToUpdateHubWithEventId(env, evt.payload, evt.id);
      await db.updateEvent.update({
        where: { id: evt.id },
        data: { publishedAt: new Date() },
      });
    } catch (err) {
      await db.updateEvent.update({
        where: { id: evt.id },
        data: {
          publishAttempts: { increment: 1 },
          lastAttemptErr: String(err).slice(0, 500),
        },
      });
      if (evt.publishAttempts + 1 >= 10) {
        logAlert("outbox.stuck-forever", { eventId: evt.id, skillId: evt.skillId });
      }
    }
  }
}
```

**Alerting threshold**: if any `UpdateEvent` row sits with
`publishedAt = NULL` AND `createdAt < NOW() - 5 min` → log `outbox.lag`
AE metric with severity warning. Ten failed attempts on a single
event → critical.

### Pattern 2 — Replay Log + Last-Event-ID (reconnect gap recovery)

The SSE protocol natively supports reconnect via the `Last-Event-ID`
header. Client stores the `id:` of the most recent event it processed
(`seenLastId` in `localStorage`). On reconnect:

```
GET /api/v1/skills/stream?skills=<csv>
Last-Event-ID: evt_01HXYZ...
```

The stream endpoint forwards the ID to the DO in the upgrade URL
(`wss://internal/ws?skills=...&lastEventId=evt_...`). DO behavior:

- **Replay log** — in-memory `Map<eventId, {at, payload}>` with 5-min
  sliding TTL (swept on every wake). All published events land here
  first, before fan-out. Bounded at ~5 updates/day × 5 min = effectively
  single-digit entries at v1 scale; explicit cap at 10k entries with
  LRU eviction for safety.
- **Resolve `lastEventId`**:
  - Hit in log → replay every event with `at > hitAt && filter.has(skillId)`
    in order, then start live stream.
  - Miss (older than 5 min or not in log) → send a synthetic
    `event: gone\ndata: {"reason":"too-old"}\n\n` as the first SSE
    frame, then close. Client interprets this as
    `409 Gone`-equivalent and falls back to `POST /api/v1/skills/check-updates`
    for full reconciliation.

The replay log is **in-memory only** — if the DO cold-starts after a
deploy, `Map.size` is 0 and every reconnect misses. That's
acceptable; deploys are rare and the check-updates fallback is correct.
No KV persistence in v1.

### Pattern 3 — Idempotency on Internal Publish (dedup at the DO)

Webhook + cron can race — both enqueue scans for the same skill
seconds apart. KV `scan-lock` catches most of this at the consumer
layer, but the outbox reconciler can also race with the normal publish
path. Idempotency at the DO boundary is the last line of defense.

`POST /api/v1/internal/skills/publish` body includes the
`eventId` (`UpdateEvent.id`) from the outbox row. The DO's `handlePublish`
checks its replay log:

```ts
private async handlePublish(req: Request): Promise<Response> {
  const event = await req.json<SkillUpdateEvent & { eventId: string }>();
  if (this.replayLog.has(event.eventId)) {
    return Response.json({ ok: true, deduped: true, delivered: 0 });
  }
  this.replayLog.set(event.eventId, { at: Date.now(), payload: event });
  // ... existing fan-out loop ...
}
```

Server-side dedup means a retried publish from the reconciler AFTER
the original publish succeeded results in zero extra client traffic.

### Pattern 4 — Client-Side Dedup (defense in depth)

Studio hook keeps `seenEventIds: Set<string>` per session. `onmessage`:

```ts
if (seenEventIds.has(ev.lastEventId)) return;
seenEventIds.add(ev.lastEventId);
// ... existing update handling ...
```

Bounded at 500 entries with FIFO eviction. Catches the small remaining
window where a replay + live event race at reconnect.

### Why all four, not fewer

| Failure mode | Caught by |
|---|---|
| Worker crash after `COMMIT`, before publish | **P1 outbox + reconciler** |
| DO evicted mid-fanout, publish succeeded but some clients missed | **P2 replay log on reconnect** |
| Webhook + cron both trigger scan; both succeed, both publish | **P3 DO idempotency by eventId** |
| Reconnect arrives while live event in flight | **P4 client dedup** |
| Event older than 5 min at reconnect | P2 `gone` frame → check-updates fallback |
| Reconciler backlog (DB lag) | P1 `outbox.lag` alert |

Each pattern is cheap on its own. The combination lifts delivery from
"best effort" to "99% within 10s P99 measurable" with a single
database table, an in-memory map, a UUID in a payload, and a client
`Set`.

### Apply to all write sources (not just scanner)

This section's guidance applies to **every code path that writes a
`SkillVersion`**:

1. **Scanner consumer** (new in this increment) — outbox row in the
   same txn as the `SkillVersion` insert.
2. **Submission-processing consumer** (existing
   `src/lib/queue/process-submission.ts`) — must be modified to
   write an outbox row whenever it creates a `SkillVersion`. This is
   additive; existing logic unchanged.
3. **Admin rescan / backfill** (existing
   `src/app/api/v1/admin/rescan-published/route.ts`) — same treatment.

One reconciler job covers all three. Source is distinguished by the
`source` column for observability but not for behavior.

### Observability additions (extends §Observability)

| Metric | Dimensions | Source |
|---|---|---|
| `outbox.pending` | — | reconciler start (count of unpublished) |
| `outbox.lag.ms` | — | reconciler per-event `NOW() - createdAt` |
| `outbox.reconciled` | `source` | reconciler on successful retry |
| `outbox.attempts-exceeded` | `source` | reconciler when attempts >= 10 |
| `do.replay.size` | — | DO publish path (`replayLog.size`) |
| `do.replay.hits` | — | DO on `Last-Event-ID` lookup |
| `do.replay.miss.gone` | — | DO on `Last-Event-ID` not in log |
| `do.publish.deduped` | — | DO when eventId already in log |
| `client.dedup.seen` | — | Studio hook beacon (optional) |

### NFR — delivery SLO

**99% of `SkillVersion` writes produce a delivered client event within
10s at P99.** Measurement: `UpdateEvent.publishedAt - UpdateEvent.createdAt`
per-event; rollup via AE percentile. Breach: investigate outbox backlog
or DO health. The reconciler + replay log are the safety nets; if
they're healthy, the SLO is met automatically.

## Webhook Protocol

### GitHub push-event subset consumed

```json
{
  "ref": "refs/heads/main",
  "after": "<commit-sha>",
  "repository": { "full_name": "org/repo", "html_url": "https://github.com/org/repo" }
}
```

### Verification

```ts
const body = await req.text();
const sig = req.headers.get("X-Hub-Signature-256");  // "sha256=<hex>"
if (!await verifyGitHubHmac(body, sig, env.GITHUB_WEBHOOK_SECRET)) {
  return new Response("bad signature", { status: 401 });
}

// Anti-replay: reject repeat X-GitHub-Delivery within 5 minutes (AC-US4-05).
const deliveryId = req.headers.get("X-GitHub-Delivery");
if (deliveryId) {
  const seenKey = `gh-delivery:${deliveryId}`;
  if (await env.SEARCH_CACHE_KV.get(seenKey)) {
    return new Response(null, { status: 200 });  // ack without side effect
  }
  await env.SEARCH_CACHE_KV.put(seenKey, "1", { expirationTtl: 300 });
}
```

`verifyGitHubHmac()` is a thin wrapper over `crypto.subtle.verify` that
matches GitHub's exact format (`sha256=` prefix, hex lowercase). Not the
same as our own `webhook-auth.ts` (which signs inbound-to-internal calls
using JSON + timestamp anti-replay). Different secret, different format.
Anti-replay is enforced on the `X-GitHub-Delivery` UUID per AC-US4-05,
reusing the KV-based pattern from `webhook-auth.ts`.

### Scanner invocation

On verified push to the tracked branch, look up `Skill` by `sourceRepoUrl`
matching `repository.html_url` and `sourceBranch === ref.split("/").pop()`.
For each match, invoke `scanOneSkill(skill, env)` (shared code path with
the cron). Log and respond within the 10s worker limit — if >10 matches
per repo, dispatch via `ctx.waitUntil`.

## Studio UI Architecture

### Shared hook: `useSkillUpdates()`

Location: `src/studio/lib/use-skill-updates.ts` (NEW, in vskill repo).

```ts
type SkillUpdateEvent = {
  type: "skill.updated";
  skillId: string;
  name: string;
  pluginName: string;
  version: string;
  previousVersion: string;
  diffSummary?: string;
  publishedAt: string;
  // gitSha, contentHash omitted from client surface for UI simplicity
};

export function useSkillUpdates(installedSkillIds: string[]): {
  updates: Map<string, SkillUpdateEvent>;   // key = skillId; only includes tracked skills with pending updates
  hasUpdate: (skillId: string) => boolean;  // convenience: updates.has(skillId)
  isTrackedForUpdates: (skillId: string) => boolean;  // derivable from check-updates response (Skill.sourceRepoUrl non-null)
  dismiss: (skillId: string) => void;
  status: "connecting" | "connected" | "fallback";  // per AC-US5-01
}
```

Responsibilities:
1. **One EventSource per tab, never more.** If `installedSkillIds` is
   short enough to fit in the URL (≤100 ids, ≤2 KB encoded), opens
   `/api/v1/skills/stream?skills=<csv>` directly. If larger, first
   `POST /api/v1/skills/stream/subscribe` with the list, then opens
   `/api/v1/skills/stream` without a query (cookie-keyed).
2. On `installedSkillIds` change, decides whether a simple re-open with
   new query suffices or the subscription needs refreshing (re-POST).
   Either way: close the old EventSource, open a new one.
3. Aggregates events into a `Map` keyed by `skillId`. Later events for
   the same skill overwrite earlier ones.
4. Tracks `visibilityState` — on `visible`, events fire a toast; on
   `hidden`, only the badge increments (per AC-US5-02).
5. Falls back to 5-min `/api/v1/skills/check-updates` polling after 60
   seconds of no successful open (per AC-US5-05), setting
   `status: "fallback"`.
6. `dismiss(skillId)` removes the entry from the map without
   round-tripping the server (server has no concept of dismissal in v1).
7. **Tracking affordance**: maintains an internal
   `trackedSet: Set<string>` built from the most recent
   `/api/v1/skills/check-updates` response, which includes a
   `trackedForUpdates: boolean` field per skill (derived server-side
   from `Skill.sourceRepoUrl !== null`). `isTrackedForUpdates(id)`
   reads this set. Untracked skills render a dim "not tracked" dot
   in `SkillRow` with a tooltip — e.g., "Upstream source not
   registered; updates won't be detected automatically." No API
   change: the `check-updates` response must start including
   `trackedForUpdates` per skill (one-field extension).

### Consumers (all in vskill `src/studio/`)

| Component | Behavior |
|---|---|
| `SkillRow` (existing) | Three-state indicator: (a) **bright blue dot** when `updates.has(skillId)` — update pending; (b) **dim gray dot with tooltip** "Upstream source not registered" when `!isTrackedForUpdates(skillId)`; (c) **nothing** when tracked and up-to-date. Click on bright dot → opens `RightPanel.UpdateAction`. |
| `SidebarSection` | Renders an "N updates" chip next to the section header (only counts tracked skills with pending updates — untracked never contribute). |
| `TopRail.UpdateBell` (NEW) | Bell icon with badge count = `updates.size`. Click → drops dropdown listing updates with version delta. |
| `RightPanel.UpdateAction` (NEW) | Inline "Install update" button that shells out to `vskill update <skill>` via the existing studio IPC. Only renders for tracked skills with a pending update. |

These components were originally designed in the superseded 0683 increment
— their shells can be pulled forward; only the data-source swap (poll →
SSE) is net-new work.

### Subscription lifecycle

Mount → single `useSkillUpdates()` instance per Studio app (hoist to the
root layout). Filter changes (e.g., user installs a new skill) recompute
the `installed` array; the hook tears down the EventSource and opens a
new one. Unmount → close.

## Security

| Concern | Mitigation |
|---|---|
| `GITHUB_TOKEN` in source | Stored in CF secrets (`wrangler secret put GITHUB_TOKEN`) and `.dev.vars` for local. Never in git. |
| `GITHUB_WEBHOOK_SECRET` leakage | Same storage model. HMAC verified with constant-time compare. |
| `INTERNAL_BROADCAST_KEY` reuse | One secret, two consumers (existing `broadcast` + new `skills/publish`). No scope expansion. |
| Public SSE auth | **None by design** — event payload contains only public skill metadata (name, version, SHA, diff summary). No PII. No user-scoped data. |
| SSE connection flooding | Reuse existing IP-based rate limit middleware on `/api/v1/skills/stream` connect. 60 concurrent opens/IP/hr is enough for real Studio users and blocks trivial flood. |
| Replay of webhook payloads | GitHub's HMAC includes the full body + their delivery ID in headers; we additionally reject payloads where the signature fails verification. (GitHub deliveries are inherently idempotent — replaying triggers a scan that no-ops against current SHA.) |
| Filter injection via `?skills=` | Filter values go into a `Set<string>` and are only used for O(1) `has()` lookups. No SQL, no shell. Cap input length at 2KB (~200 skillIds) to prevent OOM. Malformed UUIDs are dropped silently. |

## Observability

Per NFR-006, scanner, DO fan-out, webhook, and SSE connection counts
MUST be queryable via Cloudflare Analytics Engine (AE). Add a dedicated
AE binding `UPDATE_METRICS_AE` in `wrangler.jsonc`. Metrics emitted:

| Metric | Dimensions | Source |
|---|---|---|
| `scanner.runs.total` | — | every cron invocation |
| `scanner.updates.detected` | `skillId` | scanner on SHA change |
| `scanner.suppressed.locally-promoted` | `skillId` | provenance suppression |
| `scanner.errors.total` | `skillId`, `httpStatus` | per-row catch |
| `scanner.duration.ms` | — | end-of-scan timing |
| `do.connections.current` | — | DO `publish` path, `getWebSockets().length` |
| `do.fanout.size` | `skillId` | DO `publish` per event |
| `do.fanout.latency.ms` | — | DO publish roundtrip |
| `sse.connections.open` | — | SSE endpoint connect/disconnect |
| `sse.fallback.switched` | — | Studio client opt-in (via a beacon POST) |
| `webhook.received` | `repoUrl` | webhook endpoint |
| `webhook.replay.suppressed` | — | AC-US4-05 enforcement |
| `outbox.pending` | — | reconciler start (count of unpublished) |
| `outbox.lag.ms` | — | reconciler per-event `NOW() - createdAt` |
| `outbox.reconciled` | `source` | reconciler on successful retry |
| `outbox.attempts-exceeded` | `source` | reconciler when attempts ≥ 10 |
| `do.replay.size` | — | DO publish path (`replayLog.size`) |
| `do.replay.hits` | — | DO on `Last-Event-ID` lookup match |
| `do.replay.miss.gone` | — | DO on `Last-Event-ID` not in log |
| `do.publish.deduped` | — | DO when eventId already in replay log |
| `delivery.end-to-end.ms` | — | derived: `UpdateEvent.publishedAt - createdAt` |

`console.log` stays as the immediate debugging surface (visible via
`wrangler tail`); AE is the durable query store. The delivery SLO
(99% within 10s P99) is computed from `delivery.end-to-end.ms`.

## Migration / Rollout

1. **Prisma migration** — `migrations/<timestamp>_skill_source_tracking/`
   adds the four nullable columns + composite index. Reversible (no data
   loss on rollback).
2. **Seed script** — `scripts/seed-skill-source-repos.ts` (NEW):
   - Reads a curated list of ~100 skills from
     `scripts/skill-source-seed.json` (hand-authored, committed).
     Entries: `{name, sourceRepoUrl, sourceBranch?}`.
   - For each, finds the matching `Skill` row and updates
     `sourceRepoUrl` + `sourceBranch`. Idempotent.
   - Runs once per environment: `pnpm tsx scripts/seed-skill-source-repos.ts`.
3. **Deploy outbox + reconciler + scanner together** (no UI risk) —
   ships cron change + `scanner.ts` + `publish` endpoint + new
   `UpdateEvent` table + reconciler. Reconciler MUST land in the same
   deploy as the scanner; if outbox writes start without the
   reconciler running, every transient publish failure becomes a stuck
   row. Validates end-to-end at the server layer. Events go to the
   DO but no clients yet — events just get dropped (no sessions).
4. **Deploy DO + SSE** — adds `wrangler.jsonc` DO binding +
   `update-hub.ts` (with replay log + idempotency) + `stream/route.ts`
   (with `Last-Event-ID` support). After this step the pipeline is
   wired end-to-end server-side with full delivery guarantee.
5. **Deploy Studio UI** — hook + components in vskill. First ship behind
   a `FEATURE_LIVE_UPDATES` env flag (default on for Anton, opt-in for
   rest via `vskill config set live-updates true`); flip fully on after
   72 hours of clean pipeline metrics (including
   `outbox.lag.ms` P99 < 10s and zero `outbox.attempts-exceeded`).
6. **Webhook fast-path** — register GitHub webhook on the first
   first-party repo. Deploy is a no-op beyond the endpoint itself (already
   shipped step 4). Validate end-to-end (~1s latency).
7. **Submission-processing outbox retrofit** — modify the existing
   `src/lib/queue/process-submission.ts` to write an `UpdateEvent` row
   in the same txn as its `SkillVersion` insert. Non-breaking —
   clients already connected start receiving events from the
   submission path once this ships. Landing AFTER step 4 ensures the
   DO is ready to consume.

## File Manifest

### NEW files — `vskill-platform/`

```
src/lib/skill-update/
  scanner.ts                          # scanOneSkill(skillId, env) — invoked by queue consumer
  queue-consumer.ts                   # unified scan-high + scan-normal consumer
  scan-lock.ts                        # KV-backed dedup helper (scan-lock:<skillId>, TTL 30s)
  enqueue.ts                          # producers: webhook / user-trigger / cron / discovery
  update-hub.ts                       # Durable Object class (incl. replay log + idempotency)
  github-api.ts                       # thin fetch wrapper w/ ETag + RL header capture
  publish.ts                          # outbox-aware publisher: publishToUpdateHubWithEventId()
  outbox-reconciler.ts                # 30s cron — retries unpublished UpdateEvent rows
  outbox-writer.ts                    # txn helper used by every SkillVersion-writing path
  types.ts                            # SkillUpdateEvent, ScanMessage, ScanReport, UpdateEventRow
  discovery/
    enqueue.ts                        # called by /check-updates for unresolved skills
    resolver.ts                       # CF Queue consumer — infers sourceRepoUrl from metadata
    __tests__/
      enqueue.test.ts
      resolver.test.ts
  __tests__/
    scanner.test.ts
    queue-consumer.test.ts
    scan-lock.test.ts
    update-hub.test.ts
    update-hub.replay.test.ts
    update-hub.idempotency.test.ts
    github-api.test.ts
    outbox-reconciler.test.ts
    outbox-writer.test.ts

src/app/api/v1/skills/stream/route.ts                       # public SSE endpoint
src/app/api/v1/skills/stream/subscribe/route.ts             # POST subscription (>100-skill users)
src/app/api/v1/webhooks/github/route.ts                     # webhook receiver → enqueue scan-high
src/app/api/v1/internal/skills/publish/route.ts             # internal publish
src/app/api/v1/skills/[id]/register-tracking/route.ts       # explicit opt-in (light C)
src/app/api/v1/skills/[id]/rescan/route.ts                  # user "check now" → enqueue scan-high (AC-US8-01), returns {jobId}

scripts/seed-tracked-skills.ts              # per AC-US1-05
scripts/tracked-skills-seed.json            # curated 100 skills

prisma/migrations/<ts>_skill_source_tracking/migration.sql  # 4 sourceRepo* cols + 3 resolution* cols + 2 indexes
prisma/migrations/<ts+1>_update_event_outbox/migration.sql  # new UpdateEvent table + 2 indexes
```

### MODIFY files — `vskill-platform/`

```
wrangler.jsonc                   # add UPDATE_HUB DO binding + migration v2
                                 # add SCAN_HIGH_QUEUE + SCAN_NORMAL_QUEUE producers + consumers
                                 # add DISCOVERY_RESOLVE_QUEUE producer + consumer
                                 # add vars.SHARD_COUNT = "1"
                                 # change cron "0 * * * *" → "*/10 * * * *"
scripts/build-worker-entry.ts    # export { UpdateHub }; cron enqueues scan-normal batch (per-skill);
                                 # queue dispatch for scan-high/scan-normal/discovery-resolve;
                                 # 30s outbox-reconciler branch inside scheduled()
prisma/schema.prisma             # add 4 sourceRepo* cols + 3 resolution* cols + 2 indexes on Skill;
                                 # add new UpdateEvent model + 2 indexes
src/app/api/v1/skills/check-updates/route.ts  # add trackedForUpdates + resolutionState fields, enqueue resolver for unresolved
src/lib/queue/process-submission.ts  # retrofit: write UpdateEvent row in same txn as SkillVersion insert
src/app/api/v1/admin/rescan-published/route.ts  # retrofit: same outbox write pattern
.dev.vars.example                # add GITHUB_WEBHOOK_SECRET placeholder
.env.example                     # mirror
README.md                        # "Setting up webhook secret" section
```

### NEW files — `vskill/`

```
src/studio/lib/use-skill-updates.ts       # shared React hook
src/studio/components/UpdateBell.tsx      # TopRail indicator
src/studio/components/UpdateAction.tsx    # RightPanel button
src/studio/components/UpdateChip.tsx      # SidebarSection + SkillRow chip
src/studio/lib/__tests__/use-skill-updates.test.ts
```

### MODIFY files — `vskill/`

```
src/studio/components/SkillRow.tsx        # consume useSkillUpdates
src/studio/components/SidebarSection.tsx  # render UpdateChip
src/studio/components/TopRail.tsx         # render UpdateBell
src/studio/components/RightPanel.tsx      # render UpdateAction
src/studio/layout/StudioRoot.tsx          # hoist useSkillUpdates provider
```

## Testing Strategy

Detailed BDD test plans per task live in `tasks.md`. Pipeline-level
summary:

- **Unit (Vitest)**
  - Scanner SHA compare + ETag handling + provenance suppression.
  - UpdateHub fanout with filters (mocked WS).
  - HMAC verification for GitHub webhook.
- **Integration (Vitest + miniflare)**
  - End-to-end: scanner → internal publish → DO → WS → SSE.
- **E2E (Playwright)**
  - Studio tab opens → mocked publish → UpdateBell badge increments
    within 2s.
  - Visibility gating: background tab receives event → foreground
    transition fires toast once.
  - EventSource drop → 3 failures → fallback poll fires and recovers.
- **Load**
  - 100 concurrent SSE clients + 5 publishes/min; assert DO CPU well
    below limit and zero drops over 10 min.

Coverage targets: unit 95%, integration 90%, E2E 100% of P1 ACs.

## Technical Challenges

### C-1: Hibernation + in-memory filter map

**Challenge**: On DO wake after hibernation, `sessions` Map is empty. If
we forget to rehydrate from `state.getWebSockets()` we'll broadcast to
zero clients despite sockets being open.
**Solution**: Rehydrate in the constructor (CF spec: constructor runs on
every wake). Attach the filter via `ws.serializeAttachment()` at accept
time. Covered by `update-hub.test.ts` hibernation round-trip case.
**Risk**: Low — CF documents this exact pattern. Test asserts the
rehydrated filter matches.

### C-2: Scanner minute dispatch colliding with existing cron work

**Challenge**: Current cron does heavy DB reconciliation at `minute === 0`
and enrichment every run. Adding scanner at every 10 minutes risks CPU
contention (50ms budget).
**Solution**: Scanner runs on minutes {0, 10, 20, 30, 40, 50} but its
`findMany` is capped at 100 rows and runs AFTER enrichment in
`ctx.waitUntil`. Scanner failure never blocks anything else — wrapped in
its own `.catch()`. If we do see contention, bump to `*/15` (4 scans/hr)
first, shard second.
**Risk**: Medium — measured during step 3 of rollout before UI ships.

### C-3: Webhook latency budget vs CF 10s Worker cap

**Challenge**: GitHub webhook payload references a repo with N tracked
skills (worst case: a meta-repo with 50). 50 × ~200ms GitHub API call =
10s — right at the limit.
**Solution**: For webhook-invoked scans, return 200 immediately after
HMAC verify and dispatch the scan via `ctx.waitUntil`. GitHub retries on
timeout which would double-fire the scanner — mitigated by SHA-idempotent
scanner logic (same SHA = no-op).
**Risk**: Low — idempotent by design.

### C-4: SSE → WS bridge inside the Worker

**Challenge**: CF Workers can't directly upgrade a client's HTTP request
to a WebSocket talking to the DO and fan out SSE — the Worker acts as a
proxy: client SSE connection → Worker holds open `ReadableStream` →
Worker opens WS to DO stub → each DO message pushed into the stream as
an SSE event.
**Solution**: Implement in `stream/route.ts`:
```ts
// v1: single shard; helper returns 0, name is "UpdateHub-0"
const shard = 0;  // shardForSkillId(... ) when sharding activates
const hubId = env.UPDATE_HUB.idFromName(`UpdateHub-${shard}`);
const hub = env.UPDATE_HUB.get(hubId);
const upgradeReq = new Request("https://hub/ws?skills=" + encoded, {
  headers: { "Upgrade": "websocket" },
});
const wsResp = await hub.fetch(upgradeReq);
const ws = wsResp.webSocket!;
ws.accept();
ws.addEventListener("message", (ev) => controller.enqueue(`event: skill-update\ndata: ${ev.data}\n\n`));
```
**Risk**: Medium — CF edge case; covered by integration test that exercises
both client disconnect (cleanup the WS) and DO-side close (close the SSE).

## Related ADRs

- **ADR-0708-01** — UpdateHub Durable Object as cross-isolate broadcast hub.
- **ADR-0708-02** — SSE over WebSocket for public skill-update stream.
- **ADR-0688-01** — Prior SSE-over-WS decision for scope-transfer (precedent).
- **ADR-0688-02** — Provenance sidecar format (consumed by scanner).

## Related Documents

- [architecture.md](./architecture.md) — end-to-end system diagram,
  update propagation sequence, discovery/registration sequence,
  backpressure/scaling notes, file-path index.

## Out of Scope (reinforced)

- `vskill watch` CLI daemon — dropped (user decision 2026-04-24).
- **Pagination / cursors on the SSE endpoint.** This is an event stream,
  not a query result. There is no `?page=`, `?offset=`, `?cursor=`, no
  "next batch" protocol. Missed-event recovery uses the existing
  `/api/v1/skills/check-updates` diff path on reconnect, not a paginated
  event replay.
- **Active DO sharding in v1.** The shard-key algorithm is documented
  under "Scaling Triggers" and the DO is named `UpdateHub-0` from day
  one, but only one shard is spun up. Sharding activates when the
  scaling trigger fires.
- Pre-signed R2 tarball URLs for update delivery.
- Multi-upstream per skill (`TrackedSkillSource` table).
- Managed-agent classification / changelog generation.
