# 0859 — Cross-isolate reliable submission notifications (Durable Object)

## Problem

0847 delivers in-app submit + queue + native approve/reject notifications, but the live-notification transport is the **per-Cloudflare-isolate** submissions event-bus (`src/lib/event-bus.ts`). The queue consumer that emits the terminal `state_changed`/`scan_complete` decision usually runs in a **different isolate** than the one holding the desktop's SSE connection, so the live notification is **best-effort** — it frequently never arrives. The REST `?mine` feed is reliable (the panel shows correct state on open), but the proactive "you got approved/rejected" push is not.

The platform already has a **cross-isolate-reliable** fan-out: the `UpdateHub` Durable Object (singleton `idFromName("global")`) behind `/api/v1/skills/stream`, which the desktop already subscribes to (the 0855-fixed notification channel). This increment routes submission decisions through it.

## User Stories

### US-001 — Reliable decision push
As a logged-in Skill Studio user, I want to receive the approve/reject native notification reliably, regardless of which Cloudflare isolate processed my submission.

- **AC-US1-01**: On a submission terminal-state transition with a known owner, the platform publishes a `submission_decision` event to the `UpdateHub` DO keyed by `usr_<userId>`, via the existing HMAC internal publish path, idempotent on `eventId`.
- **AC-US1-02**: The desktop, when logged in, includes `usr_<userId>` in its `/api/v1/skills/stream` `?skills` filter, so it receives `submission_decision` events for its own user over the existing reliable SSE connection.
- **AC-US1-03**: On receiving a `submission_decision` event, the desktop fires the native notification (approved → informational; rejected → clickable → `/submit/<id>`), reusing the 0847 routing.

### US-002 — No regression / privacy
- **AC-US2-01**: The skill-update path and the 0855 SSE notification behavior are unaffected (the new event type is additive).
- **AC-US2-02**: Anonymous submissions (no `userId`) are NOT published to any user-channel.
- **AC-US2-03**: A desktop only ever subscribes to its OWN authenticated `userId` channel; idempotent `eventId` prevents double-notification on queue/outbox retry.

## Out of scope
- Removing the per-isolate `?mine` panel stream (kept as best-effort live UI for the queue panel).
- Background notifications when the app is fully closed (OS-level; the app must be running to hold the SSE).
