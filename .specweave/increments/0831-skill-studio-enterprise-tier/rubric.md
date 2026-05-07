---
increment: 0831-skill-studio-enterprise-tier
title: "Skill Studio enterprise tier — quality contract rubric"
generated: "2026-05-07"
source: sw-planner
version: "1.0"
status: active
---

# Quality Contract Rubric: 0831-skill-studio-enterprise-tier

Review and customize criteria (change severity, add/remove) before implementation begins.

---

## Functional Correctness (one criterion per AC cluster)

### R-001: GitHub device-flow sign-in UX [blocking]
- **Source**: AC-US1-01, AC-US1-02, AC-US1-03, AC-US1-06
- **Evaluator**: sw:grill
- **Verify**: Sign-in panel shows 8-character user code; "Open GitHub" launches browser to `github.com/login/device` via Tauri shell plugin; polling respects `interval` and stops on granted/denied/expired; errors show inline retry — studio never hangs or crashes.
- **Threshold**: All four ACs pass Playwright smoke; no client secret present in compiled binary
- **Result**: [ ] PENDING

### R-002: Token stored in OS keychain (never in plaintext) [blocking]
- **Source**: AC-US1-04, AC-US2-02
- **Evaluator**: sw:grill
- **Verify**: After successful device-flow, `settings.json` contains no `access_token` field; macOS Keychain Access shows entry under service `vskill`; after sign-out, entry is removed.
- **Threshold**: `grep -r "gho_" ~/.vskill/` returns nothing; Keychain entry present/absent as expected
- **Result**: [ ] PENDING

### R-003: Sign-in sidebar state — avatar, tier badge, sign-out [blocking]
- **Source**: AC-US1-05, AC-US2-01, AC-US2-03, AC-US2-04, AC-US2-05
- **Evaluator**: sw:grill
- **Verify**: After sign-in, sidebar shows avatar + login + tier badge pulled from `/api/v1/billing/quota`; "Sign out" is accessible from the user menu; sign-out clears cached repo metadata and reverts all tier-gated features to free state; offline revocation produces correct toast.
- **Threshold**: All five ACs pass Vitest + Playwright assertions
- **Result**: [ ] PENDING

### R-004: Home-directory disambiguation modal [blocking]
- **Source**: AC-US3-01, AC-US3-02, AC-US3-03, AC-US3-04, AC-US3-06
- **Evaluator**: sw:grill
- **Verify**: Picking `os.homedir()` shows warning modal with correct copy; "Pick again" and "Use home anyway" actions work; `~/.claude/` subtree labeled as personal-scope; non-git project folder treated as project root; invalid/non-existent path shows inline error.
- **Threshold**: All six ACs verified in Vitest component tests + T-027 parameterized classifier suite
- **Result**: [ ] PENDING

### R-005: Recent folders persist across restart [blocking]
- **Source**: AC-US3-05
- **Evaluator**: sw:grill
- **Verify**: Last 5 picked folders returned in MRU order after app restart; confirmed home-dir picks stored with `confirmed: true` flag so warning does not re-fire.
- **Threshold**: T-014 integration test passes; `settings.json` diff shows `recents.projectFolders` populated
- **Result**: [ ] PENDING

### R-006: Connected-repo widget — all render states [blocking]
- **Source**: AC-US4-01, AC-US4-02, AC-US4-03, AC-US4-04, AC-US4-05, AC-US4-06, AC-US4-07
- **Evaluator**: sw:grill
- **Verify**: Widget renders correctly for `not-git`, `local-only`, `external-git`, `github-public`, `github-private-locked`; lock icon has correct `aria-label`; sync state pill text matches `git status`/`rev-list` output; "Refresh" button and FS-watcher debounce work.
- **Threshold**: All seven ACs pass Vitest RTL tests; axe-core finds no accessibility violations on widget
- **Result**: [ ] PENDING

