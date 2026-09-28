# PR75 guarded deployment and continuation proof

No apply before root approves the final reviewed source and every required current-head CI check is green. Preserve original roots, the SEO owner, active worktrees, the main scanner, and the named crawler state volume. This plan supersedes the adaptive-OFF portion of the PR74 plan; it adds no migration or credential change.

## Fresh identities and build

VM3 preflight at 18:03:40Z: crawler container 6b4993745009807c3ac61bd3a8b6d8f2775da9d29c55137d87183775cd2d694a, image 52ff7bbdd69eeb895bd34f16c501aad3d898ba5546fa0ddee4e3c5c574e31d14, sourcea066df378c8f42ef6e5515d906d7feb996c2d475. Main scanner 2633c121f4f10ed37a6a23f0b7b762a228ab6bd3d12d2a149c30f2b79e8919ff. Env hashes still scanner 94a681b1f67f786a39d20fbce9c41c492c1c9a3b85cb25f891e61d5ca076055e and crawler 8d7f11b89c1f3a9ef67abb417d8603b32076966711199ef167b838ec7c5f28d7. Compose 3d17aee7fbf5876cb28ad8331e2310b133ba7bcbebba9c1cf3a0f4feb5b7e875. No GitHub checkpoint; one existing valid token; adaptive absent; github-sharded cooldown, submission-scanner active. This is a receipt, not permission to interrupt that active run. Re-read all fields at apply time.

Cloudflare expected initial versiond69cd63d-224c-4b37-b1c3-88aa11906a58; recheck immediately before deploy and stop on another owner's change. Root supplies actual approved merge SHA; verify remote main, local source tree and reviewed PR tree match. Use locked dependencies in the owned checkout.

Use the exact executable `/Users/antonabyzov/.nvm/versions/node/v22.20.0/bin/node`, explicitly exported PATH in the same shell for build and deployment. Record `process.version` and executable path before both commands; abort unlessv22.20.0. Exclude E2E_BYPASS, JWT_SECRET, DATABASE_URL, ENABLE_PRIVATE_REPOS. Build Worker, run verify-queue-health-build, record source/tree and full artifact hashes. Record the generated-counts file hash and actual public values as artifact inputs before restoring only that incidental source drift in this isolated checkout. Never relabel an artifact built by another Node version.

## Worker first

Deploy the reviewed merged Worker bundle containing additive typed terminal policy receipts. Existing status:error/errors fields remain compatible with older crawlers. Save CLI result and authoritative active version/100% deployment plus all six consumer/settings readbacks. A CLI consumer-reconciliation error requires readback before any retry or rollback. Smoke harness health 404, rewritten harness 404, actual anonymous private 404, catalog redirect and populated public skills/queue health. No seed/reset or synthetic production bulk submission.

## Crawler-only image and adaptive enable

Package tracked crawler source only, excluding all .env files including .env.example; record archive hash. Build a new image with immutable merge SHA/source labels in a new release directory, without touching scanner source. Validate in-image source hashes for server, scheduler, github-sharded, adaptive-search-plan, inline-submitter and source-result. Retain the old image/tag.

Before the first env write and again before each subsequent write, require the crawler running/not paused, scheduler running, all sources idle/cooldown, zero manual crawls and no coarse checkpoint; recheck crawler and scanner IDs and that file's exact original bytes. Only add/change SHARD_BISECT to 1 in /opt/scanner-worker/.env (active Compose input) and /opt/crawl-worker/.env (paired source-of-truth copy). Preserve original uid/gid/mode; backups are 0600 in an owned 0700 directory. Flush file and parent directory, emit per-file attempted/replacementCompleted/readback receipts. Partial/uncertain outcomes require fresh readback; never blind retry or overwrite drift. Tokens, assigned sources and SHARD_MODE remain unchanged. No secret values in outputs.

Immediately before promotion/recreation, require zero manual crawls, crawler running and not paused, scheduler running, every source idle/cooldown/continuation-free, the coarse checkpoint absent, unchanged env/compose/image/container identities and the protected scanner ID. If a source is active, wait for its own completion. Preserve scanner-worker_crawl-state. Promote only the crawler image tag and use `docker compose up -d --no-deps --no-build --force-recreate crawl-worker`; no compose down, migration, scanner restart or extra scheduler.

Read back new container/image/revision, in-container source hashes, adaptive 1, token count1, unchanged assigned sources and SHARD_MODE, volume identity and scanner ID. Verify health plus fresh platform heartbeat. Do not spend extra code-search quota solely to re-prove a token already confirmed by the scheduler's successful authenticated search.

## Real continuation and intake evidence

Observe only the source-owned scheduler. Capture the first live sweep ID, schema/config hash, pending probes, validated/completed leaves, phase, counters and public union checksum. After at least one normal budget continuation, confirm the same sweep ID and monotonic progress from the checkpoint; no manual reset or duplicate scheduler. Check status/heartbeat and source counters distinguish partial from complete and show totalRejected separately from legacy item errors. Retain rejection/transient history honestly.

Verify actual bulk intake outcome and read-only downstream submission/skill persistence, using new IDs or exact source identity where available; fleet-wide counts alone are not VM3 attribution. Export only count/saturation/sweep/source/hash metadata from runtime-private 0600 discovery proofs. A complete seven-root result is already retained; new partial adaptive work is not full breadth. Full-breadth acceptance remains open until both queues drain with valid coverage and durable distinct union evidence above the old ceiling. Millions of matches may require days, especially capped byte-size hot spots.

## Schema-compatible rollback

Worker rollback requires exact owned current version and root review; old receipt producer may leave new crawler pages unresolved safely. Before any schema 2 checkpoint exists and while every source is idle, the old crawler image plus the previous adaptive-OFF config can be restored with exact CAS checks. Once schema 2 progress exists, DO NOT launch the old PR74 image over that volume or delete/move the checkpoint. On a confirmed runtime regression, hold only the owned crawler service, preserve its state, and prepare a reviewed compatible fix/rollback reader. Never discard pending discoveries to make an old image start.
