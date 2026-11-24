---
title: "Before the move to the M5: what is unfinished"
thread: "thread:delegated-task:command%3Amcp%3A69961d72-e218-4a23-9b6c-5cb10e36f829%3Adelegate-task%3Aown-reports-not-claude-artifacts-20261113"
threadTitle: "Reports stay in SpecWithCode"
savedAt: "2026-11-13T19:19:25.037Z"
source: "Claude desktop"
original: "https://claude.ai/artifact/KMQWxSYB5N7EAJ9Fez58iT"
---

# Before the move to the M5: what is unfinished

## Bottom line

Nothing was lost and nothing is at risk now, but the M4 is not clean yet. I checked 591 repositories: 124 on the M4, 55 on linux-mini and 412 on the external drives.

- **Saved today.** Eight pieces of work that existed on one disk only are now on GitHub or in the archive. The biggest was the spec-os project on linux-mini: 55 commits with no remote, on a disk that is 96% full.
- **Still open in the specweave project.** 4 open pull requests in the app repository, 7 increments with uncommitted records in the shared checkout, and two live scratch copies. These must merge before the move.
- **Needs your call.** 9 decisions, listed next. Most are "dead or keep" for old work.
- **The move itself is safe for unpushed work.** Copy local files carries branches, stashes, linked worktrees, nested repositories and uncommitted files. It leaves out secrets, build output and everything in `~/.specwithcode` (scratch copies, evidence, verify checkouts).
- **EasyChamp has its own sweep.** The EasyChamp thread "M4 git cleanup and disk sweep" is already backing up and cleaning that project. I did not repeat its work.

## Your calls

Nine decisions are yours. Each has my recommendation, and none blocks the others.

| # | What | Where | My recommendation |
| --- | --- | --- | --- |
| 1 | 60 old branches and 2 stashes in the `specwithcode-dev` checkout hold commits that are on no remote. Most are from October. About 36 could not be matched to a merged pull request; the rest landed under other names. | M4 | Treat them as dead. They are bundled in the archive, so nothing is lost. Clone the app fresh on the M5 and do not carry this checkout over. |
| 2 | spec-os has 55 commits that were on no remote. They are now on a backup branch in the private `specos` repository, whose `main` holds one unrelated first commit. | linux-mini | Make the backup branch the `main` of `specos`. |
| 3 | The marketing repository: local `main` has drifted from GitHub, 20 edited files may be older versions of files GitHub already has, and 70 untracked paths include about 2.7 GB of video and images. | M4 | Let the video thread commit its scripts and plans, move the media to the Kingston library, then reset `main` to GitHub. I did not push a backup because 19 lines matched a secret pattern. |
| 4 | EasyChamp increment 0952 (pushed, no pull request) and the uncommitted plans 1028 to 1031. About 1.5 GB of screenshots and media in the umbrella are on no remote. | M4 | Tell the EasyChamp sweep thread which are dead. Archive the media to the SanDisk drive. |
| 5 | linux-mini is 96% full. The app keeps all 113 runtime versions it ever installed there, 47 GB in total. | linux-mini | Delete all but the running versions now, and fix the app so it prunes them. I can do both on your yes. |
| 6 | The credentials vault `personal-docs` in Obsidian has no Git remote. I could not confirm that Obsidian Sync is on. | M4 | Confirm Sync is on, or copy the vault to the M5 yourself. Every other secret can be restored from it. |
| 7 | Three April edits and one stash in the `claude-code` fork under anymodel. This account cannot push there. | M4 | Dead. I save a patch to the archive and leave it. |
| 8 | `whisperyoutube` was never committed and its GitHub repository is gone. One notebook and a README. | M4 | Archive it to the SanDisk drive, no new repository. |
| 9 | `RVAI` is Anna's repository. A local plan and project scaffold were never pushed, and her repository has moved on. | M4 | Archive it, do not push to her repository. |

## What I saved today

Eight pieces of work that lived on one disk are now stored elsewhere. Each push passed a secret-pattern check first, and no working tree was changed.

