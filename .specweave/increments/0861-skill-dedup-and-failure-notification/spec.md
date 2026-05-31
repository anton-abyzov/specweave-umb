# 0861 — Skill Dedup Hardening + Failure Notification

> **Source:** Deep audit workflow `weqo4pza2` (`skill-scrape-audit-and-harden`, 12 agents, adversarially stress-tested — 17 holes found & closed). Full findings: [reports/audit-and-hardening-report.md](reports/audit-and-hardening-report.md). Dedup BDD plan: [reports/dedup-test-plan.md](reports/dedup-test-plan.md).
>
> **Owner decisions (2026-05-31):** alert channel = **email only** (SendGrid); leaked tokens = **do not revoke / do not rewrite history** (reviewed, accepted risk — private repo, tokens in active git-based VM config delivery).

## Context

`vskill-platform/crawl-worker` is a mature, mostly-correct Dockerized zero-dep Node crawler on 3 Hetzner VMs (+ 10 GCP VMs) that discovers Claude `SKILL.md` skills from 8 sources, dedupes, queues (CF Queue + DLQ), SAST-scans, scores, and publishes to verified-skill.com. **This increment hardens; it does not redesign.** It reuses the existing watchdog (0748), alert evaluator (0807/0808), CF crons, 0673 collapse pattern, and 0794 canonical hash.

Three problems are **live today**: a hardcoded `2026-03-31` shard bound (date shards blind two months), a dead Neon driver in `stats-compute.js` (telemetry silently broken since 2026-05-21), and two structural classes — dedup is not airtight, and "publishing stopped" is invisible.

## User Stories & Acceptance Criteria

### US-001 — Repo-identity dedup
Resolve GitHub identity to the stable numeric `repo_id` (follow 301s, durable `full_name→repo_id` cache, 403-defer-not-duplicate), normalize the submission key, and resolve every GitHub-pointing registry listing to `(github, repo_id, path)` at ingest — so renames/transfers/URL-variants/case-variants/registry-relays stop creating duplicate submissions and duplicate tier-2 scans.

- **AC-US1-01:** `github.com/Acme/Skills` and `github.com/acme/skills.git/` both resolve to one `repo_id`; exactly one Submission (no second tier-2 scan).
- **AC-US1-02:** A transferred repo, re-crawled, follows its 301 to `/repositories/{id}`, matches the existing `repo_id`, updates the `full_name` alias, no new row.
- **AC-US1-03:** Submission natural key = `(source_type, source_id, artifact_path)` with `ON CONFLICT DO UPDATE`; re-crawl is an idempotent no-op.
- **AC-US1-04:** A skills.sh/awesome-list listing for an already-catalogued repo resolves to `(github, repo_id, path)` at ingest, recorded as an alias source — no second Submission, no second tier-2 scan.
- **AC-US1-05:** On a 403 mid-resolution for an unseen `full_name`, the item is deferred to the retry queue and NO Submission is created under the unresolved name; the cache is durable (KV/DB) and survives a watchdog bounce.
- **AC-US1-06:** With existing `Owner/Repo` + `owner/repo` duplicate rows, the two-phase backfill (normalize→merge→constraint) merges them to one, applies the unique constraint cleanly, drops no row.
- **AC-US1-07:** Two VMs racing the same key → exactly one row AND `claim-submission` grants exactly one claim (the new key and the compare-and-swap claim key agree on submission identity).

### US-002 — Precedence-DAG dedup correctness
A strict precedence DAG (`repo_id` > fork-lineage > content-hash) so forks of a catalogued repo alias (not republish), mirror/import copies auto-resolve to the oldest-created canonical, vendored copies never displace the original, and byte-identical SKILL.md across unrelated repos only FLAGS candidates.

- **AC-US2-01:** A fork whose `source.id` is catalogued (`fork=true`) is attached to the existing `skill_identity_id` as an alias; no new Skill.
- **AC-US2-02:** Two unrelated repos with identical canonicalized SKILL.md bytes are flagged as CANDIDATES (not auto-merged); near-empty boilerplate collisions stay distinct.
- **AC-US2-03:** `/admin/dedup-skills`, re-keyed on `(repo_id, content_hash)` and run on a reconciler cron governed by the DAG, collapses constraint-evading duplicates without displacing an original author.
- **AC-US2-04:** One author's two different repos (different `repo_id`s) with identical frontmatter name + boilerplate stay two distinct skills — the merge predicate (`fork-lineage OR same repo_id`) rejects owner+name+content as sufficient.
- **AC-US2-05:** A mirror/import repo (`fork=false`, `parent=null`, distinct `repo_id`, byte-identical) auto-resolves to the existing canonical (oldest `createdAt` wins) as an alias — no second canonical, no second tier-2 scan.
- **AC-US2-06:** A 1-star original vs a 5000-star `…/vendor/…` copy with identical bytes → original stays canonical (earliest-published + vendored-path guard override trustScore).

