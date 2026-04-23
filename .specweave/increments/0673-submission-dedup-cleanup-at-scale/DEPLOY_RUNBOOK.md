# DEPLOY_RUNBOOK.md — Increment 0673 (Submission dedup cleanup at scale)

> **Purpose**: end-to-end operator instructions to cleanly collapse 2,825,767 duplicate
> `Submission` rows on production Neon, apply the 0672 unique-index migration, deploy the
> 0672 code, and monitor the result. This runbook REPLACES the 0672 runbook.
>
> **Estimated total wall-time**: 2–3 h active work + 24 h monitoring (the prod cleanup
> step itself is expected to take 45–90 min; surrounding steps add ~30–60 min).
>
> **Who should run it**: an operator with prod Neon credentials (`DATABASE_URL` pointing
> at `ep-polished-haze-aea6snnj-pooler.c-2.us-east-2.aws.neon.tech`), Cloudflare `wrangler`
> auth, and either `neonctl` authenticated or `NEON_API_KEY` exported.
>
> **Required env vars**: `NEON_PROJECT_ID`, `PROD_URL` (pooled prod `DATABASE_URL`),
> `PROD_URL_DIRECT` (non-pooled prod `DATABASE_URL` — same URL with `-pooler` stripped
> from the hostname), and either `neonctl` session or `NEON_API_KEY`. `BRANCH_POOLED` /
> `BRANCH_DIRECT` are captured at Step 3.
>
> **Why both pooled and direct URLs?** The cleanup script (Steps 4 and 6) creates a
> `_0673_survivors` PostgreSQL TEMP TABLE that is session-scoped. Pooled / serverless
> connections do not guarantee session affinity across queries, so the cleanup script
> MUST run against the direct (non-pooled) endpoint. Migrations (Steps 5 and 7) can run
> against either, but the runbook uses direct for consistency. The pooled URL is still
> used by `prisma migrate` for its connection-string validation and by the application
> itself; the runbook never passes the pooled URL to the cleanup script.
>
> **Supporting docs**: [`HANDOFF.md`](./HANDOFF.md) is the single source of truth for
> where we are in the sequence — update it after each step. [`spec.md`](./spec.md) §US-005
> defines the acceptance contract for this file. ADR-0257 explains the batched-cleanup
> pattern.
>
> **Before running the scripts**: operators should `chmod +x scripts/create-neon-branch.sh
> scripts/delete-neon-branch.sh` after pulling — the files are committed without the
> execute bit.

---

## Step 1 — Preconditions

Verify every one of these BEFORE touching any branch or prod. The whole sequence assumes
they hold.

### Command(s)

```bash
# GitHub CLI authenticated (for push-deploy.sh downstream)
gh auth status

# Neon CLI authenticated
neonctl me

# Required env vars set in your shell (or in .env that you source)
[[ -n "${NEON_PROJECT_ID:-}"  ]] || echo "MISSING NEON_PROJECT_ID"
[[ -n "${PROD_URL:-}"         ]] || echo "MISSING PROD_URL (pooled prod DATABASE_URL)"
[[ -n "${PROD_URL_DIRECT:-}"  ]] || echo "MISSING PROD_URL_DIRECT (non-pooled; cleanup needs it)"
[[ -n "${NEON_API_KEY:-}"     ]] || echo "MISSING NEON_API_KEY (only if neonctl absent)"

# Sanity: PROD_URL should contain -pooler; PROD_URL_DIRECT should NOT.
grep -q 'pooler'  <<<"${PROD_URL:-}"        || echo "WARN PROD_URL does not look pooled"
grep -q 'pooler'  <<<"${PROD_URL_DIRECT:-}" && echo "WARN PROD_URL_DIRECT looks pooled (hostname contains 'pooler')"

# 0672 unique-index migration is present on vskill-platform main
cd repositories/anton-abyzov/vskill-platform
git fetch origin
git log --oneline origin/main | grep -E '5b92a50|submission.?unique' | head
ls prisma/migrations | grep -i 'submission_unique_repo_skill'
cd -

# _prisma_migrations is not in a broken state for the 0672 migration
# (run against prod — READ ONLY query)
psql "$PROD_URL" -c "SELECT migration_name, finished_at, rolled_back_at \
                     FROM _prisma_migrations \
                     WHERE migration_name LIKE '%submission_unique%' \
                     ORDER BY started_at DESC LIMIT 5;"
```

