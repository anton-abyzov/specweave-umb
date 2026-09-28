---
increment: 0874-crawl-coverage-healthcheck-and-email-alerts
title: "Crawl coverage: health-check, email alerts, verification + GitHub breadth"
type: bug
priority: P1
status: planned
created: 2026-06-18
structure: user-stories
test_mode: TDD
coverage_target: 90
---

# Feature: Crawl coverage: health-check, email alerts, verification + GitHub breadth

## Problem

The skill crawler silently under-collects and nothing alerts on it. Forensics (5-agent workflow + live API/VM probes, all citations verified 2026-06-17):

1. **GitHub discovery at ~2.4% coverage** (≈7k of ~245–288k live `SKILL.md`). `github-sharded` shards on `created:`, which GitHub **code** search silently ignores (`total_count=0`, no error). 42/49 prod shards return 0; the 7 working catch-alls each hit GitHub's 1,000-result cap → ~7k ceiling. The 0861 adaptive-bisection is disabled in prod and bisects the inert dimension anyway. Never caught — tests mock localhost and only assert the query string contains `created:`.
2. **Intake verification drops valid skills.** The bulk `SKILL.md` existence probe is unauthenticated (60 req/hr) and fail-closed — a 429/5xx becomes "404 not found", the skill is dropped (`status:"error"`, no Submission). `headCache` memoizes the transient false and poisons every sibling skill in a monorepo batch.
3. **The whole class fails silently.** skills-sh upstream `total` shrank 73,148→9,589 with `lastSkillsShError: null`; the number never leaves the VM (`getHeartbeatSources()` omits it); existing detectors can't see a per-source coverage regression. (skills.sh "748,368" = all-time **installs**, not skills — `"totalSkills":9589,"allTimeTotal":748368`; our crawler reads 9,589 correctly, the label is just misleading.)

## Goal

Make every degradation visible + alerting (health check + email), fix the genuine intake loss, and re-architect GitHub discovery to recover the ~98% it's missing — reusing the existing SendGrid alert path and the existing (sound) bisection engine.

---

## US-001: Semantic coverage health-check + email alerting (Track A)
**Project**: vskill-platform

**As a** crawler operator
**I want** a per-source coverage signal that leaves the VM and an email alert when it regresses, goes stale, or its submit ratio collapses
**So that** a silent 73k→9.5k-class drop pages me instead of passing as "healthy".

**Acceptance Criteria**:
- [ ] **AC-US1-01**: Per-source `coverageTotal`/`upstreamTotal` is added to `getHeartbeatSources()`, widened through `HeartbeatSource` + `SourceObservation`, and persisted into `SOURCE_OBS_KEY` (rides the existing heartbeat push — no VM polling).
- [ ] **AC-US1-02**: `detectCoverageRegression` (pure, in `detectors.ts`) fires **critical** when `coverageTotal < absoluteFloor` OR `< baselineHWM*(1−0.30)`, with an **upward-only** HWM baseline in `ALERTS_KV`; today's 9,590 vs 73,148 trips it.
- [ ] **AC-US1-03**: `detectCoverageStale` fires when last-success age > cooldown×1.5; `detectCoverageRatioCollapse` fires when `submittedΔ/discoveredΔ < 0.05` across 3 heartbeats.
- [ ] **AC-US1-04**: The 3 new `AlertKind`s dispatch email via the existing `sendQueueHealthAlert` SendGrid path (deduped via `shouldFire/recordFired`), run inside the existing `*/10` LIGHT cron — no new cron, no new email infra.
- [ ] **AC-US1-05**: `GET /api/v1/admin/queue-health` exposes per-source `coverageTotal` + baseline + `lastSuccessfulPublishAt`.
- [ ] **AC-US1-06**: Metric relabeled — `skillsShTotal`→`skillsShUpstreamReportedTotal`, plus `skillsShAllTimeInstalls` (homepage `allTimeTotal`) and `skillsShDiscoveredThisRun`; `README.md` updated so 9,589 skills is never compared to 748,368 installs again.

