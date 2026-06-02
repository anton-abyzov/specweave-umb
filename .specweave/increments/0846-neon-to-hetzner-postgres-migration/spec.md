---
project: vskill-platform
status: planned
structure: user-stories
test_mode: TDD
coverage_target: 80
---

# 0846 — Neon → Hetzner Postgres migration

## Context

verified-skill.com currently uses **Neon serverless Postgres** as its primary database (`ep-polished-haze-aea6snnj-pooler.c-2.us-east-2.aws.neon.tech`, schema `public`, 49 migrations applied as of 2026-05-11). Neon's pricing model bills per compute-hour + storage + branches. As the skill catalog has grown past 120K rows with 24 active Cloudflare Worker bindings and 6 cron schedules pinging Postgres on tight cadences, monthly Neon cost is climbing.

Anton already operates **3 Hetzner VMs** for crawl-workers (`5.161.69.232`, `91.107.239.24`, `5.161.56.136`) per `reference_hetzner_vms.md`. Those VMs do heavy network IO and would compete with Postgres for IO bandwidth — **do NOT colocate Postgres on a crawl-worker VM**. Spin up dedicated VMs.

**Database size estimate** (from production stats `totalSkills=118073`, `submissionTotal=116597`): catalog ~250MB, submissions ~180MB, audit events ~100-500MB depending on retention churn, billing tables negligible (<10MB). **Total ~1-2 GB today, projected ~5 GB at 250K skills.** This is far smaller than my initial sizing assumed — **CPX21 (€6/mo, 4 vCPU shared, 4GB RAM, 80GB NVMe) is sufficient for primary + standby**. Drop to CX22 (€4/mo) only if standby observation shows excess headroom over 3 months.

Adding two dedicated VMs (primary + standby) is **~€12-15/mo all-in** including Hetzner Storage Box (€3/mo for 1TB of backups) — vs Neon's per-compute-hour pricing that grows with traffic. Roughly 4-7x cheaper than the original CCX23 sizing I proposed.

**Trade-off**: ops burden. Neon handles backups, point-in-time recovery, autoscaling, security patches, OS upgrades. On Hetzner we own all of that. Acceptable trade if monthly Neon bill exceeds €100 or if Anton has bandwidth for a backup-restore drill once per quarter.

## Goals

- Move primary Postgres workload off Neon onto a Hetzner VM running PostgreSQL 16
- Set up streaming replication to a second Hetzner VM as hot standby
- Use pgBackRest for compressed encrypted backups to Hetzner Storage Box (€3/mo for 1TB) with PITR support
- Zero data loss during cutover; <5 minutes downtime
- Application config change limited to swapping `DATABASE_URL` in Cloudflare Worker secrets
- Cost <€20/mo total (CPX21 primary + CPX21 standby + €3 storage box; aim for €12-15/mo)

## Non-goals (Out of Scope)

- **Multi-region failover** — single-region (Hetzner Falkenstein) is sufficient for v1
- **Application-level pooling rework** — Prisma's built-in pool is fine; if connection limits hit, add PgBouncer in a follow-up
- **Migrating any other database** (Cloudflare KV, R2, Durable Objects, Analytics Engine) — those stay where they are
- **Re-architecting the schema** — straight lift-and-shift

## Personas

- **Anton (ops)** — needs to be able to restore from backup, monitor disk usage, apply Postgres upgrades; owns the runbook
- **Worker (runtime)** — needs to reach the new DB with same latency profile as Neon (Postgres on Hetzner DE → CF Worker in Europe region should be ~10-20ms, comparable to or faster than Neon US-East from Europe)

## User Stories

### US-001: Hetzner Postgres primary provisioning

**Project**: vskill-platform

**As** Anton, ops
**I want** a Hetzner VM running Postgres 16 with secure defaults
**So that** I can host the verified-skill.com primary database