### Expected output

- `gh auth status` → "Logged in to github.com as …"
- `neonctl me` → prints your Neon user (no auth error)
- All env-var checks silent (no `MISSING` lines)
- A single migration folder `20260421100000_submission_unique_repo_skill/` exists locally
- `_prisma_migrations` query returns EITHER zero rows (migration never applied) OR a row
  with `finished_at = NULL` AND `rolled_back_at = NULL` (pending) — anything else means a
  stale apply needs `prisma migrate resolve` BEFORE Step 7

### If this fails

- `gh auth status` fails → `gh auth login`
- `neonctl me` fails → `neonctl auth login`; alternatively skip this and rely on
  `NEON_API_KEY` fallback in the branch scripts
- Migration missing on main → pull: `cd repositories/anton-abyzov/vskill-platform && git
  pull origin main`; confirm commit `5b92a50` (from HANDOFF.md) is in `git log`
- `_prisma_migrations` shows a rolled-back row → note it; revisit at Step 7 and run
  `npx prisma migrate resolve --applied 20260421100000_submission_unique_repo_skill` or
  `--rolled-back` per the actual state

---

## Step 2 — Kill the SpecWeave dashboard + any GitHub pollers

The SpecWeave dashboard polls GitHub continuously and will consume the rate-limit budget
that the cleanup and deploy paths need. Kill it (and any ad-hoc poll scripts) before
heavy DB ops.

### Command(s)

```bash
# List likely offenders
pgrep -fl 'specweave dashboard' || true
pgrep -fl 'gh api'              || true

# Kill the dashboard if it's running
pkill -f 'specweave dashboard' || true

# Double-check nothing lingers
sleep 2
pgrep -fl 'specweave dashboard' && echo "STILL RUNNING" || echo "clean"
```

### Expected output

```text
clean
```

### If this fails

- `pkill` reports "no process matched" → nothing was running, proceed
- `STILL RUNNING` after `pkill` → find the PID: `pgrep -f 'specweave dashboard'`, then
  `kill -9 <pid>`
- If the dashboard is in a separate terminal you control, close that terminal instead of
  `pkill`ing (avoids zombie state in that shell)

---

## Step 3 — Create the Neon dry-run branch

Create a zero-copy branch from `main`. This is the rollback path for the entire sequence —
do NOT delete it until Step 10 monitoring is clean.

### Command(s)

```bash
# From the umbrella root
cd /Users/antonabyzov/Projects/github/specweave-umb

# Run the branch-creation script (captures stdout → shell variables)
OUTPUT=$(NEON_PROJECT_ID="$NEON_PROJECT_ID" \
  bash .specweave/increments/0673-submission-dedup-cleanup-at-scale/scripts/create-neon-branch.sh)

# Parse the three lines it prints: pooled, direct, name. The `name=` line is the
# authoritative branch identifier — do NOT derive it from `neonctl branches list`
# because a concurrent branch creation between steps can otherwise capture the
# wrong branch and cause the wrong one to be deleted in Step 10.
BRANCH_POOLED=$(echo "$OUTPUT" | awk -F= '/^pooled=/ {sub(/^pooled=/,""); print; exit}')
BRANCH_DIRECT=$(echo "$OUTPUT" | awk -F= '/^direct=/ {sub(/^direct=/,""); print; exit}')
BRANCH_NAME=$(echo "$OUTPUT"   | awk -F= '/^name=/   {sub(/^name=/,"");   print; exit}')
echo "pooled: $BRANCH_POOLED"
echo "direct: $BRANCH_DIRECT"
echo "name:   $BRANCH_NAME"

# Export both — downstream steps choose based on what the workload needs:
#   * cleanup script (Steps 4, 6)  → BRANCH_DIRECT / PROD_URL_DIRECT (session-scoped TEMP TABLE)
#   * prisma migrate deploy (Step 5) → BRANCH_DIRECT (connection limit friendlier)
# The pooled URL is retained for ad-hoc psql queries that don't depend on session state.
export BRANCH_POOLED BRANCH_DIRECT BRANCH_NAME

# Persist the exact branch name for Step 10 deletion (single source of truth).
printf '%s\n' "$BRANCH_NAME" | tee /tmp/0673-branch-name.txt
```

