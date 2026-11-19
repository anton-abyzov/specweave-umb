# 0898 Team usage view

## Problem

0897 (free-first pricing, approved by Anton 2026-10-12) keeps SpecWithCode free and makes companies pay for hosting, control and support. The strongest reason for a company to pay beyond hosted skills is a question no single developer's app answers: across all our engineers, which Claude, Codex and Cursor seats sit idle, which hit their limits every day, and where did work hand off because of it. Today each SpecWithCode machine knows only its own accounts' usage, and the Switch fleet view (specweave PR #2034) shows one person's Macs over SSH tunnels, not a team.

## Scope

In: an opt-in team view that aggregates per-account usage summaries from members' SpecWithCode machines: remaining 5-hour and weekly windows, limit hits per day, idle days per seat, handoffs and provider switches caused by limits; a team admin page; export as CSV; the privacy boundary below, enforced in code and stated in the UI.
Out: prompts, code, file names, thread titles or any content leaving a machine; billing or seat purchasing; SSO (0842); changing how a single machine reads usage (reuse what SpecWithCode and Switch already read).

## Acceptance Criteria

- [ ] AC-01: A member opts in per machine; nothing is sent before opt-in, and opting out stops sending and deletes that machine's history from the team view.
- [ ] AC-02: Each summary carries only: provider, account label chosen by the member, plan tier if known, window remaining, reset times, limit-hit count, handoff and provider-switch counts, machine label, timestamp. A test fails if any other field is sent.
- [ ] AC-03: The admin page lists every seat with last-30-day idle days, limit hits per day and handoffs caused by limits, sortable, with "idle 14+ days" and "hits a limit most days" filters, and exports CSV.
- [ ] AC-04: Summaries reach the team over the hosted relay (off by default) or a self-hosted endpoint; both authenticate the machine with its pairing, and transport is TLS only.
- [ ] AC-05: The view is part of the Team and Enterprise offer on /pricing only once AC-01..AC-04 pass; until then the pricing page does not mention it.

## Decisions

### Decided

- D-01 (Anton, November 19, 2026): the team view is hosted on verified-skill.com tenants (vskill-platform), not a separate SpecWithCode service. Seats and billing (0840/0841) carry over.
- D-02 (Anton, November 19, 2026): Cursor seats are listed and show "usage not readable yet" while the machine has no Cursor usage reading. When 1415's Cursor reader is switched on and reads, the same row fills in with no change here.

- D-03 (Anton, November 19, 2026, "Member's vsk_ token"): AC-04's "pairing" is the member's own verified-skill.com `vsk_` API token, the one `vskill auth login` stores and the app already reads for skill publishing, with the existing `write` scope; the platform checks the token's user is an `OrgMember` of the tenant. No new token kind or scope. A self-hosted endpoint is an HTTPS URL with its own bearer credential in the app's secret store; the `vsk_` token and the `gh auth token` fallback are never sent to any host but verified-skill.com. Connect (Clerk) is not used: it knows no tenants.
- D-04 (Anton, November 19, 2026, "Yes, migrate"): T-02 adds the `TeamUsageSummary` table described under Approach, "Platform storage", and ships with `release.sh ship platform --migrate` once its PR is reviewed and green. No existing table or row changes.

### Open

(none)

## Approach

Reconciled with the code on November 19, 2026.

**What exists and is reused (app).** Every provider instance publishes `ServerProviderUsageLimits` (`packages/contracts/src/providerUsageLimits.ts`): windows with `kind`, `usedPercent`, `resetsAt`, plus `planLabel`. `UsageLimitHistory` (`apps/server/src/usage/UsageLimitHistory.ts`) records every read per account and window for 14 days; `UsageResetLedger` records closed periods. Cursor, Grok and OpenCode Go readers are switched by 1415; 1411 builds the per-machine Subscriptions board. This increment calls no reader and changes no reader file of 1411 or 1415: it reads the published provider snapshots and `UsageLimitHistory` only, so a reader 1415 switches off simply yields "usage not readable yet". The Switch `get_usage` reader from the October text is not used; the app's own Claude reader supersedes it.

**Counts (app).** From the local projection, per provider instance and UTC day: limit hits = failed runs whose root error item has `failure.class = 'usage_limit'`; provider switches = `limit-fallback:` continuation messages, attributed to the stopped run's instance; handoffs = `limit-handoff-note:` messages (the note a machine-limit handoff leaves on the local thread). Counts only; no thread, message or run id leaves the machine.

**The summary (AC-02).** One summary per opted-in machine per UTC day, re-sent at most hourly while the day is open and its numbers changed. Wire shape, the whole of it:

```json
{ "machineLabel": "…", "at": "ISO time",
  "accounts": [ { "provider": "claudeAgent", "accountLabel": "…", "planTier": "Max 20x",
    "windows": [ { "kind": "session", "remainingPercent": 64, "lowestRemainingPercent": 12, "resetsAt": "ISO time" } ],
    "limitHits": 2, "handoffs": 1, "providerSwitches": 3 } ] }
```

`remainingPercent` is the newest read and `lowestRemainingPercent` the day's lowest from `UsageLimitHistory` (both are "window remaining"). An account with no reading sends `windows: []`, which the platform shows as "usage not readable yet" (D-02). The account label is the member's own text per instance, defaulting to the instance's display name; it is never derived from the email, `accountKey`, `subscriptionKey`, `quotaPoolId` or `credentialFingerprint`. The machine label defaults to the machine's name in SpecWithCode and is editable. A builder copies named fields into a fresh object and an exact-keys schema rejects anything else; the test captures the whole outgoing request (URL, headers, body) from a fixture with every optional provider field set (email, `subscriptionKey`, `quotaPoolId`, `credentialFingerprint`, `externalUsage.url`, credits) and fails on any key outside the list, recursively. Seats on the platform are keyed by token user + machine label + provider + account label; no machine id is sent.

**Opt-in (AC-01).** Off by default, per machine, set only by a person through a guarded RPC (agents and coordinator keys are refused, tested at the server). Kept in `<stateDir>/team-usage.json` (tenant, endpoint, labels), not in shared settings. With it off the reporter makes no request and no token lookup. Opting out stops the timer and sends `DELETE` for that machine label; the delete is retried until the platform confirms it, and the card says "Removing history…" until then.

**Transport (AC-04).** `https://verified-skill.com/api/v1/tenants/:tenantId/usage-summaries` (hosted, off by default) or a self-hosted `https://` URL with the same contract; `http://` is refused, both in the app and by the platform. Credentials per D-03.

**Idle days and the admin page (AC-03).** A seat-day is active when any window's `lowestRemainingPercent` is below the previous reading of that window with the same `resetsAt` (or the day's first reading after a reset is below 100), or when limits were hit. Idle days = days in the last 30 with no active summary from any of the member's machines for that seat. "Hits a limit most days" = limit hits on more than half of the days with a summary. Page: `/orgs/[orgSlug]/usage`, visible to tenant OWNER and ADMIN; CSV from the same rows.

