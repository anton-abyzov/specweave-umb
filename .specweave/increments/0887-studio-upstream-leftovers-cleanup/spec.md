# Studio upstream leftovers cleanup

## Problem

The T3 rename in specweave-studio (PR #29) was a text substitution. An audit on 2026-10-10 found upstream's live Clerk key, Apple account ids, store and Discord links, and the T3 mark as pixels still in the tree, plus a brand guard that could not see any of it. Full findings: project file `studio-t3-rename-audit.md`.

## Scope

In: remove every upstream identifier, link and image that needs no owner decision; make `scripts/studio-brand-audit.mjs` catch them and run in CI. Out: legal pages and the "Studio Tools" company name, keeping or removing `apps/marketing` and `apps/mobile`, default-branch choice, history rewrite.

## Acceptance Criteria

- [ ] AC-01: No upstream Clerk key, OAuth client id, Apple team id, App Store id, TestFlight or Discord link remains in tracked files.
- [ ] AC-02: `node scripts/studio-brand-audit.mjs` exits 0 on the branch without allow-listing an upstream brand mark.
- [ ] AC-03: Docs and site copy changed by the branch are true to the code (no dead store links, no stale `.env.example` claims).
- [ ] AC-04: PR anton-abyzov/specweave-studio#47 is marked ready with the final gate output in its body.

## Approach

Work happens in the clone `repositories/anton-abyzov/studio-t3-cleanup` (deps installed, branch `chore/remove-upstream-leftovers`, base `codex/0888-studio-projects` @ `1d2a44c90`). Four commits are pushed and draft PR #47 is open; its "Not finished" list is the remaining work for T-02 and T-03. T-01's edits are in those four commits but T-01 is not yet recorded in the ledger: run its Test from the clone, then `specweave task done T-01`.

In that clone always `export pnpm_config_verify_deps_before_run=false` and never set `CI=1`: pnpm 11 otherwise auto-installs and can wipe `node_modules`. Run tests with `node ../../node_modules/vite-plus/bin/vp test run <file>` from the package dir. Repo-wide typecheck, lint, format and unit suites already fail on the base commit; judge only changed files.

Do not touch LICENSE, UPSTREAM.md, recorded fixtures, `*.ndjson`, `patches/`, the legal pages or any "Studio Tools" string.

## Open questions

- Legal entity, domain and contact addresses for the legal pages.
- Keep or remove `apps/marketing` and `apps/mobile`.
- Make `codex/0888-studio-projects` the default branch or merge it into `codex/studio-claude-auth`.
- Rewrite history to remove AI authorship or leave it (private repo).

## Tasks

### T-01 First pass: keys, links, artwork, residue, guard
- AC: AC-01 | Files: .env.example, .github/workflows/*, apps/marketing/**, apps/mobile/assets/**, apps/web/**, docs/**, scripts/studio-brand-audit.mjs | Test: git grep -nE 'ARK85ZXQ4Z|6787819824|XgaxaRtd|jn4EGJjrvv' -- . ':!scripts/studio-brand-audit.mjs' ; test $? -eq 1

### T-02 Make the brand audit pass
- AC: AC-02 | Files: scripts/mobile-showcase-environment.ts, assets/**, scripts/export-android-icons.ts, scripts/studio-brand-audit.mjs, scripts/build-desktop-artifact.test.ts, .github/workflows/ci.yml | Test: node scripts/studio-brand-audit.mjs

### T-03 Fix stale copy, dead links, workflow inputs and commit identities
- AC: AC-03 | Files: apps/marketing/src/lib/site.ts, apps/marketing/src/pages/download.astro, docs/operations/**, .devcontainer/on-create.sh, .github/workflows/release-desktop.yml, apps/server/src/pullRequest/githubStackRebase.ts, apps/server/src/vcs/GitVcsDriver.ts | Test: pnpm_config_verify_deps_before_run=false corepack pnpm --filter @specweave-studio/marketing build

### T-04 Final gate and mark the PR ready
- AC: AC-04 | Files: (PR body only) | Test: gh pr view 47 -R anton-abyzov/specweave-studio --json isDraft --jq '.isDraft == false'