### Expected output

```text
pooled: postgres://neondb_owner:***@ep-....-pooler...-us-east-2.aws.neon.tech/neondb?sslmode=require
direct: postgres://neondb_owner:***@ep-....-us-east-2.aws.neon.tech/neondb?sslmode=require
name:   0673-dryrun-20260422-XXXXXX
```

Branch-create should complete in well under 5 minutes (zero-copy). `/tmp/0673-branch-name.txt`
must contain exactly the `name:` value — if it differs, STOP and investigate before Step 4.

### If this fails

- Script exits with "required env var $NEON_PROJECT_ID not set" → `export NEON_PROJECT_ID=...`
  from your vault / `.env` and retry
- `neonctl not found; falling back to Neon REST API` on stderr → expected when neonctl
  isn't installed; confirm `$NEON_API_KEY` is set and retry
- Neon API returns 4xx → check `NEON_API_KEY` validity; confirm project id matches the
  prod project (`neonctl projects list`)
- Branch creation hangs > 5 min → cancel (`Ctrl+C`), inspect `neonctl branches list`
  for the half-created branch and delete it manually before retrying

---

## Step 4 — Cleanup dry-run on the Neon branch

Run the cleanup against the branch (not prod) to confirm the script behaves at full scale.
Dry-run prints what it WOULD do; no mutations are made.

### Command(s)

```bash
cd repositories/anton-abyzov/vskill-platform

# Cleanup uses CREATE TEMP TABLE _0673_survivors (session-scoped) — must
# run against the DIRECT (non-pooled) endpoint so the session persists
# across the script's queries. Pooled/serverless shapes do NOT guarantee
# session affinity.
DATABASE_URL="$BRANCH_DIRECT" \
  npx tsx scripts/migrations/0673-cleanup-submission-dupes.ts --dry-run
```

Then run the real cleanup on the branch:

```bash
DATABASE_URL="$BRANCH_DIRECT" \
  npx tsx scripts/migrations/0673-cleanup-submission-dupes.ts
```

Sanity-check that the temp table survived (if it didn't, the cleanup was a no-op
silently — catch that here, NOT on prod):

```bash
# Expect a non-zero row count. If this returns 0 rows, the session-scoped TEMP
# TABLE did not survive between queries — do NOT proceed to prod.
psql "$BRANCH_DIRECT" -c "SELECT COUNT(*) FROM _0673_survivors;" 2>&1 \
  | head -5
```

(If `_0673_survivors` is dropped at the end of the script's session, the psql
probe above will error with "relation does not exist" — that's EXPECTED after
the script completes. The actual guard is the duplicate-pair / total-row
queries below; they will show whether the cleanup actually deleted anything.)

Validate the end state on the branch:

```sql
-- Expect 0
SELECT COUNT(*) FROM (
  SELECT 1 FROM "Submission" GROUP BY "repoUrl", "skillName" HAVING COUNT(*) > 1
) t;

-- Expect ~108,324 (tolerance: 102,907 – 113,740; ±5%)
SELECT COUNT(*) FROM "Submission";
```

### Expected output

- Dry-run log ends with something like
  `dry-run: would delete ~2825767 victims across ~91159 groups`
- Real run log ends with
  `archivedGroupCount: ~91159, deletedVictimCount: ~2825767`
