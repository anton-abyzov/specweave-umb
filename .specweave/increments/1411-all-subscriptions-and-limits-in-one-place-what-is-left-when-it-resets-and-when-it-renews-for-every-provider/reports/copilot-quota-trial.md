---
title: "1411 AC-08: GitHub's documented Copilot quota call, one trial"
increment: 1411
date: November 19, 2026
run by: the build's owner (an agent thread on the M4, acting for Anton)
---

# Copilot `account.getQuota` trial

**Result: no.** The documented call answers from the Copilot CLI's own sign-in, but the reset date it returns is the moment of the call, not the reset. It cannot replace the present reader, which is unchanged (D-05).

## How it was run

- Client: `@github/copilot-sdk` 1.0.34 as published on npm, installed with `--ignore-scripts` in a scratch folder outside every repository (`~/.specwithcode/m4/scratch/2026-11-19-1411-copilot-quota/`). The SDK starts its own bundled CLI, `@github/copilot-sdk-darwin-arm64` 1.0.34.
- Call: `new CopilotClient({ useLoggedInUser: true })`, `client.rpc.account.getQuota({})`, then `client.stop()`. No `gitHubToken` and no `selectionId` were passed.
- Environment: `COPILOT_GITHUB_TOKEN`, `GH_TOKEN` and `GITHUB_TOKEN` removed (`env -u`), and the script refuses to run if any is set.
- `COPILOT_HOME`: unset, so the client used its default, `~/.copilot`.
- The installed Copilot CLI on the machine is `GitHub Copilot CLI 1.0.105`, signed in.
- No agent signed in, no token file was opened, and `account.getCurrentAuth` was not called. The script printed only quota fields, with any key naming a token, login, email or user filtered out.

## What it returned (November 19, 2026, 06:30:11 UTC)

| Quota | Unlimited | Entitlement | Used | Remaining | `resetDate` |
|---|---|---|---|---|---|
| `premium_interactions` | no | 175,000 | 33,775 | 80.7% | `2026-11-19T06:30:12.473Z` |
| `chat` | yes | 0 | 0 | 100% | `2026-11-19T06:30:12.473Z` |
| `completions` | yes | 0 | 0 | 100% | `2026-11-19T06:30:12.473Z` |

`usageAllowedWithExhaustedQuota` and `overageAllowedWithExhaustedQuota` were true for premium requests.

## Against the signed-in CLI

AC-08 counts a yes only when the entitlement and the reset date equal what the signed-in CLI shows for its own login at the same time.

- **Reset date: no.** Every snapshot's `resetDate` was 0.8 seconds after the call started. Copilot's monthly allowance resets on the first of the month at 00:00 UTC (GitHub's billing page, `subscriptionWindowRules.json`), so the next reset is December 1, 2026. The call does not report it.
- **Entitlement: not compared.** Copilot CLI 1.0.105 opened in a pseudo-terminal at 06:31 UTC showed no quota in its footer. It shows quota only after `/statusline` gains the `quota` option, which changes the CLI's saved settings, or after a request, which spends quota. Neither was done. The entitlement of 175,000 is in AI-credit units, not the 300 or 1,500 premium requests of a legacy plan, so its meaning would need checking anyway.

Because the reset date already fails, the entitlement comparison cannot turn the result into a yes. Anton can still compare the entitlement by hand: open `copilot`, add `quota` with `/statusline`, and read the footer.

## What this means

- The present reader (`copilot_internal/user` via `gh auth token`) stays. It is the only one that reports Copilot's reset date.
- If a later SDK fills `resetDate`, run the same script again (it is in the scratch folder above) before planning a change. The amounts it returns (`entitlementRequests`, `usedRequests`) are the same fields the board now shows beside the percent.

Scratch evidence (outside the repository): `~/.specwithcode/m4/scratch/2026-11-19-1411-copilot-quota/trial.mjs`, `trial-sdk.json`, `cli-screen-2.txt`.
