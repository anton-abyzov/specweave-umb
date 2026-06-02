---
project: vskill-platform
status: planned
---

# 0846 — Neon → Hetzner Postgres migration plan

## ADRs

### ADR-001: Hetzner CCX vs CPX VM family
**Decision**: CCX23 (dedicated vCPU, 8GB RAM, 240GB NVMe, ~€20/mo).
**Rationale**: Postgres is CPU+IO bound; shared-vCPU CPX series has noisy-neighbor risk under burst load. CCX dedicated vCPU gives predictable latency. NVMe SSD is non-negotiable for any modern Postgres workload.

### ADR-002: Streaming replication vs logical replication for standby
**Decision**: Streaming (binary) replication for the hot standby; logical replication only used once during Neon→Hetzner cutover.
**Rationale**: Streaming replication is rock-solid and includes all data including DDL. Logical replication is slower, has DDL caveats, and is unnecessary for a hot standby. Use logical only for the one-shot cutover from Neon (which doesn't support binary replication out — it's managed).

### ADR-003: pgBackRest vs WAL-G vs barman
**Decision**: pgBackRest.
**Rationale**: Best-in-class compression (zstd), encryption at rest, parallel restore, PITR support, well-documented, lower CPU footprint than WAL-G. barman is older and slower. WAL-G is Yandex's tool, less ecosystem support.

## Files to create/modify

### Infrastructure
- `infrastructure/hetzner/postgres-primary.tf` (new) — Terraform module for primary VM
- `infrastructure/hetzner/postgres-standby.tf` (new) — standby VM
- `infrastructure/hetzner/pgbackrest.conf` (new) — backup config
- `infrastructure/hetzner/postgresql.conf` (new) — tuned config
- `infrastructure/hetzner/pg_hba.conf` (new) — auth config

### Application (single config change)
- Cloudflare Worker secret `DATABASE_URL` swapped via `wrangler secret put DATABASE_URL` (no code change)
- `prisma/schema.prisma` — no change; Prisma is database-agnostic via the Postgres driver
- `vskill-platform/.env.example` — update comment to reference Hetzner host

### Documentation
- `docs/runbooks/postgres-failover.md` (new) — step-by-step failover runbook
- `docs/runbooks/postgres-restore-drill.md` (new) — quarterly restore drill procedure
- `docs/runbooks/postgres-major-upgrade.md` (new) — for PG 16 → 17 in the future
- `wiki/hetzner-postgres-cost.md` (new — in Obsidian) — cost tracking

## Tooling
- **Terraform** for VM provisioning (Hetzner provider)
- **Ansible** for Postgres installation + config (idempotent re-runs)
- **pgBackRest** v2.x for backups
- **Healthchecks.io** existing infra for backup-status pings
- **Datadog or simple Loki + Grafana** for Postgres metrics (separate infra increment if needed)

## Test stack
- Restore drill: `pg_dump` from Neon → restore to staging Hetzner VM → run vitest integration tests against the staging URL
- Replication lag test: write a marker row to primary, query for it on standby within 5s
- Failover drill: stop primary process, promote standby, redirect `DATABASE_URL`, verify reads + writes within 60s

## Out-of-scope
- Multi-region replication
- Read replicas
- PgBouncer
- Postgres major-version upgrade automation

## Estimated effort
- Provisioning + config: ~2 days
- Replication + backup setup: ~1 day
- Cutover plan + dry-run: ~1 day
- Production cutover (Saturday 04:00 UTC window): ~2 hours
- Documentation + runbook validation: ~0.5 day
- **Total**: ~5 dev-days

## Risk
- Medium. The riskiest part is the one-shot cutover; mitigated by keeping Neon warm for 7 days post-cutover. Anton is comfortable with Postgres ops (he's run Postgres at EasyChamp scale before).

## When to start
Trigger conditions:
- Neon monthly cost > €100, OR
- Catalog growth > 250K rows (Neon's pricing degrades), OR
- Anton has a quiet sprint to give it focused attention

Otherwise this increment stays in `planned` indefinitely.
