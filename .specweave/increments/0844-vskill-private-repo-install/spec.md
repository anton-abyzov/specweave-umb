---
increment: 0844-vskill-private-repo-install
title: "vskill: private-repo install support"
type: feature
priority: P1
status: planned
created: 2026-05-10
structure: user-stories
test_mode: TDD
coverage_target: 90
---

# Feature: vskill — Private-repo Install Support (Enterprise-Ready)

## Overview

`vskill install --repo OWNER/REPO --all` works perfectly on public repositories
but silently fails on **private** repositories — even when the user has run
`vskill auth login` and a valid GitHub token is cached. The cause: vskill
fetches `marketplace.json` and skill payloads from `raw.githubusercontent.com`,
which **does not honor the `Authorization: Bearer <token>` header** for private
content. GitHub's raw-content host accepts only the temporary `?token=…`
query-string token used for upload-asset URLs — so the request returns 404 and
vskill prints `marketplace.json not found at OWNER/REPO`.

This increment routes all repo-content reads to `api.github.com/repos/{owner}/
{repo}/contents/{path}?ref={branch}` (which **does** honor `Authorization:
Bearer`), turns the generic 404 into actionable error messages, lays down the
enterprise-grade auth/audit story (fine-grained PATs, GitHub App tokens,
SSO/SAML preflight, install-time provenance fields), and ships
`anton-abyzov/anton-personal-skills` as the canonical worked example for the
docs.

### Concrete Repro (captured 2026-05-10 during anton-personal-skills bring-up)

```bash
$ vskill auth status
Logged in as @anton-abyzov (id=979819).

$ vskill install --repo anton-abyzov/anton-personal-skills --all --dry-run
Fetching marketplace.json...
marketplace.json not found at anton-abyzov/anton-personal-skills
Ensure the repo has .claude-plugin/marketplace.json on the default branch.

$ gh api repos/anton-abyzov/anton-personal-skills/contents/.claude-plugin/marketplace.json | jq -r '.path'
.claude-plugin/marketplace.json   # file IS there
```

### Root-cause Map

| File | Line | Issue |
|------|------|-------|
| `src/commands/add.ts` | 1631 | `manifestUrl = https://raw.githubusercontent.com/...` |
| `src/commands/add.ts` | 1708 | Same `raw.githubusercontent.com` URL in `installRepoPlugin` |
| `src/lib/github-fetch.ts` | 129 | Adds `Authorization: Bearer`, but raw host ignores it |
| `src/lib/github-fetch.ts` | ~85 | `ALLOWED_HOSTS` correctly includes both raw + api hosts |

## User Stories

### US-001: Private-repo install works end-to-end
**Project**: vskill

**As a** vskill user with private skill repos
**I want** `vskill install --repo OWNER/PRIV-REPO --all` to install successfully
**So that** I can distribute personal/internal skills without making my repo public

**Acceptance Criteria**:
- [ ] **AC-US1-01**: `vskill install --repo anton-abyzov/anton-personal-skills --all --dry-run` returns success and lists the `resume-tuner` plugin (the canary).
- [ ] **AC-US1-02**: `vskill install --repo anton-abyzov/anton-personal-skills --all` (real install) symlinks `skills/resume-tuner` into `~/.claude/skills/`.
- [ ] **AC-US1-03**: A public-repo install (`vskill install --repo posquit0/Awesome-CV --all` or any current public-canary) continues to work — no regression.
- [ ] **AC-US1-04**: The same fix applies to single-plugin installs (`vskill install --repo OWNER/REPO --plugin foo`), not only `--all`.

### US-002: Differentiated, actionable failure modes
**Project**: vskill

**As a** vskill user hitting an install failure on a private repo
**I want** to know exactly what's wrong (no token, no access, file missing)
**So that** I can fix it without reading vskill source code

**Acceptance Criteria**:
- [ ] **AC-US2-01**: When no token is cached and the repo is private, output: `Repository OWNER/REPO is private and no GitHub token is cached. Run vskill auth login first.` Exit code 2 (auth-required).
- [ ] **AC-US2-02**: When a token is cached but lacks access (403 from API, or 404 plus the user is unauthenticated against the org), output: `Token cached for vskill cannot read OWNER/REPO. Either re-run vskill auth login with broader scope, or for SSO-protected orgs authorize the token at https://github.com/orgs/ORG/sso.` Exit code 3 (auth-insufficient).
- [ ] **AC-US2-03**: When the repo is reachable but `.claude-plugin/marketplace.json` is genuinely missing, output: `Repository OWNER/REPO does not contain .claude-plugin/marketplace.json on default branch BRANCH. Found: <list of files in .claude-plugin/ if any>.` Exit code 4 (manifest-missing).
- [ ] **AC-US2-04**: When the org enforces SAML SSO and the token isn't authorized for it, surface the `X-Github-Sso` header value and the SSO authorization URL.

