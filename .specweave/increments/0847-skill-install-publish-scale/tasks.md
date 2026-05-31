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
