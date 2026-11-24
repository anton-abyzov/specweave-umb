# Folder copy carries a safe git config and flags tracked secrets

## Problem

Muse review XM-04 (high, verified): folder copy and copy-and-move classify tracked files as work before any secret check (`apps/server/src/fleet/folderTransfer/classify.ts:84`), so a tracked `.env` or credential file travels without the secret step; and a main repository's `.git` is copied as is, `config` required (`apps/server/src/fleet/folderTransfer/portableGit.ts:571`), carrying hooks, filter and fsmonitor commands and credentialed remote URLs to the destination, where later Git or agent calls run them.

Follow-ups from the same review, tracked here so they are not lost: XM-03 fleet management tokens last up to 365 days with owner scopes (`apps/server/src/fleet/fleetRedemption.ts:31`); XM-05 secret file offers skip the owner card on the server-to-server path; XM-06 legacy and `own` grants broader than shown; XM-07 transfer bearer not bound to the destination; XM-08 open sockets outlive their token.

## Scope

In: XM-04. Out: XM-03, XM-05 to XM-08 (listed for follow-up increments).

## Acceptance Criteria

- [ ] AC-01: A copied repository's `.git/config` (and `config.worktree`, submodule configs) holds only an allowlist of plain settings, with user info stripped from remote URLs and helper (`ext::`) or local-path remotes dropped; hooks, fsmonitor, filter and diff drivers, credential helpers, aliases, includes and `insteadOf` rewrites are not carried. The source keeps its own config untouched, and a later move does not report the stripped settings or hooks as source changes.
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
### Open
- none

## Tasks

### T-01 Safe git config for main repository copies
- AC: AC-01 | Files: repositories/anton-abyzov/specwithcode/apps/server/src/fleet/folderTransfer/portableGit.ts, repositories/anton-abyzov/specwithcode/apps/server/src/fleet/folderTransfer/safeGitConfig.ts, repositories/anton-abyzov/specwithcode/apps/server/src/fleet/folderTransfer/sourceDrift.ts, repositories/anton-abyzov/specwithcode/apps/web/src/components/studio/HandoffSourceChanges.tsx | Test: cd repositories/anton-abyzov/specwithcode/apps/server && npx vp test run src/fleet/folderTransfer

### T-02 Tracked secrets named in the copy review
- AC: AC-02 | Files: repositories/anton-abyzov/specwithcode/apps/server/src/fleet/folderTransfer/sourceSummary.ts | Test: cd repositories/anton-abyzov/specwithcode/apps/server && npx vp test run src/fleet/folderTransfer

### T-03 Verify and close 1328
- AC: AC-01, AC-02 | Files: .specweave/increments/1328-folder-copy-carries-a-safe-git-config-and-flags-tracked-secrets/ | Test: specweave verify 1328
