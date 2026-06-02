---
increment: 0846-neon-to-hetzner-postgres-migration
title: 'Tasks: Neon → Hetzner Postgres migration'
type: tasks
---

# Tasks

### T-001: Provision Hetzner primary VM via Terraform
**User Story**: US-001 | **AC**: AC-US1-01 | **Status**: [ ] pending
**Test Plan**: Given a clean Hetzner project, When `terraform apply` runs, Then a CCX23 VM exists in Falkenstein with NVMe SSD attached and private network configured.

### T-002: Install + tune PostgreSQL 16 via Ansible
**User Story**: US-001 | **AC**: AC-US1-02, AC-US1-03 | **Status**: [ ] pending
**Test Plan**: Given the primary VM, When the Ansible playbook runs, Then `psql -c "SHOW server_version"` returns 16.x AND `SHOW max_connections` returns 100 AND `SHOW work_mem` returns 4MB.

### T-003: SCRAM auth + TLS + firewall lockdown
**User Story**: US-001 | **AC**: AC-US1-04, AC-US1-05, AC-US1-06 | **Status**: [ ] pending
**Test Plan**: Given the primary VM, When an external IP tries to connect on 5432, Then UFW drops the connection. When a Hetzner private-net peer connects with valid SCRAM creds + TLS, Then the connection succeeds. When an invalid password is used, Then the connection fails after 1 retry.

### T-004: Provision standby VM + streaming replication
**User Story**: US-002 | **AC**: AC-US2-01, AC-US2-02, AC-US2-03 | **Status**: [ ] pending
**Test Plan**: Given the standby VM, When `INSERT INTO test (val) VALUES ('marker-1')` runs on primary, Then within 5s the same row appears in `SELECT * FROM test ON standby`.

### T-005: Verify replication lag <1s
**User Story**: US-002 | **AC**: AC-US2-04 | **Status**: [ ] pending
**Test Plan**: Given 30 sustained writes/sec on primary, When `pg_stat_replication.write_lag` is sampled every 10s for 5 min, Then no sample exceeds 1 second.

### T-006: Write failover runbook
**User Story**: US-002 | **AC**: AC-US2-05 | **Status**: [ ] pending
**Test Plan**: Given a fresh ops engineer, When they follow `docs/runbooks/postgres-failover.md` step-by-step against staging, Then they can complete failover within 10 minutes without external help.

### T-007: Install + configure pgBackRest
**User Story**: US-003 | **AC**: AC-US3-01 | **Status**: [ ] pending
**Test Plan**: Given pgBackRest installed, When `pgbackrest --stanza=vskill backup --type=full` runs at 02:00 UTC via cron, Then the backup completes within 30 min AND `pgbackrest info` shows the new backup AND Healthchecks.io receives a success ping.

### T-008: AES-256 encryption + Hetzner Storage Box upload
**User Story**: US-003 | **AC**: AC-US3-02, AC-US3-03 | **Status**: [ ] pending
**Test Plan**: Given a backup completes, When the backup file is inspected on the Storage Box, Then it is encrypted (entropy check) AND the cipher pass matches the `PGBACKREST_CIPHER_PASS` env var.

### T-009: Retention policy + restore drill
**User Story**: US-003 | **AC**: AC-US3-04, AC-US3-05 | **Status**: [ ] pending
**Test Plan**: Given backups older than 7 days, When the retention cron runs, Then daily backups older than 7d are removed. Given a quarterly restore drill, When the procedure is followed end-to-end, Then a usable Postgres instance is restored within 2 hours.

### T-010: Healthchecks.io monitoring
**User Story**: US-003 | **AC**: AC-US3-06 | **Status**: [ ] pending
**Test Plan**: Given a backup succeeds, When the post-backup hook fires, Then Healthchecks.io receives a /ping. Given a backup fails, When the failure hook fires, Then Healthchecks.io receives a /fail.

### T-011: Logical replication setup Neon → Hetzner
**User Story**: US-004 | **AC**: AC-US4-01, AC-US4-02 | **Status**: [ ] pending
**Test Plan**: Given Neon is the source and Hetzner is the subscriber, When a row is inserted on Neon, Then within 30s the row appears on Hetzner. Given pre-data + data + post-data dump completed, Then row counts match within 0.01% on both sides.

### T-012: Cutover script + DATABASE_URL swap
**User Story**: US-004 | **AC**: AC-US4-03, AC-US4-04 | **Status**: [ ] pending
**Test Plan**: Given replication is caught up (<1s lag), When the cutover script runs (stop writes, swap DATABASE_URL, redeploy Worker, resume writes), Then within 5 minutes all 10 smoke-test endpoints respond 2xx/4xx (expected codes).

### T-013: Rollback safety net + Neon warm period
**User Story**: US-004 | **AC**: AC-US4-05 | **Status**: [ ] pending
**Test Plan**: Given 7 days post-cutover have elapsed, When the rollback safety period closes, Then Neon project is deleted via API AND the deletion is logged in audit + Obsidian.

### T-014: Cost tracking + monthly report
**User Story**: US-005 | **AC**: AC-US5-01, AC-US5-02, AC-US5-03 | **Status**: [ ] pending
**Test Plan**: Given one month post-cutover, When the cost report runs, Then `wiki/hetzner-postgres-cost.md` shows VM + standby + storage box line items AND `project_cloudflare_cost_crisis.md` is updated AND savings vs Neon's 3-month average are quantified.

### T-015: Close increment + post-mortem
**User Story**: All | **AC**: implicit | **Status**: [ ] pending
**Test Plan**: Given all 14 tasks above are [x], When the closure pipeline runs (code-review → simplify → grill → judge-llm → PM gates), Then specweave complete succeeds and metadata.json flips to status=completed.
