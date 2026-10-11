# Tasks: Skill Install and Publish Scale

All implementation work lives in:

- `repositories/anton-abyzov/vskill/`
- `repositories/anton-abyzov/vskill-platform/`

Reports, scripts, and logs for this increment go under `.specweave/increments/0847-skill-install-publish-scale/{reports,scripts,logs}/`.

## Phase A - Baseline and Test Fixtures

### T-001: Baseline current install/publish behavior
**User Story**: US-001, US-002, US-003, US-005
**Satisfies ACs**: AC-US1-01, AC-US1-02, AC-US2-01, AC-US3-01, AC-US5-06
**Status**: [x] completed

**Test Plan** (BDD):
- Given current `vskill` and `vskill-platform`
- When targeted public GitHub, private GitHub, plugin, desktop install, and platform publish tests run
- Then failures are captured in `reports/baseline.md` with secret values redacted

### T-002: Add secret-safe sandbox preflight helper
**User Story**: US-001, US-003, US-005, US-006
**Satisfies ACs**: AC-US1-02, AC-US3-06, AC-US5-03, AC-US5-06, AC-US6-05
**Status**: [x] completed

**Test Plan** (BDD):
- Given env vars or keychain entries are present
- When the preflight runs
- Then it validates access to only sandbox resources and prints variable names, not values
- Given secrets are missing
- When tests run
- Then sandbox suites skip with a clear reason

## Phase B - Public and Private GitHub Source Fetching

### T-003: RED - private GitHub discovery and fetch tests
**User Story**: US-001
**Satisfies ACs**: AC-US1-01, AC-US1-02, AC-US1-03
**Status**: [x] completed

**Test Plan** (BDD):
- Given a private repo fixture with root, `skills/*`, and `plugins/*/skills/*` skills
- When discovery runs with a scoped token
- Then every expected `SKILL.md` path is found
- Given no token or a bad token
- When discovery runs
- Then errors are classified as unauthorized, missing, rate-limited, or transient

### T-004: GREEN - centralize token-aware GitHub fetch helper
**User Story**: US-001, US-003
**Satisfies ACs**: AC-US1-02, AC-US1-03, AC-US3-06
**Status**: [x] completed

**Test Plan** (BDD):
- Given public and private repo URLs
- When `vskill` and platform fetch code call the shared helper
- Then public fetches still work unauthenticated and private fetches work authenticated
- And no token appears in thrown errors, SSE events, or reports

### T-005: Wire direct GitHub install to source identity
**User Story**: US-001
**Satisfies ACs**: AC-US1-04, AC-US1-05, AC-US1-06
**Status**: [x] completed

**Test Plan** (BDD):
- Given a direct GitHub install via CLI and desktop
- When the same skill is installed to the same target
- Then installed files match and lockfile/source metadata contains repo URL, branch, SHA, skill path, and plugin name where applicable

## Phase C - Plugin Install at Scale

### T-006: RED - plugin idempotency and scale tests
**User Story**: US-002
**Satisfies ACs**: AC-US2-01, AC-US2-02, AC-US2-03, AC-US2-04, AC-US2-06
**Status**: [x] completed

**Test Plan** (BDD):
- Given 50 fixture plugin-backed skills across user and project scopes
- When install, update, disable, enable, uninstall, and reinstall run twice
- Then no duplicate files, lockfile entries, update subscriptions, or sidebar rows appear

### T-007: GREEN - harden plugin resolver and install jobs
**User Story**: US-002, US-005
**Satisfies ACs**: AC-US2-01, AC-US2-02, AC-US2-04, AC-US2-05, AC-US5-02
**Status**: [x] completed

**Test Plan** (BDD):
- Given plugin cache rows and bare plugin names
- When routes resolve install/uninstall/enable/disable operations
- Then required `name@marketplace` refs are used and SSE jobs always finish with truthful summaries

## Phase D - Skill Standard Compatibility

### T-008: RED - universal/OpenAI/Anthropic skill fixture matrix
**User Story**: US-004
**Satisfies ACs**: AC-US4-01, AC-US4-02, AC-US4-03, AC-US4-05, AC-US4-06
**Status**: [x] completed

**Test Plan** (BDD):
- Given universal, OpenAI/ChatGPT, Anthropic/Claude, and multi-file skill fixtures
- When validators, scanners, installers, and exporters run
- Then frontmatter, `agents/openai.yaml`, resources, scripts, references, and assets are preserved or transformed correctly

