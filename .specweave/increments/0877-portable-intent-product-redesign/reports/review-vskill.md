# Review — 0877 vskill maintenance and npm release

Verdict on reviewed 8ce135e: fix first · 11 changed files reviewed · 1 confirmed high finding.
Reviewer context: independent subagent for original implementation and release workflow. The remediation below was then authored by this reviewer and requires root independent verification.

## [high] src/commands/remove.ts:46 — nested removal deletes the parent installation

A child directory can own its own vskill.lock and installed skill beneath a SpecWeave umbrella. The installer explicitly writes to process.cwd() (src/commands/add.ts:990,1001,1038), but the new removal path resolves the ancestor .specweave root. Given parent and child each contain the same named skill, invoking remove with --local --force from the child deletes the parent's canonical payload and parent lock entry while leaving the child's payload and lock unchanged. The same resolver makes cleanup inspect the wrong project ownership and settings.

Reverified using the built removeCommand in an isolated temporary filesystem: exit 0; parentPayloadRemains=false; childPayloadRemains=true; parentLockHasSkill=false; childLockHasSkill=true. No personal installation was changed. A regression test then reproduced three failures before the fix.

Fix committed separately as 010a49a: resolve the nearest vskill.lock between cwd and the SpecWeave project boundary; use the resolved root explicitly for lock reads, updates, canonical/per-agent files, and Claude plugin scope. Preserve the previous nested-source behavior when no nearer installation owns a lock. Malformed local lockfiles remain ownership boundaries instead of falling through to an ancestor. Root must independently verify this remediation before release.

## Release workflow assessment

Reviewed the new .github/workflows/npm-release.yml and package 1.1.1 changes in /tmp/vskill-0877-release against origin/main, including the untracked workflow. No confirmed release-workflow regression. The job checks tag/package agreement, installs with dependency scripts disabled then rebuilds esbuild, runs the full Vitest suite, builds CLI and Studio, validates the tarball, and publishes through npm run release with scripts explicitly enabled. setup-node configures npm registry authentication using NODE_AUTH_TOKEN; the repository exposes an NPM_TOKEN secret name (read-only gh secret list verified; secret value was never read). This proves wiring and secret presence, not token validity or an actual successful publish. Release notes run only after publish succeeds.

The existing preflight rejects missing CLI/Studio artifacts; six publish-path wiring tests pass. Package.json and package-lock.json both carry 1.1.1. agents.json changes only its generated timestamp. No new broad cache deletion remains in cleanup; registered or cached third-party plugins are preserved and unreadable plugin registry data makes cleanup return without mutation.

## Verification

- Before remediation: new ownership suite, 3 failed / 1 passed, reproducing parent deletion and incorrect cleanup scope.
- After remediation: 6 targeted test files / 43 tests passed, including existing scope, dry-run, removal, and publish-path tests plus ownership boundary fixtures.
- npm run build (TypeScript compile) passed.
- git diff --check passed.
- No browser used; no package published by the reviewer.

## Root independent re-verification

Root reviewed010a49a (release cherry-pick0e18781), including nearest-lock resolution and explicit read/write/payload/plugin paths. The full release-candidate suite passes625files/6,167tests/2existing skips. A second independent reviewer also reran33 focused ownership/scope tests. Original high finding is resolved. PR139 passed all CI checks across Windows, macOS, and Linux and was merged as6eea6d8. Actual npm publication is tracked separately.
