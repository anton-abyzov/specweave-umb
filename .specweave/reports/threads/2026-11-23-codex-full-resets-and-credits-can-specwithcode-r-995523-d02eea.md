---
title: "Codex full resets and credits: can SpecWithCode read and use them"
thread: "thread:delegated-task:command%3Amcp%3A1e1e443e-237e-4f32-89be-f1e75f4a81ec%3Adelegate-task%3Ae74b14e8-9275-414d-bad3-9b36234b0d05"
threadTitle: "ChatGPT resets and credits in Usage"
savedAt: "2026-11-23T03:34:18.973Z"
date: November 22, 2026
machine: m4
type: research
---

# Codex full resets and credits: can SpecWithCode read and use them

**Answer:** yes, and most of it already ships. The Codex app-server returns the reset count, each reset's expiry and the credits balance; SpecWithCode reads them on a native (CLI) Codex sign-in, shows them in Usage, has a Redeem button, and has two opt-in fallback steps (redeem a banked reset, spend credits). The one real gap is a warning before a reset expires unused. Managed ("Sign in with ChatGPT" inside the app) sign-ins still read nothing.

## 1. Where the data comes from

**Codex app-server, `account/rateLimits/read`** (codex-cli 0.162.1, native `~/.codex/auth.json`, read-only probe on m4, November 22, 2026). Fields returned, tokens and account id not printed:

| Field | Value on m4 | Matches the screenshot |
|---|---|---|
| `rateLimits.planType` | `pro` | |
| `rateLimits.primary` | 29% used, 10080-minute window, resets November 26, 2026 10:03 AM EST | "71% left, resets in 3d 11h" |
| `rateLimits.credits` | `hasCredits: true`, `unlimited: false`, `balance: "2153.1974220000"` | "2,154 remaining" (the page rounds up) |
| `rateLimitResetCredits.availableCount` | 3 | "3 Full resets" |
| `rateLimitResetCredits.credits[]` | each has `id`, `resetType: "codexRateLimits"`, `status: "available"`, `grantedAt`, `expiresAt`, `title: "Full reset"` | |
| expiries | November 30, 2026 3:15 PM EST; December 1, 2026 5:44 PM EST; December 12, 2026 5:38 PM EST | the three dates on the page |

Redeeming is `account/rateLimitResetCredit/consume` with only an `idempotencyKey`: it consumes a full reset (both windows). The 5-hour-only or weekly-only choice on the web page is not exposed there, and which credit it takes is decided server-side (not verified as soonest-expiring).

**The web page** (`chatgpt.com/settings/usage`, read from the signed-in Chrome by resource timing only, nothing clicked) calls `backend-api/wham/usage`, `backend-api/wham/rate-limit-reset-credits`, `.../rate-limit-reset-credits/history` and `backend-api/wham/usage/plan_limit_history`. These are the same `wham` backend Codex talks to, but cookie-authenticated and undocumented. Not needed, and not worth using (terms below).

## 2. What SpecWithCode already does (origin/main `214245559`)

| Capability | Where | State |
|---|---|---|
| Read count, soonest expiry, credits balance | `apps/server/src/provider/CodexProvider.ts:615`, `apps/server/src/provider/codexUsageLimits.ts:158` | Native sign-in only; managed passes `skipNativeUsage` (`CodexProvider.ts:878`) |
| Contract | `packages/contracts/src/providerUsageLimits.ts:53` (`availableCount`, `nextExpiresAt`, `nextCreditId`) | Only the soonest expiry is kept, not all three |
| Show in Usage | `apps/web/src/components/usage/UsageLimits.tsx:311` ("3 reset credits banked · next expires in …"), `SubscriptionRow.tsx:208`, `HostLimits.tsx:186`, `ProjectUsageIndicator.tsx:110` | Shipped. Credit balance shows in `CapacityFleet.tsx:766` and the credit recovery card, not in the Subscriptions row |
| Redeem by hand | `ResetCredits` in `UsageLimits.tsx`, `CodexDriver.ts:362` | Shipped, with a confirm |
| Fallback: redeem a reset before switching models | `ProviderFallbackWorker.ts:601` (`providerLimitRedeemResets`), fresh re-read at `:923` | Shipped, off by default |
| Fallback: spend Codex credits | `ProviderFallbackWorker.ts:615` (`providerLimitSpendCredits`) | Shipped, off by default |
| Reset ledger (counts spent or expired resets) | `apps/server/src/usage/UsageResetLedger.ts`, `usageResetLedgerStore.ts` | Shipped |
| **Warn before a reset expires unused** | none found | **Missing** |
| Model tracks count banked resets as headroom | 1339 (12/12 tasks open) | Not built |

## 3. Terms

- Reading through the Codex app-server is reading what OpenAI's own client exposes through its own protocol; no scraping and no cookies. Redeeming through `consume` is the same action the Codex client offers.
- OpenAI help steers users to resets and credits at a limit: "If you need more usage, check the options available on an account you already use, such as eligible credit purchases or usage resets." (cited in `.specweave/increments/1397-named-accounts-per-provider-add-sign-in-and-switch-without-the-terminal/reports/terms-of-service.md`). So spending your own reset or credits is not "circumventing" a limit.
- Calling `chatgpt.com/backend-api/wham/*` with browser cookies would hit "automatically extracting data are prohibited" (Pro tiers help article, same report) and is undocumented. Don't build on it; it would be the only way to cover managed sign-ins.
- Spending resets or credits automatically keeps needing the owner's opt-in (the existing switches, both off).

## 4. Recommendation

**Build one thing: an "unused reset expiring" warning.** When a native Codex account has a reset with `expiresAt` inside 48 hours, show one notification and a Usage banner: "1 full reset expires Nov 30 at 3:15 PM. Use it or lose it", with the existing Redeem button and confirm. One notice per credit id, never automatic redemption.

- **Effort:** about one day, a small increment. Keep every expiry (not just the soonest) in the contract or pass the soonest credit id that already exists, one server check on the existing usage snapshot, one notification, a banner in Usage, tests.
- **Risk:** low. No new provider call, no spend, no terms question. Value: today a reset is worth one full weekly window; the first one on m4 lapses November 30 unless used.

Not recommended now: wiring banked resets into model-track decisions (belongs in 1339, after its resolver lands); reading managed sign-ins (needs the cookie route above); turning on auto-redeem by default.

## Evidence

- Probe script: `~/.specwithcode/m4/scratch/2026-11-22-codex-resets/probe.py` (prints selected fields only)
- Screenshot: `/Users/antonabyzov/.specwithcode/m4/userdata/attachments/project-coordinator-1332065e-795b-4f98-91c4-f114917e53f6-34e35897-8637-4458-863a-1d4cea5e63d2.png`
- m4's Codex sign-in in the app: `setupMode: "existing"` (native), so m4 already reads these numbers.
