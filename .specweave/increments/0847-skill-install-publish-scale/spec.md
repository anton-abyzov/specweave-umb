---
increment: 0847-skill-install-publish-scale
title: "Skill Install and Publish Scale - Plugin and GitHub Repository Flows"
type: feature
priority: P1
status: active
created: 2026-05-14
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
- [ ] **AC-US3-06**: Public and private publish sandboxes both pass, with private access using scoped GitHub credentials only.

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
- [ ] **AC-US6-02**: The release script bumps versions only after tests pass and updates package metadata consistently.
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