| Work | Was only on | Now also at |
| --- | --- | --- |
| spec-os, 55 commits | linux-mini | `anton-abyzov/specos`, branch `backup/ministorm-live-main-20261113` (private) |
| Product audit receipts, 12 commits, 157 files | M4, umbrella | `specweave-umb`, branch `codex/november-product-audit-receipts` |
| `specwithcode-dev`: 60 local-only branches, 2 stashes | M4 | Bundle and patches in `/Volumes/SanDisk APFS/Archive/specwithcode/2026-11-13-specwithcode-dev-local-only/` |
| halfturn, increment record and task evidence | M4 | `halfturn`, branch `backup/premove-20261113/uncommitted` (private) |
| Precocity invoice log, 24 new lines | M4 | `anton-personal-skills`, same branch name (private) |
| ccx-rs, 10 edited Rust files from April | M4 | `ccx-rs`, same branch name |
| My Legend hackathon, landing page and 6 edited files from June | M4 | `my-legend-cursor-hackathon`, same branch name |
| Greet demo, 5 commits for the three-languages increment | M4 | `greet-app-demo`, branch `backup/premove-20261113/main-0003` |

I deleted nothing. Removing merged leftovers is pointless before the M4 is retired, and the rule stands that uncommitted work is never deleted without your yes.

## M4

Of 124 repositories on the M4, 64 are clean and 60 have something. Paths are under `~/Projects` unless they start with `~/.specwithcode`.

### The specweave project

| Repository | What is unfinished | State |
| --- | --- | --- |
| `github/specweave-umb` (shared checkout, on `main`, 0 unpushed) | Uncommitted records of increments 1284, 1300, 1309, 1310 and new folders 1312, 1314, 1317. `release-timings.jsonl` has 2,256 new lines. `AGENTS.md` has one new rule. | Live, edited in the last 48 hours. Each owning thread commits its own. 1314 and the rule are mine. |
| same | Root `package.json` was overwritten with the app's own `package.json` on Nov 12. | A stray write by some thread. Restored to the tracked file today. |
| same | Branch `codex/november-product-audit-receipts` | Pushed today. |
| same | 58 other local branches | All on a remote already. Labels only. |
| `repositories/.../specwithcode-dev` (shared checkout) | 60 branches and 2 stashes with commits on no remote | Bundled. Your call 1. |
| `repositories/.../specwithcode` | Branch `pr303` | Open pull request 303, live today. |
| same | `fix/one-font-design-tokens`, `pr242` | Merged as pull requests 271 and 242. Labels only. |
| `repositories/.../specweave` | `docs/founders-300`, `fix/tutorial-step-code-wrap` and 15 more local branches | Merged (2217, 2151) or already on a remote. Labels only. |
| `repositories/.../specweave-status` | `status-by-product` | Merged as pull request 1. |
| `github/specwithcode-release-selftest`, `tmp-clones/swc-arm64-verify` | One generated marker file each | Nothing to save. |
| `scratch/swc-1267-t08` | Detached at release tag v1.0.230 | On GitHub. Nothing to save. |
| `scratch/oss-files/publish-check-t06` | One test commit from a publish-script check | Regenerable. Drops with the machine. |

### The app folder `~/.specwithcode/m4`

This folder does not move with a project, so anything in it must be landed or disposable.

| Path | What is unfinished | State |
| --- | --- | --- |
| `scratch/2026-11-13-machines/app` | 9 edited files, 1 new test | Live today, pull request 303. Must merge first. |
| `scratch/2026-11-13-providers-hint/app` | Clean | Live today. |
| `scratch/2026-11-11-elena-threads/branch` and `export` | 6 and 25 changed files in copies with no remote, from Nov 11 | No thread owns them. Archived today as bundles and patches in /Volumes/SanDisk APFS/Archive/specwithcode/2026-11-13-elena-threads-scratch/. The folder itself is still there. |
| `scratch/awesome-prs/*` (6 forks) | One commit each | Pushed. Six pull requests are open upstream and wait on maintainers. |
| `scratch/2026-11-05-android-native`, `2026-11-08-review-pr90`, `verify/specwithcode`, `2026-11-04-1239/umb-verify` | Merged work, pruned test files or a generated timing log | Nothing to save. |
| `evidence/1274/...`, `evidence/1236-implementation/*`, `scratch/1236-verify-audit`, handoff and probe fixtures (8 folders) | Test fixtures with fake remotes or none | Disposable. |
| `worktrees/sw-easychamp/*` (3) | Worktrees of three EasyChamp routines | In use by the routines. See Running work. |
| `scratch/2026-11-12-scratch-deps-prune/app` | My own copy | I remove it when this thread closes. |