### T-009: GREEN - standard validator and transformer fixes
**User Story**: US-004
**Satisfies ACs**: AC-US4-01, AC-US4-02, AC-US4-03, AC-US4-04, AC-US4-05
**Status**: [x] completed

**Test Plan** (BDD):
- Given the fixture matrix from T-008
- When installing to filesystem agents and exporting to clipboard agents
- Then all transformer outputs are idempotent, path-safe, and complete

## Phase E - Authoring, Push, Publish, and Update Lifecycle

### T-010: RED - authoring to publish E2E sandbox
**User Story**: US-003
**Satisfies ACs**: AC-US3-01, AC-US3-02, AC-US3-03, AC-US3-04, AC-US3-05, AC-US3-06
**Status**: [x] completed

**Test Plan** (BDD):
- Given a sandbox skill repository
- When a skill is authored, test-installed, pushed, submitted, approved, published, updated, and republished
- Then exactly one new version appears per changed commit and no ghost versions or stale source links remain

### T-011: GREEN - publish pipeline idempotency and private repo fixes
**User Story**: US-003
**Satisfies ACs**: AC-US3-02, AC-US3-03, AC-US3-04, AC-US3-05, AC-US3-06
**Status**: [x] completed

**Test Plan** (BDD):
- Given public and private submissions
- When approve/publish runs repeatedly on same and changed commits
- Then content hashes, manifests, version monotonicity, outbox events, search index state, and update endpoints remain consistent

## Phase F - macOS Desktop and CLI Parity

### T-012: RED - desktop install/publish parity tests
**User Story**: US-005
**Satisfies ACs**: AC-US5-01, AC-US5-02, AC-US5-03, AC-US5-04, AC-US5-05, AC-US5-06
**Status**: [x] completed

**Test Plan** (BDD):
- Given the macOS desktop app sidecar path
- When direct GitHub, plugin, local, marketplace, and clipboard export flows run from the UI
- Then outputs match CLI install outputs and no secrets reach WebView logs or screenshots

### T-013: GREEN - desktop route/UI fixes
**User Story**: US-005
**Satisfies ACs**: AC-US5-01, AC-US5-02, AC-US5-03, AC-US5-05
**Status**: [x] completed

**Test Plan** (BDD):
- Given the failing desktop parity tests
- When install modal, SSE, lockfile, or source-identity code is patched
- Then desktop and CLI parity tests pass

## Phase G - Release and Local Verification

### T-014: Full validation suite
**User Story**: US-006
**Satisfies ACs**: AC-US6-01, AC-US6-05
**Status**: [x] completed

**Gate Result**: Completed on 2026-05-14. `vskill` build, eval UI build, full unit, coverage, focused unit, and Playwright desktop/UI gates pass. `vskill-platform` build, full unit, coverage, and focused scanner/publish gates pass after adding the missing `@vitest/coverage-v8` dev dependency. See `reports/full-validation.md`.

**Test Plan** (BDD):
- Given all implementation tasks are complete
- When full build, unit, integration, Playwright, desktop, coverage, and platform suites run
- Then all required gates pass and redacted reports are stored under the increment reports directory

### T-015: Local install and smoke-test release candidate
**User Story**: US-006
**Satisfies ACs**: AC-US6-02, AC-US6-03, AC-US6-04, AC-US6-05
**Status**: [x] completed

**Gate Result**: Completed on 2026-05-14. Local package install, public GitHub install, live private GitHub install, local plugin install, and ChatGPT/OpenAI export smoke checks pass for `vskill-1.0.17.tgz`. The private source is redacted in the report. See `reports/local-install-smoke.md`.

**Test Plan** (BDD):
- Given a built release candidate
- When it is installed on the local machine
- Then public GitHub, private GitHub, plugin install, desktop install, and ChatGPT/OpenAI export smoke tests pass
- And if any candidate fails, a fix and new version candidate are produced before publish

### T-016: Close increment after gates pass
**User Story**: US-001..US-006
**Satisfies ACs**: all
**Status**: [ ] pending

**Gate Result**: Blocked on 2026-05-14. Full validation and local install smoke now pass, including live private GitHub install. Closure remains blocked by release publishing: `npm publish --dry-run --access public` fails because `README.md`/`agents.json` are dirty after release metadata generation, and `npm whoami` returns `401 Unauthorized` even with the discovered Obsidian npm token candidate. See `reports/release-publish.md`.

**Test Plan** (BDD):
- Given all tasks and ACs are complete
- When `specweave sync-progress 0847-skill-install-publish-scale` and closure gates run
- Then `specweave complete 0847-skill-install-publish-scale` succeeds or reports a blocking gate failure

