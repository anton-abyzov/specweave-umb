# Deploy Runbook — 0672 Queue Reliability

> **Read this entire document before running any command.** This runbook is
> intended for the human operator (Anton) to execute — Claude agents must NOT
> run any step below without explicit operator confirmation.
>
> **Target system**: production `verified-skill.com` (Cloudflare Worker
> `verified-skill-com` + Neon Postgres).
>
> **Scope**: collapse duplicate Submission rows, add
> `@@unique([repoUrl, skillName])`, deploy the upsert + cache warm-up code.
>
> **Window**: run during US off-peak (≈ 02:00 UTC) per plan.md §6. Total
> expected duration: ≈ 10 minutes including verification.

## 0. Preconditions

- [ ] On `main`, up-to-date, local working tree clean.
- [ ] All Track A–E agents have reported COMPLETION to team-lead.
- [ ] `git status` shows no uncommitted changes inside
      `repositories/anton-abyzov/vskill-platform/`.
- [ ] `vskill-platform` project is **not disabled** in the umbrella config
      (team-lead un-disabled this before spawning the integration agent).
- [ ] The production Neon `DATABASE_URL` is available to the operator (the
      umbrella .env or a password-manager entry — do NOT echo it into shell
      history; prefer pasting via a subshell or env-only var).
- [ ] `wrangler whoami` is authenticated as the Cloudflare account that owns
      `verified-skill-com`.
- [ ] `npx prisma --version` runs from
      `repositories/anton-abyzov/vskill-platform`.

## 1. Step-by-step commands

Each step is self-contained. **Do not batch-paste** the whole list — review
each command's output before moving to the next. The deploy is only resumable
between steps, not mid-step.

```bash
# 1. Move into the vskill-platform repo.
cd /Users/antonabyzov/Projects/github/specweave-umb/repositories/anton-abyzov/vskill-platform

# 2. Sync main.
git checkout main && git pull --ff-only

# 3. Dry-run the collapse to confirm the victim count matches expectation.
#    Expected: 6–7 obsidian-brain duplicates + a handful of others (see
#    spec.md §Background, reproduced at /queue?q=d on 2026-04-21).
#    DATABASE_URL must be the production Neon URL — no host override.
DATABASE_URL="<PROD_NEON_URL>" \
  npx tsx scripts/migrations/0672-collapse-submission-dupes.ts --dry-run

#   Expected stdout:
#     [0672-collapse dry-run] archivedCount=<N> changed=false archive=(none)
#     [0672-collapse dry-run] no mutations executed, no archive written. ...
#   Abort if N is wildly outside the 6–20 range.

# 4. Real collapse. Single Postgres transaction with LOCK TABLE EXCLUSIVE.
#    Writes backups/dedup-collapse-0672.json with the full victim snapshot
#    (submission row + all 5 FK child arrays per victim).
DATABASE_URL="<PROD_NEON_URL>" \
  npx tsx scripts/migrations/0672-collapse-submission-dupes.ts

#   Expected stdout:
#     [0672-collapse] archivedCount=<N> changed=true archive=<path>

# 5. Verify the archive JSON is populated.
ls -lh ../../.specweave/increments/0672-queue-reliability/backups/dedup-collapse-0672.json
jq '. | length' ../../.specweave/increments/0672-queue-reliability/backups/dedup-collapse-0672.json
#   Expected: length equals archivedCount from step 4.

# 6. Apply the unique index migration. This MUST come after step 4 — if any
#    duplicate (repoUrl, skillName) rows survive, CREATE UNIQUE INDEX will fail.
DATABASE_URL="<PROD_NEON_URL>" \
  npx prisma migrate deploy

#   Expected stdout includes:
#     Applying migration `20260421100000_submission_unique_repo_skill`

# 7. Deploy the code. This invokes prisma generate + build + wrangler deploy.
./scripts/push-deploy.sh

#   Expected stdout ends with a wrangler deploy success line printing the
#   worker URL and the uploaded version id.

# 8. Watch CF logs for 10–15 minutes during low traffic. Exit with Ctrl-C
#    once you've seen at least one hourly cron tick ("queue list warmup")
#    and confirmed zero P2002 leaks on public POST /api/v1/submissions.
wrangler tail --name verified-skill-com --format pretty

#   Expected markers over a 60+ minute window:
#     [cron] queue list warmup: wrote=5 failed=0 in <Nms>
#     (no lines matching "P2002" in response bodies)
#     (no uncaught Prisma errors)

# 9. Manual smoke A — queue renders.
curl -sS https://verified-skill.com/queue | grep -c '<tr' || true
#   Expected: a count > 10 (SSR returns rows on the first request).

# 10. Manual smoke B — dedup worked.
curl -sS 'https://verified-skill.com/queue?q=d' | \
  grep -oE '>obsidian-brain<' | wc -l
#    Expected: 0 or 1 (never more). Zero is fine; the row may be outside
#    the first 50 rows returned — confirm via the E2E instead for certainty.

# 11. Playwright smoke via E2E (optional, against prod).
E2E_BASE_URL=https://verified-skill.com \
  npx playwright test tests/e2e/queue-duplicates.spec.ts
#    Expected: both tests pass.
```