### US-003: Enterprise-grade auth knobs
**Project**: vskill

**As a** security engineer at an enterprise rolling vskill out internally
**I want** to use fine-grained PATs and/or GitHub App installation tokens, and have install-time provenance recorded
**So that** I can pass SOC2 / ISO-27001 audits without re-architecting

**Acceptance Criteria**:
- [ ] **AC-US3-01**: `VSKILL_GITHUB_TOKEN` env var overrides the cached keychain token for a single invocation (ephemeral CI usage).
- [ ] **AC-US3-02**: `VSKILL_GITHUB_APP_TOKEN` env var, when set, is treated as a GitHub App installation token (Bearer prefix preserved as-is) and is used for that invocation.
- [ ] **AC-US3-03**: A token is **never** logged at full length. The audit log records only `token_fingerprint_hash = sha256(token).slice(0, 12)`.
- [ ] **AC-US3-04**: Each install appends to `~/.vskill/installed-skills.json` an entry with: `repo`, `branch`, `commit_sha`, `marketplace_hash` (sha256 of the manifest body), `token_fingerprint_hash`, `installed_at` (ISO timestamp), `actor` (the GitHub `login` from `/user` if reachable, else `cli`).
- [ ] **AC-US3-05**: When the install reads from a fine-grained PAT scoped only to specific repos, the install succeeds; when it reads from a token authorized for a SAML-SSO org, the install also succeeds. (Test fixture proves both paths.)

### US-004: Canary + docs for the private-repo workflow
**Project**: vskill

**As a** new user trying to host a private skills repo
**I want** a concrete, end-to-end example I can copy from
**So that** I don't have to reverse-engineer the workflow

**Acceptance Criteria**:
- [ ] **AC-US4-01**: `docs/private-repos.md` exists and walks through: (1) creating a private repo with `gh repo create --private`, (2) `.claude-plugin/marketplace.json` minimum schema, (3) `.claude-plugin/plugin.json` (optional), (4) `vskill auth login`, (5) `vskill install --repo`, (6) sharing with collaborators.
- [ ] **AC-US4-02**: The doc names `anton-abyzov/anton-personal-skills` as the worked example with copy-paste commands. The repo currently contains `skills/resume-tuner/` — the doc references this minimal fixture.
- [ ] **AC-US4-03**: A "Hosting on GitHub Enterprise Server" appendix covers the `GITHUB_API_URL` env-var path (deferred follow-up if not already wired).
- [ ] **AC-US4-04**: A "CI / GitHub Actions" appendix shows the GitHub App OIDC pattern (no PATs in CI).

### US-005: Integration test that hits the live private repo
**Project**: vskill

**As a** vskill maintainer
**I want** a CI-gated test that actually installs from `anton-abyzov/anton-personal-skills`
**So that** regressions on private-repo support are caught immediately

**Acceptance Criteria**:
- [ ] **AC-US5-01**: A new test file `tests/integration/private-repo-install.test.ts` runs only when `VSKILL_E2E=1` AND `VSKILL_GITHUB_TOKEN` is set.
- [ ] **AC-US5-02**: The test invokes `vskill install --repo anton-abyzov/anton-personal-skills --all --dry-run` and asserts the `resume-tuner` plugin is enumerated.
- [ ] **AC-US5-03**: A non-E2E unit test mocks `githubFetch` and asserts that the install path uses `api.github.com/repos/.../contents/...` and never `raw.githubusercontent.com` for marketplace.json.

## Non-Goals

- Replacing the entire keychain integration (already works; we only add env-var overrides).
- Multi-account support (`vskill orgs use ORG`) — already exists; we just consume the active context.
- Full GitHub Enterprise Server support (only the `GITHUB_API_URL` env-var hook).
- Migrating away from PATs entirely — GitHub App support is an *option*, not a replacement.

## Dependencies

- Live network access to `api.github.com` and a user GitHub token (E2E only; unit tests mock).
- `anton-abyzov/anton-personal-skills` remains intact as the canary repo.

## Success Metrics

- `vskill install --repo <private>` works on the first try for the maintainer.
- Zero new findings from `vskill scan` against test fixtures.
- E2E test green on a self-hosted GitHub Actions run with a fine-grained PAT scoped to the canary repo.