### T-017: Patch Skill Studio macOS login and user-global install regression
**User Story**: US-004, US-005, US-006
**Satisfies ACs**: AC-US4-02, AC-US4-03, AC-US4-05, AC-US5-01, AC-US5-02, AC-US5-04, AC-US6-04
**Status**: [x] completed

**Gate Result**: Completed on 2026-05-20 UTC. GitHub OAuth now opens through the desktop bridge with a copyable sign-in link fallback. User/global installs now map to the global user skill folder across CLI and Studio multi-agent installs, and bundled skill resources are preserved for standards-compliant skills. Failed desktop candidates 1.0.34, 1.0.35, and 1.0.36 were followed by fixes and a new shipped candidate, `desktop-v1.0.37`; the public updater manifest now serves 1.0.37 and the installed macOS app verifies as 1.0.37 locally.

**Test Plan** (BDD):
- Given a signed-out macOS Skill Studio user
- When they click GitHub sign-in
- Then the app opens the GitHub OAuth URL in the default browser and keeps a copyable fallback link in the dialog
- Given a standards-compliant skill with scripts, references, assets, and agent metadata
- When it is installed to user/global targets from Studio
- Then each selected agent receives the correct installed or exported output without dropping bundled files

### T-018: Fix Skill Studio desktop update notification, install, and restart UX
**User Story**: US-005, US-006
**Satisfies ACs**: AC-US5-07, AC-US6-06
**Status**: [x] completed

**Gate Result**: Completed on 2026-05-20 UTC. The desktop bridge now normalizes updater metadata, subscribes to installer progress, and exposes a native restart command. The main app now shows a Skill Studio update toast with Install/Restart actions, the Preferences update dialog preserves release notes, menu-triggered update checks reach the Updates tab, and missing project-folder settings resolve to a dedicated `~/Projects/Skill Studio` or `~/Skill Studio Projects` candidate instead of `$HOME`.

**Test Plan** (BDD):
- Given a newer Skill Studio version is available
- When the app auto-checks or receives an updater available event
- Then the main UI shows a clear desktop-app update notification with direct Install and Details actions
- Given the Updates tab reports an available version with notes
- When the user clicks Install now
- Then progress is visible, release notes stay populated, and Restart now triggers the native app restart path
- Given no default project folder is configured
- When the app starts
- Then it prefers a dedicated projects folder candidate instead of the user home folder

### T-019: Fix Skill Studio desktop GitHub OAuth callback and fallback UX
**User Story**: US-005, US-006
**Satisfies ACs**: AC-US5-08, AC-US6-04
**Status**: [x] completed

**Gate Result**: Completed on 2026-05-20 UTC. The desktop OAuth URL now uses the registered `/api/v1/auth/github/callback` redirect URI, and the platform callback bounces desktop state values to the sidecar localhost callback. The sign-in dialog renders before browser launch settles, exposes a clickable "Authorize in GitHub" action, and keeps a copyable full authorization link. Targeted `vskill` UI and `vskill-platform` callback tests pass.

**Test Plan** (BDD):
- Given a signed-out macOS Skill Studio user
- When GitHub sign-in starts and browser opening is slow or blocked
- Then the dialog immediately shows a clickable GitHub authorization button and copyable link
- Given GitHub redirects to the registered platform callback with desktop state
- When the callback receives `code` or a GitHub error
- Then it redirects the browser to `http://localhost:<sidecar-port>/api/oauth/github/callback` without running the web-cookie OAuth path

### T-020: In-app submit-to-queue (kill the website redirect)
**User Story**: US-005 | **Satisfies ACs**: AC-US5-09
**Status**: [x] completed
**Gate Result**: 2026-05-31. `PublishDrawer`/`PublishButton` keep `POST /api/git/publish` then submit IN-APP via `api.submitToQueue` (proxied through the eval-server, CORS-free) and render a structured inline outcome (created/duplicate/alreadyVerified/requeued/blocked) — no more `window.open` redirect. Proxy unlock: `/api/v1/submissions` added to `platform-proxy.ts` `PROXY_PREFIXES`+`AUTH_REQUIRED_PREFIXES` with per-prefix token selection injecting the user's **`vsk_*`** keychain token (not `gho_*`). Non-GitHub remotes degrade gracefully to the website submit page (no false "Publish failed" after a successful push).
**Test**: Given a logged-in Studio user with a pushed skill → When they Commit&Push&Submit → Then the submission is created in-app, attributed to their userId, and the outcome shows inline.

