# 0932 crawler rollout

PASS. October 21, 2026. All three Hetzner crawlers run the reviewed submission-scanner change from PR 176, merge `8df21dfec72137e61763361d0de3197d9b3aadf4`. The parent confirmed Cloudflare production version `cd550753-3cb9-4306-beba-3d347569f8d6` and successful release gates before any crawler restart.

## Runtime readbacks

| VM | Host | Docker health | Scheduler/source count | New crawler container |
|---|---|---|---|---|
| vm3 | 5.161.56.136 | healthy | running / 3 | `c64b8415910040accc76604fb4b9a7927ed9abc8e0bcde8c0b62072d4c42045b` |
| vm2 | 91.107.239.24 | healthy | running / 5 | `69465be19fe2bbd888ed42fbc38c8e3e4f5e7350a6b840e071422cf7580d2fc8` |
| vm1 | 5.161.69.232 | healthy | running / 2 | `0ffb0143ce38ad2d4ec5391db3f174307dc97aaa5be9ec3ffed393f1597e93a7` |

Every running `/app/sources/submission-scanner.js` has SHA-256 `840f92d148e806ed99e9af27869c1df203c8337e074360f62b4ebde019aaaa4c`. The merged GitHub blob and local source were compared before preparation. Host source code matched the previous running images on all three hosts; after copying only `/opt/crawl-worker/sources/submission-scanner.js`, each built image matched the prepared host source tree.

The rollout order was VM3, VM2, VM1. Each host was healthy and idle immediately before `docker compose up -d --no-deps crawl-worker` from `/opt/scanner-worker`. Each new container passed its Docker health check and HTTP health/scheduler readback before the next host was changed.

## Preserved state and rollback

All main scanner container IDs, images, start times, runtime environment hashes, and mounts remained unchanged. Crawler runtime environment hashes, `/opt/scanner-worker/.env`, `/opt/crawl-worker/.env`, `/opt/scanner-worker/docker-compose.yml`, configured sources, persistent state volumes, and read-only GitHub App secret mounts were preserved. No secrets were printed or changed.

The state volume on every host remains `/var/lib/docker/volumes/scanner-worker_crawl-state/_data`, mounted at `/tmp/crawl-state`. No checkpoint was copied, deleted, reset, or rewritten by deployment tooling. Active schedulers naturally changed checkpoint/cache digests on VM2/VM3. VM3 added a new active-sweep file; its retained `/var/lib/docker/volumes/scanner-worker_crawl-state/_data/github-sharded-last-completed.json` still had its October 15, 2026 modification time. VM1 had zero checkpoint files before and after. Therefore the receipts assert preserved volume identity, not frozen checkpoint bytes during resumed processing.

Rollback source files and image tags were verified against each prior running version before image build:

- vm3 on `5.161.56.136`: `/root/0932-crawler-rollout-20261021/vm3/submission-scanner.js`, Docker tag `scanner-worker-crawl-worker:0932-rollback-20261021-vm3`, image `sha256:26017cd40fcb77873959c61fb3b72e3e9bd0b89cff81d32994e14e4d7ffa3265`.
- vm2 on `91.107.239.24`: `/root/0932-crawler-rollout-20261021/vm2/submission-scanner.js`, Docker tag `scanner-worker-crawl-worker:0932-rollback-20261021-vm2`, image `sha256:49499be2bd187aab23988823369860e6f0f64ebbce5cbf22e25a8c9912b93d7e`.
- vm1 on `5.161.69.232`: `/root/0932-crawler-rollout-20261021/vm1/submission-scanner.js`, Docker tag `scanner-worker-crawl-worker:0932-rollback-20261021-vm1`, image `sha256:78f3ad5f3cf3b7b9cbd2353cdc98ac32e56a0fdaa48b5ec480eb206453938a74`.

## Evidence

- [/Users/antonabyzov/Projects/github/specweave-umb/.specweave/increments/0932-vskill-publish-pin-and-search-loop/reports/crawler-rollout-20261021.json](/Users/antonabyzov/Projects/github/specweave-umb/.specweave/increments/0932-vskill-publish-pin-and-search-loop/reports/crawler-rollout-20261021.json)
- [/Users/antonabyzov/Projects/github/specweave-umb/.specweave/increments/0932-vskill-publish-pin-and-search-loop/reports/crawler-preparation-baseline-20261021.json](/Users/antonabyzov/Projects/github/specweave-umb/.specweave/increments/0932-vskill-publish-pin-and-search-loop/reports/crawler-preparation-baseline-20261021.json)
- [/Users/antonabyzov/Projects/github/specweave-umb/.specweave/increments/0932-vskill-publish-pin-and-search-loop/reports/crawler-prepared-20261021.json](/Users/antonabyzov/Projects/github/specweave-umb/.specweave/increments/0932-vskill-publish-pin-and-search-loop/reports/crawler-prepared-20261021.json)
- [/Users/antonabyzov/Projects/github/specweave-umb/.specweave/increments/0932-vskill-publish-pin-and-search-loop/reports/crawler-rollout-vm3-20261021.json](/Users/antonabyzov/Projects/github/specweave-umb/.specweave/increments/0932-vskill-publish-pin-and-search-loop/reports/crawler-rollout-vm3-20261021.json)
- [/Users/antonabyzov/Projects/github/specweave-umb/.specweave/increments/0932-vskill-publish-pin-and-search-loop/reports/crawler-rollout-vm2-20261021.json](/Users/antonabyzov/Projects/github/specweave-umb/.specweave/increments/0932-vskill-publish-pin-and-search-loop/reports/crawler-rollout-vm2-20261021.json)
- [/Users/antonabyzov/Projects/github/specweave-umb/.specweave/increments/0932-vskill-publish-pin-and-search-loop/reports/crawler-rollout-vm1-20261021.json](/Users/antonabyzov/Projects/github/specweave-umb/.specweave/increments/0932-vskill-publish-pin-and-search-loop/reports/crawler-rollout-vm1-20261021.json)

Live registry publication and restored version content remain the parent task. No product source commit, platform deploy, registry write, credential change, main scanner restart, or GitHub PR mutation was performed by this rollout worker.
