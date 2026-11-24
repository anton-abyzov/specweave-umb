# Folder copy carries a safe git config and flags tracked secrets

## Problem

Muse review XM-04 (high, verified): folder copy and copy-and-move classify tracked files as work before any secret check (`apps/server/src/fleet/folderTransfer/classify.ts:84`), so a tracked `.env` or credential file travels without the secret step; and a main repository's `.git` is copied as is, `config` required (`apps/server/src/fleet/folderTransfer/portableGit.ts:571`), carrying hooks, filter and fsmonitor commands and credentialed remote URLs to the destination, where later Git or agent calls run them.

Follow-ups from the same review, tracked here so they are not lost: XM-03 fleet management tokens last up to 365 days with owner scopes (`apps/server/src/fleet/fleetRedemption.ts:31`); XM-05 secret file offers skip the owner card on the server-to-server path; XM-06 legacy and `own` grants broader than shown; XM-07 transfer bearer not bound to the destination; XM-08 open sockets outlive their token.

## Scope

In: XM-04. Out: XM-03, XM-05 to XM-08 (listed for follow-up increments).

## Acceptance Criteria

- [ ] AC-01: A copied repository's `.git/config` (and `config.worktree`, submodule configs) holds only an allowlist of plain settings, with passwords and tokens stripped from remote URLs (a plain ssh user name such as `git@` stays) and helper (`ext::`) or local-path remotes dropped; hooks, fsmonitor, filter and diff drivers (except the exact filter Git LFS installs), credential helpers, aliases, includes and `insteadOf` rewrites are not carried. The source keeps its own config untouched, and a later move does not report the stripped settings or hooks as source changes.
- [ ] AC-02: The copy review lists tracked files that match the secret patterns (up to 50) with "Tracked in Git, so it travels with the repository's history. If it holds a secret, remove it from Git and rotate it."

## Approach

New `folderTransfer/safeGitConfig.ts`: an allowlist rewrite of every config in the frozen snapshot (`git config --no-includes --null --list`, then a fresh file), hooks folders skipped while copying, and the external-worktree origin URL passed through the same URL check. The drift check compares the live config as the copy would carry it, and ignores hooks. Tracked secret-like files become `secretHints` in the source summary, which the review already shows.

Why a hint and not a gate for tracked secrets: the file is in the Git objects and history the copy carries anyway, so holding back the working file would not keep the secret off the destination. The fix is to remove it from Git and rotate it, which the hint says.

## Decisions

### Asked
- none
### Defaulted (change any before sw-do)
- D-01 Strip, don't warn: unsafe Git settings never travel; the owner can re-add them on the destination.
- D-02 Tracked secrets are named in the review, not held back (see Approach).
- D-03 Plain ssh user names (`git@`) and the exact Git LFS filter travel; AC-01 amended to match the code (owner, November 24, 2026, accepting the triage recommendation).
### Open
- none

## Tasks

### T-01 Safe git config for main repository copies
- AC: AC-01 | Files: repositories/anton-abyzov/specwithcode/apps/server/src/fleet/folderTransfer/portableGit.ts, repositories/anton-abyzov/specwithcode/apps/server/src/fleet/folderTransfer/safeGitConfig.ts, repositories/anton-abyzov/specwithcode/apps/server/src/fleet/folderTransfer/sourceDrift.ts, repositories/anton-abyzov/specwithcode/apps/web/src/components/studio/HandoffSourceChanges.tsx | Test: cd repositories/anton-abyzov/specwithcode/apps/server && npx vp test run src/fleet/folderTransfer

### T-02 Tracked secrets named in the copy review
- AC: AC-02 | Files: repositories/anton-abyzov/specwithcode/apps/server/src/fleet/folderTransfer/sourceSummary.ts | Test: cd repositories/anton-abyzov/specwithcode/apps/server && npx vp test run src/fleet/folderTransfer