### R-007: 50-skill counter visible + warning color at 45-50 [blocking]
- **Source**: AC-US5-01, AC-US5-02, AC-US5-06, AC-US5-07
- **Evaluator**: sw:grill
- **Verify**: Status bar shows `N/50` for free tier and "Unlimited" for Pro; warning yellow applied at counts 45-50; counter sums project roots + personal-scope deduplicated by `name@version`; count computed locally, reconciled with cache (no per-create API call).
- **Threshold**: Vitest tests for counts 44, 47, 50 pass; Rust unit test for skill-counting dedup logic passes
- **Result**: [ ] PENDING

### R-008: 51st-skill paywall hard-blocks create [blocking]
- **Source**: AC-US5-03, AC-US5-04, AC-US5-05
- **Evaluator**: sw:grill
- **Verify**: On 51st create attempt no skill file is written; PaywallModal appears with correct copy; "Upgrade" opens pricing URL; "Maybe later" closes; existing grandfathered skills remain visible/editable; focus trap + ESC work.
- **Threshold**: Integration test confirms IPC returns `blocked: true` with no FS side-effects; Playwright PaywallModal keyboard test passes
- **Result**: [ ] PENDING

### R-009: Quota force-sync race condition resolved [blocking]
- **Source**: AC-US5-04, AC-US5-07
- **Evaluator**: sw:grill
- **Verify**: If user just upgraded to Pro and cache is stale, background force-sync with `?fresh=1` dismisses the paywall and allows create; on 5s timeout create remains blocked; no partial write in any failure path.
- **Threshold**: Async race integration test passes for both "sync succeeds" and "sync times out" branches
- **Result**: [ ] PENDING

### R-010: `GET /api/v1/billing/quota` — correct shape for all tiers [blocking]
- **Source**: AC-US6-01, AC-US6-02, AC-US6-04, AC-US6-05, AC-US6-06
- **Evaluator**: sw:grill
- **Verify**: 401 for anonymous; free → `skillLimit:50`; pro/enterprise → `skillLimit:null`; all responses include `serverNow` ISO timestamp; OpenAPI doc matches actual response; T-028 integration tests cover all four states.
- **Threshold**: All T-028 test cases GREEN; `curl` against staging returns correct shapes
- **Result**: [ ] PENDING

### R-011: `POST /api/v1/billing/quota` — telemetry upsert + rate-limit [blocking]
- **Source**: AC-US6-03, AC-US6-04, AC-US6-05
- **Evaluator**: sw:grill
- **Verify**: POST updates `lastReportedSkillCount` and `quotaSyncedAt`; 7th POST within 60s returns 429 with `Retry-After` header.
- **Threshold**: T-028 rate-limit test case GREEN; DB inspection shows correct field values after POST
- **Result**: [ ] PENDING

### R-012: GitHub App CTA — Pro only, correct URL, state-token validation [blocking]
- **Source**: AC-US7-01, AC-US7-02, AC-US7-03, AC-US7-04, AC-US7-05, AC-US7-06
- **Evaluator**: sw:grill
- **Verify**: Free-tier user sees TierGate (not install CTA); Pro-tier user sees "Install GitHub App" CTA; CTA opens correct URL with state token; deep-link callback triggers re-detect; post-install shows "GitHub App connected" badge; uninstall reverts to `private-needs-app`.
- **Threshold**: All six ACs pass Vitest + deep-link handler tests
- **Result**: [ ] PENDING

### R-013: Tier gates — inline, non-nagging, single canonical upgrade URL [blocking]
- **Source**: AC-US8-01, AC-US8-02, AC-US8-03, AC-US8-04, AC-US8-05, AC-US8-06
- **Evaluator**: sw:grill
- **Verify**: `TierGate` is inline (no modal); all "Upgrade" buttons use same `PRICING_URL` constant; anonymous users get "Sign in" prompt; `tierFeatures` lookup is the single change point; copy snapshot passes dark-pattern wordlist linter.
- **Threshold**: All six ACs pass; wordlist linter finds no forbidden phrases
- **Result**: [ ] PENDING

