# Connect devices behind one address do not lock each other out

## Problem

Found while measuring Connect traffic (increment 1153, October 31, 2026). Over the M4's tunnel `prod-1eb2a6d08a9bea51.spec-weave.com`, from 06:00 to 08:10 UTC, Ministorm's Linux desktop app made 625 `POST /api/studio-connect/mint-credential`, 636 `GET /.well-known/studio/environment` and 607 `POST /oauth/token` answered 429, plus 235 `GET /api/studio/fleet/remote-workers` answered 401. Each of those runs also costs a relay `POST /v1/environments/:id/connect`, about 250 an hour.

Two defects compound:

1. `apps/server/src/auth/CredentialFailureLimiter.ts:179` keys Connect requests by `cf-connecting-ip`. Every device behind one home or office address shares one budget of 30 failures per 10 minutes. One device that keeps presenting a refused credential blocks token exchange for all of them, the owner's phone on the same Wi-Fi included, for 10 minutes at a time.
2. The web client's authenticated fleet requests (`apps/web/src/studio/fleetRequest.ts:158`, `requestRemoteWorkers`) treat a 401 as a stale token: they discard it and run a full relay connect, mint and token exchange again, then poll again. A 401 that a fresh token cannot fix (missing grant or scope; the M4 shows `needs_grant` for this pairing) becomes a loop, and the client ignores the 429 `retry-after`.

## Scope

In: a limiter key that does not merge distinct clients behind one address once a DPoP key or device id is presented; 401s that a new token cannot fix stop the re-authorization loop; clients honour `retry-after` on 429 from an environment. Out: the relay-side changes of 1153.

## Acceptance Criteria

- [ ] AC-01: Failed credentials from one DPoP key or device behind an address do not block a different device behind the same address.
- [ ] AC-02: A fleet request that gets 401 after one fresh token stops re-authorizing and backs off (5 minutes or more) until the grant changes.
- [ ] AC-03: A client that receives 429 with `retry-after` from an environment waits at least that long before the next token exchange.

## Approach

Limiter key: `cf:<ip>:<dpop-jkt>` when a DPoP proof header is present, otherwise as today. Fleet requests: distinguish `EnvironmentScopeRequiredError` and `EnvironmentOperationForbiddenError` from a stale-token 401 and do not retry those with a new token. Supervisor: map `EnvironmentRateLimitedError` to a transient error carrying `retryAfterMs` and use it as the delay floor.

## Decisions

### Asked
- none
### Defaulted (change any before sw-do)
- D-01 Key by DPoP thumbprint, not device id, because the thumbprint is checked cryptographically.
### Open
- none

## Tasks

### T-01 Limiter key per DPoP key behind one address
- AC: AC-01 | Files: repositories/anton-abyzov/specwithcode-dev/apps/server/src/auth/CredentialFailureLimiter.ts | Test: focused unit test

### T-02 Stop fleet re-authorization loops on unfixable 401
- AC: AC-02 | Files: repositories/anton-abyzov/specwithcode-dev/apps/web/src/studio/fleetRequest.ts, repositories/anton-abyzov/specwithcode-dev/packages/client-runtime/src | Test: focused unit test

### T-03 Honour retry-after on environment 429
- AC: AC-03 | Files: repositories/anton-abyzov/specwithcode-dev/packages/client-runtime/src/connection/errors.ts, repositories/anton-abyzov/specwithcode-dev/packages/client-runtime/src/connection/supervisor.ts | Test: focused unit test

### T-04 Verify and close 1155
- AC: AC-01, AC-02, AC-03 | Files: none | Test: specweave verify 1155-connect-devices-behind-one-address-do-not-lock-each-other-out