## 2. Rollback

Trigger rollback if any of the following occurs within the first 24 h:

- `wrangler tail` shows Prisma error objects leaking into HTTP response bodies.
- POST `/api/v1/submissions` returns HTTP 5xx on previously-working payloads.
- `SELECT COUNT(*) FROM "Submission" GROUP BY "repoUrl", "skillName" HAVING COUNT(*) > 1`
  returns non-zero rows (should be impossible post-index, but verify).
- The hourly warm-up cron consistently logs `failed>0` for > 2 consecutive hours.

### Rollback commands

```bash
cd /Users/antonabyzov/Projects/github/specweave-umb/repositories/anton-abyzov/vskill-platform

# A. Revert the code deploy (keeps DB changes in place). This is the fastest
#    mitigation — restores the old submission-dedup.ts + 60s TTL + pre-warm-up
#    behavior while leaving the unique index intact (safe — doesn't create
#    duplicates, just means new submissions hit P2002 at the create call).
git revert --no-edit <merge-commit-sha>
git push origin main
./scripts/push-deploy.sh

# B. (Optional) Drop the unique index. Only if revert alone doesn't resolve
#    the issue AND the pre-revert code relies on the non-unique index shape.
DATABASE_URL="<PROD_NEON_URL>" psql <<'SQL'
BEGIN;
DROP INDEX IF EXISTS "Submission_repoUrl_skillName_key";
CREATE INDEX IF NOT EXISTS "Submission_repoUrl_skillName_idx"
  ON "Submission"("repoUrl", "skillName");
COMMIT;
SQL

# C. (Catastrophic only) Restore deleted victim rows from the archive.
#    Use only if dedup-collapse-0672.json reveals a production regression
#    (e.g., a published-skill row was erroneously collapsed into a survivor
#    whose state machine is now in a bad state).
DATABASE_URL="<PROD_NEON_URL>" \
  npx tsx scripts/migrations/0672-restore-submission-dupes.ts --i-understand-this-is-prod

#   Expected: restore script reads
#     .specweave/increments/0672-queue-reliability/backups/dedup-collapse-0672.json
#   and re-inserts victim rows with their original IDs, re-points FK children
#   back. The restore script refuses to run unless the flag is passed and
#   DATABASE_URL looks like a Neon host.
```

### Rollback decision matrix

| Symptom | Step A | Step B | Step C |
|---|---|---|---|
| App regressed but DB is fine | Yes | No | No |
| App regressed + P2002 leaking | Yes | Consider | No |
| Data-integrity regression (wrong survivor) | Yes | Yes | Yes |

## 3. Post-deploy monitoring (first 24 h)

- [ ] Hourly cron: `wrangler tail` shows `[cron] queue list warmup: wrote=5 failed=0` every hour.
- [ ] `/queue` cold-load spot-check every 6 hours returns rows on first HTTP request.
- [ ] `/queue?q=d` shows exactly 0 or 1 `obsidian-brain` row.
- [ ] P2002 in logs: zero in HTTP responses, informational only in server logs.
- [ ] No new duplicate `(repoUrl, skillName)` groups materialize (run the
      SELECT above at T+24h).

## 4. References

- [spec.md](./spec.md) — AC-US1-01, AC-US2-03, AC-US2-04 govern the success criteria.
- [plan.md](./plan.md) §6 — full rollout sequence and risk table.
- [tasks.md](./tasks.md) — T-028..T-031 are the Track E tasks gating this deploy.
- Collapse script: `repositories/anton-abyzov/vskill-platform/scripts/migrations/0672-collapse-submission-dupes.ts`
- Restore script: `repositories/anton-abyzov/vskill-platform/scripts/migrations/0672-restore-submission-dupes.ts`
- Migration SQL: `repositories/anton-abyzov/vskill-platform/prisma/migrations/20260421100000_submission_unique_repo_skill/migration.sql`