### T-04 A stripped origin never forces the move review
- AC: AC-01 | Files: repositories/anton-abyzov/specwithcode/apps/server/src/fleet/folderTransfer/sourceDrift.ts, repositories/anton-abyzov/specwithcode/apps/server/src/fleet/folderTransfer/sourceService.ts, repositories/anton-abyzov/specwithcode/apps/server/src/fleet/handoffGitTypes.ts, repositories/anton-abyzov/specwithcode/apps/server/src/fleet/folderTransfer/portableGit.ts, repositories/anton-abyzov/specwithcode/apps/server/src/fleet/folderTransfer/safeGitConfig.ts | Test: cd repositories/anton-abyzov/specwithcode/apps/server && npx vp test run src/fleet/folderTransfer
- Review finding (Sol, November 24, 2026): changing only a stripped local-path origin still emits a repository change, because the manifest keeps the source origin and identity (`sourceDrift.ts:137-147`, `:374-415`).

### T-05 Project secret patterns flag tracked files; preview wording
- AC: AC-02 | Files: repositories/anton-abyzov/specwithcode/apps/server/src/fleet/folderTransfer/sourceSummary.ts, repositories/anton-abyzov/specwithcode/apps/server/src/fleet/folderTransfer/classify.ts, repositories/anton-abyzov/specwithcode/apps/server/src/fleet/folderTransfer/secretLocations.ts, repositories/anton-abyzov/specwithcode/apps/web/src/components/studio/HandoffSecretsStep.tsx | Test: cd repositories/anton-abyzov/specwithcode/apps/server && npx vp test run src/fleet/folderTransfer
- Review findings: tracked files matching only the project's Secret files patterns get no hint (`sourceSummary.ts:22-28`); the preview heads those Git rows "Not copied" although they travel with history (`HandoffSecretsStep.tsx:209-223`).

### T-03 Verify and close 1328
- AC: AC-01, AC-02 | Files: .specweave/increments/1328-folder-copy-carries-a-safe-git-config-and-flags-tracked-secrets/ | Test: specweave verify 1328

## Closure triage (November 24, 2026)

Shipped in PR #354 (squash `b89033665`, v1.0.321). Closing review by GPT-6.2 Sol (Codex) at main `f3ce25682`: **fix**, so not verified or closed.
- High, AC-01: a stripped local-path origin can still force the move review (manifest keeps source origin and identity). `sourceDrift.ts:137-147`, `:374-415`; `folderTransfer/sourceService.ts:984`
- High, AC-02: tracked files matching only the project's own Secret files patterns get no Git hint. `sourceSummary.ts:22-28`; `classify.ts:93-100`
- Medium, AC-01: ssh and scp-style URLs keep their user name (deliberate, `safeGitConfig.ts:94-108`); the AC says user info is stripped.
- Medium, AC-01: the standard Git LFS filter is carried (deliberate `LFS_FILTER`, `safeGitConfig.ts:61-67`); the AC says filter drivers are not carried.
- Medium: the preview heads tracked-secret rows "Not copied" while their hint says the file travels with history. `HandoffSecretsStep.tsx:209-223`
Open for the owner: amend AC-01 to allow `git@` user names and the LFS filter, or strip them.

Fixed in PR #878 (merge `2b126b324`, November 24, 2026), GPT-6.2 Sol ship after four rounds:
- T-04: a main repository's origin is compared only through its sanitized config; an external worktree's copy now carries the cleaned origin (credentials and query stripped), and the drift basis records the origin the copy wrote (snapshot's own config) to compare with the live one. `handoffGitTypes.ts` (`canonicalOrigin`) and the manifest header stay unchanged, since clone-from-origin and reconcile read them.
- T-05: project Secret files patterns flag tracked files and, inside a containing folder, match from the project's top (`secretPatternMatcher(patterns, projectRelativePath)`, also used for untracked secrets); the preview heads Git rows "Copied with the repository".
