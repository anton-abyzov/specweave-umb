---
increment: 0725-studio-platform-proxy-prod-default
title: Studio platform-proxy default to verified-skill.com (502 hotfix)
type: hotfix
priority: P1
status: completed
created: 2026-04-25T00:00:00.000Z
structure: user-stories
test_mode: TDD
coverage_target: 90
extends:
  - 0712-0708-followups-scanner-outbox-do-alarm-and-e2e
---

# Hotfix: Studio platform-proxy default to verified-skill.com (502)

## Overview

`vskill studio` runs the eval-server on a port-hashed local port (e.g. 3162 for the umbrella). The studio frontend issues *relative* fetches like `/api/v1/skills/stream` and `/api/v1/skills/check-updates`. Increment 0712 (T-016A/B) added `src/eval-server/platform-proxy.ts` to forward those paths to a vskill-platform target driven by `VSKILL_PLATFORM_URL`, with a default of `http://localhost:3017`.

That default is wrong for the common case. Most users run `vskill studio` standalone — they do **not** have a local vskill-platform / `wrangler dev` / `next dev` running on port 3017. Every relative skill API call therefore returns **502 Bad Gateway** from the proxy's `platform_unreachable` envelope, and the Skill Studio sidebar/SSE update bell sits in a permanent reconnect loop.

The fix is one line: change the default to `https://verified-skill.com`, which is exactly what `src/api/client.ts:10` already does for the CLI's own HTTP calls (`DEFAULT_BASE_URL = "https://verified-skill.com"`). Production endpoints are verified live: `GET /api/v1/skills/stream?skills=…` returns `200 text/event-stream` with a `: connected` keepalive, and `POST /api/v1/skills/check-updates` returns `200 application/json`. Local-platform devs (the rare case) can still point the proxy at their dev instance via `VSKILL_PLATFORM_URL=http://localhost:3017`.

**Target repo:** `repositories/anton-abyzov/vskill`.
**Sync project:** `vskill`.

## Personas

- **Skill Studio user (P1):** Opens `vskill studio`, expects the update-pipeline UI (`UpdateBell`, sidebar dot, check-updates poll fallback) to work against the production catalog without spinning up a private platform deployment.
- **vskill-platform contributor (P2):** Runs `wrangler dev --port 3017` locally and wants the studio to point at *their* platform instance, not production.

## User Stories

### US-001: Studio works against production by default
**Project**: vskill

**As a** Skill Studio user running `vskill studio` without a local vskill-platform
**I want** the eval-server's `/api/v1/skills/*` proxy to forward to `https://verified-skill.com` by default
**So that** the SSE stream + check-updates fallback poll succeed out-of-the-box and I never see `502 platform_unreachable` from a fresh install

**Acceptance Criteria**:
- [x] **AC-US1-01**: `getPlatformBaseUrl()` returns `https://verified-skill.com` when the `VSKILL_PLATFORM_URL` env var is unset or empty (replacing the previous `http://localhost:3017` default).
- [x] **AC-US1-02**: `getPlatformBaseUrl()` continues to honor `VSKILL_PLATFORM_URL` when set — devs running a local platform can opt back in via `VSKILL_PLATFORM_URL=http://localhost:3017`. Trailing-slash stripping behavior is preserved.
- [x] **AC-US1-03**: A new unit test in `src/eval-server/__tests__/platform-proxy.test.ts` covers the unset-env path explicitly: temporarily delete `VSKILL_PLATFORM_URL`, assert `getPlatformBaseUrl() === "https://verified-skill.com"`, restore the env. The test is hermetic — it does not perform a network call against verified-skill.com.
- [x] **AC-US1-04**: The header comment in `platform-proxy.ts` and the inline comment block are updated to reflect the new default and the rationale (mirror `src/api/client.ts` `DEFAULT_BASE_URL`). Stale references to "default `http://localhost:3017`" are removed or rewritten.
- [x] **AC-US1-05**: All 12 existing `platform-proxy.test.ts` tests continue to pass — the default-change does not regress the env-set path, the trailing-slash strip, the 502 envelope on unreachable upstream, or any forwarding behavior.
- [x] **AC-US1-06**: A rebuilt `vskill` dist (`npm run build` in `repositories/anton-abyzov/vskill`) loads `platform-proxy.js` with the new default; running `vskill studio` against the umbrella project on port 3162 with `VSKILL_PLATFORM_URL` unset issues `/api/v1/skills/check-updates` and `/api/v1/skills/stream` requests that hit `https://verified-skill.com` and receive `200` rather than `502`.

## Out of scope

- Changes to vskill-platform / `verified-skill.com` itself — the production endpoints already work.
- Changes to `src/api/client.ts` — its default is already correct.
- Changes to the studio UI's reconnect/poll logic — the hook in `src/eval-ui/src/hooks/useSkillUpdates.ts` is unchanged.
- Multi-target failover (e.g. try local first, fall back to prod) — explicitly **not** the chosen design. A single deterministic default keeps the proxy predictable; opt-in to local via env.

## Non-functional requirements

- **NFR-001**: Hermetic tests — no test in this increment performs a live HTTP request to `verified-skill.com`. The default-resolution test asserts the string only.
- **NFR-002**: Backward compat — anyone currently relying on `VSKILL_PLATFORM_URL=http://localhost:3017` (explicit env) is unaffected. Only the *unset* path changes.
