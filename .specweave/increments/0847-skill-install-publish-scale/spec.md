---
increment: 0847-skill-install-publish-scale
title: Skill Install and Publish Scale - Plugin and GitHub Repository Flows
type: feature
priority: P1
status: completed
created: 2026-05-14T00:00:00.000Z
structure: user-stories
test_mode: TDD
coverage_target: 90
---

# Feature: Skill Install and Publish Scale - Plugin and GitHub Repository Flows

## Overview

Harden and verify the full skill lifecycle at scale across the `vskill` desktop/CLI and `vskill-platform` registry:

- Author a standards-compliant skill.
- Install it from local/plugin sources.
- Install it directly from GitHub repositories, including public and private repositories.
- Push updates to GitHub and detect/publish new versions.
- Publish through verified-skill.com without invisible or duplicated registry state.
- Install from the macOS desktop app and from the `vskill` command with equivalent results.
- Export or transform the same skill for OpenAI/ChatGPT, Anthropic/Claude, and other supported agent formats.

Secrets are local test inputs only. Values may be loaded from repo `.env*` files and the configured Obsidian credential notes, but must never be printed, committed, written into reports, or copied into fixtures. Test reports may mention only variable names and pass/fail status.

## Personas

### P-001: Skill Author
A user authoring a skill locally who expects edit, test-install, push, submit, publish, update, and reinstall to work without manual file surgery.

### P-002: Private Repository Publisher
A user with a private GitHub repository containing `SKILL.md`, `skills/*/SKILL.md`, or `plugins/*/skills/*/SKILL.md`. They expect authenticated discovery, scanning, publishing, and install to work exactly like public repository flows.

### P-003: Desktop-First User
A macOS app user who clicks through the Studio UI instead of using the terminal. They expect install/publish progress to stream clearly and to finish with the same files and versions the CLI would produce.

### P-004: Multi-Agent User
A user installing one skill into Claude, Codex, Cursor, Copilot, ChatGPT/OpenAI, Anthropic-compatible formats, Aider, Windsurf, and other supported agents. They expect each target to receive the right format, not a lossy copy.

## Scope

In scope:

1. Baseline and harden `vskill` direct GitHub install from public and private repositories.
2. Baseline and harden plugin install via Claude plugin cache/CLI routes and local plugin sources.
3. Verify skill authoring, test-install, promote, push, submit, approve, publish, version bump, update detection, and reinstall.
4. Verify ChatGPT/OpenAI clipboard/export and Anthropic/Claude plugin/skill compatibility according to the current skill standard.
5. Verify macOS desktop app flows and CLI flows share the same lifecycle behavior.
6. Add automated public/private sandbox coverage and secret preflight guards.
7. Release patched `vskill` and `vskill-platform` versions locally and, after tests pass, through the existing release commands.

Out of scope:

- Adding a new paid feature tier.
- Adding new unrelated agent targets.
- Changing Apple entitlements unless a failing notarization test proves it is required.
- Exposing secret values in docs, logs, screenshots, or test fixtures.

## User Stories

### US-001: Direct GitHub Install Works for Public and Private Repositories (P1)
**Project**: vskill

**As a** skill user
**I want** to install skills directly from a GitHub repository
**So that** I can use skills without first packaging them as marketplace plugins.

**Acceptance Criteria**:
- [x] **AC-US1-01**: Public GitHub repositories are discovered through root `SKILL.md`, `skills/<name>/SKILL.md`, and `plugins/<plugin>/skills/<name>/SKILL.md` paths.
- [x] **AC-US1-02**: Private GitHub repositories are discovered with an authenticated token path and do not fall back to unauthenticated raw URLs when a token is available.
- [x] **AC-US1-03**: Private repository failures distinguish `401/403 unauthorized`, `404 missing`, rate limit, and transient network errors in CLI and desktop UI.
- [x] **AC-US1-04**: `vskill install <github-ref>` and the desktop install modal produce equivalent installed files for the same skill and agent target.
- [x] **AC-US1-05**: Lockfile/source metadata records enough provenance to check updates later: normalized repo URL, branch, commit SHA, skill path, and plugin name when applicable.
- [x] **AC-US1-06**: Path traversal and unsafe ref strings are rejected before any filesystem write.