- Duplicate-pair count returns `0`
- Total `Submission` row count within the ±5% tolerance band

### If this fails

- `victim count outside ±5%` → STOP. Read
  `.specweave/increments/0673-submission-dedup-cleanup-at-scale/backups/dedup-summary-0673.json`
  and inspect per-group anomalies BEFORE retrying. Do NOT proceed to prod.
- Script errors on `Neon 64 MB response limit` → bug in the cleanup script's batching; file
  an issue and halt. (ADR-0257 §3.2 is exactly designed to prevent this; seeing it means a
  query regressed.)
- Script SIGTERM / connection drop mid-run → simply re-run the same command; checkpoint
  at `.specweave/.../checkpoints/progress.json` resumes from the last completed batch
  (US-003 AC-US3-02)

---

## Step 5 — Apply the unique-index migration on the Neon branch

Once the branch is clean, confirm `prisma migrate deploy` applies the 0672 index without
P2002 errors. This proves prod will apply cleanly.

### Command(s)

```bash
cd repositories/anton-abyzov/vskill-platform

DATABASE_URL="$BRANCH_DIRECT" \
  npx prisma migrate deploy
```

Verify:

```sql
SELECT indexname, indisunique
FROM pg_indexes i
JOIN pg_index x ON x.indexrelid = (i.schemaname||'.'||i.indexname)::regclass
WHERE tablename = 'Submission'
  AND indexname = 'Submission_repoUrl_skillName_key';
```

### Expected output

- `prisma migrate deploy` → `1 migration found in prisma/migrations` →
  `Applying migration '20260421100000_submission_unique_repo_skill'` → `Done.`
- `pg_indexes` row: `Submission_repoUrl_skillName_key | t`

### If this fails

- `P2002 (unique constraint violation)` during apply → cleanup missed rows. Re-run Step 4
  (cleanup is idempotent; second run deletes 0 if clean). Then retry Step 5.
- `Migration already applied` / nothing to do → branch inherited apply state from prod; not
  a problem if the pg_indexes check confirms the index exists. If the migrations table says
  "rolled back", run `npx prisma migrate resolve --applied
  20260421100000_submission_unique_repo_skill` and retry.
- Any other error → halt and debug against the branch (prod is still untouched).

---

## Step 6 — Prod cleanup

Run the cleanup against production. Expected wall-time 45–90 min. The script is resumable
(checkpoint at `checkpoints/progress.json`) — if the terminal dies, re-run the same
command and it picks up where it stopped.

### Command(s)

```bash
cd repositories/anton-abyzov/vskill-platform

# Pre-flight: confirm quiescence (48h write-free window)
psql "$PROD_URL" -c "SELECT COUNT(*) FROM \"Submission\" \
                     WHERE \"createdAt\" > NOW() - INTERVAL '48 hours';"
# Must return 0 — if non-zero, STOP and investigate the write source.

# Run the cleanup against the DIRECT (non-pooled) prod endpoint. CREATE TEMP TABLE
# _0673_survivors is session-scoped; the pooled hostname (pgbouncer) cannot guarantee
# session affinity across the script's queries. The --i-understand-this-is-prod
# flag is required when the hostname is recognized as prod — the script enforces
# this against both pooled and direct prod hostnames (AC-US2-05).
DATABASE_URL="$PROD_URL_DIRECT" \
  npx tsx scripts/migrations/0673-cleanup-submission-dupes.ts \
  --i-understand-this-is-prod
```

Monitor progress in a second terminal:

```bash
tail -f .specweave/increments/0673-submission-dedup-cleanup-at-scale/checkpoints/progress.json
```

### Expected output

- Pre-flight quiescence query returns `0`
- Cleanup log shows repeated `batch N: deleted=10000 elapsedMs=...` lines
- Final log: `deletedVictimCount: ~2825767, archivedGroupCount: ~91159, clean=true`
- Summary archive at
  `.specweave/increments/0673-submission-dedup-cleanup-at-scale/backups/dedup-summary-0673.json`
  is under 10 MB (`ls -lh` should show ~9 MB)