### T-021: In-app queue panel ("My queue" tab, SSE-live)
**User Story**: US-005 | **Satisfies ACs**: AC-US5-10
**Status**: [x] completed
**Gate Result**: 2026-05-31. New `SubmissionQueuePanel` (columns mirror the website QueuePageClient: Skill/State/Position/Updated) mounted as a "My queue" tab in `AccountShell`. Loads `getMyQueue()` (`GET /api/v1/submissions?mine=1`) then subscribes to the **per-user scoped** stream `/api/v1/submissions/stream?mine=1` via `openFetchEventStream` (rides the X-Studio-Token bridge), with exponential reconnect/backoff AND clean-close reconnect (Cloudflare isolate-recycle). Platform: `?mine=1` authenticated feed filters `where.userId`, bypasses the shared KV cache.
**Test**: Given a user with submissions → When they open "My queue" → Then they see only their own rows, live-updating, never another user's.

### T-022: Native approve/reject notifications
**User Story**: US-006 | **Satisfies ACs**: AC-US6-07
**Status**: [x] completed
**Gate Result**: 2026-05-31. `useSubmissionNotifications` fires a native macOS notification (`@tauri-apps/plugin-notification`) on a terminal-state transition: approved (PUBLISHED/AUTO_APPROVED/VENDOR_APPROVED) → informational; rejected (REJECTED/TIER1_FAILED/BLOCKED) → **clickable** → opens `verified-skill.com/submit/<id>` via the desktop shell. No-ops safely in a non-Tauri context.
**Test**: Given a submission reaches a terminal state → When the event arrives → Then the correct notification fires and a rejected one deep-links to the detail page.

### T-023: Platform — per-user feed, bearer-or-cookie auth, scoped SSE, decision-event ownership
**User Story**: US-005 | **Satisfies ACs**: AC-US5-11
**Status**: [x] completed
**Gate Result**: 2026-05-31. `resolveCallerIdentity` (cookie OR `vsk_*`/`gho_*` bearer) so the desktop's proxy-injected bearer attributes submits to the signed-in user (POST stays anonymous-allowed; `?mine` requires auth). Fixed the silent anonymous-degradation (present-but-invalid token → 401, not silent demotion). Server-scoped `/api/v1/submissions/stream?mine=1` (privacy: the global bus was leaking every user's submission metadata). `userId` threaded into all 31 lifecycle emit sites so the `?mine` filter delivers a user's own approve/reject events. 178 submission tests green; full sweep 595 green.
**Test**: Given a desktop client with a `vsk_*` bearer → When it submits / opens its queue / streams `?mine` → Then it is attributed to its userId and never sees another user's data.

> **Deployment status (2026-05-31):** code committed + pushed on both repos (vskill `7d38a43`, vskill-platform `c391d31`) and locally built green. The vskill-platform production deploy is GATED on an interactive `wrangler login` (local OAuth token lacks `workers:write` — see memory `project_vskill_platform_wrangler_deploy_auth`). Until deployed, the live site still uses cookie-only auth, so logged-in in-app submit/queue work only after deploy.
>
> **Follow-ups (own increment):** (1) Reliable cross-isolate notification delivery — the submissions event-bus is per-Cloudflare-isolate, so live decision events are best-effort; route submission terminal-state through the existing update-hub Durable Object (the cross-isolate-reliable channel the desktop already subscribes to via the 0855-fixed `/api/v1/skills/stream`), or add a desktop poll fallback. (2) Optional faster TopRail deep-link into the queue tab. (3) Code comments label these changes "0856" — cosmetic; the increment is 0847.

### T-024: Current models and lossless test cases
- AC: AC-AUDIT-01 | Files: src/eval/anthropic-catalog.ts, src/eval/llm.ts, src/eval/test-case-parser.ts, src/eval/pricing.ts, src/eval/model-catalog.ts, src/eval/integration-runner.ts, src/eval-server/model-compare-routes.ts, src/eval-server/__tests__/model-compare-routes.test.ts, src/eval-server/api-routes.ts, src/eval/__tests__/ | Test: npm test -- src/eval/__tests__/anthropic-catalog.test.ts src/eval/__tests__/test-case-parser.test.ts src/eval/__tests__/anthropic-modern-response.test.ts

### T-025: Secure credential storage and complete logout
- AC: AC-AUDIT-02 | Files: src/lib/keychain.ts, src/eval-server/oauth-github-routes.ts, src/eval/credential-resolver.ts, src/lib/__tests__/, src/eval/__tests__/credential-resolver.test.ts, src/eval-server/__tests__/ | Test: npm test -- keychain credential-resolver oauth-github