**Acceptance Criteria**:
- [ ] **AC-US1-01**: New **DEDICATED** Hetzner VM provisioned (CPX21 — 4 vCPU shared, 4GB RAM, 80GB NVMe, €6/mo) in Falkenstein. Must NOT be colocated on existing crawl-worker VMs (network IO contention). Resize-up path documented if catalog growth justifies it.
- [ ] **AC-US1-02**: PostgreSQL 16 installed via official apt repo, listening on private IP only (no public exposure)
- [ ] **AC-US1-03**: postgresql.conf tuned for ~16 connections from CF Workers + ~10 connections from cron jobs (max_connections=100, work_mem=4MB, effective_cache_size=6GB)
- [ ] **AC-US1-04**: pg_hba.conf allows SCRAM-SHA-256 only; password complexity enforced
- [ ] **AC-US1-05**: TLS enabled (ssl=on, self-signed cert acceptable for v1; LetsEncrypt cert for v2)
- [ ] **AC-US1-06**: UFW firewall: only Hetzner private network can reach 5432; SSH from Anton's IPs only

### US-002: Hot standby replication

**Project**: vskill-platform

**As** Anton, ops
**I want** streaming replication to a second VM
**So that** I can fail over within minutes if the primary VM is destroyed

**Acceptance Criteria**:
- [ ] **AC-US2-01**: Second Hetzner VM provisioned (same spec) as warm standby
- [ ] **AC-US2-02**: Primary configured with wal_level=replica, max_wal_senders=10, archive_mode=on, archive_command shipping to Hetzner Storage Box
- [ ] **AC-US2-03**: Standby running streaming replication via recovery.conf (or primary_conninfo for PG12+)
- [ ] **AC-US2-04**: Replication lag <1s under normal load (verified by pg_stat_replication)
- [ ] **AC-US2-05**: Documented failover runbook at docs/runbooks/postgres-failover.md

### US-003: pgBackRest backups + PITR

**Project**: vskill-platform

**As** Anton, ops
**I want** automated daily backups with point-in-time recovery
**So that** I can recover from data corruption or operator error

**Acceptance Criteria**:
- [ ] **AC-US3-01**: pgBackRest installed on primary; full backup runs nightly 02:00 UTC; incremental backups every 6h
- [ ] **AC-US3-02**: Backups encrypted with AES-256 (key in Cloudflare Worker secret PGBACKREST_CIPHER_PASS)
- [ ] **AC-US3-03**: Backups shipped to Hetzner Storage Box (€3/mo for 1TB)
- [ ] **AC-US3-04**: 7-day daily retention + 4-week weekly retention + 6-month monthly retention
- [ ] **AC-US3-05**: Quarterly restore drill — runbook tested end-to-end at least once before cutover
- [ ] **AC-US3-06**: Backup status monitored via Healthchecks.io ping (existing infra)

### US-004: Migration cutover

**Project**: vskill-platform

**As** Anton, ops
**I want** a low-downtime cutover plan from Neon to Hetzner
**So that** verified-skill.com users see <5 minutes of degradation

**Acceptance Criteria**:
- [ ] **AC-US4-01**: pg_dump --section=pre-data --section=data --section=post-data from Neon, restored to Hetzner primary during off-peak window (Saturday 04:00 UTC per project_cloudflare_cost_crisis.md cost-optimization patterns)
- [ ] **AC-US4-02**: Logical replication slot on Neon → Hetzner for catch-up of writes during dump window (Neon supports logical replication on Pro tier)
- [ ] **AC-US4-03**: DATABASE_URL wrangler secret updated to Hetzner connection string; wrangler deploy to flip the cutover
- [ ] **AC-US4-04**: Smoke-test 10 endpoints (login, /skills, /pricing, /account, /billing/subscription, /billing/seats/usage, webhook, cron tick, audit log read, skill SSE) within 5 minutes of cutover
- [ ] **AC-US4-05**: Neon kept warm for 7 days post-cutover as rollback safety net; deleted on day 8

### US-005: Cost monitoring

**Project**: vskill-platform

**As** Anton, ops
**I want** monthly cost dashboard for the Hetzner setup
**So that** I can verify the savings vs Neon's current bill

**Acceptance Criteria**:
- [ ] **AC-US5-01**: New entry in wiki/hetzner-postgres-cost.md tracking primary VM + standby VM + storage box monthly cost
- [ ] **AC-US5-02**: Update project_cloudflare_cost_crisis.md memory with the new monthly total
- [ ] **AC-US5-03**: First-month cost report compared to Neon's last 3-month average

## Out-of-scope items (deferred to future increments)

- PgBouncer connection pooling (if needed, add as 0847)
- Multi-region (Falkenstein + Helsinki) — add as 0848 if traffic requires
- Postgres major-version upgrade automation
- Read replicas for analytics queries