- Final `SELECT COUNT(*) FROM "Submission";` in the log is within the ±5% tolerance band

### If this fails

- Pre-flight returns non-zero → STOP. Something is writing to `Submission` again. Find
  the source (likely a re-enabled `/api/v1/admin/rescan-published` or a manual script)
  and stop it BEFORE running the cleanup.
- Script halts mid-run (network drop, terminal closed) → re-run the same command. Per
  AC-US3-02 the checkpoint handles resume; expect `resuming from batch N, lastProcessedId=...`
  in the log.
- Script logs `already clean: 0 batches to process` and exits 0 → cleanup was done
  previously. Skip to Step 7.
- `P2002` mid-run → shouldn't happen (unique index not applied yet). If it does, the
  schema changed unexpectedly — halt and compare `prisma/schema.prisma` vs prod.
- Wall-time exceeds 2 h → acceptable; the script is safe to let run. If you must abort,
  SIGINT is safe (partial-batch transaction rolls back).

---

## Step 7 — Apply unique-index migration on prod

With cleanup complete, apply the 0672 migration on prod.

### Command(s)

Pre-flight the `_prisma_migrations` table (per AC-US5-02 "if this fails"):

```sql
SELECT migration_name, started_at, finished_at, rolled_back_at, applied_steps_count
FROM _prisma_migrations
WHERE migration_name LIKE '%submission_unique%'
ORDER BY started_at DESC
LIMIT 5;
```

Then:

```bash
cd repositories/anton-abyzov/vskill-platform

DATABASE_URL="$PROD_URL" \
  npx prisma migrate deploy
```

Verify:

```sql
SELECT indexname, indisunique
FROM pg_indexes i
JOIN pg_index x ON x.indexrelid = (i.schemaname||'.'||i.indexname)::regclass
WHERE tablename = 'Submission'
  AND indexname = 'Submission_repoUrl_skillName_key';
```

### Expected output

- Migration applies cleanly: `Applying migration
  '20260421100000_submission_unique_repo_skill'` → `Done.`
- `pg_indexes` returns `Submission_repoUrl_skillName_key | t`
- No P2002 errors emitted during apply (this is the implicit test of cleanup completeness)

### If this fails

- `P2002` during apply → cleanup was incomplete. Re-run Step 6 (idempotent). Duplicate-
  pair count query must return 0 BEFORE retrying Step 7.
- `_prisma_migrations` shows the migration as "rolled back" → resolve before applying:
  `npx prisma migrate resolve --rolled-back 20260421100000_submission_unique_repo_skill`
  (or `--applied` if `indisunique=true` already). Then retry `migrate deploy`.
- Migration "already in non-recoverable failed state" → the apply has poisoned the
  history; escalate — do NOT use `migrate reset` against prod.

---

## Step 8 — Deploy 0672 code (Cloudflare Workers)

Deploy the 0672 code (`upsertSubmission` + cache warm-up) that has been sitting on
`main` (commit `5b92a50`) waiting for the schema to catch up.

### Command(s)

```bash
cd repositories/anton-abyzov/vskill-platform

# push-deploy.sh wraps `wrangler deploy` with the project's conventions
./scripts/push-deploy.sh
```

### Expected output

- Wrangler build succeeds
- Deploy completes: `Published vskill-platform (X.XX sec)` →
  `https://...workers.dev` URL printed
- Within ~1 h the hourly queue-list warmup cron log shows `wrote=5 failed=0`
  (check via Cloudflare dashboard → Workers → Logs, or `wrangler tail`)

### If this fails

- Wrangler auth error → `wrangler login`
- Build fails TypeScript errors → inspect CI; do NOT deploy around the errors
- `wrote=5 failed=0` never appears within 1 h → tail the worker:
  `wrangler tail vskill-platform --format json | grep queue-list-warmup`; investigate
  KV or Neon connectivity issues in the cron path

---

## Step 9 — Smoke tests

Run the Playwright E2E suite against the deployed preview URL, plus a manual spot-check.

