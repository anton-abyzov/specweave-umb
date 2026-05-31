# 0861 — Tasks

> 13 tasks. Live outages (T-011/T-012) and security note (T-001) first. Channel = **email only**. Tokens = **not revoked** (owner decision). Tests: `npx vitest run` + `npx playwright test`. Dedup BDD: [reports/dedup-test-plan.md](reports/dedup-test-plan.md). Work happens in `repositories/anton-abyzov/vskill-platform`.

### T-001: Security finding — record accepted risk (NO code change)
**AC**: AC-US5-01 | **Status**: [x] resolved (owner decision)
Owner reviewed the leaked-PAT finding (5 `ghp_` tokens + 2 API keys across 13 git-tracked `crawl-worker/.env.{vm1-3,gcp-vm1-10}` files) and **elected NOT to revoke or rewrite history** — the per-VM env files are the git-based config-delivery mechanism; repo is private. No action. Documented so it is not re-flagged. Do NOT add a `.gitignore` or `git rm --cached` these files (would break VM config delivery).

### T-011: Fix hardcoded date upper bound (LIVE outage)
**AC**: AC-US6-01 | **Status**: [x] completed (crawl-worker node:test 16/16)
`github-sharded.js:37` `2026-03-31` → dynamic `now()`-based rolling window (mirror `github-graphql-check`); add adaptive bisection (read `total_count`, split until `<1000`).
**Test**: shards cover Apr–May 2026; a `>1000` window bisects until `<1000`.

### T-012: Remove dead Neon driver (LIVE outage)
**AC**: AC-US6-02 | **Status**: [x] completed (crawl-worker node:test 6/6)
`stats-compute.js` → point at Hyperdrive or delete the dead telemetry path; surface errors loudly.
**Test**: runs without the Neon driver; no silent failure.

### T-002: resolveRepoIdentity with durable cache
**AC**: AC-US1-02, AC-US1-05 | **Status**: [x] completed (DEDUP-01..04/19; vitest + crawl-worker node:test green)
`crawl-worker/lib`: normalize URL → follow 301 → `/repositories/{id}`; persist `full_name→repo_id` **durably** (KV/Postgres, never in-memory). On 403/rate-limit, defer to retry — never fall back to the unresolved name.
**Test**: DEDUP-01..04, DEDUP-19.

### T-003: Two-phase Submission natural-key migration (MANUAL-GATED on prod)
**AC**: AC-US1-03, AC-US1-06, AC-US1-07 | **Status**: [x] code+tests complete (DEDUP-11/20 green). MANUAL GATE: prod two-phase cutover not run (files + reports/migration-cutover-plan.md only).
`(repoUrl, skillName)` → `(source_type, source_id, artifact_path)`: (1) normalize+resolve into staging, (2) MERGE pre-existing case/`.git`/slash dups (0673 pattern), (3) add unique constraint + `ON CONFLICT DO UPDATE`. Migrate `claim-submission` key in lockstep. **Never add the index on un-deduped data.** Implement + dry-run + test only; do NOT run against production unattended.
**Test**: DEDUP-11, DEDUP-20.

### T-004: Precedence DAG + fork-lineage + tightened merge predicate
**AC**: AC-US2-01, AC-US2-04 | **Status**: [x] completed (resolve.ts; DEDUP-05/13/14 green)
Single-repo `GET` fork/parent/source; DAG: `repo_id` auto-merge → fork-lineage auto-alias only if `fork=true` AND `source.id` catalogued. Merge predicate = `fork-lineage OR same repo_id` (owner+name+content NOT sufficient).
**Test**: DEDUP-05, DEDUP-13, DEDUP-14.

### T-005: Cross-repo content-hash pass (candidate + mirror resolve)
**AC**: AC-US2-02, AC-US2-05 | **Status**: [x] completed (resolve.ts; DEDUP-08/09/10/15 green)
Reuse 0794 canonical hash as a global lookup. Unrelated byte-identical → CANDIDATE flag only; mirror/import (`fork=false`, identical bytes) → auto-resolve to oldest-`createdAt` canonical as alias.
**Test**: DEDUP-08, DEDUP-09, DEDUP-10, DEDUP-15.

### T-006: Scheduled dedup reconciler + vendored-path guard
**AC**: AC-US2-03, AC-US2-06 | **Status**: [x] completed — decision core (reconcile.ts; DEDUP-06/12/16/17) + apply-side `applyReconcileDecisions` in src/db/dedup/merge.ts (alias losers, repoint children, never delete; DEDUP-16 vendored→alias) + `src/lib/cron/dedup-reconciler.ts` (re-key load on (repo_id via Repository.id surrogate, content_hash) → reconcileGroup → applyReconcileDecisions; per-group error containment) wired into build-worker-entry.ts dispatch + cohort-dispatch.ts (`DEDUP_RECONCILE_CRON = "30 3 * * *"`, cohort "dedup-reconcile") + wrangler.jsonc triggers.crons. `/admin/dedup-skills` re-keyed onto (repo_id, content_hash) governed by the DAG (earliest-published override replaces legacy lowest-trustScore; aliases instead of isDeprecated tombstone; dryRun → planReconcileGroups). Tests green: apply-reconcile.test.ts (5), dedup-reconciler.test.ts (9), cohort-dispatch.test.ts (7), admin route.test.ts (4), build-worker-entry.test.ts (4). Migration NOT applied; no DB connection. NOTE: SIBLING_LINK group is advisory (no schema column to persist siblingGroup) — UI grouping pass is the consumer. VERIFY (2026-05-31): re-confirmed on full suite — dedup surface 296/296 green; DEDUP-06/12/16/17 covered + passing. No DB command, no commit, no deploy by verifier.
Re-key `/admin/dedup-skills` on `(repo_id, content_hash)`; reconciler cron governed by the DAG with a vendored-path guard (`vendor/`, `third_party/`, `node_modules/`, `examples/`) and earliest-published weighting that OVERRIDES the legacy "deprecate lowest trustScore".
**Test**: DEDUP-12, DEDUP-16, DEDUP-17 + reconciler integration.

