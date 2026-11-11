# Automatic crash reports, daily download stats and download click counts

## Problem

When a user's install crashes or a turn fails, nothing reaches us: PostHog is off with no key, OTLP runs only if the user configures it, and the relay's Workers Logs is the only server-side signal. Download numbers per platform per day are not tracked either, and the download buttons on spec-weave.com carry data-track attributes that nothing reads.

## Scope

In: automatic sanitized crash and error reports from the desktop main process, renderer and child processes, the server (fatal failures, failed turns by failure category) and the Expo mobile app, sent to a new relay endpoint and logged as one structured Workers Logs line; an off switch in Settings > Data & privacy and STUDIO_CRASH_REPORTS=false; a daily download snapshot GitHub Action with per-platform deltas and a print script; download click counts on spec-weave.com/code and apps/marketing to a relay site-events endpoint. Out: native iOS/Android (Swift/Kotlin) crash reporting, a crash dashboard, storing reports beyond Workers Logs retention.

## Acceptance Criteria

- [ ] AC-01: A desktop renderer crash (kill -9 of a renderer) on a released build appears in the relay Workers Logs as one crash_report line with version, surface, OS, arch, category and no home path, token or account id.
- [ ] AC-02: Turning off Settings > Data & privacy > Send crash and error reports automatically, or STUDIO_CRASH_REPORTS=false, sends nothing.
- [ ] AC-03: The relay rejects oversized (413), malformed (400) and over-limit (429) reports.
- [ ] AC-04: The download-stats workflow writes a dated snapshot to the download-stats branch and today.mjs prints downloads today by platform.
- [ ] AC-05: A download click on spec-weave.com/code/download produces one site_event line with platform and asset.

## Approach

Shared payload, sanitizer and validator in packages/shared/src/crashReport.ts used by every sender and by the relay. Relay: raw handlers in infra/relay/src/reports/Reports.ts with Cloudflare Rate Limiting bindings per install hash, global and per IP. Server CrashReporter service plus a sync uncaughtExceptionMonitor writing pending files flushed on next start; desktop DesktopCrashReporter for main, render-process-gone, child-process-gone and server child exits. Setting crashReportsEnabled lives in ServerSettings (default true) and the desktop reads the same settings.json. Cloudflare Web Analytics already runs on spec-weave.com via edge injection, so only click counts were added (Web Analytics has no custom events).

## Decisions

### Asked
- D-01 worktree for this work → owner made it by hand (2026-11-10)
- D-02 reports on by default, off switch in settings, env and team rules → owner: "Yes, I agree. Go with the recommended approach." (2026-11-10)
### Defaulted (change any before sw-do)
- D-03 site analytics: keep Cloudflare edge-injected Web Analytics, add relay click counts instead of a third-party tool
### Open
- none

## Tasks

### T-01 Shared payload, relay endpoints, server and desktop reporters, settings UI and docs
- AC: AC-01, AC-02, AC-03 | Files: repositories/anton-abyzov/specwithcode-dev/packages/shared/src/crashReport.ts, repositories/anton-abyzov/specwithcode-dev/infra/relay/src/reports/Reports.ts, repositories/anton-abyzov/specwithcode-dev/apps/server/src/telemetry/CrashReporter.ts, repositories/anton-abyzov/specwithcode-dev/apps/desktop/src/telemetry/DesktopCrashReporter.ts, repositories/anton-abyzov/specwithcode-dev/apps/web/src/components/settings/PrivacySettings.tsx, repositories/anton-abyzov/specwithcode-dev/apps/mobile/src/features/diagnostics/crashReporting.ts | Test: cd repositories/anton-abyzov/specwithcode-dev && ./node_modules/.bin/vp test run packages/shared/src/crashReport.test.ts infra/relay/src/reports apps/server/src/telemetry apps/desktop/src/telemetry/DesktopCrashReporter.test.ts apps/web/src/components/settings/PrivacySettings.test.tsx

### T-02 Daily download snapshot action
- AC: AC-04 | Files: repositories/anton-abyzov/specwithcode-dev/.github/workflows/download-stats.yml, repositories/anton-abyzov/specwithcode-dev/scripts/download-stats/lib.mjs | Test: cd repositories/anton-abyzov/specwithcode-dev && node --test scripts/download-stats/lib.test.mjs

### T-03 Download click counts on the sites
- AC: AC-05 | Files: repositories/anton-abyzov/specweave/docs-site/src/lib/siteEvents.ts, repositories/anton-abyzov/specwithcode-dev/apps/marketing/src/lib/siteEvents.ts | Test: cd repositories/anton-abyzov/specwithcode-dev && ./node_modules/.bin/vp test run apps/marketing/src/lib

### T-04 Release, deploy and verify on this Mac
- AC: AC-01, AC-04, AC-05 | Files: repositories/anton-abyzov/specwithcode-dev/docs/operations/relay-observability.md | Test: cd repositories/anton-abyzov/specwithcode-dev && node scripts/download-stats/today.mjs

### T-05 Verify and close 1283
- AC: AC-01, AC-02, AC-03, AC-04, AC-05 | Files: .specweave/increments/1283-automatic-crash-reports-daily-download-stats-and-download-click-counts/spec.md | Test: specweave verify 1283
