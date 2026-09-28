# 0874 recovery evidence — 2026-09-28

Draft PR [74](https://github.com/anton-abyzov/vskill-platform/pull/74), head `9792c5236e02b92bcce6a732bee1f1570696c311`, base `e3718ee6ea7dbac3b25a4d2a9a098e3c33d40857`. The branch starts from the rewritten history. Original roots, other owners, credentials and shared handoff pointers were preserved.

T-006, T-007, T-008, T-009 and T-019 are implemented and tested. T-017 remains blocked despite its local failed-sweep guard: VM3 last 06:54 UTC run falsely advertised 7/7 completed with seven 401s, 600 discoveries and 32 submissions. This is not a clean sweep or more than 7,000 proof. Runtime legacy `SHARD_MODE=size-date` normalizes to size-bisect, but `SHARD_BISECT` is absent, so adaptive expansion is disabled. Credential-owner repair and explicit adaptive-bisection configuration require separate lead handling; no secrets or live state were changed.

The deployed owner packet identifies Compose service `crawl-worker`, container `scanner-worker-crawl-worker-1`, `/opt/scanner-worker/docker-compose.yml`, and `GITHUB_TOKENS` loaded from `/opt/scanner-worker/.env`; key also exists in `/opt/crawl-worker/.env`. The local provisioning source is `crawl-worker/.env.vm3` according to deploy.sh. Values were never printed. Separate successful local live API guard used the audit gh identity and does not validate the deployed token.

Node 22 affected platform suite: 244 passed / 29 files. Complete crawler: 208 passed / 1 explicit no-token skip. Separate real API dimension guard: 1 passed (all 4 queries). Dedup/migration suite: 294 passed / 1 DB-fixture skip. Full TypeScript check remains red at 314 diagnostics on both base and branch, zero added diagnostics after normalization.

Independent lead review resolved two findings: identity deferral now preserves full intake provenance and the existing retry budget; failed-shard checkpoints now replay unaccepted discoveries after exhausted bulk retries. Review approved exact head with no critical/high findings. CI and lead merge decision remain separate. Deploy intake producer and queue consumer together after approval; this packet performs no merge/deploy.

See manifest.json for task mapping and SHA-256 receipts. Source-failure red/green evidence retains the earlier six-test subset; the full crawler receipt includes the final seventh regression.