### T-013: Registry ingest-time resolution
**AC**: AC-US1-04 | **Status**: [x] completed — SubmissionRegistryAlias model + SubmissionRegistry enum (skillssh|skillsmp|awesome|other; github intentionally excluded) added to schema.prisma; FILE-ONLY migration prisma/migrations/20260531000002_0861_registry_alias/migration.sql (hand-written, validated offline via `prisma migrate diff --from-empty` — index name truncated to Prisma's canonical `..._artifactPat_idx` so post-cutover diff shows no drift; NOT applied). Pure decision core src/db/dedup/registry-alias.ts (`decideRegistryIngest` + `registryOriginFromSource`): a relay → already-catalogued (github, repo_id, artifactPath) → RECORD_ALIAS; non-relay (github-sharded/direct, origin=null) or non-github/first-sighting → CREATE_SUBMISSION. Wired into bulk/route.ts after natural-key resolution: RECORD_ALIAS inserts a SubmissionRegistryAlias (idempotent on (registry, listingId)) and SKIPS both upsertSubmission and the queue enqueue — no second tier-2 scan; new `aliased` counter + `status:"aliased"` detail. DB boundary in src/lib/submission/registry-alias-store.ts (findFirst by natural key + create with P2002→no-op). crawl-worker/sources/skills-sh.js now sends source="skills-sh" + listingId/listingUrl. Tests green: registry-alias.test.ts (11 pure-core), bulk/__tests__/registry-alias.test.ts (4 route integration — asserts upsertSubmission/queue NOT called on alias path), full dedup+bulk surface 110/110, crawl-worker skills-sh 16/16. NO DB connection opened; only offline prisma validate/generate/diff-from-empty. VERIFY (2026-05-31): re-confirmed on full suite — DEDUP-07/18 covered + passing; migration 20260531000002_0861_registry_alias is FILE-ONLY/UNAPPLIED (cutover is operator's job, out of scope). No DB command, no commit, no deploy by verifier.
At ingest, resolve every GitHub-pointing registry/awesome-list/skills.sh listing to `(github, repo_id, path)` via `resolveRepoIdentity` BEFORE creating a Submission; record the registry as an alias source. Non-GitHub forges keep a non-github `source_id`.
**Test**: DEDUP-07, DEDUP-18.

### T-007: Enrich scheduler heartbeat with cumulative counters
**AC**: AC-US3-03, AC-US3-04 | **Status**: [x]
`scheduler.js`: per-source monotonic `{discoveredTotal, submittedTotal, publishedTotal}` + `lastSuccessfulPublishAt` + `lastRunAt` + `lastError` + `consecutiveErrors`; CF side stamps `heartbeat-received-at`.
**Test**: counters monotonic; staleness uses received-at.

### T-008: Throughput-floor + source-dark + detector-blind detectors (EMAIL)
**AC**: AC-US3-01, AC-US3-02, AC-US3-05 | **Status**: [x]
Add `AlertKind` `discovery-floor`, `source-dark`, `detector-blind` to `types.ts`; add `detectDiscoveryFloor` (24h Skill count + escalating TTL), `detectSourceDark` (counter-flat-while-`lastRunAt`-advances), and a `detector-blind` trap on the evaluator's own query exception, on the `*/10` evaluator. Route via the existing **SendGrid email** transport (`sendQueueHealthAlert`). Exclude dead-man + detector-blind from the digest.
**Test**: counter-flat fires `source-dark`; Prisma throw fires `detector-blind` not silent green; ack snoozes then re-pages.

### T-009: External per-VM dead-man's-switch (EMAIL)
**AC**: AC-US4-01, AC-US4-02, AC-US4-03, AC-US4-04 | **Status**: [x]
Per-VM Healthchecks.io pings (one UUID per VM + a CF-pinged aggregate) gated on confirmed-publish + confirmed-DB-write (NOT the bare schedule tick); `/fail` on exception; Healthchecks email delivery; second independent dead-man (cron-job.org); persist-to-store on total failure. **No Telegram/Slack/Discord — email only.**
**Test**: skip VM2's ping → VM2 red, VM1/VM3 green; 200-with-0-skills does not ping; DB-down flips L2 red; total-failure → alert persisted.

### T-010: Regression — claim-key ↔ natural-key interaction
**AC**: AC-US1-07 | **Status**: [x] completed (src/db/dedup/claim-natural-key-concurrency.test.ts 9/9 — N-way concurrency one-row+one-claim, recoverStaleReceived terminal escalation, finalize idempotency, alert dedup window all confirmed intact)
Explicit concurrency test that `claim-submission`'s compare-and-swap key and the new `(source_type, source_id, path)` key agree on "same submission". Confirm `recoverStaleReceived` escalation, finalize idempotency, and existing alert dedup windows intact.
**Test**: `npx vitest run` + `npx playwright test`.
