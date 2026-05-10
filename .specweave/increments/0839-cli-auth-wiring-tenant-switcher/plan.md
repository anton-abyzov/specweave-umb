# 0839 — Implementation Plan

## Architecture Summary

Two surfaces, one shared `~/.vskill/config.json` file as the single source of truth for "active tenant":

```
┌─────────────────────────────────────────────────────────────────────┐
│ vskill CLI                            Studio (eval-server runtime) │
│ ┌────────────┐                         ┌────────────────────────┐  │
│ │ commands/  │                         │ TenantPicker.tsx       │  │
│ │  add.ts    │                         │   ↕ /__internal/       │  │
│ │  install.ts│ ──┐                  ┌─→│     active-tenant      │  │
│ │  list.ts   │   │                  │  └────────────────────────┘  │
│ │  market…   │   │                  │                              │
│ │  orgs.ts   │ ──┴──┐               │  eval-server.ts adds         │
│ │  whoami.ts │      │               │  /__internal/active-tenant   │
│ └────────────┘      │               │  handler → writes config.json│
│                     ▼               │                              │
│              src/api/client.ts ─────┘                              │
│              (Bearer interceptor)                                   │
│                     │                                               │
│                     ▼                                               │
│              ~/.vskill/config.json   ←── single source of truth    │
│              { currentTenant: "..." }      for active tenant       │
└─────────────────────────────────────────────────────────────────────┘
                                │
                                ▼ (HTTP)
┌─────────────────────────────────────────────────────────────────────┐
│ vskill-platform (Cloudflare Workers / Next.js)                     │
│  POST /api/v1/auth/github/exchange-for-vsk-token   (NEW)           │
│  GET  /api/v1/account/tenants                      (NEW)           │
│  GET  /api/v1/account/repos                        (existing)      │
│  All routes use requireUserOrGithubBearer (already accepts both)   │
└─────────────────────────────────────────────────────────────────────┘
```

## ADRs

### ADR-001: gho_ vs vsk_ token coexistence

**Decision:** Store BOTH tokens in the keychain under distinct service names, never one-or-the-other.
- Keychain service `vskill-github` — `gho_*` (raw GitHub OAuth, used for direct GitHub API calls like `/user`, `/installation/repositories`, GraphQL).
- Keychain service `vskill-token` — `vsk_*` (verified-skill API token, used for ALL `verified-skill.com` calls).

**Rationale:**
- `gho_*` is GitHub's property and is the only thing GitHub accepts. We can't replace it.
- `vsk_*` is our property — we control its scopes, TTL, and revocation. Sending `gho_*` to verified-skill.com works (the platform validates via `GET /user`) but it costs a GitHub API call per inbound request and gives us zero ability to revoke without touching GitHub.
- `requireUserOrGithubBearer` (vskill-platform/src/lib/auth/bearer.ts:223) already validates both prefixes; no platform changes needed.
- Distinct service names keep `keytar` lookups O(1) and avoid prefix-sniffing.

**Consequences:**
- `client.ts` interceptor must prefer `vsk_*` when present, fall back to `gho_*`.
- `auth login` mints `vsk_*` AFTER the device flow yields `gho_*`. Failure of the exchange step is non-fatal (login still works in "legacy mode").
- `auth logout` clears both keychain entries AND best-effort revokes `vsk_*` server-side via `DELETE /api/v1/auth/sign-out-all`.

### ADR-002: --tenant resolution priority

**Decision:** Active tenant resolved in this order, first match wins:
1. `--tenant <slug>` CLI flag (per-command override)
2. `VSKILL_TENANT` env var (CI / scripted use)
3. `currentTenant` in `~/.vskill/config.json` (the persistent active tenant)
4. Auto-pick if user has exactly N=1 tenant
5. Error: `Multiple tenants available — set one with \`vskill orgs use <slug>\`.`

**Rationale:** Mirrors `kubectl` / `gcloud` UX. Per-command flag > env > config > sensible default > explicit error. Never silently picks one of N>1.

**Consequences:**
- `commands/orgs.ts` exposes `use` to write the config file. No flag-only mode (env-only is supported but not advertised).
- Studio UI uses the same precedence — its `TenantPicker` writes config #3, and the picker reads/displays it.

### ADR-003: New endpoint vs reuse `/account/repos` for tenant list

**Decision:** Add a dedicated `GET /api/v1/account/tenants` route. Do NOT derive the tenant list from `/account/repos`.

**Rationale:**
- `/account/repos` returns repos grouped by `ownerLogin` — that's a side effect, not a contract. A user can be a member of a tenant with zero installed repos (just installed the App on the org-level for billing).
- A dedicated endpoint surfaces `role` (owner/admin/member from `OrgMember.role`), `installationId`, `tenantId`, `slug`, `name` — fields a generic repos query has no business returning.
- Caching: tenant membership changes rarely (org joins/leaves), so this can be aggressively cached (5 min TTL). Repos list churns more.

**Consequences:**
- One small new route handler. Joins User → OrgMember → Tenant → Installation.
- `TenantPicker` and `vskill orgs list` share this single endpoint.

## Files

### New