### EasyChamp

The EasyChamp sweep thread handles this project. It reported no commit missing from a remote, and it copied both stashes and the uncommitted text to `backup/20261112/*` and `backup/stash-0-m4-20261113` on GitHub.

| Repository | What is unfinished | State |
| --- | --- | --- |
| `sw-easychamp` (on `develop`, 171 behind) | 21 edited record files, 28 untracked entries: plans 1028 to 1031, reports, and about 1.5 GB of screenshots and media | Text is backed up. Media is on no remote. Your call 4. |
| `sw-easychamp/.worktrees/0952-1026963` | 3 edited record files; branch pushed, no pull request | Backed up. Your call 4. |
| `sw-easychamp/.worktrees/manual-bracket-tutorial` | 7 untracked tutorial scripts | Backed up. The sweep thread is removing this worktree. |
| `ec-landing` | Older draft of the bracket tutorial, 2 files and 4 scripts | Superseded by pull request 245. |
| `ec-standings-api` | One stash from Oct 25 | Backed up on GitHub. |
| `ec-apicore-lib` | `.DS_Store` only | Nothing to save. |

### Other repositories

| Repository | What is unfinished | State |
| --- | --- | --- |
| `github/marketing` | Drifted `main`, 20 edited files, 70 untracked paths | Live video work. Your call 3. |
| `halfturn`, `github/anton-personal-skills`, `ccx-rs`, `my-legend-cursor-hackathon`, `experiments/swc-demo-greet-fleet` | Uncommitted or unpushed work | Saved today. |
| `github/anymodel-umb/.../claude-code` | 3 edited files, 1 stash, from April | Your call 7. |
| `github/whisperyoutube` | No commit, remote gone | Your call 8. |
| `github/RVAI` | 5 untracked files | Your call 9. |
| `github/hack26-crypto` | 6 evidence screenshots | Already on the `mine` remote, branch `backup/evidence-20261112`. |
| `github/_events/lerobot_hackathon` | 35 large data files deleted from disk | Still on GitHub. Nothing to save. |
| `github/_events/soflo25/RAG-to-Riches` | One edited secrets file from 2025, in someone else's repository | Never pushed. Listed with the secrets below. |
| `github/anymodel-umb`, `experiments/swc-demo-skills`, `guitar-robot-trainer` | Generated state, install output, editor settings | Nothing to save. |

## linux-mini

Of 55 repositories, 41 are clean, and the one real risk, spec-os, is saved. No build, test or agent job from the specweave project is running there.

| Path | What is unfinished | State |
| --- | --- | --- |
| `~/live/spec-os` | 55 commits, no remote. A server runs from this folder (up 22 hours). | Saved today. Your call 2. |
| `~/.specwithcode/ministorm/worktrees/add-device-flow` | Branch `add-device-dialog`, 1 commit | Merged as pull request 248. |
| `ministorm/worktrees/specweave/*` (about 40) | Thread worktrees, newest from Nov 12 | All clean, nothing unpushed. They stay until their threads close. |
| `ministorm/verify/*` (3) | Detached release-check checkouts | On GitHub. Nothing to save. |
| `ministorm/scratch/ios-width`, `ios-machine`, `worktrees/composer-voice-machine` | Clean, pushed branches | Nothing unpushed. |
| Handoff and move test fixtures (4), whisper.cpp clones (2), Codex plugin cache | Test or tool data | Disposable. |
| `ministorm/userdata/machine-handoffs` | 9.3 GB of folder-copy staging, 5 copies from Oct 30 to Nov 13 | Left by handoffs. Not checked file by file. |

**Running there:** the app service and its server (1.0.273), an older launcher process (1.0.180, up 32 hours), the Connect tunnel, one Devin session (28 hours), one Claude session (12 hours), the spec-os server, Docker with no containers, and the OBS sender. No scheduled jobs.

