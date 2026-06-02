# Implementation Plan: Skill Install and Publish Scale - Plugin and GitHub Repository Flows

## Overview

This increment is a cross-repo hardening and verification loop. The main code changes are expected in `repositories/anton-abyzov/vskill/` and `repositories/anton-abyzov/vskill-platform/`.

The likely root risk is split source handling:

- `vskill` already supports direct GitHub discovery, plugin cache discovery, multi-agent install, clipboard export, and desktop SSE install jobs.
- `vskill-platform` already supports submissions, scanning, approval, publishing, version manifests, outbox update events, and skill update endpoints.
- Some paths still assume public GitHub raw URLs or source-name-only identity, which is fragile for private repositories, plugins, and republish loops.

The implementation should preserve existing behavior and add authenticated/private coverage, identity consistency, parity tests, and release verification.

## Architecture

### Components

- `GitHubSourceFetcher` (vskill): token-aware discovery and content fetch abstraction used by CLI install, desktop install, update checks, and source resolver.
- `PluginSourceResolver` (vskill): existing plugin cache and plugin CLI resolver hardened for idempotency and `name@marketplace` operations.
- `InstallDispatcher` (vskill): existing `installSkillToMultipleAgents` plus route/job hardening for public/private/plugin sources.
- `SkillStandardValidator` (vskill): validates `SKILL.md`, resources, frontmatter, optional `agents/openai.yaml`, and transformer-safe parsed skill payloads.
- `PublishPipeline` (vskill-platform): existing submission/upsert/publish flow hardened for private fetches, canonical identity, idempotency, and version monotonicity.
- `DesktopParityHarness` (vskill): Playwright/macOS route tests that compare UI actions against CLI outputs.
- `ReleaseVerifier` (scripts/tests): local install and smoke-test script that runs after package build and before publish/deploy.

### Data Model

Extend or normalize source metadata where missing:

```ts
interface SkillSourceIdentity {
  sourceType: "github" | "github-plugin" | "plugin" | "marketplace" | "local" | "registry";
  repoUrl?: string;
  owner?: string;
  repo?: string;
  branch?: string;
  commitSha?: string;
  skillPath?: string;
  pluginName?: string;
  marketplace?: string;
  version?: string;
  contentHash?: string;
}
```

The same logical identity should be used for:

- lockfile source entries
- installed sidebar rows
- update subscriptions
- platform `Submission`
- platform `Skill`
- platform `SkillVersion`
- install telemetry

### API Contracts

- `POST /api/studio/install-skill`
  - Existing desktop install route. Add or verify support for `sourceIdentity` and authenticated direct GitHub install fallback.
- `GET /api/studio/install-skill/:jobId/stream`
  - Existing SSE route. Verify replay, final summary, and no secret leakage.
- `POST /api/v1/submissions`
  - Platform submission intake. Verify public/private repo, `skillPath`, dedupe, and state response.
- `PATCH /api/v1/admin/submissions/:id/approve`
  - Platform approval/publish. Verify content hash and private fetch handling.
- `GET /api/v1/skills/:owner/:repo/:skill/versions`
  - Verify latest publish version appears exactly once.
- `GET /api/v1/skills/check-updates`
  - Verify installed clients see new versions by source identity.

## Technology Stack

- TypeScript/Node for CLI, eval server, installer, platform app, and tests.
- Rust/Tauri for macOS desktop packaging and sidecar integration.
- Vitest for unit and integration tests.
- Playwright for desktop/UI and platform E2E.
- Prisma/Postgres, Cloudflare/OpenNext, and platform KV/Durable Object pieces as already present.
- GitHub API with scoped tokens for private repository test fixtures.

## Architecture Decisions

### AD-001: Centralize GitHub Fetching

Do not patch private-token support separately into every call site. Create or consolidate around a shared token-aware fetch helper so public/private behavior, branch detection, 401/403/404 classification, and rate-limit handling stay consistent.

### AD-002: Prefer Source Identity Over Display Name

Dedup and update checks must not rely on display name alone. The same skill name can appear in a plugin, direct repo, registry, and local authoring source. Use normalized repo URL, skill path, plugin name, and commit/version identifiers.

