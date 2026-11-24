# Verify — 0854-source-link-deprecation-pipeline

FAIL · 2026-10-27T21:14:19.180Z · commands from explicit

## Commands

### `cd /Users/antonabyzov/.specwithcode/m4/worktrees/vskill-platform/0854-isolated-runtime && PWDEBUG=0 PLAYWRIGHT_HTML_OPEN=never node_modules/.bin/vitest run check-source SourceLinkAndBanner.test.tsx src/lib/cron/__tests__/source-probe.test.ts src/lib/cron/__tests__/stale-source-sweep.test.ts --maxWorkers=4` → exit 0 (2s)

```

stderr | src/lib/cron/__tests__/stale-source-sweep.test.ts > runStaleSourceSweep > trips the breaker after 3 consecutive transient errors and keeps the cursor
[stale-source-sweep] circuit breaker tripped after 3 consecutive transient errors

stdout | src/lib/cron/__tests__/stale-source-sweep.test.ts > runStaleSourceSweep > trips the breaker after 3 consecutive transient errors and keeps the cursor
[stale-source-sweep] processed 8 skills, deprecated 0, skipped-recent 0, healthy 0, transient 8 (circuit tripped)

stdout | src/lib/cron/__tests__/stale-source-sweep.test.ts > runStaleSourceSweep > treats 3xx as healthy
[stale-source-sweep] processed 1 skills, deprecated 0, skipped-recent 0, healthy 1, transient 0

stdout | src/lib/cron/__tests__/stale-source-sweep.test.ts > runStaleSourceSweep > defaults to a batch of 500
[stale-source-sweep] processed 0 skills, deprecated 0, skipped-recent 0, healthy 0, transient 0

stderr | src/lib/cron/__tests__/stale-source-sweep.test.ts > runStaleSourceSweep > reports only probes actually started before the breaker stops queued work
[stale-source-sweep] circuit breaker tripped after 3 consecutive transient errors

stdout | src/lib/cron/__tests__/stale-source-sweep.test.ts > runStaleSourceSweep > reports only probes actually started before the breaker stops queued work
[stale-source-sweep] processed 10 skills, deprecated 0, skipped-recent 0, healthy 0, transient 10 (circuit tripped)

stdout | src/lib/cron/__tests__/stale-source-sweep.test.ts > runStaleSourceSweep > refuses a write when repoUrl changes after selection
[stale-source-sweep] processed 1 skills, deprecated 0, skipped-recent 1, healthy 0, transient 0

stdout | src/lib/cron/__tests__/stale-source-sweep.test.ts > runStaleSourceSweep > refuses a write when skillPath changes after selection
[stale-source-sweep] processed 1 skills, deprecated 0, skipped-recent 1, healthy 0, transient 0

stdout | src/lib/cron/__tests__/stale-source-sweep.test.ts > runStaleSourceSweep > refuses a write when sourceBranch changes after selection
[stale-source-sweep] processed 1 skills, deprecated 0, skipped-recent 1, healthy 0, transient 0

stdout | src/lib/cron/__tests__/stale-source-sweep.test.ts > runStaleSourceSweep > refuses a write when tenantId changes after selection
[stale-source-sweep] processed 1 skills, deprecated 0, skipped-recent 1, healthy 0, transient 0

stdout | src/lib/cron/__tests__/stale-source-sweep.test.ts > runStaleSourceSweep > refuses a write when privacy changes after selection
[stale-source-sweep] processed 1 skills, deprecated 0, skipped-recent 1, healthy 0, transient 0

 ✓ src/lib/cron/__tests__/stale-source-sweep.test.ts (18 tests) 23ms
stdout | src/app/api/v1/skills/__tests__/check-source.waitUntil.test.ts > GET /api/v1/skills/check-source — waitUntil deprecation pipeline > threads deprecateStaleSkill through ctx.waitUntil and writes isDeprecated:true to DB on 404
[check-source] Auto-deprecated owner/repo/skill

stdout | src/app/api/v1/skills/__tests__/check-source.waitUntil.test.ts > GET /api/v1/skills/check-source — waitUntil deprecation pipeline > falls through to inline await when no Cloudflare context is available (local dev)
[check-source] Auto-deprecated owner/repo/skill

 ✓ src/app/api/v1/skills/__tests__/check-source.waitUntil.test.ts (5 tests) 11ms
 ✓ src/app/api/v1/skills/__tests__/check-source.cache.test.ts (10 tests) 13ms
 ✓ src/app/api/v1/skills/__tests__/check-source.safety.test.ts (61 tests) 190ms
 ✓ src/app/skills/[owner]/[repo]/[skill]/__tests__/SourceLinkAndBanner.test.tsx (24 tests) 257ms

 Test Files  6 passed (6)
      Tests  145 passed (145)
   Start at  17:14:17
   Duration  1.28s (transform 197ms, setup 152ms, collect 317ms, tests 505ms, environment 449ms, prepare 227ms)
```