**Platform storage (D-04).** New table `TeamUsageSummary` in `prisma/tenancy.prisma`, one row per tenant, user, machine label, provider, account label and UTC day: `id`, `tenantId` (FK Tenant, cascade), `userId` (FK User, cascade), `machineLabel`, `provider`, `accountLabel`, `day` (date), `planTier?`, `windows` (JSON, the validated windows), `active` (bool), `limitHits`, `handoffs`, `providerSwitches` (int), `reportedAt`, `createdAt`, `updatedAt`; unique on (tenantId, userId, machineLabel, provider, accountLabel, day); indexes (tenantId, day) and (tenantId, userId, machineLabel). Rows older than 35 days are deleted on each write for that tenant, so no cron is added. KV is not used, so there is no KV/DB dual write.

## Review

- Reviewer: openai (gpt-6.1-sol)
- Depth: deep
- Required: yes

Muse is out until November 23, 2026 and Codex is at 100%, so each PR is reviewed on Copilot Enterprise (`acpRegistry_copilot`) with GPT-6.1 Sol, security first for the endpoint and auth, under Anton's standing rule of November 18, 2026 ("Yes, as a standing rule").

## Tasks

### T-01 Local daily usage summary with the field allowlist
- AC: AC-01, AC-02, AC-04 | Files: repositories/anton-abyzov/specwithcode/packages/contracts/src/teamUsage.ts [new], repositories/anton-abyzov/specwithcode/packages/contracts/src/teamUsage.test.ts [new], repositories/anton-abyzov/specwithcode/packages/contracts/src/index.ts [exists], repositories/anton-abyzov/specwithcode/packages/contracts/src/rpc.ts [exists], repositories/anton-abyzov/specwithcode/apps/server/src/teamUsage/ [new], repositories/anton-abyzov/specwithcode/apps/server/src/project/vskillApiToken.ts [new], repositories/anton-abyzov/specwithcode/apps/server/src/project/SkillPublishingAdapter.ts [exists], repositories/anton-abyzov/specwithcode/apps/server/src/server.ts [exists], repositories/anton-abyzov/specwithcode/apps/server/src/ws.ts [exists], repositories/anton-abyzov/specwithcode/apps/server/src/auth/RpcAuthorization.ts [exists], repositories/anton-abyzov/specwithcode/apps/server/src/observability/RpcInstrumentation.ts [exists] | Test: cd repositories/anton-abyzov/specwithcode && node node_modules/vite-plus/bin/vp test run packages/contracts/src/teamUsage.test.ts apps/server/src/teamUsage