## US-002: Authenticated tri-state intake verification (Track B)
**Project**: vskill-platform

**As a** skill submitter
**I want** the intake SKILL.md probe to distinguish a transient rate-limit from a genuine 404
**So that** valid skills aren't silently dropped during crawl windows.

**Acceptance Criteria**:
- [ ] **AC-US2-01**: The bulk probe is authenticated — `cfEnv.GITHUB_TOKEN` threaded through `cachedCheck → checkSkillMdExists → detectBranch` (60→5,000 req/hr).
- [ ] **AC-US2-02**: `checkSkillMdExists` returns tri-state `{exists, transient}`; in `bulk/route.ts` a transient (403/429/5xx/timeout) is **deferred** (reuse the 403 identity-defer path), and "not found" is pushed only on a confirmed 404.
- [ ] **AC-US2-03**: `headCache` never memoizes a transient false — one rate-limited probe cannot cascade-drop sibling skills in the same monorepo batch.
- [ ] **AC-US2-04**: Per-source `{submitted,skipped,errors,deferred,aliased}` counters thread into `inline-submitter.js` + scheduler `lastResult` and expose `submit_rate`/`intake_notfound_rate` on `/coverage`.
- [ ] **AC-US2-05**: A confirmed same-repository, different full case-preserving artifact path gets a distinct durable Submission with a readable path-qualified label after an exact canonical miss. Bounded create races may reuse only the complete exact tuple; old rows, scope, state and labels remain unchanged. Unknown constraints, deleted rows, unrelated qualified-name collisions and private/tenant boundaries fail closed.
- [ ] **AC-US2-06**: Publication and orphan-PUBLISHED recovery bind to the exact complete canonical tuple and authoritative DB linkage. Existing valid exact-artifact URLs stay stable; new distinct paths, including case differences and shared basenames, cannot collide or overwrite another Skill. Atomic metadata/version/outbox/link predicates preserve identity and scope through races; failed identity proofs never report successful publication.
- [ ] **AC-US2-07**: Durable readable labels and case-preserving artifact paths survive DB, raw SQL, KV, list, search and cache projections. Shared dedup keeps different known paths distinct, collapses duplicate snapshots of one ID, and preserves path-missing legacy compatibility without merging it into a known different artifact.

## US-003: GitHub discovery breadth via size-bisection (Track C)
**Project**: vskill-platform

**As a** crawler operator
**I want** discovery to shard on the live `size:` dimension instead of the inert `created:` one
**So that** GitHub coverage climbs from ~2.4% toward the full ~245k corpus.

**Acceptance Criteria**:
- [ ] **AC-US3-01**: `splitSizeRange` bisects an integer range at the midpoint and returns `null` on a single value; the open-ended top root is capped (`[10001,null]`→`[10001,384000]`) before bisecting.
- [ ] **AC-US3-02**: `bisectWindow` accepts an injected `split` fn (default `splitDateWindow`, back-compatible); `expandPlanByBisection` bisects on `shard.size` when `shardMode==="size-bisect"`.
- [ ] **AC-US3-03**: `buildShardPlan` supports `"size-bisect"` mode and is data-driven — `config.sizeShards` is honored (the currently-dead param is fixed).
- [ ] **AC-US3-04**: A terminal leaf renders as `size:N..N` (never bare `size:N`, which 422s); unit tests prove bisection tiles `[0,N]` with no gaps and no over-cap leaves for the SKILL.md corpus.
- [ ] **AC-US3-05**: The expanded leaf plan is persisted in the checkpoint so the `shardMode`-keyed resume replays an identical plan across the 120-min windows.
- [ ] **AC-US3-06**: A live size-bisect run discovers ≫7k distinct repos with `shardsZeroResultCount`≈0 (vs the 42/49-zero baseline).
- [ ] **AC-US3-07**: `github-graphql-check` widened (`LOOKBACK_MONTHS` 3→~12, topic allow-list extended); the Worker-path dead `generateTimeShardedQueries` is quarantined with a note that the VM owns code-search breadth.
- [ ] **AC-US3-08**: A real-API CI guard (gated on `GITHUB_TEST_TOKEN`) asserts `created:`→0 and `size:`→>0 so the dead dimension can never silently return.

