# Referrals from anymodel.dev are counted through to the SpecWithCode download

## Problem

On November 27, 2026 the owner approved plan C + E for AnyModel: an open-model track in SpecWithCode, and anymodel.dev rebuilt as an agent bench. The approval came with a gate. A one-week funnel check decides whether anymodel.dev is worth keeping, and if almost no visitors reach SpecWithCode, the plan switches to D (retire it). Today that check cannot be measured.

- anymodel.dev links to `https://specwithcode.com/?utm_source=anymodel&utm_medium=site`. That URL 301s to `https://spec-weave.com/code/?utm_source=anymodel&utm_medium=site`, keeping the query.
- The live page is built from `repositories/anton-abyzov/specweave/docs-site`. Its click tracking (`docs-site/src/lib/siteEvents.ts`) sends `download_click` and similar events to the relay's `POST /v1/site-events`. The events carry no campaign source, so a download cannot be tied back to anymodel.dev.
- The relay validator (`repositories/anton-abyzov/specwithcode/packages/shared/src/crashReport.ts` `parseSiteEvent`) accepts only six event names. It drops unknown fields.
- Cloudflare Web Analytics on spec-weave.com keeps the referrer host, but it is sampled in steps of 10. Baseline for October 29 to November 27, 2026: 0 page loads referred by anymodel.dev, against 8,820 with no referrer and 430 from Google.
- The relay's site events exist only as Worker log lines. The observability query API refuses the M5 wrangler OAuth token, so counts can be read back only with `wrangler tail`.

## Scope

In:

- The relay accepts a `referral_landing` event and an optional `source` token on every site event, and logs `source`.
- docs-site reads `utm_source` once per page load, keeps it in memory only, and sends one `referral_landing`. It adds `source` to every later event in the same page session, which covers a client-side move to the download page.
- The privacy page says the campaign tag is sent.
- A one-week collector on M5 records site-event lines to a file, plus a daily count script.

Out:

- Cookies, storage or identifiers.
- A database table for counts.
- Changes to anymodel.dev, which belong to increment 1512.
- Attribution across full page reloads after the first page.

## Acceptance Criteria

- [x] AC-01: `parseSiteEvent` accepts `{"v":1,"event":"referral_landing","platform":"other","source":"anymodel","page":"/code/"}`. It keeps a `source` of up to 32 characters matching `[a-z0-9._-]`, lowercased, and drops any other `source` value without rejecting the event. Existing events parse exactly as before.
- [x] AC-02: The relay logs `source` on the `site_event` line when it is present. `docs/operations/relay-observability.md` lists the new event and field.
- [x] AC-03: On spec-weave.com, opening `/code/?utm_source=anymodel` sends one `referral_landing` with `source: "anymodel"`. Its later `download_click`, after moving to `/code/download/` within the same page session, carries `source: "anymodel"`. Without `utm_source`, the events are byte-for-byte as before. Do Not Track still suppresses every send.
- [x] AC-04: The privacy page's description of site events mentions the campaign tag from the link followed (`utm_source`), and says it is not stored in the browser.
- [ ] AC-05: The relay deployed from `main` accepts the new event, shown by a live `wrangler tail` line with `source: "anymodel"` from a headless visit. A collector on M5 has recorded `site_event` lines for 7 days to `~/.specwithcode/m5/evidence/anymodel-funnel/`, and `count.sh` prints per-day totals of `referral_landing` and `download_click` by source.

## Approach

1. **specwithcode** `packages/shared/src/crashReport.ts`:
   - add `referral_landing` to `SITE_EVENT_NAMES`;
   - add `source?: string` to `SiteEvent`;
   - make `parseSiteEvent` keep a valid `source`;
   - add tests next to it.

   Then `infra/relay/src/reports/Reports.ts` logs `source`, with a test in `Reports.test.ts`, and the observability doc gets a line. This merges first: `deploy-relay` runs on every push to main.
2. **specweave** `docs-site/src/lib/siteEvents.ts`:
   - `referralSource(search)`;
   - `startSiteEvents` captures it at start, sends `referral_landing` once, and adds `source` to events;
   - unit tests in `src/lib/__tests__/siteEvents.test.ts`;
   - the privacy text in `docs-site/src/pages/privacy.md`.

   It merges after the relay is live, because an old relay rejects `referral_landing` with 400 (harmless, but uncounted).
3. **Collector.**
   - `scripts/anymodel-funnel/collect.sh` runs `npx wrangler tail <relay worker> --format json --search site_event` in a restart loop and appends JSON lines.
   - `count.sh` groups the lines by day, event and source.
   - Both live in the evidence folder, not a repository: it is a one-off measurement, outside the umbrella.
   - A LaunchAgent is not used. The loop runs as a background process started by this thread and stops after 7 days.

Risks:

- `wrangler tail` samples under heavy load. The site-event volume is a few per hour, so this is not a concern.
- A tail session can drop, so the loop restarts it and the gaps are logged.
- The 301 from specwithcode.com keeps the query (checked November 27, 2026).

Rejected:

- A D1 counters table: a schema change, and the owner asks before migrations.
- sessionStorage: the privacy page promises no storage.
- Cloudflare Web Analytics alone: it is sampled in tens and has no query string.

## Decisions

### Asked
- D-01: Funnel gate → the owner said on November 27, 2026: "If the one-week funnel check shows almost no visitors reaching SpecWithCode, switch to D."
### Defaulted (change any before sw-do)
- D-02: "Almost no visitors" → fewer than 10 `referral_landing` events with source `anymodel` in 7 days, and no `download_click` with that source. Reversible; the owner can set another line.
- D-03: Source token → only the `utm_source` value is sent. `utm_medium` and `utm_campaign` are dropped.
### Open
- none

## Tasks

### T-01 Relay accepts referral_landing and a source token
- AC: AC-01, AC-02 | Files: repositories/anton-abyzov/specwithcode/packages/shared/src/crashReport.ts, repositories/anton-abyzov/specwithcode/packages/shared/src/crashReport.test.ts, repositories/anton-abyzov/specwithcode/infra/relay/src/reports/Reports.ts, repositories/anton-abyzov/specwithcode/infra/relay/src/reports/Reports.test.ts, repositories/anton-abyzov/specwithcode/docs/operations/relay-observability.md | Test: vp test run packages/shared/src/crashReport.test.ts infra/relay/src/reports/Reports.test.ts (in the specwithcode checks copy)

### T-02 spec-weave.com sends the campaign source
- AC: AC-03, AC-04 | Files: repositories/anton-abyzov/specweave/docs-site/src/lib/siteEvents.ts, repositories/anton-abyzov/specweave/docs-site/src/lib/__tests__/siteEvents.test.ts, repositories/anton-abyzov/specweave/docs-site/src/pages/privacy.md | Test: npx vitest run src/lib/__tests__/siteEvents.test.ts (in docs-site)

### T-03 Live check and one-week collector
- AC: AC-05 | Files: ~/.specwithcode/m5/evidence/anymodel-funnel/collect.sh, ~/.specwithcode/m5/evidence/anymodel-funnel/count.sh | Test: INCLUDE_TESTS=1 bash ~/.specwithcode/m5/evidence/anymodel-funnel/count.sh shows the headless check's referral_landing and download_click with source anymodel; plain count.sh leaves test-windows.txt traffic out and lists all-source events per day as the liveness signal
