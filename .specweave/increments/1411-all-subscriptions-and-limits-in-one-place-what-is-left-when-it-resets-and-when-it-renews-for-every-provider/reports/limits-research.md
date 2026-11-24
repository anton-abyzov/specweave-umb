---
title: "Limits, resets and renewal dates per provider"
increment: 1411
author: Claude Fable 5.2
second take: Muse Wonder Full 1.0, Extra High (merged in section 4)
date: November 18, 2026
---

# Limits, resets and renewal dates per provider

Read on November 18, 2026. Vendor sentences in quotation marks were copied from the page named beside them. App paths are in `repositories/anton-abyzov/specwithcode` at `origin/main` `c46e2efe5`. Sections 1 to 3 are the first take; section 4 merges the second take (Muse Wonder Full) and says where the two differ.

## 1. Answer

The board Anton asks for ships: Usage > Limits > Subscriptions (increment 1340). It lists every account that has a usage reading, with its windows, what is left, the reset countdown and a renewal date. An account with no reading has no row (`packages/shared/src/usageLimits.ts:78-88`, `:266`, `:705-713`); the first version of this note said "every account", which the review of November 18, 2026 showed to be wrong. Four things keep it from answering his questions:

- An account whose reader is off, or whose provider reports nothing, is not on the board at all.

- No vendor reports a renewal date through a supported interface, so that field is filled only when he sets a day.
- Cursor shows nothing on a Mac unless a Keychain read is turned on, and Cursor documents no way to read usage at all.
- Copilot is read through an undocumented endpoint with a GitHub token. A documented call exists (`account.getQuota`), but nothing shows yet that the app can reach it; 1411 AC-08 records a trial and the reader stays as it is.