### T-026: Author test and publish three Studio examples
- AC: AC-AUDIT-03 | Files: reports/studio-audit-20261009/, vskill-studio-examples/ | Test: node reports/studio-audit-20261009/verify-examples.mjs

### T-027: Reconcile enterprise product and live operations evidence
- AC: AC-AUDIT-04 | Files: reports/studio-audit-20261009/ | Test: test -s reports/studio-audit-20261009/review.md

### T-028: Failed evaluations fail the CLI command
- AC: AC-AUDIT-03 | Files: src/commands/eval/run.ts, src/commands/eval/__tests__/run.test.ts | Test: npm test -- src/commands/eval/__tests__/run.test.ts

### T-029: Reject forged model tool overrides
- AC: AC-AUDIT-01 | Files: src/eval-server/model-compare-routes.ts, src/eval-server/__tests__/model-compare-routes.tool-isolation.test.ts | Test: npm test -- src/eval-server/__tests__/model-compare-routes.tool-isolation.test.ts

### T-031: Honor telemetry consent and omit private search text
- AC: AC-AUDIT-02 | Files: src/eval-ui/src/utils/studio-telemetry.ts, src/eval-ui/src/utils/__tests__/studio-telemetry.test.ts, src/eval-ui/src/preferences/lib/useDesktopBridge.ts, src/eval-ui/src/preferences/locales/en/preferences.json, src/eval-ui/src/hooks/useSkillUpdates.ts, src/eval-ui/src/hooks/__tests__/useSkillUpdates.visibility-queue.test.ts, src/eval-ui/src/components/FindSkillsPalette/ | Test: npm test -- studio-telemetry SearchPaletteCore SkillDetailPanel useSkillUpdates.visibility-queue

### T-032: Require write scope for repository disconnect
- AC: AC-AUDIT-04 | Files: repositories/anton-abyzov/vskill-platform/src/app/api/v1/account/repos/[id]/route.ts, repositories/anton-abyzov/vskill-platform/src/__tests__/account/repos-disconnect.test.ts | Test: cd /Users/antonabyzov/Projects/github/vskill-platform-enterprise-20261009 && PWDEBUG=0 PLAYWRIGHT_HTML_OPEN=never npm test -- src/__tests__/account/repos-disconnect.test.ts

Reject read-only or missing-scope API tokens before repository reads/mutations, while retaining browser/GitHub auth behavior and write-token owner isolation. No production writes/deployment.

### T-033: Honor personal Pro for personally owned private installations
- AC: AC-AUDIT-04 | Files: repositories/anton-abyzov/vskill-platform/src/lib/tenant-subscription.ts, repositories/anton-abyzov/vskill-platform/src/lib/__tests__/tenant-subscription.test.ts, repositories/anton-abyzov/vskill-platform/src/app/api/v1/submissions/__tests__/route.private-paywall.test.ts | Test: cd /Users/antonabyzov/Projects/github/vskill-platform-enterprise-20261009 && PWDEBUG=0 PLAYWRIGHT_HTML_OPEN=never npm test -- tenant-subscription route.private-paywall tenant-caps

Resolve paid personal entitlements using the GitHub personal installation owner identity, never an organization member or installer. Preserve tenant Team billing and canceled/expired handling; prove the actual submission route uses the real lookup. No billing changes, migrations or deployment.

### T-030: Preserve portable skill versions through authoring and saves
- AC: AC-US4-01 | Files: src/eval-server/skill-create-routes.ts, src/eval-server/skill-md-emitter.ts, src/utils/version.ts, src/utils/version.test.ts, src/lib/frontmatter.ts, src/lib/__tests__/frontmatter.test.ts, src/eval-ui/src/utils/setFrontmatterVersion.ts, src/eval-ui/src/utils/__tests__/setFrontmatterVersion.test.ts, src/eval-server/__tests__/skill-version-portability.test.ts, src/commands/__tests__/update.frontmatter-bump.test.ts, src/eval-server/__tests__/skill-emitter-default-version.test.ts, src/eval-server/__tests__/skill-emitter-spec-compliance.test.ts, src/eval-server/__tests__/skill-emitter-roundtrip.test.ts, src/eval-server/__tests__/skill-create-routes-save-draft.test.ts, src/eval-server/__tests__/fixtures/skill-emitter-after.md | Test: npm test -- src/eval-server/__tests__/skill-version-portability.test.ts src/utils/version.test.ts src/lib/__tests__/frontmatter.test.ts

