# Slow worker: fewer false drops, honest timeout reason, last seen keeps counting

## Problem

On November 14, 2026 the Ubuntu worker linux-mini ran short of memory. From 3:10 PM to 4:35 PM EST its replies to the M4 slowed from 0.3 s to 4 s typical and 26 s worst, and at 4:49:42 PM it stopped answering. Its service then cycled: the Connect tunnel returned 530/1033, hung, 502 and 530 again. The machine really was unreachable, so "Can't reach linux-mini" was correct. Three things in the app were wrong around it (evidence: M4 `server.trace.ndjson`, read-only audit of main at `7e5e9f22c5`):

1. The client dropped the worker four times while it was still alive (3:32, 3:53, 4:39 PM). A remote session counted only a Pong as proof of life and closed after about 20 seconds without one, although replies arrived 7 to 15 seconds before each drop with the Pong queued behind them. Each drop cost the struggling worker a full reconnect and resubscribe.
2. For five minutes the banner said "Could not connect relay environment." The relay probes a machine's endpoint for up to 10 s but its own request deadline is 9 s, so a slow machine always came back as a bare 504 that the client reads as the relay being down. The relay's own answers for this case (a timed-out connect, an offline status) could never be returned.
3. "last seen 5m ago" froze between reconnect attempts, which grow to minutes apart, because the label read the clock inside a memo with no time input.

## Scope

In: remote session liveness counts any frame from the server; the relay's endpoint probe timeout fits inside its request deadline; the chat banner's last-seen label keeps counting.

Out: worker-side recovery (restarting a cloudflared that lost its edge connections, the systemd start limit, a watchdog for a hung service). These need the worker's own logs from this incident first and are a follow-up. Changing the reconnect backoff. Rewording the DNS or firewall hint.

## Acceptance Criteria

- [ ] AC-01: A remote session stays connected while frames keep arriving from the server without a Pong, including frames 12 s apart, and still closes with "stopped responding" after about 30 s with no frame at all.
- [ ] AC-02: When a machine's endpoint accepts a relay probe but does not answer, the relay returns its own result inside the 9 s request deadline: a timed-out connect, or an offline status with "Managed endpoint health request timed out."
- [ ] AC-03: While a chat's machine is unreachable, the banner's "last seen N ago" advances with time when nothing else changes, and no timer runs while the machine is reachable.

## Approach

- `packages/client-runtime/src/rpc/session.ts`: apply `answerPingsWhileHeard` to every session. This machine keeps its 40 s budget; a remote server gets `REMOTE_ANSWERED_SILENCE_MS` = 10 s, so total silence closes the socket after about 30 s (20 s before). The budget is short because a remote socket can stay half open, unlike loopback.
- `infra/relay/src/environments/EnvironmentConnector.ts`: `ENVIRONMENT_MINT_REQUEST_TIMEOUT_MS` 10 s to 7 s, leaving 2 s for the link lookup, proof checks and the response. The client already maps the typed timeout to reason `timeout`. The relay deploys on merge to main (`deploy-relay`).
- `apps/web/src/hooks/useClockWhile.ts` and `apps/web/src/components/ChatView.tsx`: a 30 s clock that runs only while the chat's machine is unreachable feeds the label.
- Rejected: a longer remote budget (25 s or more) delays noticing a dead machine too much; raising the relay deadline above 9 s would let the client's 10 s abort win and lose the server trace.
- Risk: a half-open remote socket is noticed about 10 s later than before.

## Decisions

### Asked
- none
### Defaulted (change any before sw-do)
- D-01 Remote silence budget is 10 s (dead after about 30 s), sized to the 26 s worst reply seen in the incident.
- D-02 Worker-side auto-recovery waits for the worker's journal from this incident, then gets its own increment.
### Open
- none

## Tasks

### T-01 Remote sessions count any frame as proof of life
- AC: AC-01 | Files: repositories/anton-abyzov/specwithcode/packages/client-runtime/src/rpc/session.ts, repositories/anton-abyzov/specwithcode/packages/client-runtime/src/rpc/session.test.ts, repositories/anton-abyzov/specwithcode/packages/client-runtime/src/connection/thisMachine.ts | Test: pnpm --dir packages/client-runtime exec vp test run src/rpc/session.test.ts

### T-02 Relay endpoint probe answers inside the request deadline
- AC: AC-02 | Files: repositories/anton-abyzov/specwithcode/infra/relay/src/environments/EnvironmentConnector.ts, repositories/anton-abyzov/specwithcode/infra/relay/src/environments/EnvironmentConnector.test.ts, repositories/anton-abyzov/specwithcode/infra/relay/src/http/Api.test.ts | Test: pnpm --dir infra/relay exec vp test run --config ../../vite.config.ts --dir . src/environments/EnvironmentConnector.test.ts src/http/Api.test.ts

### T-03 Last seen keeps counting in the chat banner
- AC: AC-03 | Files: repositories/anton-abyzov/specwithcode/apps/web/src/hooks/useClockWhile.ts, repositories/anton-abyzov/specwithcode/apps/web/src/hooks/useClockWhile.test.tsx, repositories/anton-abyzov/specwithcode/apps/web/src/components/ChatView.tsx | Test: pnpm --dir apps/web exec vp test run src/hooks/useClockWhile.test.tsx src/lib/machineStatus.test.ts

### T-04 Verify and close 1335
- AC: AC-01, AC-02, AC-03 | Files: .specweave/increments/1335-slow-worker-fewer-false-drops-honest-timeout-reason-last-seen-keeps-counting/spec.md | Test: specweave verify 1335

## Closure triage (November 24, 2026)

Shipped in PR #396 (squash `6a7c99bfe`, v1.0.302). The November 14 Muse record was at pre-squash `1341b8a9` and `session.ts` changed since, so it was not reused. Closing review by GPT-6.2 Sol (Codex) at main `f3ce25682`: **fix**, so not verified or closed.
- High, AC-01: on mobile resume the supervisor's 3 s foreground health probe can end a live remote session while frames arrive 12 s apart. `packages/client-runtime/src/connection/supervisor.ts:781`, `:858`, `:1030`
- High, AC-02: the fixed 7 s probe starts after auth, link lookup and proof signing, so setup over 2 s still yields the relay's 504. `EnvironmentConnector.ts:140`, `:440`, `:597`; `Api.ts:203`, `:248`
- High, AC-03: the 30 s clock also runs while a reachable machine asks for device approval. `ChatView.tsx:3733`; `connection/reach.ts:120`
Needs a fix increment.
