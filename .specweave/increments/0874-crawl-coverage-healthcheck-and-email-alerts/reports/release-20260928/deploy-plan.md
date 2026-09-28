# 0874 guarded delivery plan

Reviewed source: `9f2b9795faaea5350c99639ce3c60d1764d678cb`, PR 74. Root owns merge and final deployment approval. Required current-head CI must be green; re-read active owners and remote main immediately before applying anything. Do not run the broad deployment helpers: `scripts/push-deploy.sh` replays migrations and `scanner-worker/deploy.sh <single-IP>` misindexes VM overrides and restarts both services.

## Authoritative prestate

- Repository: `anton-abyzov/vskill-platform`; remote main `e3718ee6ea7dbac3b25a4d2a9a098e3c33d40857` before this release. After merge record the actual merge SHA and verify its tree contains the reviewed PR tree.
- Cloudflare Worker: `verified-skill-com`, production version `42eade92-cc55-43de-944f-f76321b3bc18`, deployment timestamp `2026-09-26T03:14:03.203Z`. Read back immediately before deploying; stop if another owner changed it.
- VM3: `5.161.56.136`, compose project `/opt/scanner-worker/docker-compose.yml`, service `crawl-worker`, container `scanner-worker-crawl-worker-1`, ID `f92748edbe5c6f4a615347b6fceed52e4273d447e64eede83a1ce4d4d5c74b07`, image `sha256:30ab3d044ff029b283144a1fae6540a267ca606d44165bfd0752e2fbed04f99a`.
- Runtime sources remain `github-sharded,skills-sh,submission-scanner`. Named volume `scanner-worker_crawl-state` is mounted at `/tmp/crawl-state`. No github-sharded checkpoint existed at 16:44Z; inspect again, preserve all state.
- The reviewed credential repair applied at 16:34:54Z, without restart. Only `GITHUB_TOKENS` changed, retaining existing valid entry1; no rotation, new credential, or personal CLI token. Both file readbacks matched; secure rollback copies are under `/root/vskill-release-backups/0874-20260928T163454Z`.
- Current env hashes: scanner `.env` `94a681b1f67f786a39d20fbce9c41c492c1c9a3b85cb25f891e61d5ca076055e`; crawler `.env` `8d7f11b89c1f3a9ef67abb417d8603b32076966711199ef167b838ec7c5f28d7`. The running container still has its old two-entry pool until recreation.

## Platform first

1. Build the approved merged source in its isolated checkout with Node22 and locked dependencies. Never set `E2E_BYPASS`, the fixture JWT, or the disposable DATABASE_URL for the Worker build/deploy. Already verified: production Next build, `npm run build:worker`, `node scripts/verify-queue-health-build.mjs`.
2. Record SHA256 of `.open-next/worker-with-queues.js` and git source/tree identities. The one Worker bundle contains the matching `bulk_intake_retry` producer and consumer; do not deploy one half independently.
3. Recheck Cloudflare production version and active owners, then root-approved `npx wrangler deploy`. No `prisma migrate`/`db push`: 0861 migration readback already proved the production schema is applied.
4. Save deploy output/version, confirm 100% deployment points to that version, run `node scripts/verify-queue-health-deploy.mjs`, and probe real public endpoints plus denied private URLs without credentials. Preserve health/API receipts; a homepage 200 alone is insufficient.

## VM3 crawler only

1. Package **tracked** `crawl-worker/` source at the approved merge SHA via `git archive`. Untracked `.env` files must never enter the Docker build context (`COPY . .` is broad). Extract into a new owned directory under `/opt/crawl-worker-releases/<sha>`. Do not overwrite a dirty source directory or scanner source.
2. Build image `vskill-crawl-worker:<sha>` with OCI revision/source labels from this secret-free context. Save build digest, image ID, and in-image SHA256 hashes of server, scheduler, sources/github-sharded.js and lib/inline-submitter.js. Tag the current image under a rollback-specific tag before changing the compose service image tag.
3. Initial reviewed release retains adaptive expansion OFF (current SHARD_BISECT absent/false). Do not set SHARD_BISECT=1 until the separate resumable expansion task passes review and tests. SHARD_MODE=size-date is normalized by existing code to size-bisect, but this initial run uses the seven coarse roots; label it explicitly. Retain the reviewed valid token repair unchanged.
4. Recheck container/image/compose/env identities and both `/status.activeCrawls` and scheduler source statuses. Avoid interrupting an active source: schedule the bounded recreation in an idle window. Never delete a checkpoint or reset a crawl to manufacture completion.
5. Tag the reviewed new image to the existing compose-generated `scanner-worker-crawl-worker` image name, then `docker compose up -d --no-deps --no-build --force-recreate crawl-worker` from `/opt/scanner-worker`. This acts on only the owned crawler service; never `compose down` or restart scanner/VM1/VM2.
6. Read back new container ID/image/revision label, hashes, assigned sources, token count1, unchanged SHARD_MODE and adaptive-off setting, unchanged checkpoint volume and scanner container ID. Run authenticated code-search from the new runtime without printing credentials, confirm /health and heartbeat delivery, then observe scheduler-owned work. Do not start a second manual crawler.

## Valid sweep evidence and duration

Initial runtime recovery requires an honest complete seven-root sweep with authenticated search, zero lost intake and downstream persistence readback. It is not full breadth and does not satisfy AC-US3-06. Full breadth after the follow-on requires a real completed adaptive plan: mode=size-bisect, expanded leaf count and completed count equal, zero lost submissions/auth errors, accurate deferred/accepted/skipped counters, preserved replay after failures, distinct repo+path discovery well above the prior ~7k ceiling, and platform heartbeat/coverage readback. Save metrics before/after and the complete run result. An HTTP healthy response or old `7/7` result is not sweep proof.

A full broad sweep may span hours or days at GitHub's code-search quota. **Current code expands the whole plan before saving a checkpoint**, so a large corpus can exhaust the 120-minute window before expansion becomes resumable. Confirm or repair this before claiming end-to-end completion; do not increase timeouts or clear state as a substitute. Single-byte or max-depth leaves may still exceed the 1,000-result cap; report this limitation rather than claiming exhaustive corpus coverage.

## Rollback

Cloudflare: re-read version first; root may roll back to the recorded prestate version if it is still the immediately preceding owned deployment. Do not overwrite a newer owner's deployment. Queue retry compatibility must be considered before reverting the producer/consumer bundle.

VM3: retain old image and current secure env backups. On a verified regression, compare current owned container and env hashes, restore only the changed configuration keys when their current values still match this release, retag the previous image, and recreate only crawl-worker. Keep the valid token repair; never automatically restore the rejected token. Preserve named checkpoint volume. Any uncertain write/restart requires fresh authoritative readback before retrying.
