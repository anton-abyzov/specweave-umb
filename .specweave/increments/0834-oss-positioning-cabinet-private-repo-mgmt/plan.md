# Plan — 0834 OSS positioning + Account cabinet + Private-repo mgmt parity

## Architecture overview

Three surfaces (web, Tauri desktop, npx studio) → one platform API → one Postgres DB.

```
                    ┌─────────────────────────────────────────────┐
                    │  verified-skill.com  (Cloudflare Workers)   │
                    │  Next.js 15 + Prisma                        │
                    │  /api/v1/account/*  ← SOURCE OF TRUTH       │
                    └─────────────────┬───────────────────────────┘
                                      │  HTTP/JSON
        ┌─────────────────────────────┼─────────────────────────────┐
        │                             │                             │
┌───────▼────────┐          ┌─────────▼─────────┐         ┌─────────▼─────────┐
│ Web /account/* │          │ Tauri desktop     │         │ npx vskill studio │
│ Next.js page   │          │ eval-ui WebView   │         │ eval-server +     │
│ uses shared    │          │ + Bearer token    │         │ eval-ui browser   │
│ <ConnectedRepos│          │ (keyring)         │         │ tab + cookie      │
│ Table />       │          │                   │         │                   │
└────────────────┘          └───────────────────┘         └───────────────────┘
        │                             │                             │
        └─────────────── all three import ──────────────────────────┘
                                  │
                ┌─────────────────▼─────────────────┐
                │ src/eval-ui/src/components/account│
                │  • ConnectedReposTable.tsx        │
                │  • ProfileForm.tsx                │
                │  • PlanCard.tsx                   │
                │  • TokensTable.tsx                │
                │  • NotificationsForm.tsx          │
                │  • DangerZone.tsx                 │
                │  + hooks/useAccount.ts            │
                └───────────────────────────────────┘
```

The component-extraction rule is the load-bearing decision: by putting the React components in the existing `src/eval-ui` package and importing them from both the Next.js platform repo and the Tauri desktop repo, we get **identical-by-construction** rendering. A status-dot colour change in one component re-skins all three surfaces.

## Backend (vskill-platform)

### Prisma schema additions

```prisma
model ConnectedRepo {
  id                  String   @id @default(cuid())
  userId              String
  user                User     @relation(fields: [userId], references: [id], onDelete: Cascade)
  githubInstallationId BigInt
  ownerLogin          String
  ownerAvatarUrl      String
  repoName            String
  repoFullName        String   // "owner/name"
  isPrivate           Boolean
  syncStatus          SyncStatus @default(GREEN)
  lastSyncedAt        DateTime?
  lastErrorMessage    String?
  skillsCount         Int      @default(0)
  connectedAt         DateTime @default(now())
  disconnectedAt      DateTime?
  @@unique([userId, repoFullName])
  @@index([userId, disconnectedAt])
}

enum SyncStatus {
  GREEN  // healthy, recently synced
  AMBER  // reauth needed (token expired)
  GREY   // idle (no activity in 24h)
  RED    // error during sync
}

model ApiToken {
  id           String    @id @default(cuid())
  userId       String
  user         User      @relation(fields: [userId], references: [id], onDelete: Cascade)
  name         String
  tokenHash    String    @unique  // sha256(plaintext)
  tokenPrefix  String    // first 12 chars: "vsk_xxxxxx..."
  scopes       String[]  // ["read"], ["read", "write"]
  lastUsedAt   DateTime?
  createdAt    DateTime  @default(now())
  expiresAt    DateTime
  revokedAt    DateTime?
  @@index([userId, revokedAt])
  @@index([tokenHash])
}

model AccountExport {
  id          String    @id @default(cuid())
  userId      String
  user        User      @relation(fields: [userId], references: [id], onDelete: Cascade)
  status      ExportStatus @default(QUEUED)
  requestedAt DateTime  @default(now())
  completedAt DateTime?
  downloadUrl String?
  expiresAt   DateTime?  // download URL expires 7d after completion
}

enum ExportStatus { QUEUED PROCESSING READY FAILED EXPIRED }

// Existing User model gains:
//   bio                String?
//   publicProfile      Boolean @default(true)
//   notificationPrefs  Json    @default("{}")
//   deletedAt          DateTime?
//   connectedRepos     ConnectedRepo[]
//   apiTokens          ApiToken[]
//   accountExports     AccountExport[]
```