"Hourly" today means a five-hour window, and it exists for Claude (Pro, Max), Codex (Plus, Business Standard), OpenCode Go, Antigravity (Google AI Pro and Ultra) and, as a session window of unpublished length, Muse Code. Only Claude, Codex and Muse report what is left in it without a token read. Copilot is monthly. Cursor and Grok are weekly (Cursor's legacy plans monthly). Devin is daily and weekly. No vendor has a one-hour limit.

## 2. Per provider

| Provider | Windows the vendor enforces | What the app reads today | Supported? | Missing |
|---|---|---|---|---|
| Claude Code | Five-hour session and weekly; a separate weekly limit for Fable on some plans; verified Ultra has no five-hour limit | The Agent SDK's usage call and the streamed `rate_limit_event` (`apps/server/src/provider/claudeUsageLimits.ts:1-12`) | The CLI's own call, no token read; the SDK names it experimental (`apps/server/src/provider/ClaudeProvider.ts:531`). The documented surface is the status line | Renewal date |
| Codex (ChatGPT plan) | Five-hour and weekly on Plus and Business Standard; Pro tiers have no five-hour limit (paraphrase, see section 3) | `account/rateLimits/read` on the Codex app-server (`apps/server/src/provider/CodexProvider.ts:584`) | Yes, the CLI's own protocol | Renewal date |
| GitHub Copilot | A monthly allowance in AI credits; reset at 00:00 UTC on the first of the month | `GET https://api.github.com/copilot_internal/user` with a token from the environment or `gh` (`apps/server/src/provider/copilotUsageLimits.ts:48-50`, `:252`) | No. Documented alternative: `account.getQuota` | The right unit; renewal date |
| Cursor | One weekly pool on current plans; two monthly pools on legacy plans; no hourly limit | `api2.cursor.sh` `DashboardService` with Cursor's token from the Keychain or `auth.json` (`apps/server/src/provider/cursorUsageLimits.ts:143-190`); off on macOS by default | No. Nothing documented | Everything on a Mac by default |
| Grok | One shared weekly pool since June 2026 | `cli-chat-proxy.grok.com/v1/billing` with the token from `auth.json` (`apps/server/src/provider/grokUsageLimits.ts:122`, `:162`) | No, reads the token | Plan, renewal date |
| OpenCode Go | Five-hour (20% of the month), weekly (50%, resets Monday 00:00 UTC), monthly (resets with the paid period) | `opencode.ai/zen/go/v1/usage` with the token from `auth.json` (`apps/server/src/provider/openCodeUsageLimits.ts:55-72`) | No, reads the token | Renewal date, though the monthly reset is it |
| Muse Code | Session and weekly, as the CLI reports them; Meta's pages could not be read | `muse usage --json` and `usage/read` (`apps/server/src/provider/Drivers/MuseDriver.ts:195`, `:247`) | The CLI's own command, no token read | Window length, renewal date |
| Antigravity | Pro and Ultra: a quota refreshed every five hours inside a weekly limit; free: weekly | Nothing | No reader documented | Everything; link to its Settings page |
| Gemini CLI | A daily request cap by sign-in type (second take, not re-read) | Nothing | No reader documented | Everything |
| Devin | Daily and weekly (re-read); Max weekly only and Teams shared credits per the second take, not re-read | Nothing | Enterprise API only | Everything; link to its plan page |
| Pi, other ACP agents | Not known | Nothing | | Everything |

## 3. Sources

**Claude.** `https://support.claude.com/en/articles/11647753-how-do-usage-and-length-limits-work`: "Paid plans have two types of usage limits: a session limit that resets every five hours, and weekly limits that reset once every week." "The period starts when you send your first message, and your limit resets in full five hours later." "Weekly limits reset at a fixed time each week that is assigned to your account." "Verified Ultra accounts don't have a five-hour limit." "Your reset day and time stay the same regardless of when you start using Claude or when your subscription begins." The status line receives `rate_limits.five_hour` and `rate_limits.seven_day`, each with `used_percentage` and `resets_at` in epoch seconds, "only for claude.ai Pro, Max, and Ultra subscribers" (`https://code.claude.com/docs/en/statusline`). No page gives a renewal date.

**Codex.** `https://developers.openai.com/codex/pricing` (redirects to `https://learn.chatgpt.com/docs/pricing`; read in part, the page was cut at about 40,000 characters). The three sentences that follow came back from a page reader's summary of that page, not from the page text itself, so treat them as paraphrase until the page is read whole: "Pro plans currently have no five-hour limit." "Weekly limits may also apply." "You can find your current limits in the usage dashboard" (`https://chatgpt.com/codex/settings/usage`). The window rule for Codex in T-01 is not written from them; it is written from what `account/rateLimits/read` returns for the plan. `https://help.openai.com/en/articles/20001498-how-resets-work-in-codex` returned 403 and was not read. No page read gives a renewal date.

**GitHub Copilot.** `https://docs.github.com/en/copilot/concepts/billing/billing-for-individuals`: "your allowance resets to the full monthly amount at 00:00:00 UTC on the first day of each calendar month." "This reset date is fixed and does not change based on your subscription billing date." "in most cases your billing cycle will start on the day you sign up for Copilot." Allowances are in AI credits ("1 AI credit = $0.01 USD"): Pro 1,500, Pro+ 7,000, Max 20,000 a month. `https://docs.github.com/en/copilot/how-tos/copilot-sdk/features/usage-and-billing`: "`account.getQuota` reports the authenticated user's remaining Copilot entitlement", with `entitlementRequests`, `usedRequests`, `remainingPercentage` and `resetDate` ("ISO 8601 date when the quota resets") per snapshot (`premium_interactions`, `chat`, `completions`). The subscription's own billing day is not in that answer.

**Cursor.** `https://cursor.com/help/models-and-usage/usage-limits`: "every paid plan includes one weekly pool of usage for Cursor models"; "your included pool refreshes weekly."; legacy plans: "included usage is split into two monthly pools" and "usage resets monthly with your billing cycle." The CLI's slash commands (`https://cursor.com/docs/cli/reference/slash-commands`) have no usage command, and no page read documents a usage API for a personal account. Only a reset date is documented, not a time.

**Where to look (attribution not verified).** These two sentences sat in the Cursor paragraph; the first names `grok.com`, and neither was re-read on its vendor's page. "open Usage at grok.com/dashboard ... It shows how much of your weekly pool you've used, the next reset date, and your prepaid credit." "The reset date is shown on the Spending tab."

## 4. Second take (Muse Wonder Full 1.0, Extra High)

Independent, same question, nine providers. I checked its code claims at `c46e2efe5` and re-read six of its vendor pages; what follows is what held.

**Where the two takes agree.** Claude and Codex are the only two with a supported, token-free read of what is left and when it resets. No vendor reports a renewal date through a supported interface. Cursor, Grok and OpenCode are read only by holding the vendor's token. Copilot's allowance resets at 00:00 UTC on the first of the month, which is not the billing day.

**Where they differ.** The second take found no documented call for Copilot that returns what is left. The first take's `account.getQuota` was re-read after that and stands: `https://docs.github.com/en/copilot/how-tos/copilot-sdk/features/usage-and-billing` says "`account.getQuota` reports the authenticated user's remaining Copilot entitlement.", with `entitlementRequests` ("Requests included in the entitlement, or `-1` for unlimited"), `usedRequests`, `remainingPercentage` and `resetDate`. Two cautions from the same page: the amounts are in requests, while the billing page counts AI credits, and the call reads "the connection's global auth context" unless a GitHub token is passed. Whether the app's `copilot --acp` connection answers it is H1 in the spec.

**What the second take added, verified.**

- Claude's reader calls `usage_EXPERIMENTAL_MAY_CHANGE_DO_NOT_RELY_ON_THIS_API_YET` (`apps/server/src/provider/ClaudeProvider.ts:531`). It reads no token, but the vendor does not promise it.
- Codex's `account/rateLimits/read` is documented: "`usedPercent` is current usage within the quota window." "`windowDurationMins` is the quota window length." "`resetsAt` is a Unix timestamp (seconds) for the next reset." (`https://learn.chatgpt.com/docs/app-server`, read verbatim).
- A window in the contract is a percent only (`packages/contracts/src/providerUsageLimits.ts:20-32`). Copilot's `entitlement` and `remaining` are parsed and dropped (`apps/server/src/provider/copilotUsageLimits.ts:67-70`).
- `renewsAt` and `planLabel` are written by no reader. Cursor's `billingCycleEnd` on legacy plans and OpenCode Go's monthly reset are renewal dates by the vendors' own wording and are used only as window resets.
- OpenCode Go (`https://opencode.ai/docs/go/`, verbatim): "The 5-hour limit is 20% of your monthly allowance. The window starts when you first use your allowance and lasts five hours." "The weekly limit is 50% of your monthly allowance. It resets on Monday at 00:00 UTC." "Your monthly allowance resets when a new paid period starts."
- Grok (`https://docs.x.ai/grok/faq`, verbatim): "you get one shared weekly usage pool that you can spend however you like across any Grok product." "The usage pool limit resets every week on a schedule shown in the Usage tab in Settings."
- Antigravity (`https://antigravity.google/docs/plans`, verbatim): "A high, generous quota, refreshed every five hours until the weekly limit is reached" (Google AI Pro). "You can view baseline quota usage across models on the Settings page".
- Devin (`https://docs.devin.ai/desktop/accounts/quota`, verbatim): "Your quota resets on a daily and weekly basis, based on the calendar date."
- `packages/shared/src/providerUsageLinks.ts` links four vendors only.
- The Muse Code login watcher reads Muse's `auth.json` for the email and sign-in kind (`apps/server/src/provider/loginWatch.ts:88-112`). It uses no token, and it is one more login-file read for 1401 D-01.

**Not verified, kept out of the spec.** Its Gemini CLI numbers, Cursor's team Admin API limits, Devin's enterprise endpoints, the GitHub REST usage reports, and everything it marked "from memory, unverified". Meta's Muse pages returned 401 to it, so nothing about Muse's plans is from the vendor.

**Its three suggestions.** Publish the plan and the renewal date from data already read; carry amounts beside the percent; give providers with no reader a row with the published windows and a link. All three are in the spec (AC-01 to AC-04).

## 5. What could not be read

- `https://help.openai.com/en/articles/20001498-how-resets-work-in-codex`: 403.
- The second half of `https://learn.chatgpt.com/docs/pricing` and of `https://cursor.com/docs/models-and-pricing`: cut by the reader. The Cursor quotes are from the part that was read. The Codex pricing sentences came back the same way to both takes, as a reader's summary of the part past 40,000 characters, so they agree but are still not verbatim (section 3).
- What the board shows on the installed app (1.0.338) was not looked at; the statements about the board are from the code.

Corrections from the review of November 18, 2026 (its S2):

- The Cursor citation `cursorUsageLimits.ts:143-190` in section 2 leaves out the endpoint and the request, which are at `cursorUsageLimits.ts:23` and `:198-207`.
- A `grok.com/dashboard` quote sat inside the Cursor paragraph of section 3. It now has its own paragraph there, marked as not verified.
- Sections 1 and 2 state a Muse Code session window, while Meta's pages could not be read. The window is what the CLI reports (`muse usage --json`); its length and whether every plan has it are not confirmed by any vendor page.