## Acceptance criteria

0/12 met

| AC | Met | Acceptance | Text |
|---|---|---|---|
| AC-US1-01 |   | open | Visiting `/skills/{owner}/{repo}/{skill}` whose `skillPath` 404s upstream causes `Skill.isDeprecated=true` in DB within 10 seconds of page load. |
| AC-US1-02 |   | open | When the client check-source call reports `offline`, the rendered source-path link visually indicates broken state (line-through + warning glyph + descriptive `title`/`aria-label`). The link stays clickable so power users can confirm the upstream 404 themselves. |
| AC-US1-03 |   | open | The `<DeprecationBanner>` mounts on every skill detail page that has a `repoUrl` + `skillPath` (not only when `isDeprecated` is already true) so the live source check runs. |
| AC-US2-01 |   | open | `deprecateStaleSkill` and `undeprecateSkill` are invoked via `getCloudflareContext({ async: true }).ctx.waitUntil(...)` with a typeof-function guard for local dev. Pattern matches `src/app/api/v1/auth/login/route.ts:91-105`. |
| AC-US2-02 |   | open | Unit test mocks `getCloudflareContext`, captures the waitUntil promise, awaits it, and asserts `prisma.skill.updateMany` was called with `data: { isDeprecated: true }`. |
| AC-US3-01 |   | open | `npx tsx scripts/backfill-stale-source.ts --dry-run` prints the list of skills it would deprecate and includes `stephengpope/thepopebot/kie-ai` in the production data. |
| AC-US3-02 |   | open | Without `--dry-run` the script deprecates the matched skills (sets `isDeprecated=true`) and invalidates the relevant KV search-index shards via the Cloudflare REST API. |
| AC-US3-03 |   | open | Script supports `--limit N` and `--max-age-days N` flags; uses `p-limit` concurrency control (default 10) to avoid hammering raw.githubusercontent.com. |
| AC-US4-01 |   | open | `runStaleSourceSweep` exists at `src/lib/cron/stale-source-sweep.ts` and processes >=500 skills/run by default. |
| AC-US4-02 |   | open | Cron triggers only deprecate on definitive 404 from raw.githubusercontent.com (not 429/5xx/3xx); shares the circuit-breaker pattern from `runEnrichmentBatch`. |
| AC-US4-03 |   | open | Cron is wired into `scripts/build-worker-entry.ts` and the cohort dispatch, runs at a gated minute on the existing schedule so no new wrangler cron trigger is needed. |
| AC-US4-04 |   | open | KV search-shard cleanup uses the existing `updateSearchShard()` helper for deprecated skills. |

## Tasks (ledger)