## US-004: Coverage ground-truth bridge + secret-hygiene prerequisite (Track A↔C)
**Project**: vskill-platform

**As a** crawler operator
**I want** the GitHub undercount itself to be a monitored signal, and the exposed VM tokens locked down before any prod change
**So that** breadth regressions alert and committed secrets stop leaking.

**Acceptance Criteria**:
- [ ] **AC-US4-01**: A daily `filename:SKILL.md` ground-truth probe + `shardsZeroResultCount` detector alerts when >50% shards return zero (dead-dimension signature) OR coverage ratio < 10%; a loud "date qualifier ineffective on code search" assertion logs when a date-bearing shard is 0 while its parent is >0.
- [x] **AC-US4-02**: `.env.vm*`/`.env.gcp-vm*` are added to `.gitignore` and `git rm --cached`-ed (13 files); `.env.vm.example` template added; the exposed PATs are flagged for rotation (Anton rotates — MANUAL, pending), and the prod size-bisect flip (T-C06) stays gated until rotation is confirmed.

## Out of scope
GH Archive / BigQuery exhaustive backfill; full git-history secret purge (BFG/filter-repo) — separate security increment.

## Recovery implementation boundary — 2026-09-28

Use rewritten vskill-platform origin/main e3718ee6 as the source base. This lane owns T-006, T-007, T-008, T-009 and T-019; T-017 includes a bounded failed-sweep signal repair after live read-only evidence showed seven 401s hidden under success; its production run remains read-only and blocked. 0861 migration state is read-only verification. Extend the existing task file sets for regression coverage and durable intake retry plumbing. A transient probe must not become confirmed absence, poison memoized sibling checks, select an unrelated fallback skill, or disappear after an acknowledged queue retry. Retain candidate/source provenance through retries. No production mutation or deployment before independent review; no shared handoff-pointer changes.

## Authorized release repair — 2026-09-28

The required privacy E2E failures and Node database connection exhaustion are necessary release gates for crawler PR74. These bounded repairs live in the existing0874 increment and isolated worktree. Original dirty roots, existing SEO/release owners, and cross-tool handoff pointers remain protected.

- **AC-REL-01**: The full required0826 suite runs without skips or weakened checks, proving paid publishing, FREE denial without writes, real private404 responses, authorized200 and populated public catalog isolation.
- **AC-REL-02**: The same suite passes with PostgreSQL max_connections=100; Node reuses its database pool while Cloudflare and explicit Worker contexts retain separate I/O clients.


## Distinct-artifact recovery boundary — 2026-09-28

T030 closes only exact canonical uniqueness recovery. Its final delivery proof preserves the failed packaging artifact, guarded rollback and all historical errors; the current run is not clean. Twenty-two newly exposed entries have legitimate distinct paths that collide with ten existing legacy Submission rows (nineteen linked-Skill matches). T031 owns this follow-on through publication and read-surface identity. Use a fresh isolated branch from merged `7f86c79ceeee190d6017d6e2f857a68ea522067a`; preserve all original owners and fixtures. Source authority is the complete tuple `[sourceType, stable sourceId, case-preserving artifactPath]`, never a decoded label or queue payload. Use a bounded full-tuple discriminator only for new publication identities; preserve exact linked legacy URLs. No global slug change, DDL, historical backfill/delete, synthetic production input, manual replay, crawler/scanner restart, privacy relaxation or shared handoff mutation. Independent review and required CI precede root-owned Worker release. Natural read-only hashed baselines must prove new tuples settle without old Submission/Skill identity, name or privacy overwrite. T017 and T027 full-sweep gates remain open.
