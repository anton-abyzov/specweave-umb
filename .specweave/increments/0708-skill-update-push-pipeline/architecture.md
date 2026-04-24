# 0708 — Skill Update Push Pipeline: Architecture

## Context

verified-skill.com is the serving plane for a growing catalog of skills
installed by Skill Studio users. Today, users learn about upstream
updates only by manually running `vskill outdated` or by the UI polling
from every tab, burning GitHub rate limit. This increment introduces a
centralized push pipeline: **all four scan-triggering paths** (webhook
fast-path, user "check now", 10-min cron, and discovery resolver)
funnel into **one unified scanner queue** with priority lanes, a
hibernatable Durable Object fans SHA-change events out to connected
Studio tabs over SSE, and the catalog grows continuously through a
**discovery resolver** that piggybacks on the platform's existing
`/check-updates` traffic (Option D, see `plan.md` §"Skill Discovery &
Registration"). Everything runs on Cloudflare Workers. Target marginal
cost: $5–15/mo.

## Unified Scanner Queue (integration point)

Every path that could trigger a GitHub scan enters the same queue. Four
producers, two queues (high + normal), one consumer, one GitHub client,
one rate-limit accounting surface. No direct GitHub fetch lives outside
the consumer.

```mermaid
flowchart LR
    subgraph Producers["Producers (enqueue ScanMessage)"]
        P1["Webhook receiver<br/>/webhooks/github<br/>priority HIGH"]
        P2["User 'check now'<br/>POST /skills/:id/rescan<br/>priority MEDIUM"]
        P3["Cron sweep<br/>*/10 min, top 100<br/>priority LOW"]
        P4["Discovery resolver<br/>after inference<br/>priority LOW"]
    end

    subgraph Queues["CF Queues"]
        QH[(scan-high<br/>batch 5 / 2s<br/>concurrency 6)]
        QN[(scan-normal<br/>batch 20 / 10s<br/>concurrency 2)]
    end

    subgraph Consumer["Unified consumer"]
        C["handleScanBatch<br/>queue-consumer.ts"]
        Lock{{"scan-lock KV<br/>TTL 30s"}}
        RL{{"GitHub RL check<br/>remaining >= 500 ?"}}
        Scan["scanOneSkill<br/>scanner.ts"]
    end

    subgraph Out["Outputs"]
        DB[("Neon<br/>SkillVersion insert<br/>lastSeenSha update")]
        Pub["POST /internal/skills/publish"]
        Hub["UpdateHub DO"]
        DLQ["submission-dlq"]
        Shed["log queue.scan.shed<br/>ACK without retry"]
        Skip["ACK — no GitHub call"]
    end

    P1 -->|source: webhook| QH
    P2 -->|source: user-trigger| QN
    P3 -->|source: cron| QN
    P4 -->|source: discovery| QN

    QH -->|batch| C
    QN -->|batch| C

    C --> Lock
    Lock -->|hit + SHA still fresh| Skip
    Lock -->|miss or webhook newer| RL
    RL -->|low + cron/discovery| Shed
    RL -->|OK or webhook/user| Scan
    Scan --> DB
    Scan --> Pub
    Pub --> Hub
    C -.->|max retries hit| DLQ

    classDef p fill:#eef,stroke:#66a
    classDef q fill:#ffe,stroke:#a90
    classDef c fill:#efe,stroke:#696
    classDef out fill:#fee,stroke:#a66
    class P1,P2,P3,P4 p
    class QH,QN q
    class C,Scan,Lock,RL c
    class DB,Pub,Hub,DLQ,Shed,Skip out
```

## End-to-End System Architecture

```mermaid
flowchart LR
    subgraph Upstream["Upstream sources"]
        GH["GitHub repos<br/>anthropic-skills/<br/>verified-skill/<br/>community/"]
        WH["GitHub push webhook"]
    end

    subgraph Client["Client — Skill Studio"]
        Studio["Studio tab<br/>useSkillUpdates hook"]
        EventSource["EventSource<br/>GET /skills/stream"]
        PollFB["5-min poll fallback<br/>/skills/check-updates"]
    end

    subgraph Worker["Cloudflare Worker — verified-skill.com"]
        Cron["Cron trigger<br/>*/10 * * * *<br/>enqueues 100 skills"]
        Scanner["Scanner<br/>scanOneSkill<br/>scanner.ts"]
        QConsumer["Queue consumer<br/>queue-consumer.ts<br/>dedup + RL guard"]
        GhClient["GitHub API client<br/>github-api.ts<br/>ETag + RL header capture"]
        WebhookEP["POST /webhooks/github<br/>HMAC verify, anti-replay<br/>→ enqueue scan-high"]
        RescanEP["POST /skills/:id/rescan<br/>user 'check now'<br/>→ enqueue scan-normal"]
        CheckEP["POST /skills/check-updates<br/>+ trackedForUpdates field<br/>+ resolutionState field"]
        Resolver["Discovery resolver<br/>discovery/resolver.ts<br/>queue consumer"]
        InternalPub["POST /internal/skills/publish<br/>X-Internal-Key HMAC"]
        StreamEP["GET /skills/stream<br/>SSE proxy to DO<br/>?skills=csv or cookie sub"]
        SubEP["POST /skills/stream/subscribe<br/>cookie-backed filter"]
    end

    subgraph Storage["Storage"]
        DB[("Neon Postgres<br/>Skill + SkillVersion<br/>+ sourceRepoUrl + resolution cols<br/>+ UpdateEvent outbox")]
        KV[("Workers KV<br/>ETag + subs + scan-lock<br/>+ github-rl:remaining")]
        ScanQH["CF Queue scan-high<br/>webhook only"]
        ScanQN["CF Queue scan-normal<br/>cron + user + discovery"]
        DiscQ["CF Queue discovery-resolve<br/>batch 10 / 3s"]
    end

    subgraph DO["Durable Object"]
        Hub["UpdateHub-0<br/>hibernatable WS<br/>Map&lt;WS,filter&gt;<br/>fanout match skillId"]
    end

    GH -->|push event| WH
    WH -->|HMAC signed| WebhookEP
    WebhookEP -->|enqueue HIGH| ScanQH
    Cron -->|per-skill enqueue| ScanQN
    Studio -->|'check now'| RescanEP
    RescanEP -->|enqueue NORMAL| ScanQN
    ScanQH -->|batch| QConsumer
    ScanQN -->|batch| QConsumer
    QConsumer -->|dedup OK + RL OK| Scanner
    Scanner -->|commits/:branch + ETag| GhClient
    GhClient -->|REST| GH
    GhClient -->|RL headers| KV
    Scanner -->|new SkillVersion| DB
    Scanner -->|event| InternalPub
    InternalPub -->|stub fetch| Hub
    Studio -->|open| EventSource
    Studio -.->|if blocked| PollFB
    EventSource -->|SSE| StreamEP
    StreamEP <-->|internal WS| Hub
    Hub -->|skill.updated frames| StreamEP
    StreamEP -->|SSE events| EventSource
    Studio -->|installed list| CheckEP
    CheckEP -->|enqueue unresolved| DiscQ
    DiscQ -->|batch| Resolver
    Resolver -->|fetch SKILL.md<br/>or plugin manifest| GH
    Resolver -->|upsert sourceRepoUrl| DB
    Resolver -->|enqueue initial scan LOW| ScanQN
    PollFB -->|fallback path| CheckEP

    classDef ext fill:#eef,stroke:#66a
    classDef worker fill:#efe,stroke:#696
    classDef store fill:#fee,stroke:#a66
    classDef do fill:#fef,stroke:#96a
    class GH,WH ext
    class Cron,Scanner,QConsumer,GhClient,WebhookEP,RescanEP,CheckEP,Resolver,InternalPub,StreamEP,SubEP worker
    class DB,KV,ScanQH,ScanQN,DiscQ store
    class Hub do
```

## Update Propagation Flow

How a single upstream commit becomes an "Update available" badge in a
Studio tab. Both paths (webhook fast-path and cron polling) converge on
the same internal publish step.

```mermaid
sequenceDiagram
    autonumber
    participant Dev as Upstream author
    participant GH as GitHub
    participant WH as Webhook endpoint
    participant Cron as Cron trigger
    participant QH as scan-high queue
    participant QN as scan-normal queue
    participant QC as Queue consumer
    participant Sc as Scanner
    participant DB as Neon DB
    participant Pub as Internal publish
    participant Hub as UpdateHub DO
    participant SSE as SSE endpoint
    participant App as Studio tab

    Note over Dev,GH: skill A releases v1.2.3
    Dev->>GH: git push main (new SHA)

    alt First-party repo with webhook
        GH-->>WH: push event (HMAC)
        WH->>WH: verify X-Hub-Signature-256
        WH->>WH: dedupe X-GitHub-Delivery
        WH->>QH: enqueue {skillId, source: webhook, expectedSha}
    else Third-party repo (no webhook)
        Cron->>DB: findMany top 100 by lastCheckedAt ASC
        DB-->>Cron: skill rows
        Cron->>QN: sendBatch [{skillId, source: cron}, ...]
    end

    QH->>QC: batch (high, concurrency 6)
    QN->>QC: batch (normal, concurrency 2)
    QC->>QC: read scan-lock:{skillId}
    alt lock fresh + SHA unchanged
        Note right of QC: ACK, skip GitHub
    else
        QC->>QC: check github-rl:remaining
        alt remaining < 500 and source cron/discovery
            Note right of QC: shed message, ACK
        else
            QC->>Sc: scanOneSkill(skillId)
            Sc->>GH: GET /commits/:branch + If-None-Match
            GH-->>Sc: 200 + new commit
            Sc->>QC: write scan-lock + RL remaining
        end
    end

    Sc->>Sc: check 0688 provenance sidecar
    alt locally promoted
        Sc->>DB: update lastSeenSha + lastCheckedAt
        Note right of Sc: suppressed — no publish
    else upstream change
        Sc->>DB: insert SkillVersion + update Skill.currentVersion
        Sc->>Pub: POST /internal/skills/publish (X-Internal-Key)
        Pub->>Hub: stub.fetch /publish
        Hub->>Hub: for ws in sessions: if filter.has(skillId) send
        Hub-->>SSE: WS frame skill.updated
        SSE-->>App: event: skill.updated data: {...}
        App->>App: update Map, visibility check
        alt tab visible
            App->>App: toast + badge increment
        else tab hidden
            App->>App: badge increment only
        end
    end
```

## User "Check Now" Flow (on-demand rescan)

The user clicks "Check now" on a skill row in Studio — same pipeline,
different entry point. The result arrives via the normal SSE fan-out,
so there is no special return channel for this flow.

```mermaid
sequenceDiagram
    autonumber
    participant App as Studio tab
    participant RE as POST /skills/:id/rescan
    participant QN as scan-normal queue
    participant QC as Queue consumer
    participant Sc as Scanner
    participant Pub as Internal publish
    participant Hub as UpdateHub DO
    participant SSE as SSE endpoint

    App->>RE: POST /skills/:id/rescan
    RE->>RE: rate-limit 10/min/session
    RE->>QN: enqueue {skillId, source: user-trigger, forceRefresh: true, requestId}
    RE-->>App: 202 {jobId: requestId}
    App->>App: show spinner on skill row

    QN->>QC: batch
    QC->>QC: read scan-lock
    Note right of QC: forceRefresh=true skips dedup window
    QC->>Sc: scanOneSkill(skillId)
    Sc->>Sc: GitHub call, compare SHA
    alt SHA unchanged
        Sc->>Sc: no-op, update lastCheckedAt
        Note right of Sc: no event published — UI clears spinner on timeout
    else new SHA
        Sc->>Pub: publish skill.updated
        Pub->>Hub: stub.fetch /publish
        Hub-->>SSE: WS frame
        SSE-->>App: SSE event skill.updated
        App->>App: spinner → toast + badge
    end
```

Key property: the user-trigger flow is identical to cron from the
consumer onwards — same dedup, same rate-limit guard, same
propagation. `forceRefresh` only bypasses the 30s scan-lock window; it
never bypasses the rate-limit guard, so we never burn budget on a user
click when GitHub is already at its limit.

## Delivery Guarantee — Outbox as Junction

The transactional outbox is the junction between the **write side**
(any code path that creates a `SkillVersion`) and the **broadcast
side** (DO fan-out). Every write enters the outbox in the same DB
transaction as the version row; a reconciler cron owns the
"eventually delivered" guarantee. Details and code in plan.md
§Delivery Guarantee.

```mermaid
flowchart LR
    subgraph Write["Write side — every SkillVersion writer"]
        Sub["Submission consumer<br/>process-submission.ts"]
        ScanC["Scanner consumer<br/>queue-consumer.ts"]
        Admin["Admin rescan<br/>admin/rescan-published"]
    end

    subgraph DB["Neon Postgres"]
        SV[("SkillVersion<br/>new row")]
        UE[("UpdateEvent outbox<br/>publishedAt=NULL<br/>publishAttempts=0")]
        TXN{{"ONE transaction<br/>(Prisma $transaction)"}}
    end

    subgraph Publish["Broadcast side"]
        FF["fire-and-forget<br/>publishToUpdateHub<br/>WithEventId"]
        Recon["outbox-reconciler<br/>every 30s<br/>retries unpublished"]
        IPE["POST /internal/skills/publish<br/>X-Internal-Key + eventId"]
        Hub["UpdateHub DO<br/>replay log + idempotency<br/>dedup on eventId"]
        SSE["Connected SSE clients"]
    end

    Sub --> TXN
    ScanC --> TXN
    Admin --> TXN
    TXN --> SV
    TXN --> UE
    TXN -->|COMMIT| FF

    FF -->|success| Mark["UPDATE UpdateEvent<br/>SET publishedAt = NOW"]
    FF -.->|failure / worker dies| UE

    UE -.->|publishedAt NULL<br/>+ createdAt < now-10s| Recon
    Recon --> IPE
    FF --> IPE
    IPE --> Hub
    Hub --> SSE
    Hub -.->|eventId already seen| Dedup["no-op<br/>200 deduped=true"]

    classDef write fill:#eef,stroke:#66a
    classDef db fill:#fee,stroke:#a66
    classDef pub fill:#efe,stroke:#696
    class Sub,ScanC,Admin write
    class SV,UE,TXN db
    class FF,Recon,IPE,Hub,SSE,Mark,Dedup pub
```

Key property: if the Worker crashes after `COMMIT` but before `FF`
fires, the row sits with `publishedAt=NULL` and the reconciler picks
it up within ~30s. If the DO already processed the eventId (e.g., the
crash happened between DO success and `Mark`), the reconciler's retry
is deduped at the DO and `publishedAt` still gets set on retry success.

## Client Reconnect with Last-Event-ID

Shows how the DO's in-memory replay log closes the gap when a Studio
tab reconnects after a blip, and how the `gone` fallback hands off to
full reconcile via `check-updates`.

```mermaid
sequenceDiagram
    autonumber
    participant App as Studio tab
    participant ES as EventSource
    participant SSE as SSE endpoint
    participant Hub as UpdateHub DO
    participant Log as DO replay log<br/>(in-memory Map, 5-min TTL)
    participant Check as /skills/check-updates

    Note over App,ES: WiFi drops; seenLastId = "evt_01HXA"

    App->>ES: reconnect
    ES->>SSE: GET /skills/stream?skills=...<br/>Last-Event-ID: evt_01HXA
    SSE->>Hub: upgrade WS ?skills=...&lastEventId=evt_01HXA
    Hub->>Log: lookup evt_01HXA
    alt hit — within 5-min TTL
        Log-->>Hub: {at, payload}
        Hub->>Hub: gather events where<br/>at > hitAt AND filter.has(skillId)
        loop each missed event
            Hub-->>SSE: WS frame (replay)
            SSE-->>ES: event: skill.updated<br/>id: evt_...<br/>data: {...}
            ES->>App: onmessage (dedup via seenEventIds)
        end
        Hub->>SSE: [switch to live stream]
    else miss — older than 5 min or evicted
        Hub-->>SSE: WS frame {type: "gone"}
        SSE-->>ES: event: gone<br/>data: {"reason":"too-old"}
        ES->>App: onmessage gone
        App->>App: close EventSource
        App->>Check: POST /skills/check-updates<br/>{skills: [installed]}
        Check-->>App: full state snapshot
        App->>App: reconcile + reopen EventSource
    end
```

## Race: Webhook + Cron for Same Skill (idempotency in action)

Demonstrates how `scan-lock:<skillId>` KV (consumer layer) and the
DO's `eventId` idempotency (publish layer) together ensure exactly
one broadcast per upstream change, even when two producers race.

```mermaid
sequenceDiagram
    autonumber
    participant GH as GitHub push
    participant WH as Webhook endpoint
    participant Cron as Cron trigger
    participant QH as scan-high queue
    participant QN as scan-normal queue
    participant QC as Queue consumer
    participant KV as scan-lock KV
    participant DB as Neon DB
    participant Hub as UpdateHub DO

    Note over GH: Upstream pushes SHA=abc to repo R
    GH->>WH: push event (HMAC)
    WH->>QH: enqueue {skillId, source: webhook, expectedSha: abc}
    Note over Cron: Cron tick happens within the same 10s window
    Cron->>QN: enqueue {skillId, source: cron}

    par Webhook consumer path (wins)
        QH->>QC: batch (priority high)
        QC->>KV: read scan-lock:{skillId}
        KV-->>QC: absent
        QC->>KV: put scan-lock {sha: oldSha} TTL 30s
        QC->>DB: BEGIN txn
        QC->>DB: INSERT SkillVersion (sha=abc)
        QC->>DB: INSERT UpdateEvent (id=evt_01HXB, ...)
        QC->>DB: COMMIT
        QC->>Hub: POST /internal/skills/publish {eventId: evt_01HXB, ...}
        Hub->>Hub: replayLog.has(evt_01HXB)? no
        Hub->>Hub: store + fanout to matching WS
        Hub-->>QC: 200 {deduped: false, delivered: N}
    and Cron consumer path (loses, silently)
        QN->>QC: batch (priority normal)
        QC->>KV: read scan-lock:{skillId}
        KV-->>QC: present
        Note over QC: lock fresh — skip GitHub call, no DB write, no publish
        QC->>QC: ACK message
    end

    Note over Hub: Exactly one SkillVersion, one UpdateEvent, one broadcast.
    Note over Hub: Had scan-lock missed, DO idempotency on evt_01HXB<br/>would dedup a second publish attempt anyway.
```

## Skill Discovery & Registration Flow (Option D + light C)

How a skill whose `sourceRepoUrl` is NULL in the DB gets promoted into
the tracked catalog without manual seeding. Discovery rides on
`/check-updates` traffic the Studio already sends.

```mermaid
sequenceDiagram
    autonumber
    participant App as Studio tab
    participant Check as /skills/check-updates
    participant DB as Neon DB
    participant Q as CF Queue<br/>discovery-resolve
    participant R as Resolver
    participant GH as GitHub
    participant Sc as Scanner

    App->>Check: POST {skills: [installed list]}
    Check->>DB: findMany skills + sourceRepoUrl
    loop for each skill with null sourceRepoUrl
        Check->>DB: check resolutionState
        alt never tried OR backoff elapsed
            Check->>Q: send {skillId, hint: Skill.repoUrl}
            Check->>DB: set resolutionState = pending
        else recently failed
            Note right of Check: skip — exponential backoff
        end
    end
    Check-->>App: {results: [..., trackedForUpdates: false, resolutionState: "pending"]}
    App->>App: render dim dot on untracked skills

    rect rgba(230,240,255,0.5)
        Note over Q,R: async — batch 10 / 3s window
        Q->>R: batch
        loop each message
            R->>GH: GET raw SKILL.md
            GH-->>R: content + frontmatter
            R->>R: parse frontmatter.repository<br/>OR plugin manifest repo<br/>OR homepage metadata
            alt URL inferred with high confidence
                R->>R: verify exists + has SKILL.md at path
                R->>DB: UPDATE Skill SET sourceRepoUrl,<br/>sourceBranch, resolutionState=resolved
                Note right of R: next cron picks it up
            else ambiguous or missing
                R->>DB: resolutionState=unresolvable<br/>resolutionAttempts++
                Note right of R: surfaced in UI — user can opt-in manually
            end
        end
    end

    Note over App: next check-updates call
    App->>Check: POST {skills: [...]}
    Check->>DB: fetch w/ sourceRepoUrl now set
    Check-->>App: trackedForUpdates: true
    App->>App: dim dot → tracked (no visual state until an update)

    rect rgba(255,240,230,0.5)
        Note over App: explicit opt-in path (light C)
        App->>App: user clicks "Register for tracking" on unresolvable skill
        App->>Check: POST /skills/:id/register-tracking<br/>{repoUrl, branch}
        Check->>Check: rate-limit per session (10/hr)
        Check->>GH: verify repo exists + SKILL.md reachable
        Check->>DB: UPDATE Skill SET sourceRepoUrl,<br/>resolutionState=user-registered
    end
```

**Why Option D + light C**:
- Zero friction for ~80% of skills (metadata already carries the repo).
- Privacy-neutral: `/check-updates` already carries the installed list;
  we're not adding new telemetry, just acting on what we have.
- Abuse-resistant: the resolver only trusts URLs it can verify from
  skill metadata already in our DB (signed submission path). The
  explicit-opt-in path (light C) is rate-limited per session.
- Reuses the existing CF Queues infrastructure (new
  `discovery-resolve` queue alongside `submission-processing` and
  `eval-processing`). Separate queue keeps latency SLOs isolated.
- Scales: at 1000 users × 50 unique skills, ~50k discovery jobs
  processed over days via queue batching — no burst load on the
  scanner cron.

## Backpressure & Scaling

- **Scan queue depth** — AE metric `queue.scan.depth` per queue. If
  `scan-high` depth >50 for >2 min, something is wrong at the webhook
  path (normal is 0–2). If `scan-normal` depth >500 sustained, bump
  `max_concurrency` from 2 to 4, then 6.
- **Scan latency P99** — AE metric `queue.scan.latency.ms` dimensioned
  by `source`. Webhook P99 target <2 s; user-trigger P99 <5 s; cron
  P99 <30 s. Breach triggers investigation, not auto-scaling.
- **Rate-limit shedding** — `queue.scan.shed` >0 per hour is only
  expected under partial GitHub outage or abuse; steady state is 0.
  Sustained shedding → bump cron cadence down before discovery
  starves.
- **Cron cadence** — v1 runs `*/10` (600 GH req/hr budget). At 200
  tracked skills, bump to `*/5` (1200 req/hr, still 24% of 5k PAT).
  Pure `wrangler.jsonc` change, no code.
- **DO sharding** — single `UpdateHub-0` in v1. When tracked skills
  cross ~500 sustained OR concurrent SSE connections cross ~3000,
  flip `SHARD_COUNT` in `wrangler.jsonc`. The pre-wired
  `shardForSkillId()` helper routes to `UpdateHub-1`, `UpdateHub-2`,
  etc. Stream endpoint groups filter by shard, opens one internal WS
  per shard, multiplexes onto one client SSE. No client protocol
  change.
- **Discovery queue depth** — watch `queue:discovery-resolve:depth`
  metric. If sustained backlog >1000, scale `max_concurrency` from 5
  to 10 or add a second consumer. Resolver is idempotent (SHA-keyed)
  so retries are safe.
- **GitHub rate limit** — scanner uses `If-None-Match` ETag caching;
  steady-state 304 responses don't count against quota. The consumer
  emits `scanner.errors.total` grouped by httpStatus; if 429s appear,
  we back off the batch by halving `max_batch_size` until recovery.
- **SSE connection pressure** — each Worker isolate can hold
  thousands of long-lived HTTP connections; the DO is the chokepoint
  first. Sharding hits before connection count ever does.
- **Outbox lag** — AE metric `outbox.lag.ms` P99. Healthy <10s;
  >30s sustained triggers investigation (reconciler starved, DB
  contention, or DO rejecting publishes). `outbox.attempts-exceeded`
  >0 is critical — a specific event is stuck.
- **Replay log size** — DO `do.replay.size` should be small (single
  digits at v1 velocity). >1000 entries means either event-storm or a
  stuck sweep; investigate before LRU eviction kicks in.

## File paths

| Purpose | Path |
|---|---|
| Scanner core (per-skill) | `repositories/anton-abyzov/vskill-platform/src/lib/skill-update/scanner.ts` |
| Unified queue consumer | `repositories/anton-abyzov/vskill-platform/src/lib/skill-update/queue-consumer.ts` |
| Scan dedup KV lock | `repositories/anton-abyzov/vskill-platform/src/lib/skill-update/scan-lock.ts` |
| Enqueue producers (webhook/cron/user/discovery) | `repositories/anton-abyzov/vskill-platform/src/lib/skill-update/enqueue.ts` |
| GitHub API client w/ ETag + RL capture | `repositories/anton-abyzov/vskill-platform/src/lib/skill-update/github-api.ts` |
| UpdateHub Durable Object (w/ replay log + idempotency) | `repositories/anton-abyzov/vskill-platform/src/lib/skill-update/update-hub.ts` |
| Publish → DO helper (eventId-aware) | `repositories/anton-abyzov/vskill-platform/src/lib/skill-update/publish.ts` |
| Outbox reconciler (30s cron) | `repositories/anton-abyzov/vskill-platform/src/lib/skill-update/outbox-reconciler.ts` |
| Outbox write helper (txn wrapper) | `repositories/anton-abyzov/vskill-platform/src/lib/skill-update/outbox-writer.ts` |
| Submission consumer (retrofit for outbox) | `repositories/anton-abyzov/vskill-platform/src/lib/queue/process-submission.ts` |
| Admin rescan (retrofit for outbox) | `repositories/anton-abyzov/vskill-platform/src/app/api/v1/admin/rescan-published/route.ts` |
| Event types | `repositories/anton-abyzov/vskill-platform/src/lib/skill-update/types.ts` |
| Discovery resolver (consumer) | `repositories/anton-abyzov/vskill-platform/src/lib/skill-update/discovery/resolver.ts` |
| Discovery enqueue (from check-updates) | `repositories/anton-abyzov/vskill-platform/src/lib/skill-update/discovery/enqueue.ts` |
| Public SSE endpoint | `repositories/anton-abyzov/vskill-platform/src/app/api/v1/skills/stream/route.ts` |
| Subscription endpoint | `repositories/anton-abyzov/vskill-platform/src/app/api/v1/skills/stream/subscribe/route.ts` |
| Webhook receiver (enqueues scan-high) | `repositories/anton-abyzov/vskill-platform/src/app/api/v1/webhooks/github/route.ts` |
| User "check now" endpoint | `repositories/anton-abyzov/vskill-platform/src/app/api/v1/skills/[id]/rescan/route.ts` |
| Internal publish endpoint | `repositories/anton-abyzov/vskill-platform/src/app/api/v1/internal/skills/publish/route.ts` |
| Existing check-updates (modified) | `repositories/anton-abyzov/vskill-platform/src/app/api/v1/skills/check-updates/route.ts` |
| Manual registration (light C) | `repositories/anton-abyzov/vskill-platform/src/app/api/v1/skills/[id]/register-tracking/route.ts` |
| Cron dispatcher | `repositories/anton-abyzov/vskill-platform/scripts/build-worker-entry.ts` |
| Worker bindings | `repositories/anton-abyzov/vskill-platform/wrangler.jsonc` |
| Schema | `repositories/anton-abyzov/vskill-platform/prisma/schema.prisma` |
| Seed (bootstrap) | `repositories/anton-abyzov/vskill-platform/scripts/seed-tracked-skills.ts` |
| Existing internal-auth helper | `repositories/anton-abyzov/vskill-platform/src/lib/internal-auth.ts` |
| Existing webhook-auth helper | `repositories/anton-abyzov/vskill-platform/src/lib/webhook-auth.ts` |
| Studio hook | `repositories/anton-abyzov/vskill/src/studio/lib/use-skill-updates.ts` |
| Studio UpdateBell | `repositories/anton-abyzov/vskill/src/studio/components/UpdateBell.tsx` |
| Studio update action | `repositories/anton-abyzov/vskill/src/studio/components/UpdateAction.tsx` |
| Studio row/section chip | `repositories/anton-abyzov/vskill/src/studio/components/UpdateChip.tsx` |
| Related ADRs | `.specweave/docs/internal/architecture/adr/0708-01-*.md`, `0708-02-*.md`, `0688-01-*.md` (precedent), `0688-02-*.md` (provenance) |