Migration: additive only. Backfill `publicProfile = true` for existing users; `notificationPrefs = {}` defaults handle the rest.

### API endpoints (all under `/api/v1/account/*`)

| Method | Path | Purpose |
|---|---|---|
| GET | `/profile` | Return user profile (includes tier from existing User.tier) |
| PATCH | `/profile` | Update displayName, bio, publicProfile |
| GET | `/repos` | List connected repos, KV-cached 60s |
| POST | `/repos/{id}/resync` | Force resync (drops cache + enqueues scan) |
| DELETE | `/repos/{id}` | Soft-disconnect (set disconnectedAt) |
| GET | `/repos/connect` | Server-rendered pre-flight page → redirect URL |
| GET | `/repos/github/callback` | OAuth-style callback → persists installations |
| GET | `/tokens` | List user tokens (no plaintext) |
| POST | `/tokens` | Create token (returns plaintext ONCE) |
| DELETE | `/tokens/{id}` | Revoke token |
| GET | `/skills/summary` | Public/private counts + recent activity |
| GET | `/notifications` | Get prefs |
| PATCH | `/notifications` | Update prefs |
| POST | `/sign-out-all` | Revoke all sessions/tokens |
| POST | `/export` | Enqueue account export |
| POST | `/delete` | Soft-delete account |

All endpoints use existing `requireUserOrGithubBearer` middleware extended to also accept `vsk_*` Bearer tokens.

### KV cache strategy

Connected-repos list cache key: `account:repos:{userId}` TTL 60s. Invalidated immediately on connect/disconnect/resync. Reads in <1ms; cold reads in <50ms.

### CSRF for connect flow

State token: `csrf-{userId}-{timestamp}-{nonce}` signed with `INTERNAL_BROADCAST_KEY` (existing). Stored in HttpOnly cookie. Callback verifies cookie matches state-query-param, rejects otherwise.

## Frontend — Web (vskill-platform)

### Routing

```
/account                 → redirect to /account/profile
/account/profile         → ProfileTab (uses ProfileForm component)
/account/billing         → BillingTab (uses PlanCard + InvoiceTable)
/account/repos           → ReposTab (uses ConnectedReposTable + summary chip)
/account/repos/connect   → ConnectFlow (pre-flight page)
/account/skills          → SkillsTab (uses SkillsSummary + RecentActivity)
/account/tokens          → TokensTab (uses TokensTable + GenerateModal)
/account/notifications   → NotificationsTab (uses NotificationsForm)
/account/danger          → DangerTab (uses DangerZone)
```

Shared layout: `src/app/account/layout.tsx` renders the sidebar nav + header strip + `{children}` slot.

### Top-nav avatar dropdown

Add `<UserMenu>` to the existing site header. Menu items: "Account settings" (→ /account/profile), divider, "Sign out".

### Mobile responsive

Below 768px: sidebar becomes a sticky top dropdown (`<Select>`). Below 640px: ConnectedReposTable becomes a card-list (each row = `<RepoCard>`).

## Frontend — Desktop + npx studio (vskill)

### Component extraction

All `<account/*>` components live in `src/eval-ui/src/components/account/`. They are:

- Rendering-pure: take props, emit events, no fetch/cookie logic inside.
- Data layer in `src/eval-ui/src/hooks/useAccount.ts` — thin React Query wrapper around the `/api/v1/account/*` endpoints.
- Platform-aware: the hook reads `platformBaseUrl` from a context (web: `verified-skill.com`; desktop: `verified-skill.com`; npx-studio: same with optional override env).

