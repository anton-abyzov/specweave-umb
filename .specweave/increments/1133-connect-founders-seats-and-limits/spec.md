# Connect founders seats and limits

## Problem

Connect allows 3 managed tunnels per account through a hard-coded constant (`infra/relay/src/environments/ManagedTunnelLimits.ts:18`), changed only by hand-inserted D1 rows. Anton approved a "Founding 1,000" promo on 2026-10-28: the first 1,000 Connect accounts get 10 machines, everyone else keeps 3, and total spend stays capped. The relay has no account record, no signup order, no global counter and no kill switch. The capacity check and the allocation insert are separate (`ManagedEndpointProvider.ts:1023` then `ManagedEndpointAllocations.ts:273`), so concurrent links can exceed any cap. spec-weave.com is a Free Cloudflare zone with a 200 DNS-record cap (16 used): each linked machine is one record, so linking fails opaquely at about 184 machines. Analysis: https://claude.ai/artifact/Eq6W6y8hKqUEpkpAPLruuY

## Scope

In: relay D1 tables and migration for Connect accounts and the founders promo; atomic founder grant on first managed link; limit lookup (override, founder, configurable free default); race-free capacity check folded into the allocation insert; a global managed-machine cap from config; kill switch; a public founders counter endpoint; distinct error reasons and the register/recover error mapping fix; client copy for the reasons. Out: billing/paid plans, the website copy (done in the violet branch), Cloudflare plan or zone changes.

## Acceptance Criteria

- [ ] AC-01: The first managed link of a new account creates a Connect account row; while seats remain and grants are open, it receives the next founder number, atomically, and two concurrent first links can never exceed the seat cap or share a number.
- [ ] AC-02: The machine limit resolves as manual override, else the promo's founder limit (10) for founders, else `RELAY_CONNECT_FREE_TUNNEL_LIMIT` (default 3).
- [ ] AC-03: Concurrent links for different machines of one account can never exceed the account's limit; re-linking an already allocated machine still succeeds at the limit.
- [ ] AC-04: When `RELAY_GLOBAL_MANAGED_TUNNEL_CAP` is set, new machine allocations stop at that total across all accounts, already allocated machines keep working, and the error carries reason `service_capacity`; account-limit errors carry `account_limit`.
- [ ] AC-05: Setting the promo's grants to closed stops new founder numbers without changing existing founders; deleting an account removes its Connect account row and never returns its seat.
- [ ] AC-06: `GET /v1/public/founders` (no auth) returns seat cap, seats granted, seats left and whether grants are open.
- [ ] AC-07: Register-tunnel and recover-tunnel return the same 403 limit error as link instead of `upstream_unavailable`, and client copy distinguishes account limit from service capacity.
- [ ] AC-08: The relay typechecks and its full test suite passes; the migration applies to an empty D1 and to the baseline schema.

## Approach

Files: new migration `infra/relay/migrations/d1/<ts>_connect_founders/` (+ snapshot), `persistence/schema.ts` (`relay_connect_accounts`, `relay_connect_promos` seeded `founders`, cap 1000, founder limit 10, open), new `environments/ConnectAccounts.ts` (D1 `batch` of conditional writes; no read-then-write), `ManagedTunnelLimits.ts` (resolve only), `ManagedEndpointAllocations.ts` `reserve` (conditional `INSERT ... SELECT ... WHERE count < limit AND global count < cap`, empty RETURNING with no existing row = exceeded), `ManagedEndpointProvider.ts`, `EnvironmentLinker.ts`, `Config.ts`/`worker.ts`, `http/Api.ts`, `account/AccountDeletion.ts`, `packages/contracts/src/relay.ts` (optional `reason`), `packages/client-runtime/src/relay/errorPresentation.ts`, `apps/server/src/cloud/relayResponse.ts`.

Global cap counts allocations whose link is live (each is one DNS record and at most one tunnel), so it also guards the DNS-record cap: set it to 180 on prod until the zone moves to Pro, then 1500. Rejected: Clerk metadata as source of truth (extra API calls, no atomicity); counting live tunnels only (lets DNS records exceed the zone cap).

## Decisions

### Asked
- D-01 Promo shape → Founding 1,000, 10 machines, free default 3, global cap ~$2,250/mo (Anton, "yes, do this", 2026-10-28)
### Defaulted (change any before sw-do)
- D-02 "First N" means first N accounts to link a managed machine, not first N signups.
- D-03 Prod global cap 180 until the tunnel zone is on Pro, then 1500.
### Open
- none

## Tasks

### T-01 Connect accounts, founder grant and limit resolution
- AC: AC-01, AC-02, AC-05 | Files: infra/relay/migrations/d1, infra/relay/src/persistence/schema.ts, infra/relay/src/environments/ConnectAccounts.ts, infra/relay/src/environments/ConnectAccounts.test.ts, infra/relay/src/environments/ManagedTunnelLimits.ts, infra/relay/src/environments/ManagedTunnelLimits.test.ts, infra/relay/src/environments/EnvironmentLinker.ts, infra/relay/src/account/AccountDeletion.ts, infra/relay/src/Config.ts, infra/relay/src/worker.ts | Test: cd infra/relay && npx vp test run --config ../../vite.config.ts --dir . src/environments

### T-02 Race-free account and global caps
- AC: AC-03, AC-04 | Files: infra/relay/src/environments/ManagedEndpointAllocations.ts, infra/relay/src/environments/ManagedEndpointAllocations.test.ts, infra/relay/src/environments/ManagedEndpointProvider.ts, infra/relay/src/environments/ManagedEndpointProvider.test.ts | Test: cd infra/relay && npx vp test run --config ../../vite.config.ts --dir . src/environments

### T-03 Public counter, error reasons and client copy
- AC: AC-06, AC-07 | Files: infra/relay/src/http/Api.ts, packages/contracts/src/relay.ts, packages/client-runtime/src/relay/errorPresentation.ts, apps/server/src/cloud/relayResponse.ts | Test: cd infra/relay && npx vp test run --config ../../vite.config.ts --dir .

### T-04 Verify and close 1133
- AC: AC-08 | Files: none | Test: cd infra/relay && npx tsc --noEmit && npx vp test run --config ../../vite.config.ts --dir .
