---
increment: 0754-studio-search-502-cdn-loopback
title: 'P0: Studio search 502 — Cloudflare CDN loopback 403'
type: hotfix
priority: P0
status: completed
created: 2026-04-26T00:00:00.000Z
structure: user-stories
test_mode: TDD
coverage_target: 90
---

# Feature: P0 hotfix — Studio search 502 caused by Cloudflare worker-loopback 403

## Overview

**PRODUCTION OUTAGE.** `https://verified-skill.com/api/v1/studio/search` returns HTTP 502 with body `{"error":"search_unavailable"}` for **every query** (verified: `q=react`, `q=python`, `q=skill-builder`, `q=anton`, `q=test` — 100% of probes return 502 in <200ms, well below the 5s upstream timeout). The local Skill Studio's find palette (`vskill/src/eval-ui/src/components/FindSkillsPalette/SearchPaletteCore.tsx:168`, `DEFAULT_SEARCH_URL = "/api/v1/studio/search"`) is therefore completely unusable — every search shows nothing.

The upstream `/api/v1/skills/search` works fine (200 OK in 0.5–0.9s when probed directly from outside the worker). So the failure is not in the search engine — it's in the proxy hop.

**Root cause** (confirmed by reading the route + correlating with the prior 0708 fix):
- The proxy at `vskill-platform/src/app/api/v1/studio/search/route.ts:153` dispatches its upstream call via `globalThis.fetch("https://verified-skill.com/api/v1/skills/search?...")`.
- Cloudflare Workers refuse to fetch their own zone via the public custom domain — this is the documented "worker-loopback 403" behavior.
- The fetch fails immediately, the route's catch block at line 178 logs `studio_proxy_fetch_error` and emits the sanitized 502.
- The exact same bug was diagnosed and fixed for the publish-client in commit `665a63c` (`fix(0708): publish-client uses WORKER_SELF_REFERENCE binding to avoid CDN loopback 403`). The fix uses the `WORKER_SELF_REFERENCE` service binding (already wired in `wrangler.jsonc:81-86`) which routes worker-to-worker inside the CF network — no CDN hop, no 403.
- The studio-search proxy was added later (0715/0716) and never got the binding treatment, hence this regression.

This increment ships the same WORKER_SELF_REFERENCE binding pattern to the studio-search route, restoring the local Skill Studio find palette to working order.

## User Stories

### US-001: Restore Skill Studio search functionality (P0)
**Project**: vskill-platform

**As a** Skill Studio user trying to find a published skill via the find palette
**I want** the studio's search endpoint to return real results instead of 502 `search_unavailable`
**So that** I can find skills I just published (e.g., my `anton-abyzov/vskill/skill-builder`) and any other skill in the registry

**Acceptance Criteria**:
- [x] **AC-US1-01**: `GET https://verified-skill.com/api/v1/studio/search?q=react` returns HTTP 200 with a JSON envelope `{ results: [...], total: number }` after this fix is deployed (no more 502).
- [x] **AC-US1-02**: The proxy routes its upstream fetch through `env.WORKER_SELF_REFERENCE.fetch(...)` when the Cloudflare context exposes that binding, falling back to `globalThis.fetch(...)` otherwise (for dev/test where no CF context exists).
- [x] **AC-US1-03**: All existing proxy semantics are preserved byte-identically: 60s LRU cache + ETag + 304 path, 60-req-per-minute token bucket per cf-connecting-ip, 5s `UPSTREAM_TIMEOUT_MS` via AbortController, 499 on client disconnect, sanitized 502 on upstream 5xx/malformed/timeout, 4xx pass-through.
- [x] **AC-US1-04**: `q=skill-builder` (the user's missing-skill query that initially exposed the outage) returns a result list including `anton-abyzov/vskill/skill-builder` somewhere in the response (ranking position is a separate follow-up — for THIS increment, "appears at all when limit is high enough" is sufficient).

---

### US-002: TDD-locked test coverage for the binding decision (P0)
**Project**: vskill-platform

**As a** vskill-platform maintainer
**I want** unit tests that pin the proxy's binding-vs-fetch decision to the WORKER_SELF_REFERENCE pattern
**So that** any future regression that re-introduces a raw `globalThis.fetch` against the public domain breaks CI instead of silently shipping another production outage

**Acceptance Criteria**:
- [x] **AC-US2-01**: A new test asserts the proxy uses `env.WORKER_SELF_REFERENCE.fetch(...)` when the Cloudflare context provides that binding (mirrors `publish-client.test.ts` "uses the WORKER_SELF_REFERENCE service binding when present" test).
- [x] **AC-US2-02**: A new test asserts the proxy falls back to `globalThis.fetch(...)` when no service binding is provided (so dev/local/test environments keep working without a CF context).
- [x] **AC-US2-03**: Both new tests fail BEFORE the source change (RED) and pass AFTER (GREEN) — TDD discipline preserved.

---

### US-003: Live-production smoke verification (P0)
**Project**: vskill-platform

**As a** maintainer responsible for confirming the outage is resolved
**I want** a documented manual smoke check against the deployed production endpoint
**So that** closure of this increment certifies the customer-visible 502 is gone, not just that local tests pass

**Acceptance Criteria**:
- [x] **AC-US3-01**: After deploy, `curl https://verified-skill.com/api/v1/studio/search?q=react` returns HTTP 200 with a `results` array.
- [x] **AC-US3-02**: After deploy, the user's originally-reported query `q=skill-builder&limit=50` returns a `total` >= 31 and the `results` array contains `anton-abyzov/vskill/skill-builder` (proves the user's specific skill is now discoverable).

