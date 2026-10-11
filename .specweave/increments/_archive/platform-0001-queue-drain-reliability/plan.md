---
increment: 0001-queue-drain-reliability
title: "Submission Queue Drain Reliability — Plan"
status: active
created: 2026-05-14
---

# Plan

## Investigation Order

1. Read queue/admin/internal API and worker code to map the production drain path.
2. Inspect local env files for credential locations without printing secrets.
3. Query production API and database for queue/user freshness.
4. SSH into the worker hosts listed in deployment/env files and inspect service/container logs.
5. Apply the smallest production remediation that restores draining.
6. If current infrastructure is structurally unreliable, migrate the database or worker host and cut over.
7. Add durable prevention in code, deployment scripts, or runbooks.
8. Verify with unit tests, build, production health checks, and live queue movement.

## Architecture Hypotheses

- The Next.js/OpenNext app runs on Cloudflare and uses Neon Postgres through Prisma.
- Scanner/crawl workers run on Hetzner or GCP VMs and call internal platform endpoints with `WORKER_SECRET`.
- The stuck queue can happen even when VMs are up if workers point at stale env, wrong callback URL, missing `WORKER_SECRET`, exhausted GitHub tokens, or crashed containers.
- A new Postgres server should only replace Neon if production DB reachability, cost, or lifecycle risk is the root cause; otherwise reusing the current managed database is safer.

## Risk Controls

- Do not print secrets.
- Prefer non-destructive database reads before writes.
- Do not reset/delete production submissions unless explicitly required to unblock queue semantics.
- Snapshot/export production data before any database migration.