### Desktop sidebar

Add new "Account" entry below "Skills" in the sidebar (`src/eval-ui/src/components/Sidebar.tsx`). Click opens `<AccountShell>` in the main pane (replaces studio editor). Uses a router stub (`useState<"profile"|"billing"|...>`) since this is in-app, not URL-driven.

### Tauri Bearer auth

Desktop reads token from existing keyring (0831). `useAccount` hook receives token via context. All fetches: `Authorization: Bearer ${token}`.

### npx studio

The eval-server already has cookie auth when the user signs in via the browser tab. Account view uses the same cookie. Identical to web — same component tree, same hook.

## Sync resilience

### Status determination

```ts
function computeSyncStatus(repo: ConnectedRepo, now: Date): SyncStatus {
  if (repo.lastErrorMessage) return "RED";
  if (repo.installationTokenExpired) return "AMBER";
  if (!repo.lastSyncedAt) return "GREY";
  const ageMs = now.getTime() - repo.lastSyncedAt.getTime();
  if (ageMs > 24 * 60 * 60 * 1000) return "GREY";
  return "GREEN";
}
```

Status is computed at read time (in the API endpoint), not stored — keeps the row source-of-truth simple.

### Resync

`POST /repos/{id}/resync` enqueues a scan job (existing scan-high queue) and immediately responds 202. Client optimistically shows spinner; polls `/repos/{id}` every 2s for 10s; falls back to a manual refresh.

## Security

- **Tokens at rest**: SHA256-hashed. Plaintext shown ONCE in create response. Prefix-only displayed in table.
- **Token validation**: hash lookup in `requireUserOrGithubBearer` middleware. O(1) with index.
- **Re-auth gate** on destructive actions: sign-out-all, export, delete. Last login >5 min → prompt for fresh OAuth.
- **CSRF** on connect flow. Reused on token-create + delete-account modals.
- **Rate limit** (1000/hr default, 60/min for `/repos/{id}/resync`).
- **Audit log**: every destructive action writes to existing audit log table with `userId`, `action`, `ip`, `userAgent`.

## Testing

| Layer | Tool | Files |
|---|---|---|
| Unit (server) | Vitest | `src/__tests__/account/*.test.ts` |
| Unit (component) | Vitest + JSDOM | `src/__tests__/components/account/*.test.tsx` |
| SSR | Vitest + Next.js test utils | `src/__tests__/pricing-page.test.tsx`, `src/__tests__/account-page.test.tsx` |
| Cargo | Tauri | `src-tauri/tests/account_*.rs` |
| E2E | Playwright | `e2e/account-flow.spec.ts`, `e2e/connect-disconnect.spec.ts`, `e2e/desktop/account-parity.spec.ts` |

Coverage target: 90% statements on `/api/v1/account/*` and `account/*` components.

## Dependencies / risks

- **Risk R-1**: GitHub App slug may differ from "verified-skill" — agent must look it up at connect-flow runtime (env or DB).
- **Risk R-2**: Existing email mailto sweep may surface in places we don't expect (release notes, blog posts) — agent runs grep across both repos and confirms no false negatives.
- **Risk R-3**: `requireUserOrGithubBearer` extension to accept `vsk_*` tokens must not break existing GitHub-Bearer callers — extend with strict prefix match.
- **Risk R-4**: Tauri WebView must trust verified-skill.com cookies — already does (0831 device-flow uses same pattern). Confirm no CORS regression.

## ADRs

- ADR-0834-01: Component extraction to eval-ui (decided: yes — single-source three-surface rendering).
- ADR-0834-02: Disconnect does NOT call GitHub uninstall (decided: yes — Netlify pattern).
- ADR-0834-03: Tokens hashed with SHA256, prefix-only display (decided: industry standard).
- ADR-0834-04: Soft-delete with 30-day grace (decided: industry standard for SaaS).
- ADR-0834-05: KV cache 60s for connected repos (decided: balances freshness vs read latency).
