# PR74 deployed source and runtime readback

Approved PR head `9f2b9795faaea5350c99639ce3c60d1764d678cb` merged as `a066df378c8f42ef6e5515d906d7feb996c2d475` at 2026-09-28 16:56:51 UTC. Trees match (`321fed9e30f8be76ef9c3da5889673417494efeb`). All six current-head CI checks passed before root merged.

## Cloudflare

Worker `verified-skill-com` is live at 100% on version `d69cd63d-224c-4b37-b1c3-88aa11906a58` since 17:02:44 UTC. Bundle upload succeeded, but Wrangler exited1 while redundantly reconciling the existing scan-normal consumer (Cloudflare generic10013). No blind retry or rollback was attempted. Authoritative readback proved all six queues retain the correct Worker, active delivery, exact configured consumer settings and DLQs. Root reviewed this readback and approved continuing.

Public curl checks: production harness and rewritten test harness health URLs404; private-shaped route404; catalog307 to /skills; real skills page200; API returned two actual records; queue-health schema2 returned200. The internal dry-run queue-health verifier also passed. A read-only production query found an actual existing private skill row; its anonymous URL returned404. Only a hash of that private URL is retained. No production fixture was seeded or reset.

Build environment explicitly removed E2E_BYPASS, JWT_SECRET, DATABASE_URL and ENABLE_PRIVATE_REPOS; this isolated checkout had no local env files. The deployed build used host Node26 after a shell PATH reset. Prior reviewed full tests/build used22, and an additional explicit Node22.20.0 build plus queue-health build verification passed after deployment. The Node22 generated artifacts differ, so the deployed bundle is NOT claimed to be the Node22 artifact. The full deployed artifact hash manifest is preserved. The unchanged entrypoint hash is `e352f941f51a59119e9cdf1739eb4a3b0b910406d072b516c6e0374fecac9147`.

## VM3

At 17:08:38 UTC, only crawl-worker was recreated, after fresh exact container/image/env/compose and manual/scheduler idle checks. New container `6b4993745009807c3ac61bd3a8b6d8f2775da9d29c55137d87183775cd2d694a` runs image `sha256:52ff7bbdd69eeb895bd34f16c501aad3d898ba5546fa0ddee4e3c5c574e31d14`, with OCI revision a066df37. Four in-container source hashes match git. The tracked-only build context excluded even .env.example.

The main scanner remains `2633c121f4f10ed37a6a23f0b7b762a228ab6bd3d12d2a149c30f2b79e8919ff`. The named checkpoint volume was preserved. Sources remain github-sharded, skills-sh and submission-scanner; SHARD_MODE remains size-date (normalized in source to size-bisect), adaptive expansion remains OFF. The already approved token-pool repair took effect: one existing valid token, code-search200 before recreation, runtime user-auth200 after recreation. No token was rotated, revoked, newly created, printed, or copied into artifacts. Platform KV received a fresh healthy heartbeat.

The scheduler started its own seven-root sweep. At this checkpoint it is still running, so neither seven-root completion nor full corpus coverage is claimed. T017 remains open. Existing Tier2 LLM failures can fall back to Tier1-only publication by unchanged explicit product policy; publication counts do not prove successful Tier2 analysis.

Production READ ONLY readback at17:11:44 UTC found three newly fully-keyed submissions (two published), and28 new public skills since restart. These are fleet-wide counts, not attribution of every record to VM3. No migration was rerun.