---

### US-002: Plugin Install Scales and Stays Idempotent (P1)
**Project**: vskill

**As a** user installing skills from plugins
**I want** plugin-backed skills to install, update, disable, and uninstall cleanly
**So that** plugin packaging is a reliable distribution path.

**Acceptance Criteria**:
- [x] **AC-US2-01**: Claude plugin cache discovery handles installed, enabled, disabled, user-scope, and project-scope plugins without requiring the removed `claude plugin list` command.
- [x] **AC-US2-02**: Bare plugin names resolve to `name@marketplace` where required for enable, disable, uninstall, and install commands.
- [x] **AC-US2-03**: Plugin-backed skills dedupe against direct GitHub and marketplace copies using stable source identity, not only display name.
- [x] **AC-US2-04**: Re-running the same plugin install is idempotent: no duplicate files, duplicate lockfile entries, duplicate update subscriptions, or duplicated sidebar rows.
- [x] **AC-US2-05**: Plugin install errors stream through the desktop SSE UI with actionable status and do not leave jobs stuck.
- [x] **AC-US2-06**: Plugin install/uninstall tests cover at least 50 fixture skills and mixed scope installs.

---

### US-003: Authoring, Push, Submit, Publish, and Version Updates Are One Reliable Loop (P1)
**Project**: vskill-platform

**As a** skill publisher
**I want** the authoring-to-publish loop to preserve version and provenance
**So that** verified-skill.com shows the latest reviewed skill without ghost versions or stale source links.

**Acceptance Criteria**:
- [x] **AC-US3-01**: A local authored skill can be test-installed, pushed to GitHub, submitted, scanned, approved, published, and reinstalled from the registry in an automated sandbox.
- [x] **AC-US3-02**: Republish detects changed SKILL.md content by canonical content hash and creates exactly one new `SkillVersion` row per new commit.
- [x] **AC-US3-03**: Publishing rejects non-monotonic versions, missing versions when required, malformed semver, and changed post-scan content with clear states.
- [x] **AC-US3-04**: Publishing a skill with multiple files records a stable manifest and diff summary; rerunning publish on the same commit is idempotent.
- [x] **AC-US3-05**: Platform search, skill detail, versions, diff, update check, and install tracking endpoints all surface the newly published version.
- **AC-US3-06** (moved 2026-10-11 to 0896-hosted-private-skill-publishing as AC-03; hosted private publishing is not implemented and stays behind HOSTED_PRIVATE_PUBLISHING_AVAILABLE=false): Public and private publish sandboxes both pass, with private access using scoped GitHub credentials only.

---

### US-004: Skill Standard Compatibility Covers OpenAI, ChatGPT, Anthropic, and Universal Skills (P1)
**Project**: vskill

**As a** multi-agent user
**I want** one skill source to install or export correctly across agent standards
**So that** I do not maintain separate copies for each AI tool.

**Acceptance Criteria**:
- [x] **AC-US4-01**: `SKILL.md` validation enforces required frontmatter (`name`, `description`) and preserves optional fields (`version`, `author`, `metadata`, `agents/openai.yaml`) without data loss.
- [x] **AC-US4-02**: Claude/Anthropic-compatible filesystem installs preserve full `SKILL.md` content and bundled resources.
- [x] **AC-US4-03**: ChatGPT/OpenAI Tier 3 export emits a complete paste-ready blob and, when `agents/openai.yaml` exists, preserves the OpenAI-facing metadata in the export path.
- [x] **AC-US4-04**: Per-agent transformers for Cursor, Copilot, Aider, Windsurf, Continue, and related targets are idempotent and path-safe.
- [x] **AC-US4-05**: Large skills with `scripts/`, `references/`, `assets/`, nested agent metadata, and multi-file resources install without truncation.
- [x] **AC-US4-06**: Generated fixtures include a universal skill and a provider-specific skill, and both pass scanner, install, export, and update tests.

---

### US-005: macOS Desktop App and CLI Have Parity (P1)
**Project**: vskill

**As a** desktop app user
**I want** the macOS Studio UI to perform the same lifecycle actions as the CLI
**So that** I can author, install, push, publish, and update skills from the app with confidence.

