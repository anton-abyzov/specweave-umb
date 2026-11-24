# Connect network traffic at scale

## Problem

SpecWithCode Connect works for one user today, but its traffic was never measured or modelled for many users. Measured on October 24-31, 2026 (Cloudflare GraphQL, zone spec-weave.com, Worker `specweavestudiorelay-api-prod-*`):

- The relay served 6,063 requests in 7 days, all real traffic from one account. 632 of them (10%) were `POST /v1/environments/:id/connect` answered `502`: desktop builds retry connecting to two offline machines about every 3 minutes, all day, and each try holds a Worker for up to the 10 s mint timeout.
- `POST /v1/client/environment-link-challenges` plus `environment-links` ran 544 times from a `node` client, in bursts of about 46 an hour: a link loop on a host that is already linked.
- Worker CPU averages about 55 ms per request and nearly every request makes one subrequest. Session JWTs are verified with the Clerk secret key, so each cold isolate fetches JWKS from Clerk's Backend API; CLI OAuth tokens first fail a JWT check and then call the Backend API on every request. Clerk's Backend API is rate limited per instance.
- Scanners probe the relay host (`/.env`, `/.git/config`, about 200 a week); each costs a Worker run.
- Each linked machine owns one Cloudflare Tunnel and one CNAME in the spec-weave.com zone. Cloudflare includes 1,000 tunnels per account, then $4.50 per tunnel a month (Tunnels for Platforms); DNS records per zone are capped by plan. `RELAY_GLOBAL_MANAGED_TUNNEL_CAP=180` is the current guard; idle-tunnel cleanup runs in `dry-run`.

## Scope

In: relay auth without Clerk round trips; client backoff for unreachable machines; stopping the relink loop; a per-user relay rate limit; scanner and rate-limit rules on the Pro zone where credentials allow; a report with the traffic map and the 100 / 1,000 / 10,000 user cost model; relay deploy and app release; live check that the M4, Ministorm and the phone stay connected.

Out: replacing per-machine Cloudflare Tunnels with a Durable Object WebSocket relay (a design change with its own cost trade-off; recommended in the report, needs the user's decision); anything with a new recurring cost; Argo (Connect app traffic rides tunnels, Argo bills per GB and gives no measured gain here).

## Acceptance Criteria

- [ ] AC-01: With `CLERK_JWT_KEY` set, a Clerk session JWT verifies with no Backend API call; a key rotation falls back to remote JWKS; `oat_` OAuth tokens skip the JWT attempt and a verified OAuth token is reused for 60 s per isolate, rejected ones are never cached.
- [ ] AC-02: A client that gets `environment_endpoint_unavailable` or `environment_endpoint_timed_out` from `/connect` backs off exponentially with jitter (capped at 5 minutes) per environment instead of retrying on a fixed short interval, and resets on success or a status change to online.
- [ ] AC-03: A host that is already linked does not create new link challenges or links in a loop; link attempts back off on failure.
- [ ] AC-04: The Pro zone blocks scanner paths on the relay host and rate-limits the relay API per IP (webhooks excluded), added by ref without replacing other zone rules. (An in-Worker limiter was rejected: the HttpApi contract would need a new 429 error on every endpoint, and the edge rule stops the request before it costs a Worker run.)
- [ ] AC-05: The report at `.specweave/increments/1153-connect-network-traffic-at-scale/reports/connect-traffic-at-scale.md` has the traffic map, measured numbers, the scale and cost table and the changes made.
- [ ] AC-06: The relay is deployed, existing sessions survive the deploy, the app is released, and the M4, Ministorm and the phone stay connected afterwards.

## Approach

Relay: `infra/relay/src/http/Api.ts` (pinned-key verification, OAuth cache, rate limit), `src/worker.ts` and `src/Config.ts` (`CLERK_JWT_KEY`, limiter binding), `.github/workflows/deploy-relay.yml` (pass the variable). The Clerk JWT public key is public; it goes in the `production` environment variables.

Clients: the connect retry loop and the link loop found by the client audit (see Tasks for files).

Edge: WAF custom rule for scanner paths and a Pro rate-limiting rule on `relay.spec-weave.com`, applied only if an API token or dashboard session with Zone WAF permission is available. The existing zone rules (scripted-POST block) must be preserved, so the rules are added, never managed as a whole entrypoint ruleset from IaC.

Risks: a relay deploy replaces the Worker, not tunnels; DPoP access tokens and environment sessions are stateless or in D1 and survive. Verify with `/health`, a live connect from the M4 and the phone after deploy.

## Decisions

### Asked
- none
### Defaulted (change any before sw-do)
- D-01 Per-tunnel architecture stays for this increment; DO WebSocket relay is a report recommendation only (reversible).
- D-02 OAuth verification cache TTL 60 s (revocation delay bound).
- D-03 Argo not enabled (no measured benefit, new per-GB cost).
### Open
- none

## Tasks

### T-01 Verify Clerk tokens without Backend API round trips
- AC: AC-01 | Files: infra/relay/src/http/Api.ts, infra/relay/src/Config.ts, infra/relay/src/worker.ts, infra/relay/src/http/Api.test.ts, .github/workflows/deploy-relay.yml, infra/relay/.env.example | Test: cd infra/relay && npx vp test run --config ../../vite.config.ts --dir . src/http/Api.test.ts

### T-02 Back off connect retries to unreachable machines
- AC: AC-02 | Files: packages/client-runtime/src/connection/supervisor.ts, packages/client-runtime/src/connection/supervisor.test.ts, apps/web/src/cloud/managedAuth.tsx | Test: cd packages/client-runtime && npx vp test run src/connection/supervisor.test.ts

### T-03 Stop the relink loop on linked hosts
- AC: AC-03 | Files: apps/server/src/server.ts, apps/server/src/cloud/CloudLink.ts, apps/server/src/cloud/CloudLink.storedLinkRuntime.test.ts | Test: cd apps/server && npx vp test run src/cloud/CloudLink.storedLinkRuntime.test.ts src/cloud/CloudLink.test.ts

### T-04 Relay rate limit and scanner block at the Pro edge
- AC: AC-04 | Files: infra/relay/scripts/edge-rules.mjs, .github/workflows/relay-edge-rules.yml | Test: gh workflow run relay-edge-rules.yml, then a scanner path on relay.spec-weave.com returns 403

### T-05 Report with traffic map and scale model
- AC: AC-05 | Files: .specweave/increments/1153-connect-network-traffic-at-scale/reports/connect-traffic-at-scale.md | Test: file exists with the three sections

### T-06 Deploy relay, release app, live connection check
- AC: AC-06 | Files: none | Test: curl https://relay.spec-weave.com/health and a live connect from M4, Ministorm and phone

### T-07 Verify and close 1153
- AC: AC-01, AC-02, AC-03, AC-04, AC-05, AC-06 | Files: none | Test: specweave verify 1153-connect-network-traffic-at-scale