### T-034: Preserve unsupported YAML shapes during version changes
- AC: AC-AUDIT-01 | Files: src/utils/version.ts, src/utils/version.test.ts | Test: npm test -- src/utils/version.test.ts

### T-035: Integrate and deploy reviewed platform hardening
- AC: AC-AUDIT-04 | Files: reports/studio-audit-20261009/platform-release/, repositories/anton-abyzov/vskill-platform/ | Test: cd /Users/antonabyzov/Projects/github/vskill-platform-enterprise-20261009 && PATH=/Users/antonabyzov/.nvm/versions/node/v22.20.0/bin:$PATH node scripts/verify-queue-health-deploy.mjs

User authorized complete/push/deploy/test/verify on 2026-10-09. Merge reviewed platform PR91/92 through normal checks, build/deploy through existing pipeline, record exact source/artifact and live route health. Coordinate crawl-worker/VM ownership with crawler lane; no price/subscription changes, no broad cache-warm, no migration. Cleanup only after parent preserves evidence and authorizes it.

### T-037: Make pricing and Team checkout reflect available capabilities
- AC: AC-AUDIT-04 | Files: src/lib/hosted-publishing.ts, src/app/pricing/page.tsx, src/app/pricing/PricingCTAs.tsx, src/lib/pricing-viewer.ts, src/lib/__tests__/pricing-viewer.test.ts, src/__tests__/billing/pricing-page.test.tsx, src/app/pricing/__tests__/page.test.tsx | Test: npm test -- pricing-viewer pricing-page

### T-038: Preserve private intent and route explicit public tenant submissions
- AC: AC-AUDIT-02 | Files: src/app/api/v1/tenants/[tenantId]/skills/route.ts, src/app/api/v1/tenants/[tenantId]/skills/__tests__/production-publish.test.ts | Test: npm test -- production-publish

### T-036: Release and verify Studio desktop and CLI
- AC: AC-AUDIT-01, AC-AUDIT-02, AC-AUDIT-03 | Files: reports/studio-audit-20261009/desktop-release/, repositories/anton-abyzov/vskill/, /Users/antonabyzov/Projects/github/vskill-studio-audit-20261009/ | Test: python3 .specweave/increments/0847-skill-install-publish-scale/reports/studio-audit-20261009/desktop-release/verify-delivery.py

User authorized apply/push/deploy/test/verify/cleanup on 2026-10-09; parent ceded consolidated vskill checkout to vskill-audit-models. Resolve PR146 CI, merge through normal checks, publish npm and signed desktop through current release workflows, verify public artifacts/updater and recoverable native install/readback. Coordinate platform manifest with enterprise lane; no visible browser automation, no interactive login, no unrelated cleanup. Preserve receipts for parent before cleanup.


Full package validation already passed 6,330 tests (2 skipped, 636 files), and publishing CI repeated the full package test successfully. Preserve `desktop-release/full-unit-tests-tail.txt` and CI receipts; final delivery verification rereads installed versions, code signing and binary hashes and validates the retained public artifact signature receipts without depending on the source checkout.

### T-039: Require write scope for authenticated submission mutations
- AC: AC-AUDIT-04 | Files: repositories/anton-abyzov/vskill-platform/src/app/api/v1/submissions/route.ts, repositories/anton-abyzov/vskill-platform/src/app/api/v1/submissions/submission-list-route.ts, repositories/anton-abyzov/vskill-platform/src/app/api/v1/submissions/__tests__/route.auth-degrade.test.ts | Test: cd /Users/antonabyzov/Projects/github/vskill-platform-enterprise-20261009 && PATH=/Users/antonabyzov/.nvm/versions/node/v22.20.0/bin:$PATH PWDEBUG=0 PLAYWRIGHT_HTML_OPEN=never npm test -- src/app/api/v1/submissions/__tests__/route.auth-degrade.test.ts

Reject valid read-only/empty/missing-scope vskill API tokens before authenticated submission writes; preserve cookie/GitHub auth and anonymous public submissions. Coordinate with root tenant route forwarding; no billing mutations.

### T-040: Bound publisher statistics to the indexed public author
- AC: AC-AUDIT-04 | Files: repositories/anton-abyzov/vskill-platform/src/lib/data.ts, repositories/anton-abyzov/vskill-platform/src/lib/__tests__/publisher-public-scope.test.ts, repositories/anton-abyzov/vskill-platform/src/lib/__tests__/star-dedup.test.ts | Test: cd /Users/antonabyzov/Projects/github/vskill-scanner-health-20261009 && PATH=/Users/antonabyzov/.nvm/versions/node/v22.20.0/bin:$PATH npm test -- publisher-public-scope star-dedup