### Command(s)

```bash
cd repositories/anton-abyzov/vskill-platform

# Automated E2E smokes (both specs shipped with 0672)
npx playwright test \
  tests/e2e/queue-duplicates.spec.ts \
  tests/e2e/queue-cold-load.spec.ts

# Manual spot-checks — open in browser
echo "visit https://verified-skill.com/queue          (expect non-empty list, fast render)"
echo "visit https://verified-skill.com/queue?q=d      (expect exactly 1 obsidian-brain row)"
```

### Expected output

- Both Playwright specs pass (green)
- `/queue` first-load renders within 1.5 s (AC-US1-04)
- `/queue?q=d` shows exactly one row for `obsidian-brain` under `anton-abyzov/vskill`
- No duplicate rows visible to the eye on `/queue`

### If this fails

- Playwright fails on `queue-duplicates.spec.ts` → duplicates still visible; confirm the
  unique index actually applied via the Step 7 pg_indexes check; if it did, the cache may
  be stale — wait for the hourly warm-up or force a refresh via the admin endpoint
- Playwright fails on `queue-cold-load.spec.ts` → cold-load p95 regression; inspect CF
  logs for slow Neon queries; not a rollback trigger — investigate independently
- `/queue` is empty → the cache warm-up hasn't run yet. Wait up to 1 h, then re-check.

---

## Step 10 — 24 h monitoring + increment closure

Confirm the cleanup is stable over a full day before closing 0672 and 0673.

### Command(s)

Every ~6 h for 24 h:

```sql
-- Must stay at 0 for the entire window
SELECT COUNT(*) FROM "Submission" s
JOIN "Submission" s2
  ON s."repoUrl" = s2."repoUrl"
 AND s."skillName" = s2."skillName"
 AND s.id != s2.id;
```

```bash
# Confirm no P2002 errors leaking into Cloudflare logs
wrangler tail vskill-platform --format json | grep -i 'P2002\|unique.*constraint' | head
```

After 24 h of clean monitoring:

```bash
# Delete the dry-run Neon branch (Step 3 created it — it's no longer needed)
NEON_PROJECT_ID="$NEON_PROJECT_ID" \
  bash .specweave/increments/0673-submission-dedup-cleanup-at-scale/scripts/delete-neon-branch.sh \
  "$(cat /tmp/0673-branch-name.txt)"

# Close both increments
specweave complete 0672-queue-reliability
specweave complete 0673-submission-dedup-cleanup-at-scale
```

### Expected output

- Duplicate-pair query returns `0` every check for 24 h
- Zero P2002 log lines in CF tail
- `delete-neon-branch.sh` prints `deleted 0673-dryrun-...`
- Both `specweave complete` invocations print `increment closed` and update
  `metadata.json.status = "completed"`

### If this fails

- Duplicate-pair query returns non-zero at any point → STOP. A write path re-emerged.
  Check Cloudflare logs for `rescan-published` traffic and any other `Submission.create`
  call sites. Investigate before closing the increment. The unique index will prevent
  duplicates via P2002, but the leak source still needs fixing.
- P2002 log lines appear → expected ONLY from `rescan-published` in-flight races that are
  caught by `skipDuplicates: true` — verify by grepping the caller. Anything else is a
  regression.
- `delete-neon-branch.sh` fails → retry; or delete manually via `neonctl branches delete`
  or the Neon console. NOT blocking for closure if monitoring is clean.

---

## Rollback

Three scenarios, ordered by tier (cheapest first).

### Tier 1 — during Steps 3–5 (Neon branch only, prod untouched)

```bash
NEON_PROJECT_ID="$NEON_PROJECT_ID" \
  bash .specweave/increments/0673-submission-dedup-cleanup-at-scale/scripts/delete-neon-branch.sh \
  "$(cat /tmp/0673-branch-name.txt)"
```

Zero prod impact — the branch is a zero-copy, so deleting it reclaims no meaningful
storage and erases no production data. Restart at Step 3 with a fresh branch.