**Disk:** 7.2 GB free of 157 GB. `~/.specwithcode` holds 77 GB, of which 47 GB is the 113 kept runtime versions (your call 5).

## External drives

No project, thread or worktree runs from a drive, and nothing on the drives is waiting to be merged. All 412 repositories there are archives.

| Area | Repositories | What it is |
| --- | --- | --- |
| `SanDisk APFS/Archive/old-projects` | 314 | Old job, test and own projects, 2016 to 2025. Many have uncommitted files, as archived. |
| `SanDisk APFS/Archive/specwithcode` | 67 | Scaffold demos, October scratch, preserved clones and today's bundle. |
| `SanDisk APFS/Archive/disk-cleanup-20261029` | 9 | Projects retired on Oct 29. Three have small uncommitted edits: SkillUp (9 files), ai-reset (4), kinweave (1). |
| `KINGSTON` | 12 | Swift package caches for MatchCam, a tutorial demo, and worktree leftovers of ec-arena-ui from Nov 11. Two entries in `trash-review-20261110` are broken worktree links. |
| `SanDisk APFS/Personal/obsidian-backups` | 1 | An August copy of the `ai-power` vault. |

The three Oct 29 projects are the only recent ones with uncommitted edits. Say the word and I push those to backup branches too.

## Running work

The M4 is busy: about 60 threads worked in the last 24 hours, 7 of them in the last hour. The move needs a quiet window.

### Open pull requests

| Repository | Open | Notes |
| --- | --- | --- |
| `specwithcode` (the app) | 303, 304 (draft), 269, 268 | 303 and 304 are from today. 268 and 269 are from Nov 12. All four belong to live threads. |
| `specweave` | 2275 | Automated DORA metrics update. |
| `vskill-platform` | 207 | Dependabot. |
| `sw-easychamp` and its services | 341 (draft), ec-chat-api 187, ec-matchcam 22, ec-gitops 320, ec-betting-api 37 and 38 | EasyChamp threads. |
| `specwithcode-dev` (archived) | 1254, 1236, 1110 | The repository is archived, so these can never merge. Dead unless redone in the public repository. |
| Others of yours | sketchmate 26 and 15, orbita 16, 7 and 6, wc26-web 9, wc26-scraper 1 | Two to four weeks old. |
| Other people's lists | 8 | "Add SpecWithCode" and "Add EasyChamp" requests that wait on maintainers. They do not depend on any machine. |

### Threads on the M4

| Project | Open threads | With a worktree path |
| --- | --- | --- |
| specweave | 973 | 773 |
| EasyChamp | 159 | 18 |
| No project | 56 | |
| Percy | 41 | |
| Nine smaller projects | 42 | |

The app records 49 turns as running. 46 of them date from October and are stale records left by restarts. Three may be real: "App Store rejections fix and resubmit", "Miami drop game: Gemini build" and "Football passing sim build (Unreal, M4)".

Thread history does not move with Copy local files. A coordinator handoff carries the project goal, instructions, memory and the coordinator's and workers' chats. 973 open threads is a lot to carry, so resolving the finished ones first makes the handoff smaller.

### Routines

Ten routines are enabled on the M4. They keep running there until each is moved or recreated on the M5.

| Project | Routine |
| --- | --- |
| specweave | Hourly disk space and merged worktree cleanup |
| specweave | Disk space guard for Codex and Claude Code cleanup |
| specweave | Next release: M4 install with threads running |
| specweave | Releases missing Windows/Linux runs |
| specweave | Cancel Cursor subscription reminder (Dec 10) |
| EasyChamp | DCFC Square daily dues sync and Jotform check |
| EasyChamp | Daily SEO watch and fix |
| EasyChamp | New Relic repair watch |
| EasyChamp | Stripe Connect fraud watch |
| Percy | Proactive briefing |

Three EasyChamp routines run in worktrees made on Oct 3. Two of the specweave routines are about the M4 itself and should stay on it or be retired with it.

## Secrets and machine setup

Use the app's own copy for project secrets and sign in again for accounts. Copy local files leaves secret-like files out by default, lists them under **Secret files** in its preview, and sends the ones you tick. I listed files by name only and read none.

### Secret files inside projects

59 ignored secret-like files sit under `~/Projects`.

