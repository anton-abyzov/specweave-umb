# Chaos rig: relay retries and file-transfer faults

## Problem

Relay faults have shipped as bugs: 10% of relay calls were 502 retries to offline machines (1153), and both concurrent final-chunk retries published the same file (1218); see also 1155 and 1335. Fixes got unit tests, none a recurring run with real network faults. No staging relay exists (`deploy-relay.yml` deploys only `--stage prod`), and `infra/relay` has no local run script; its in-memory D1 is a test stand-in.

Source: `.specweave/reports/threads/2026-11-24-chaos-loop-methodology-and-specwithcode-16f346-d9d984.md`, candidate 3.

## Scope

In: two scratch-home servers, the existing fault TLS proxy from `scripts/studio-limit-handoff/verify.mjs`, and a stub relay endpoint that answers 502, 429 and slow replies on a seeded schedule. Scenarios: two peers offline for an hour (fake clock), three machines reconnecting at once, concurrent final-chunk retries of a file transfer.

Out: measuring the hosted relay's own cost (needs a real staging relay later); Board and ledger lag (1421, 1058), which were worktree and commit gaps, not network faults. This verifies 1153 AC-02 (backoff) and does not replace it.

## Acceptance Criteria

- [ ] AC-01: A stub relay serves the client's relay calls locally and answers 502, 429 (with Retry-After) and slow replies on a seeded schedule; the seed is recorded in the receipt.
- [ ] AC-02: Backoff invariant: against an offline peer, a client's retries are bounded and spaced by backoff (counted per peer over the scenario), and a 429 Retry-After is honoured.
- [ ] AC-03: Exactly-once invariant: under concurrent final-chunk retries and dropped replies, a transferred file is published exactly once on the receiver, with the sender's checksum.
- [ ] AC-04: Three machines reconnecting at once all converge to connected within a bounded time without a retry storm (total calls under a stated cap).
- [ ] AC-05: Same seed replays the same fault schedule and verdict; the rig runs report-only on the nightly chaos job from 1465.

## Approach

Reuse 1465's runner and checker layout. A small Node stub relay implements only the endpoints the client calls (read from the client code, not invented), with a seeded fault table. Two or three scratch servers point their relay base URL at the stub. The checker counts calls per peer from the stub's own log and reads each receiver's transfer state through the server's query path.

Risk: the client may not allow overriding the relay base URL; if not, a test-only environment override is the smallest change and goes through review.

## Decisions

### Asked
- none
### Defaulted (change any before sw-do)
- D-01 Stub relay, not a staging deploy → default; a staging relay is a separate decision about cloud spend.
- D-02 Report-only on the shared nightly chaos job → default (reversible).
### Open
- none

## Tasks

### T-01 Stub relay with seeded faults
- AC: AC-01 | Files: repositories/anton-abyzov/specwithcode/scripts/studio-chaos/relay-rig/stub-relay.mjs | Test: node --test repositories/anton-abyzov/specwithcode/scripts/studio-chaos/relay-rig/stub-relay.test.mjs

### T-02 Scenario runner with two or three scratch servers
- AC: AC-02, AC-03, AC-04 | Files: repositories/anton-abyzov/specwithcode/scripts/studio-chaos/relay-rig/run.mjs | Test: node repositories/anton-abyzov/specwithcode/scripts/studio-chaos/relay-rig/run.mjs --seed 1 --scenario offline-peer

### T-03 Backoff and exactly-once checker
- AC: AC-02, AC-03, AC-05 | Files: repositories/anton-abyzov/specwithcode/scripts/studio-chaos/relay-rig/check.mjs | Test: node --test repositories/anton-abyzov/specwithcode/scripts/studio-chaos/relay-rig/check.test.mjs

### T-04 Add to the nightly chaos job
- AC: AC-05 | Files: repositories/anton-abyzov/specwithcode/.github/workflows/chaos-nightly.yml | Test: run the workflow once and confirm the relay receipt artifact