### Tier 2 — cleanup partial on prod (Step 6 halted mid-way)

Do nothing destructive. The cleanup is forward-only, transactional per batch, and
resumable. Two valid resolutions:

1. **Resume** (preferred): re-run the exact same Step 6 command. Checkpoint at
   `.specweave/.../checkpoints/progress.json` makes this idempotent — already-processed
   victim IDs are skipped.
2. **Abandon and leave partial**: the DB is internally consistent (every surviving
   Submission still has its state events; no dangling FKs). You can decide later whether
   to resume or whether to take a different approach. No restore needed because the
   summary archive is not a restore artifact — it's audit metadata.

### Tier 3 — cleanup complete on prod but unique-index apply fails (Step 7 errors)

Re-run Step 6 (cleanup is idempotent — 0 deletes on an already-clean table). Then retry
Step 7. If `_prisma_migrations` is in a "rolled back" state, use `prisma migrate resolve`
first (see Step 7 "If this fails").

### Tier 4 — disaster (data loss suspected, 24 h window)

The Neon branch created in Step 3 IS the authoritative rollback path for 24 h (Neon's
default branch retention). Do NOT delete it until Step 10 monitoring is fully clean.

If disaster is confirmed:
1. Halt all writes (pause the worker via `wrangler rollback`).
2. Promote the Step-3 branch to the primary via the Neon console (or open a ticket with
   Neon support for a point-in-time recovery — Neon retains 7 days of PITR by default
   even without a named branch).
3. Update DNS / connection strings to point at the restored branch.
4. Open an incident-response increment; abandon 0673 by setting
   `metadata.json.status = "abandoned"`.

---

## Do NOT do this

These four actions are forbidden during the cleanup window. Each has a failure mode that
will undo hours of work.

1. **Do NOT re-enable `/api/v1/admin/rescan-published` during the cleanup window.** It
   is the dormant leak source responsible for 40–50% of the 2.8 M-row disaster. It stays
   operationally disabled until AFTER Step 10 closes. Re-enabling it mid-cleanup would
   race the in-flight delete batches and create fresh duplicates.
2. **Do NOT skip the Neon branch dry-run (Steps 3–5) and jump straight to prod cleanup
   (Step 6).** The branch run is the only chance to catch a regression in the cleanup
   script at full scale without touching prod. "It worked in unit tests" is not a
   substitute; Neon's 64 MB response limit is an integration-level failure mode.
3. **Do NOT run `prisma migrate deploy` BEFORE the cleanup** (Step 7 before Step 6). The
   unique-index apply will fail with P2002 against the 2.8 M duplicates, and depending on
   Prisma's failure mode it may leave the `_prisma_migrations` table in a poisoned state
   that is painful to recover.
4. **Do NOT delete the Step-3 Neon dry-run branch before the Step 10 24-h monitoring
   window completes.** That branch is the disaster-rollback path. Neon PITR retains 7
   days by default, but a named, pinned branch is the fast path. `delete-neon-branch.sh`
   is cheap to rerun — save it for after the 24-h check.

---

## Known warnings (cosmetic, non-blocking)

- Living-docs sync may emit GitHub 404s or API errors during Step 10 closure. These are
  documented as cosmetic per 0657 and 0672. Do NOT re-open the increment over them.
- The summary archive
  (`.specweave/increments/0673-.../backups/dedup-summary-0673.json`) is JSON Lines, not
  a single JSON document. Tools that expect one-document-per-file will choke. Use
  `jq -s` or `python3 -c 'import json; [json.loads(l) for l in open(...)]'` to parse.
- `/api/v1/admin/rescan-published` remains operationally disabled after the deploy. The
  in-flight dedup fix (US-004) only guarantees that IF it is ever re-enabled, it cannot
  re-cause the disaster.

---

## Session hand-off

Update [`HANDOFF.md`](./HANDOFF.md) after each step. The "current state" + "next step"
fields are the authoritative resume point for a new session picking this up cold.