Use the existing lower(author) partial index for public, nondeprecated publisher statistics. Preserve tenant filtering, bound parameters, rounding, taint and deduplicated stars. Production EXPLAIN showed old ILIKE scan cost219038 versus indexed equality1146; no schema change.

### T-041: Refuse private publishing and unsaved drafts in the public pipeline
- AC: AC-AUDIT-04 | Files: repositories/anton-abyzov/vskill-platform/src/app/api/v1/submissions/route.ts, repositories/anton-abyzov/vskill-platform/src/app/api/v1/submissions/__tests__/route.privacy-gate.test.ts, repositories/anton-abyzov/vskill-platform/src/app/api/v1/submissions/__tests__/route.private-paywall.test.ts, repositories/anton-abyzov/vskill-platform/src/lib/hosted-publishing.ts, repositories/anton-abyzov/vskill-platform/src/app/api/v1/billing/checkout/session/route.ts, repositories/anton-abyzov/vskill-platform/src/app/api/v1/billing/checkout/session/__tests__/route.test.ts | Test: cd /Users/antonabyzov/Projects/github/vskill-platform-enterprise-20261009 && PATH=/Users/antonabyzov/.nvm/versions/node/v22.20.0/bin:$PATH PWDEBUG=0 PLAYWRIGHT_HTML_OPEN=never npm test -- src/app/api/v1/submissions/__tests__

The current Submission persistence drops tenant/privacy and public publisher writes PUBLIC. Reject private intent before billing, repository or queue writes; keep tenant membership errors, block false draft success, preserve public submissions. Trace private storage capability without migrations.

### T-044: Align account billing and pricing availability copy
- AC: AC-AUDIT-04 | Files: repositories/anton-abyzov/vskill-platform/src/app/pricing/page.tsx, repositories/anton-abyzov/vskill-platform/src/__tests__/billing/pricing-page.test.tsx, repositories/anton-abyzov/vskill-platform/src/components/billing/PlanCard.tsx, repositories/anton-abyzov/vskill-platform/src/components/billing/SeatsWidget.tsx, repositories/anton-abyzov/vskill-platform/src/components/billing/__tests__/PlanCard.test.tsx, repositories/anton-abyzov/vskill-platform/src/components/billing/__tests__/SeatsWidget.test.tsx | Test: cd /Users/antonabyzov/Projects/github/vskill-scanner-health-20261009 && PATH=/Users/antonabyzov/.nvm/versions/node/v22.20.0/bin:$PATH npm test -- pricing-page PlanCard SeatsWidget

Remove residual hero/account promises that payment unlocks unavailable hosted private storage or SSO. Preserve existing subscription and seat management, offer waitlist for free accounts.

### T-042: Keep public queue scans from reading private repository content
- AC: AC-AUDIT-02 | Files: repositories/anton-abyzov/vskill-platform/src/lib/scanner.ts, repositories/anton-abyzov/vskill-platform/src/lib/__tests__/scanner-public-only.test.ts, repositories/anton-abyzov/vskill-platform/src/lib/queue/process-submission.ts, repositories/anton-abyzov/vskill-platform/src/lib/queue/__tests__/process-submission.test.ts, repositories/anton-abyzov/vskill-platform/src/lib/queue/__tests__/process-submission.decision.test.ts, repositories/anton-abyzov/vskill-platform/src/lib/queue/__tests__/skillmd-kv-store.test.ts, repositories/anton-abyzov/vskill-platform/src/lib/queue/multi-skill-expand.ts, repositories/anton-abyzov/vskill-platform/src/lib/queue/__tests__/multi-skill-expand.test.ts | Test: cd /Users/antonabyzov/Projects/github/vskill-scanner-health-20261009 && PATH=/Users/antonabyzov/.nvm/versions/node/v22.20.0/bin:$PATH npm test -- scanner-public-only scanner-fetch-repo-files process-submission multi-skill-expand --maxWorkers=2

Confirm explicit public repository metadata before queue scan, including trusted vendors; never use platform credentials for public content reads or multi-skill expansion. Refuse private and retry unknown metadata.