| Path | Purpose |
|------|---------|
| `vskill/src/commands/orgs.ts` | `orgs list / use / current` subcommands |
| `vskill/src/commands/whoami.ts` | Combined auth + tenant status |
| `vskill/src/lib/active-tenant.ts` | Read/write `currentTenant` in `~/.vskill/config.json`, with merge semantics |
| `vskill/src/lib/active-tenant.test.ts` | Unit tests for the config helper |
| `vskill/src/api/client.test.ts` | Unit tests for the new Bearer interceptor + tenant header |
| `vskill/src/commands/orgs.test.ts` | Unit tests for the orgs subcommands |
| `vskill/src/commands/whoami.test.ts` | Unit tests for whoami |
| `vskill/src/eval-ui/src/components/private/TenantPicker.tsx` | Studio sidebar tenant switcher |
| `vskill/src/eval-ui/src/components/private/TenantPicker.test.tsx` | Component tests (Vitest + Testing Library) |
| `vskill-platform/src/app/api/v1/auth/github/exchange-for-vsk-token/route.ts` | gho_ → vsk_ exchange endpoint |
| `vskill-platform/src/app/api/v1/auth/github/exchange-for-vsk-token/route.test.ts` | Endpoint tests (200, 401 invalid gho, 5xx GitHub down) |
| `vskill-platform/src/app/api/v1/account/tenants/route.ts` | List tenants for the authenticated user |
| `vskill-platform/src/app/api/v1/account/tenants/route.test.ts` | Endpoint tests (0/1/N tenants, 401 unauthenticated) |
| `vskill/e2e/0839-cli-auth-tenant-switcher.spec.ts` | Playwright E2E covering login → orgs use → install |

### Modified

| Path | Change |
|------|--------|
| `vskill/src/api/client.ts` | Add `getAuthHeader()` + `getTenantHeader()` interceptor; cache token per process |
| `vskill/src/commands/auth.ts` | After device flow, call `exchange-for-vsk-token`; store both tokens; logout clears both |
| `vskill/src/commands/add.ts` | Add `--tenant <slug>` flag; multi-tenant resolution loop; 402/403 handling |
| `vskill/src/commands/list.ts` | (No code change beyond inheriting `client.ts` interceptor — verified by test) |
| `vskill/src/commands/marketplace.ts` | (No code change beyond inheriting `client.ts` interceptor — verified by test) |
| `vskill/src/lib/keychain.ts` | Add `getVskillToken()` / `setVskillToken()` / `deleteVskillToken()` for the `vskill-token` service |
| `vskill/src/index.ts` (or wherever commands are registered) | Register `orgs` and `whoami` commands |
| `vskill/src/eval-ui/src/components/private/ConnectGitHubCard.tsx` | Render `<TenantPicker />` when N≥1 tenants; preserve empty-state CTA when N=0 |
| `vskill/src/eval-server.ts` | Add `/__internal/active-tenant` GET/POST handler — reads/writes config.json |

### Reference (read-only — don't modify)

- `vskill-platform/src/lib/auth/bearer.ts` — existing `requireUserOrGithubBearer` already accepts both prefixes
- `vskill-platform/prisma/schema.prisma` — `ApiToken`, `OrgMember`, `Tenant`, `Installation` models exist from 0834
- `vskill/src/commands/auth.ts:122-228` — existing device-flow login

## Test Strategy

- **Unit (Vitest):** mock `keytar` and `fetch`; verify interceptor decisions, config-file merge, command dispatching, error messages match AC-IDs.
- **Integration (Vitest):** spin up the route handlers with a test database (existing platform test infra); verify exchange + tenants endpoints with 200/401/403/5xx paths.
- **E2E (Playwright):** one full path — `auth login` (mock device flow) → `orgs list` → `orgs use acme` → `add private-skill` returns 200. Plus a second tenant in the test DB with no entitlement → `add private-skill` returns 402 with upgrade URL.
- **Coverage targets:** unit 95% on new files, integration 90% on new endpoints, E2E covers all 5 user stories' golden path.

## Risks & Mitigations

| Risk | Mitigation |
|------|------------|
| Keychain unavailable in CI / headless | `lib/keychain.ts` already has a file-based fallback; new helpers reuse it |
| `gho_` token expires mid-session | `client.ts` 401 handler prints re-login message; doesn't auto-delete |
| Studio + CLI race-write `~/.vskill/config.json` | Use atomic write (write to `.tmp`, rename); merge unknown keys on read |
| `exchange-for-vsk-token` GitHub API rate-limit | Cache `GET /user` result for 60s per token; return 503 on rate-limit (not 5xx) |
| Tenant list endpoint slow on N>20 orgs | Single Prisma query with joins; expected <100ms p95; add Cloudflare cache header |
| Migration impact on existing logged-in users | First post-deploy login mints `vsk_*` automatically; existing sessions keep working in "legacy mode" until next login |

## Rollout

1. Land platform changes (exchange + tenants endpoints) FIRST — they're additive.
2. Land CLI changes — interceptor is gated on token presence (anonymous flow unaffected).
3. Land Studio TenantPicker — replaces ConnectGitHubCard for N≥1 case only; N=0 unchanged.
4. Verify in staging: log in fresh, run `orgs list`, switch tenant, install a private skill, open Studio, confirm tenant matches.
5. No feature flags — backwards-compatible by construction.
