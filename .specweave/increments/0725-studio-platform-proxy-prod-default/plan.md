# Implementation Plan: Studio platform-proxy default to verified-skill.com (502 hotfix)

## Overview

One-line default-constant flip in `src/eval-server/platform-proxy.ts` plus a hermetic unit test that pins the unset-env behavior, plus a comment refresh. No new modules, no public API changes, no schema changes, no UI changes.

## Architecture

### Why the default is wrong today

`platform-proxy.ts` was added in 0712 (T-016A/B) to fix the same-origin gap between `vskill studio` (eval-server, port-hashed e.g. 3162) and the vskill-platform (Next.js / Cloudflare Worker on 3017 in dev). The gap-fix is correct: any unhandled `/api/v1/skills/*` request gets forwarded to the platform. The default target, however, was scoped to *the dev-platform-on-3017 case* — which is the rare case. The common case is a user running `vskill studio` standalone with no local platform; for them, the default forces a 502 reconnect loop.

Meanwhile, the CLI half of the same codebase (`src/api/client.ts:10`) has always defaulted to `https://verified-skill.com`:

```ts
const DEFAULT_BASE_URL = "https://verified-skill.com";
function resolveBaseUrl(): string { … process.env.VSKILL_API_BASE … }
```

The studio half should mirror that.

### The fix

`src/eval-server/platform-proxy.ts:34`:

```ts
// before
const DEFAULT_PLATFORM_URL = "http://localhost:3017";
// after
const DEFAULT_PLATFORM_URL = "https://verified-skill.com";
```

`getPlatformBaseUrl()` already does the right thing — it checks `process.env.VSKILL_PLATFORM_URL` first, and falls back to `DEFAULT_PLATFORM_URL`. Only the constant value changes; the resolution logic, the trailing-slash strip, and the export shape are untouched.

The `proxyToPlatform()` function already handles HTTPS upstream correctly — line 111 picks `https` vs `http` from the resolved URL's `protocol`, and line 116 uses `target.port || (protocol==="https:" ? 443 : 80)` so the standard 443 default applies when the URL has no explicit port. Verified by reading the file: no other lines need to change.

### Header comment refresh

The block comment at the top of `platform-proxy.ts` currently says:

```
// (Next.js / Cloudflare Worker, default http://localhost:3017 in dev).
//   - Target URL is configurable via `VSKILL_PLATFORM_URL` env (default
//     `http://localhost:3017`). Must include scheme + host + port.
```

Rewrite to reflect the new default:

```
// (default https://verified-skill.com — the production worker — for parity
//  with src/api/client.ts:10 DEFAULT_BASE_URL).
//   - Target URL is configurable via `VSKILL_PLATFORM_URL` env (default
//     `https://verified-skill.com`). Local-platform devs override via
//     `VSKILL_PLATFORM_URL=http://localhost:3017`. Must include scheme +
//     host (port optional for https://verified-skill.com).
```

## Test strategy

`src/eval-server/__tests__/platform-proxy.test.ts` already has a `describe("getPlatformBaseUrl")` block. Add one `it()` to that block:

```ts
it("defaults to https://verified-skill.com when VSKILL_PLATFORM_URL is unset", () => {
  const original = process.env.VSKILL_PLATFORM_URL;
  delete process.env.VSKILL_PLATFORM_URL;
  try {
    expect(getPlatformBaseUrl()).toBe("https://verified-skill.com");
  } finally {
    if (typeof original !== "undefined") {
      process.env.VSKILL_PLATFORM_URL = original;
    }
  }
});
```

Hermetic — no live network call. The existing 12 tests are not modified. The empty-string variant is also covered (the existing `length > 0` check at platform-proxy.ts:52 falls through to the default).

The `beforeAll` in this file sets `VSKILL_PLATFORM_URL` to a fake-port URL before any test runs, so the new `it()` must save+restore around its `delete`. The pattern matches the existing trailing-slash test at lines 123–127.

## Build + verification

1. `cd repositories/anton-abyzov/vskill && npx vitest run src/eval-server/__tests__/platform-proxy.test.ts` — expect 13/13 green.
2. `cd repositories/anton-abyzov/vskill && npm run build` — produces `dist/eval-server/platform-proxy.js` with the new default.
3. Sanity: `node -e "import('./dist/eval-server/platform-proxy.js').then(m => { delete process.env.VSKILL_PLATFORM_URL; console.log(m.getPlatformBaseUrl()); })"` should print `https://verified-skill.com`.
4. Live verification: with no local platform running on 3017, restart `vskill studio` against the umbrella project (port 3162) and confirm the browser network panel shows `/api/v1/skills/check-updates` returning `200` (proxied through 3162 → verified-skill.com). The `502 platform_unreachable` envelope should no longer appear.

## Risks + mitigations

- **R1 — verified-skill.com outage** propagates to dev: low likelihood (production has been stable through 0708/0712 closure); mitigation is the existing `502 platform_unreachable` envelope path which is unchanged.
- **R2 — local-platform devs surprised** when their `wrangler dev --port 3017` is no longer the default target: explicit opt-in via `VSKILL_PLATFORM_URL=http://localhost:3017`. The plan.md note from 0712 about needing `wrangler dev` is amended in passing — but that's documentation, not code.
- **R3 — IPv4 vs IPv6 or DNS issues** in CI: not a concern, the new test is hermetic and asserts the string only.

## ADR

No new ADR required. The decision is a small inversion of an earlier default that was never the subject of an ADR. Recorded in this plan.md as the canonical reference: increment 0725 amends 0712 T-016B's default-target choice, leaving the proxy mechanism intact.
