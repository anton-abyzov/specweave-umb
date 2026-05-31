# 0861 — Plan

> Architecture decisions distilled from [reports/audit-and-hardening-report.md](reports/audit-and-hardening-report.md). Read the report for evidence (file:line) and the full adversarial-review table.

## What already works — DO NOT rebuild

GitHub 1000-cap sharding; durable CF Queue + persisted DLQ; idempotency at every hop; 10-min scheduled recovery; off-box dead-VM (pure-liveness) detection (0748); multi-signal alert evaluator with dedup hygiene (0807/0808); DB unique constraints; within-skill content-hash (0794); 2.8M historical dup collapse + `/admin/dedup-skills` (0673); three-layer auto-restart; monorepo multi-`SKILL.md` expansion; PAT rotation + adaptive backoff. **Reuse these; this increment fills the gaps between them.**

## Dedup architecture — three orthogonal axes + a precedence DAG

```
Axis 1  SOURCE   = GitHub numeric repo_id           (the ONLY auto-merge key for same-repo)
Axis 2  ARTIFACT = (repo_id, normalized dir path)   (case-PRESERVING; one row per SKILL.md dir)
Axis 3  CONTENT  = SHA-256(canonicalized SKILL.md)  (reuse 0794; raises CANDIDATES, never auto-merges alone)

PRECEDENCE DAG (resolver contract):
 1. repo_id match        -> AUTO-MERGE  (any URL/name/case variant of the same repo)
 2. fork lineage         -> AUTO-ALIAS  only if fork==true AND source.id catalogued
 3. mirror/import        -> CONTENT-HASH AUTO-RESOLVE only if unrelated repos AND byte-identical
                            AND vendored-path guard passes. Canonical = oldest createdAt. Loser = alias.
 4. content-hash, other  -> CANDIDATE FLAG ONLY. Never auto-merge.
```

**Tightened merge predicate (closes the false-merge hole):** auto-merge requires `fork-lineage OR same repo_id`. `owner + frontmatter-name + content-hash` together are **not** sufficient — two distinct `repo_id`s with identical name+boilerplate stay two skills.

**Layered dedup keys:** crawl-time bloom/seen-set (first line, false-positives harmless) → migrated DB natural key `(source_type, source_id, artifact_path)` with `INSERT … ON CONFLICT DO UPDATE` (authoritative last line). Every GitHub-resolvable listing (incl. skills.sh / awesome-lists) resolves to `(github, repo_id, path)` **at ingest**, recording the registry as an alias source — so cross-source arrivals converge before the LLM scan, not after.

**Key risks to get right (from stress-test):** (a) the two-phase backfill must merge pre-existing case/`.git`/slash dups BEFORE adding the unique constraint; (b) `full_name→repo_id` cache must be durable + 403 must defer (never fall back to the unresolved name — that mints a dup).

## Notification architecture — three layers, each covering the others' blind spot

| Layer | Catches | Runs where | Channel |
|---|---|---|---|
| **L1 in-process error signal** | exceptions, per-source consecutive failures | enriched 60s heartbeat → off-box detector | Telegram + SendGrid |
| **L2 external dead-man** (Healthchecks.io) | dead VM(s), dead CF crons, dead platform | hosted SaaS (separate failure domain) | Healthchecks → Telegram + email |
| **L3 anomaly / throughput floor** | alive-but-zero-work (the "publishing STOPPED" case) | off-box CF `*/10` evaluator (Prisma) | Telegram + SendGrid |

**Load-bearing fixes (the 7 alerting holes):** heartbeat carries **monotonic cumulative** counters + distinct `lastSuccessfulPublishAt` (counter-flat-while-`lastRunAt`-advances = silent zero, pages); L2 ping fires **only after a confirmed publish + DB write**, not on the schedule tick; **one Healthchecks check per VM** (+ aggregate); **`detector-blind`** alert when the detector's own DB query throws; **dual egress** + a second SaaS dead-man so providers aren't a shared SPOF; compare **CF-side received-at** (clock-skew-proof); **escalating** severity with bounded ack-snooze.

**Survives a dead VM?** Yes — L2 lives on Healthchecks.io (separate domain), per-VM, pinged only on real work; cron-job.org backstops Healthchecks itself; L3 detection runs off-box and `detector-blind` covers DB-down. Residual: simultaneous failure of Telegram + SendGrid + Healthchecks + cron-job.org → mitigated by persist-on-total-failure.

## Discovery — only the LIVE fixes land here
T-011 (rolling date bound, replaces hardcoded `2026-03-31`) and T-012 (remove dead Neon driver) are present-tense outages, pulled in. All other discovery-breadth work → 0862.

## Sequencing
**Security (T-001) first and blocking** → dedup-key migration (T-002/T-003) → dedup resolver + axes (T-004..T-009) → live discovery fixes (T-011/T-012) → notification (T-010/T-013/T-014). Highest implementation risk: the two-phase backfill (T-003) and the per-VM heartbeat gating (T-014).

## Test strategy
Dedup: 20 Vitest cases in [reports/dedup-test-plan.md](reports/dedup-test-plan.md), one per hole. Notification: integration tests for counter-flat detection, per-VM Healthchecks isolation, confirmed-publish gating, `detector-blind`, dual-provider failover, escalation, received-at staleness. Security: a must-pass gate asserting tokens return 401 and `git ls-files` shows only `*.example`. Run `npx vitest run` + `npx playwright test` after each task.