## Functional Requirements

### FR-001: Service-binding-first dispatch
When `getCloudflareContext({async:true})` resolves with `env.WORKER_SELF_REFERENCE` defined, the proxy MUST dispatch its upstream fetch via the binding. When the binding is absent (local dev, vitest, jest, or any non-Cloudflare runtime), it MUST fall back to `globalThis.fetch`.

### FR-002: No semantic change to the public contract
Request/response shape, status codes, headers (`ETag`, `X-Cache`, `Cache-Control`, `Server-Timing`), rate-limit allowance, cache TTL, timeout duration — all stay byte-identical to the pre-fix behavior. This is a transport swap, not an API revision.

### FR-003: Resilient binding lookup
The `getCloudflareContext` import must be inside a try/catch so any failure to resolve the CF context (e.g., during local `next dev` without `wrangler dev`) degrades gracefully to `globalThis.fetch` instead of throwing.

## Success Criteria

- Production endpoint returns HTTP 200 for arbitrary search queries within 5 minutes of deploy.
- The originally-affected user (Anton) can find `anton-abyzov/vskill/skill-builder` via the Studio find palette.
- New vitest unit tests pin the binding decision and pass on first GREEN.
- Existing studio-search route tests (cache hit/miss, ETag, rate-limit, timeout, etc.) continue to pass — no regressions.
- `npx wrangler tail` shows zero `studio_proxy_fetch_error` log lines after deploy (was firing on every request before).

## Out of Scope

- **Search ranking improvements** (the secondary bug where `anton-abyzov/vskill/skill-builder` ranks #31 of 31 due to popularity-weighted scoring). That's a separate follow-up increment.
- **`/api/v1/skills` LIST endpoint filter wiring** (`q=`, `author=`, `source=` params silently ignored). Separate follow-up.
- **Submission `isVendor` drift** (submission has `isVendor:false` while the published Skill row has `labels:[vendor,certified]`). Separate cleanup.
- **Auto-rebuild of the KV search index after publish** (currently admin-triggered via `POST /api/v1/admin/rebuild-search`). Separate reliability increment.
- **Replacing the HTTP proxy with a direct in-process function call** (eliminating the round trip entirely is tempting but is a refactor, not a hotfix).
- **5s timeout tuning** — the timeout is a defensive constant, not the cause of this outage; out of scope.

## Dependencies

- `wrangler.jsonc` already declares `WORKER_SELF_REFERENCE` as a service binding to the `verified-skill-com` worker (lines 81-86) — present, no infra change needed.
- `@opennextjs/cloudflare` is already a dependency (used elsewhere via `getCloudflareContext`).
- Deploy pipeline: `npm run deploy` (= `npx @opennextjs/cloudflare deploy`) — no change needed.