### T-05 Opt-in card on the machine
- AC: AC-01, AC-04 | Files: repositories/anton-abyzov/specwithcode/apps/web/src/components/settings/TeamUsageSettings.tsx [new], repositories/anton-abyzov/specwithcode/apps/web/src/components/settings/TeamUsageSettings.test.tsx [new], repositories/anton-abyzov/specwithcode/packages/client-runtime/src/state/server.ts [exists], repositories/anton-abyzov/specwithcode/apps/web/src/components/settings/PrivacySettings.tsx [exists] | Test: cd repositories/anton-abyzov/specwithcode/apps/web && node ../../node_modules/vite-plus/bin/vp test run src/components/settings/TeamUsageSettings.test.tsx
- **Dependencies**: T-01

### T-02 Team endpoint storing summaries per tenant
- AC: AC-04 | Files: repositories/anton-abyzov/vskill-platform/prisma/tenancy.prisma [exists], repositories/anton-abyzov/vskill-platform/prisma/migrations/ [new folder], repositories/anton-abyzov/vskill-platform/src/app/api/v1/tenants/[tenantId]/usage-summaries/ [new], repositories/anton-abyzov/vskill-platform/src/app/api/v1/tenants/usage-orgs/ [new], repositories/anton-abyzov/vskill-platform/src/lib/team-usage/ [new] | Test: endpoint auth and schema tests (`npx vitest run src/lib/team-usage src/app/api/v1/tenants/[tenantId]/usage-summaries`)
- The wire contract is the one under Approach, "The summary"; it does not wait for T-01's code.

### T-03 Admin page and CSV export
- AC: AC-03 | Files: repositories/anton-abyzov/vskill-platform/src/app/orgs/[orgSlug]/usage/ [new], repositories/anton-abyzov/vskill-platform/src/lib/team-usage/ [new] | Test: page renders filters and CSV from fixture data
- **Dependencies**: T-02

### T-04 Pricing page mention after acceptance
- AC: AC-05 | Files: repositories/anton-abyzov/specweave/docs-site/src/pages/pricing.tsx | Test: cd repositories/anton-abyzov/specweave/docs-site && npm run build
- **Dependencies**: T-01, T-02, T-03, T-05, and AC-01..AC-04 passing on the released build