**Acceptance Criteria**:
- [x] **AC-US5-01**: Desktop install modal covers direct GitHub, plugin, local authored, marketplace, and clipboard-export targets.
- [x] **AC-US5-02**: Desktop progress streams are replayable and finish with a truthful success/error summary.
- [x] **AC-US5-03**: Desktop cannot expose GitHub, NPM, Cloudflare, database, or platform tokens to the WebView or logs.
- [x] **AC-US5-04**: Desktop E2E runs on macOS using the sidecar/server path that users actually ship.
- [x] **AC-US5-05**: CLI and desktop parity tests compare file outputs, lockfile metadata, source identity, and version displayed in the sidebar/detail panel.
- [x] **AC-US5-06**: Missing secrets cause clear test skips, not false failures.
- [x] **AC-US5-07**: Skill Studio desktop app updates surface as a clear notification in the main UI, and the Install flow downloads, installs, and offers a real restart action.
- [x] **AC-US5-08**: Desktop GitHub OAuth uses the registered GitHub callback URL, bounces desktop state back to localhost, and shows a clickable/copyable authorization fallback before browser-open settles.

---

### US-006: Release Loop Verifies, Installs Locally, and Publishes New Versions (P1)
**Project**: vskill

**As a** maintainer
**I want** every fix cycle to end in tested local installs and releasable versions
**So that** broken skill install/publish paths do not linger between releases.

**Acceptance Criteria**:
- [x] **AC-US6-01**: Full validation runs `npm run build`, `npx vitest run`, `npx playwright test`, desktop sidecar/build checks, platform build/tests, and targeted private/public sandbox suites.
- [x] **AC-US6-02**: The release script bumps versions only after tests pass and updates package metadata consistently.
- [x] **AC-US6-03**: The newly built `vskill` package is installed on the local machine and smoke-tested with public GitHub, private GitHub, plugin, and ChatGPT/OpenAI export flows.
- [x] **AC-US6-04**: Any failed release candidate is followed by a fix and a new version candidate rather than reusing the same broken version.
- [x] **AC-US6-05**: Reports are written only under `.specweave/increments/0847-skill-install-publish-scale/reports/` and contain no secret values.
- [x] **AC-US6-06**: Desktop update notification and install/restart behavior are covered by focused automated tests before the next release.

## Functional Requirements

### FR-001: Authenticated GitHub Fetching
All GitHub repository discovery and file fetch paths must support a token-aware path for private repositories. Token values stay in process memory only and are sourced from environment or keychain, never committed.

### FR-002: Source Identity Contract
Every installed or published skill must carry stable identity: `sourceType`, `repoUrl`, `branch`, `commitSha`, `skillPath`, `pluginName`, `version`, and `contentHash` where available.

### FR-003: Install Dispatcher Contract
The install dispatcher must isolate per-agent failures, return one result per target, and never let one failed transformer abort the rest.

### FR-004: Publish Idempotency Contract
Publishing the same repo, skill path, version, and commit twice must not create duplicate `Skill`, `SkillVersion`, outbox, update, or install tracking rows.

### FR-005: Secret-Safe Verification
Tests may use `GITHUB_TOKEN`, `GH_TOKEN`, `VSKILL_TEST_GITHUB_PAT`, `NPM_TOKEN`, platform database URLs, Cloudflare deployment tokens, and Obsidian-stored credentials, but only through environment variables or keychain. Reports must redact values.

## Success Criteria

- Public direct GitHub install passes end to end.
- Private direct GitHub install passes end to end.
- Plugin install and uninstall pass at scale.
- Authoring, push, submit, approve, publish, update, and reinstall pass end to end.
- Desktop and CLI outputs match for equivalent flows.
- ChatGPT/OpenAI export and Anthropic/Claude-compatible install pass with the same source skill.
- Local machine has the newly built package installed and smoke-tested.
- No secrets appear in git diff, reports, stdout summaries, screenshots, or fixtures.

## Dependencies

- `vskill` install routes: `src/eval-server/install-skill-routes.ts`, `install-engine-routes.ts`, `plugin-discovery.ts`, `plugin-ref-resolver.ts`, `github-tree.ts`, `installer/multi-install.ts`.
- `vskill` desktop app: `src-tauri`, sidecar, eval UI install modal, update and publish UI surfaces.
- `vskill-platform` submission and publish pipeline: `src/lib/submission/*`, `src/lib/scanner.ts`, API routes under `src/app/api/v1/submissions`, `admin/submissions`, and `skills`.
- Local secrets: repo `.env*`, vskill-platform `.env*`, and Obsidian credential notes. Values are never copied into increment artifacts.