### US-003 — Throughput-floor / silent-stall alerting (email)
A throughput-floor and per-source "went dark" alert driven by monotonic cumulative counters (counter-flat-while-`lastRunAt`-advances, compared on CF-side received-at), plus a `detector-blind` alert when the evaluator's own DB query throws — so a "publishing produced ~0 while the VM is up" condition reaches me by **email**, even during a DB outage.

- **AC-US3-01:** Below the configured 24h `Skill`-created floor → a `discovery-floor` email alert with **escalating** severity (ack snoozes a bounded window, then re-pages).
- **AC-US3-02:** A source whose cumulative `submitted/publishedTotal` is flat across N heartbeats while `lastRunAt` advances → a `source-dark` alert naming that source.
- **AC-US3-03:** The heartbeat carries per-source monotonic cumulative `{discoveredTotal, submittedTotal, publishedTotal}` + distinct `lastSuccessfulPublishAt`, `lastRunAt`, `lastError`, `consecutiveErrors`.
- **AC-US3-04:** A fast/frozen VM clock cannot hide a dead source — staleness is computed on CF-side `heartbeat-received-at`, never the VM-reported `lastRunAt`.
- **AC-US3-05:** When Postgres/Hyperdrive is down and the detector's query throws, a `detector-blind` high-severity alert fires (excluded from the digest) — never a silent green.

### US-004 — External dead-man's-switch (email)
An external dead-man's-switch (Healthchecks.io) with one check per VM plus an aggregate, pinged only after a confirmed successful publish + DB write — so a single dead VM among three, or a simultaneous VM+Cloudflare outage, still reaches me by email.

- **AC-US4-01:** A VM pings `hc-ping.com/<vm-uuid>` only after a cycle that produced ≥1 published-or-confirmed-unchanged skill AND a confirmed DB write; a cycle that merely iterated (e.g. 200 with 0 parsed skills) does NOT ping (L3 discovery-floor is the safety net).
- **AC-US4-02:** On an in-process exception the VM POSTs `/fail` to its check, flipping it red immediately.
- **AC-US4-03:** Three VMs each have their own UUID; skipping VM2's ping turns VM2 red while VM1/VM3 stay green; a 4th aggregate check catches all-three-dead off-box.
- **AC-US4-04:** Healthchecks.io delivers email; a second independent dead-man (cron-job.org) backstops it; on total provider failure the alert is persisted to a queryable store.

### US-005 — Security finding (reviewed, accepted)
The audit found 5 live `ghp_` PATs (one "full admin") + `INTERNAL_API_KEY` + `SKILLSMP_API_KEY` across 13 git-tracked `crawl-worker/.env.{vm1-3,gcp-vm1-10}` files (no `.gitignore`).

- **AC-US5-01:** **Owner reviewed and elected NOT to revoke or rewrite history** — the per-VM env files are the git-based config-delivery mechanism for the VMs; the repo is private. **No code change.** Recorded here as an accepted risk so it is not re-flagged. (Reversible later via a GitHub App installation token if the deploy mechanism is changed first.)

### US-006 — Live outage fixes
- **AC-US6-01:** Past `2026-03-31`, `github-sharded.js` uses a dynamically computed `now()`-based rolling date window (no hardcoded bound); a `>1000` window bisects until `<1000`; April–May 2026 repos are covered by real date shards.
- **AC-US6-02:** `stats-compute.js` no longer imports/uses the `neon()` driver (points at Hyperdrive or the telemetry path is removed) and does not fail silently.

## Out of scope → 0862-crawler-discovery-completeness
GH-Archive/BigQuery firehose, github-events sampling fix, GitLab scheduler wiring, per-source incremental cursors, T1-only-fallback re-scan, new registry sources (anthropics/skills marketplace, skills.sh sitemap, awesome-lists).