| Task | State | By | Evidence | Note |
|---|---|---|---|---|
| T-001 | done | claude@antons-macbook-m4max | cd /Users/antonabyzov/Projects/github/specweave-umb/reposit… | Shipped in 72c610d3; on main and in the live worker build d… |
| T-002 | done | claude@antons-macbook-m4max | cd /Users/antonabyzov/Projects/github/specweave-umb/reposit… | Shipped in 72c610d3. |
| T-003 | done | claude@antons-macbook-m4max | cd /Users/antonabyzov/Projects/github/specweave-umb/reposit… | Shipped in 72c610d3. |
| T-004 | done | claude@antons-macbook-m4max | cd /Users/antonabyzov/Projects/github/specweave-umb/reposit… | Shipped in 72c610d3. |
| T-005 | done | claude@antons-macbook-m4max | cd /Users/antonabyzov/Projects/github/specweave-umb/reposit… | Shipped in 72c610d3; page.tsx imports SourceCheckProvider/S… |
| T-006 | done | claude@antons-macbook-m4max | cd /Users/antonabyzov/Projects/github/specweave-umb/reposit… | Shipped in 72c610d3. |
| T-007 | done | claude@antons-macbook-m4max | cd /Users/antonabyzov/Projects/github/specweave-umb/reposit… | Shipped in 72c610d3. |
| T-008 | done | claude@antons-macbook-m4max | cd /Users/antonabyzov/Projects/github/specweave-umb/reposit… | Shipped in 72c610d3. |
| T-009 | done | claude@antons-macbook-m4max | cd /Users/antonabyzov/Projects/github/specweave-umb/reposit… | cohort-dispatch.ts itself was not edited: the sweep runs in… |
| T-010 | done | claude@antons-macbook-m4max | cd /Users/antonabyzov/Projects/github/specweave-umb/reposit… | Wired in 72c610d3; d52c2d5f is the RELEASE_GIT_SHA of the l… |
| T-011 | done | claude@antons-macbook-m4max | cd /Users/antonabyzov/Projects/github/specweave-umb/reposit… | Script shipped in 72c610d3 with --dry-run, --limit, --max-a… |
| T-012 | done | claude@antons-macbook-m4max | cd /Users/antonabyzov/Projects/github/specweave-umb/reposit… | Full 'npx vitest run' on 5d72701b: 743 files/7894 tests pas… |
| T-013 | skipped | claude@antons-macbook-m4max |  | Moot: the dry-run's check that kie-ai appears in the deprec… |
| T-014 | skipped | claude@antons-macbook-m4max |  | Goal already met in production. curl https://verified-skill… |
| T-015 | done | disk-completion-0854 | Source PR #180 merge fe24b00e2fa1c6d23bd0a8a22a40b509dd5680… |  |
| T-016 | done | disk-completion-0854 | PR182 head40f188b4ec4fb231abbc94a01454b3981c403153:87 tests… |  |
| T-017 | done | codex@antons-macbook-m4max | Actual headless page200 in local workerd exactdeployedfe8cc… |  |
| T-018 | open |  |  |  |
| T-019 | open |  |  |  |
| T-020 | done | disk-completion-0854 | PR182 merged ff7156ab4afbb89ad418424421709a22982a35f4 after… |  |
| T-021 | done | disk-completion-0854 | PR183 source f0d09124d8386f3945f0b958907f95d6d510ac56 indep… |  |
| T-022 | done | codex@antons-macbook-m4max | PR185 exact-head03b4875 independently SHIP,145focused+35int… |  |

18/22 done · 2 skipped · 0 claimed · 0 blocked · 0 stale · 2 open

### Skipped

- T-013 — Moot: the dry-run's check that kie-ai appears in the deprecate list can no longer pass, because kie-ai is already isDeprecated=true in prod (live API, updatedAt 2026-05-27T18:34:39Z) and the script selects only isDeprecated:false skills (scripts/backfill-stale-source.ts:139). The script's flags are verified in T-011. A prod dry-run to size any remaining backlog needs Anton's go-ahead: npx tsx scripts/backfill-stale-source.ts --dry-run. (claude@antons-macbook-m4max)
- T-014 — Goal already met in production. curl https://verified-skill.com/api/v1/skills/stephengpope/thepopebot/kie-ai on 2026-10-20 returns skill.isDeprecated=true, updatedAt 2026-05-27T18:34:39Z. That was during 0854 development, before the 72c610d3 commit (20:32Z), so neither the stale-source-sweep cron nor this backfill did it. The ongoing backlog is drained by the hourly sweep (build-worker-entry.ts LIGHT cohort, minute 0) in the live build d52c2d5f, which removes skills from the shards. Running scripts/backfill-stale-source.ts against prod for any remaining backlog still needs Anton's go-ahead. (claude@antons-macbook-m4max)