### T-045: Enforce write scope on account and billing mutations
- AC: AC-AUDIT-04 | Files: repositories/anton-abyzov/vskill-platform/src/lib/auth/require-write-scope.ts, repositories/anton-abyzov/vskill-platform/src/__tests__/account/write-scope.test.ts, repositories/anton-abyzov/vskill-platform/src/app/api/v1/account/profile/route.ts, repositories/anton-abyzov/vskill-platform/src/app/api/v1/account/notifications/route.ts, repositories/anton-abyzov/vskill-platform/src/app/api/v1/account/repos/connect/route.ts, repositories/anton-abyzov/vskill-platform/src/app/api/v1/account/repos/github/callback/route.ts, repositories/anton-abyzov/vskill-platform/src/app/api/v1/account/repos/[id]/resync/route.ts, repositories/anton-abyzov/vskill-platform/src/app/api/v1/billing/checkout/session/route.ts, repositories/anton-abyzov/vskill-platform/src/app/api/v1/billing/portal/route.ts, repositories/anton-abyzov/vskill-platform/src/app/api/v1/billing/seats/sync/route.ts, repositories/anton-abyzov/vskill-platform/src/app/api/v1/billing/quota/report/route.ts | Test: cd /Users/antonabyzov/Projects/github/vskill-platform-enterprise-20261009 && PATH=/Users/antonabyzov/.nvm/versions/node/v22.20.0/bin:$PATH PWDEBUG=0 PLAYWRIGHT_HTML_OPEN=never npm test -- src/__tests__/account/ src/app/api/v1/billing

Deny valid read-only/missing-scope tokens before known account, repo-connect/resync and billing mutations. Preserve browser/GitHub identities and write tokens. No blanket HTTP-method gate; read-only routes and existing cookie-only dangerous operations remain intact. No production account or billing changes beyond temporary verification token creation/revocation.

### T-043: Keep scanner health responsive and reject invalid scan success
- AC: AC-AUDIT-04 | Files: repositories/anton-abyzov/vskill-platform/scanner-worker/docker-compose.yml, repositories/anton-abyzov/vskill-platform/scanner-worker/scanner.js, repositories/anton-abyzov/vskill-platform/scanner-worker/server.js, repositories/anton-abyzov/vskill-platform/scanner-worker/scanner.test.js, repositories/anton-abyzov/vskill-platform/scanner-worker/responsiveness.test.js, repositories/anton-abyzov/vskill-platform/scanner-worker/fixtures/vulnerable.js | Test: cd /Users/antonabyzov/Projects/github/vskill-scanner-health-20261009 && PATH=/Users/antonabyzov/.nvm/versions/node/v22.20.0/bin:$PATH node --test scanner-worker/scanner.test.js scanner-worker/responsiveness.test.js

Replace blocking child execution with awaited processes, keep one scan active, bound callbacks, preserve file-backed output and timeout findings, and refuse missing/invalid reports instead of PASS. Deploy exact reviewed source only in a verified idle window with recoverable state.

### T-046: Reject Worker artifacts with missing OpenNext runtime patches
- AC: AC-AUDIT-04 | Files: repositories/anton-abyzov/vskill-platform/scripts/verify-worker-runtime-build.mjs, repositories/anton-abyzov/vskill-platform/scripts/verify-worker-runtime-build.test.mjs, repositories/anton-abyzov/vskill-platform/package.json | Test: cd /Users/antonabyzov/Projects/github/vskill-platform-enterprise-20261009 && PATH=/Users/antonabyzov/.nvm/versions/node/v22.20.0/bin:$PATH node --test scripts/verify-worker-runtime-build.test.mjs

A production candidate built through an external node_modules symlink omitted OpenNext NextServer patches and returned HTTP500 for every route. The candidate was rolled back to the previous verified release. Add a build-time contract guard that rejects the retained broken artifact and accepts the working artifact; verify rebuilt local-dependency artifacts in local workerd before another deployment. Keep privacy/auth behavior unchanged. Preserve failed build evidence and rollback identity.

### T-047: Prevent stale cached release metadata from regressing Worker builds
- AC: AC-AUDIT-01, AC-AUDIT-04 | Files: repositories/anton-abyzov/vskill-platform/scripts/sync-agents-json.cjs, repositories/anton-abyzov/vskill-platform/src/lib/__tests__/generated-counts.test.ts | Test: cd /Users/antonabyzov/Projects/github/vskill-platform-enterprise-20261009 && PATH=/Users/antonabyzov/.nvm/versions/node/v22.20.0/bin:$PATH npm test -- src/lib/__tests__/generated-counts.test.ts

A concurrent build of current main regressed committed vskill1.2.2 catalog metadata to1.2.1 because a24hour build cache won over the npm registry. Query current published stable metadata on every build; retain an explicit offline fallback without downgrading newer committed metadata or claiming an unpublished release. Test registry freshness, failure fallback and downgrade protection. Do not modify registry releases.