| Project folder | Files | Where |
| --- | --- | --- |
| `sw-easychamp` | 32 | ec-mobile 10, ec-iac-infrastructure 5, the umbrella and its `.specweave` 4, and one or two each in ec-chat-api, ec-arena-ui, ec-sim-ui, ec-scrapers-dashboard, ec-ml-api, ec-console-ui, ec-coach-ui, ec-club-mobile, ps23-site |
| `github/specweave-umb` | 16 | Umbrella root 3, vskill-platform 6, specwithcode-dev 2, and 5 that are build output or old report copies and need no copy |
| `github/anymodel-umb` | 3 | |
| `github/my-legend-cursor-hackathon` | 2 | |
| Six single-file projects | 6 | snap-to-league, nvidia-nemotron3-nano-omni, hack26-openai, hack26-crypto, dadecountyfc, abyzov-easychamp-tax-filing |

For each project you move: start the handoff, pick Copy local files, tick everything under Secret files except build output, and approve. The preview shows names and sizes, never contents. The app then reminds you to rotate what was sent.

### What is not in any project

These live in your home folder and no project copy carries them.

| What | On the M4 | How it gets to the M5 |
| --- | --- | --- |
| Provider sign-ins: Claude, Codex, Gemini, Cursor, Copilot | `~/.claude`, `~/.codex`, `~/.gemini`, `~/.cursor` | Sign in again on the M5. The app never copies these. |
| GitHub | `~/.config/gh`, Git uses it as its credential helper | `gh auth login` on the M5. |
| SSH keys | 10 key pairs in `~/.ssh` plus `config`: GitHub, GitLab, Hetzner, Google Compute, linux-mini | Copy the folder by AirDrop or a USB drive, never through a repository. Or make a new key per machine and add it to each service, which is cleaner. |
| Cloud command lines | `~/.aws`, `~/.config/gcloud`, `~/.kube`, `~/.config/hcloud`, `~/.config/rclone`, `~/.terraform.d`, `~/.docker/config.json` | Sign in again where the tool allows it (gcloud, aws sso, docker). Copy the rest with the SSH keys. |
| App Store and Android signing | `~/.appstoreconnect`, `~/.asc`, `~/.fastlane`, `~/.android` | Copy with the SSH keys. The release builds run on the M1 runner, so the M5 needs these only if it will release. |
| Tokens in files | `~/.npmrc`, `~/.netrc`, `~/.gnupg`, and anything exported in `~/.zshrc`, `~/.zshenv`, `~/.zprofile` | Copy the shell files and review them. Recreate the npm token with `npm login`. |
| Keychain items | For example `kie-api-key` and `blotato-api-key` | Not copyable by file. Re-add each from the Obsidian note that holds it, or turn on iCloud Keychain. |
| Obsidian vaults | `personal-docs` (credentials, no Git remote), `engineering-docs` (no Git remote), `ai-power` (on GitHub, clean) | Your call 6. This vault is the source for everything above. |
| Tool state | `~/.specweave`, `~/.agents` (skills), `~/.vskill`, `~/.local/bin` | Reinstall with `specweave` and `vskill install`. Copy `~/.local/bin` if you keep own scripts there. |

If you want every project to arrive with all secrets in one step, Migration Assistant does that, Keychain included. It also skips the from-scratch test you asked for, so I would not use it here.

## Suggested order

Do the move in this order, so that the M4 is quiet and clean when the copy starts.

1. Answer the nine calls above.
2. Merge or close the four open pull requests in the app repository, then let the owning threads commit their increment records from the shared checkout.
3. Release the Machines page, then remove the M5 registration and add it again from scratch. That part is yours, and I have not touched the M5.
4. Stop new work on the M4 for the copy. Pull request 269 makes the restart dialog list running threads, so once it ships, use it to see that none is left.
5. On the M5: sign in to GitHub and the providers, then copy the SSH keys and the home-folder items.
6. Move one small project first, for example halfturn, with Copy local files and its secret files. Check it builds on the M5.
7. Move specweave, then EasyChamp. Tick the secret files in each preview.
8. Move or recreate the ten routines on the M5.
9. Keep the M4 folders for a week before deleting anything.