## October 2026 audit acceptance

Requested 2026-10-09: audit current enterprise pricing/auth/storage, supported models, testcase fidelity, real creation/testing/publication, catalog health/adoption and integration with SpecWeave Studio. Current upstream sources take precedence over historical checkbox evidence. Preserve other active Studio/crawler owners; no pricing changes or enterprise rollout on this audit.

- [x] **AC-AUDIT-01**: Verified current model IDs are selectable with provider-compatible requests and testcase round-trips preserve headings/newlines.
- [x] **AC-AUDIT-02**: Sign-out clears both platform and GitHub credentials including legacy fallbacks; fallback key files are owner-only. Optional usage telemetry requires consent and excludes search text. Tenant publication preserves authentication, owner/admin authorization and private-submission boundaries.
- [x] **AC-AUDIT-03**: Three useful authored example skills have reproducible tests, public source receipts and truthful registry queue/publication status.
- [x] **AC-AUDIT-04**: Enterprise, production queue/crawler, actual adoption and Studio integration conclusions cite fresh evidence and distinguish unsupported claims.

### T-032 Require write scope for repository disconnect
- AC: AC-AUDIT-04 | Files: repositories/anton-abyzov/vskill-platform/src/app/api/v1/account/repos/[id]/route.ts, repositories/anton-abyzov/vskill-platform/src/__tests__/account/repos-disconnect.test.ts | Test: cd /Users/antonabyzov/Projects/github/vskill-platform-enterprise-20261009 && PWDEBUG=0 PLAYWRIGHT_HTML_OPEN=never npm test -- src/__tests__/account/repos-disconnect.test.ts

Reject read-only or missing-scope API tokens before repository reads/mutations, while retaining browser/GitHub auth behavior and write-token owner isolation. No production writes/deployment.

### T-033 Honor personal Pro for personally owned private installations
- AC: AC-AUDIT-04 | Files: repositories/anton-abyzov/vskill-platform/src/lib/tenant-subscription.ts, repositories/anton-abyzov/vskill-platform/src/lib/__tests__/tenant-subscription.test.ts, repositories/anton-abyzov/vskill-platform/src/app/api/v1/submissions/__tests__/route.private-paywall.test.ts | Test: cd /Users/antonabyzov/Projects/github/vskill-platform-enterprise-20261009 && PWDEBUG=0 PLAYWRIGHT_HTML_OPEN=never npm test -- tenant-subscription route.private-paywall tenant-caps

Resolve paid personal entitlements using the GitHub personal installation owner identity, never an organization member or installer. Preserve tenant Team billing and canceled/expired handling; prove the actual submission route uses the real lookup. No billing changes, migrations or deployment.

### T-035: Integrate and deploy reviewed platform hardening
- AC: AC-AUDIT-04 | Files: reports/studio-audit-20261009/platform-release/, repositories/anton-abyzov/vskill-platform/ | Test: cd /Users/antonabyzov/Projects/github/vskill-platform-enterprise-20261009 && PATH=/Users/antonabyzov/.nvm/versions/node/v22.20.0/bin:$PATH node scripts/verify-queue-health-deploy.mjs

User authorized complete/push/deploy/test/verify on 2026-10-09. Merge reviewed platform PR91/92 through normal checks, build/deploy through existing pipeline, record exact source/artifact and live route health. Coordinate crawl-worker/VM ownership with crawler lane; no price/subscription changes, no broad cache-warm, no migration. Cleanup only after parent preserves evidence and authorizes it.

## October 9 release authorization

Anton explicitly requested applying all reviewed changes, pushing, deploying, testing, verifying and cleaning this job's worktrees. This supersedes the earlier draft-only release hold. Existing unrelated owners and their worktrees remain protected. Include the reproduced Team checkout and tenant-production publication repairs; pricing copy must describe shipped local versus hosted features without promising unimplemented SSO. Keep current billing amounts and customer subscriptions unchanged.

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