### AD-003: Use Real Sandbox Repositories for Final Proof

Unit tests cover error taxonomy and parser branches. Final proof needs public and private GitHub sandbox repos because raw URLs, contents API, auth, and default branch behavior differ in practice.

### AD-004: Treat Secrets as Inputs, Never Artifacts

Env files and Obsidian notes are allowed only to locate required credentials. Tests must load values into process env/keychain and redact every output. Reports record variable names and status only.

### AD-005: Release Candidates Are Disposable

If a candidate fails local install or desktop smoke tests, patch and bump a new candidate version. Do not publish or deploy a known-broken candidate under the same version.

## Implementation Phases

### Phase 0: Baseline and Secret Preflight

- Inventory current dirty worktree and protect unrelated user edits.
- Discover required credentials by variable name only.
- Add a redaction helper for test reports if missing.
- Run baseline targeted tests to capture current public/private/plugin failures.

### Phase 1: GitHub Source Fetching

- Add token-aware GitHub repository fetch helper.
- Update CLI and platform fetch paths to use it for private repositories.
- Preserve unauthenticated public behavior for speed and rate-limit isolation.
- Add error taxonomy tests.

### Phase 2: Plugin and Install Idempotency

- Harden plugin cache discovery and plugin ref resolution where tests expose gaps.
- Verify multi-agent install can consume direct GitHub, plugin, local, registry, and clipboard sources.
- Strengthen lockfile/source identity writes and dedupe.

### Phase 3: Skill Standard Compatibility

- Add fixtures for universal, OpenAI/ChatGPT, Anthropic/Claude, and multi-file skills.
- Validate `SKILL.md`, bundled resources, optional `agents/openai.yaml`, and transformer output.
- Verify Tier 1/2 filesystem installs and Tier 3 clipboard exports.

### Phase 4: Publish and Update Lifecycle

- Extend platform submission/publish tests for public/private repos.
- Verify content-hash, manifest, monotonic version, ghost-version prevention, update outbox, search, detail, versions, and install tracking.
- Add republish test that pushes a new commit and expects exactly one new version.

### Phase 5: Desktop and CLI E2E

- Build/use the macOS sidecar path.
- Test desktop install modal and SSE streams for direct GitHub, plugin, local, marketplace, and clipboard export.
- Compare CLI and desktop filesystem outputs and lockfile metadata.

### Phase 6: Release and Local Install

- Run full vskill and platform validation.
- Build packages.
- Install the new vskill locally.
- Smoke test public GitHub, private GitHub, plugin, and ChatGPT/OpenAI export flows.
- Bump/publish/deploy only after the above passes.

## Testing Strategy

Required commands before closure:

- In `repositories/anton-abyzov/vskill`:
  - `npm run build`
  - `npx vitest run`
  - `npx playwright test`
  - `npm run desktop:sidecar:build`
  - `npm run desktop:build` or the project-approved lighter macOS packaging smoke when full build is too slow for iteration
- In `repositories/anton-abyzov/vskill-platform`:
  - `npm run build`
  - `npx vitest run`
  - `npx playwright test`
- Increment closure:
  - `npx vitest run --coverage` where applicable
  - `specweave sync-progress 0847-skill-install-publish-scale`
  - `specweave complete 0847-skill-install-publish-scale` after gates pass

Sandbox tests must skip clearly when a required secret variable is missing and fail loudly when a token is over-scoped.

## Technical Challenges

### Private GitHub Fetching

Raw GitHub URLs and GitHub API contents behave differently for private repositories. Use a helper that first authenticates metadata/default branch calls and then fetches content with authenticated headers or Contents API fallback.

### Source Duplication

The same skill may appear through multiple origins. The fix is stable source identity plus idempotent lockfile and platform uniqueness checks.

### Desktop Secret Isolation

The desktop WebView must not see token values. Use keychain/server-side env, redacted SSE events, and existing `X-Studio-Token` hardening patterns.

### Release Safety

Publishing and local package install touch the user's machine. Use sandbox repos and dry-run/smoke gates first, then perform release commands only after the test matrix is green.