### R-014: Pricing page — SSR, three columns, SEO meta, waitlist [blocking]
- **Source**: AC-US9-01, AC-US9-02, AC-US9-03, AC-US9-04, AC-US9-05
- **Evaluator**: sw:grill
- **Verify**: `/pricing` renders without JS; three columns present; `<title>`, `<meta name="description">`, OG image present; waitlist POST upserts correctly; `/account/subscription` placeholder exists; "Pricing" in nav.
- **Threshold**: Playwright test with `javaScriptEnabled: false` passes all assertions; Vitest waitlist unit test GREEN
- **Result**: [ ] PENDING

### R-015: 7-day offline grace period — serverNow-based clock [blocking]
- **Source**: AC-US10-01, AC-US10-02, AC-US10-03, AC-US10-04, AC-US10-05, AC-US10-06
- **Evaluator**: sw:grill
- **Verify**: Cache considered fresh for exactly 7 days from `serverNow`; free-tier cap still enforced from stale cache; single non-intrusive toast on sync failure (no repeated toasts); successful sync resets clock; app launches silently attempt sync.
- **Threshold**: T-029 boundary tests at day 6/7/8 all pass; clock-skew `clockSkewMs` applied in all comparisons
- **Result**: [ ] PENDING

---

## Infrastructure Criteria

### R-016: Test coverage — unit 95%, integration 90% [blocking]
- **Source**: spec.md coverage targets
- **Evaluator**: sw:grill
- **Verify**: `cargo tarpaulin` for Rust modules (auth, project, quota) reports ≥95% line coverage; Vitest coverage for TypeScript components reports ≥90%.
- **Threshold**: Coverage reports show no module below threshold; CI pipeline enforces threshold
- **Result**: [ ] PENDING

### R-017: E2E Playwright auth-flow spec passes in CI [blocking]
- **Source**: T-030
- **Evaluator**: sw:grill
- **Verify**: `npx playwright test e2e/desktop/auth-flow.spec.ts` exits 0 with no real Keychain or GitHub API calls made; all 8 assertion screenshots captured.
- **Threshold**: CI run shows 0 failures; stub injection confirmed via network log showing no `api.github.com` requests
- **Result**: [ ] PENDING

### R-018: No token in settings.json, logs, or crash reports [blocking]
- **Source**: ADR-0831-01, Non-functional security requirements
- **Evaluator**: sw:grill
- **Verify**: `grep -rI "gho_\|ghp_\|github_pat_" ~/.vskill/ ~/.config/vskill/ /tmp/` returns nothing after normal sign-in + sign-out cycle; crash report fixture (if crash reporting is enabled) contains no auth headers.
- **Threshold**: Zero matches on grep; confirmed by code review of `reqwest` log middleware configuration
- **Result**: [ ] PENDING

### R-019: Sidebar.tsx stays under 1500-line limit [non-blocking]
- **Source**: CLAUDE.md §Limits
- **Evaluator**: sw:grill
- **Verify**: `wc -l repositories/anton-abyzov/vskill/src/eval-ui/src/components/Sidebar.tsx` ≤ 1500 after UserMenu + ConnectedRepoWidget are wired in.
- **Threshold**: Line count ≤ 1500; extract to sub-components if over limit
- **Result**: [ ] PENDING

### R-020: Prisma migration is reversible and doesn't break existing rows [blocking]
- **Source**: T-001, ADR-0831-04
- **Evaluator**: sw:grill
- **Verify**: `npx prisma migrate reset` on a populated test DB + re-apply migration succeeds; all existing `User` rows have `tier = FREE` after migration; `PricingWaitlist` table created with correct unique constraint.
- **Threshold**: Migration up + down cycle completes without errors; existing user count unchanged
- **Result**: [ ] PENDING
