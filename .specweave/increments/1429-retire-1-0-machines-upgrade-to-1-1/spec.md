# Retire 1.0: machines upgrade to 1.1

Draft, planned. Nothing here is decided beyond Anton's words below; the open questions go to him before any task starts.

## Problem

Anton, November 19, 2026, 5:47 PM, on 1422's Versions card (relayed by the coordinator): "Think about what the best solution is. I suggest moving to 1.1 soon and just getting rid of all 1.0 versions at some point, so that you cannot download it and you could only upgrade. This will be kind of mandatory." On the Older app card: "Maybe for early versions, it makes sense because they are not stable."

Why it matters now:

- 1428's one-way join holds only between machines that both run 1.1 or newer (1422 D-08). Each path kept for an older build cost a design round in 1422 (`1422-*/reports/design-review-1.md` to `design-review-3.md`), and some rules cannot hold against an older app at all (an older new-machine app cannot declare a join, so its code approves a full device).
- Every release so far is 1.0.x (1.0.394 on November 19, 2026). The 1.1.0 cut was approved on November 13 and rescheduled on November 17, and is still waiting on Anton's gate call (`feedback_release_coordination_with_m4`). From 1.1.0, builds are Insiders until the daily train promotes them (`docs/studio/release-train.md`).

What stands in the way today:

- The version skew rule (October 19, 2026, `reference_update_install_mechanics`, "version skew policy"): no blanket "must be on latest" enforcement; block only per operation. Retiring 1.0 changes that rule for 1.0 only; Anton's words above are the change, and this increment writes it down.
- No forced updates on a busy machine (`decision_no_forced_updates`, `decision_update_pause_setting`, increment 1304): an automatic update waits for quiet unless the machine's owner turned on "Pause running work for updates". A required upgrade must still wait for a quiet moment.
- Updaters: service agent `channel: stable` skips 1.1+ prereleases, so 1.0 machines reach 1.1 only once the train promotes a 1.1 build to stable, or on the Insiders track.

## Scope

In:

- A 1.0 machine learns that 1.1 is required, says so on its own screen with the reason, and installs 1.1 at the next quiet moment (never cutting running work unless its owner allowed that).
- After the cutoff, no download path offers 1.0: the website, `install.sh`, `install.ps1`, the CLI and the GitHub release that updaters and links read.
- After the cutoff, a 1.1 machine refuses to join, pair or hand off with a 1.0 machine and names the machine to update.

Out:

- Choosing or dispatching the 1.1.0 version. That is Anton's go through the release process (`request-release.sh`, the train); no thread picks a version.
- 1428's join rules.
- Deleting published 1.0 releases or tags (updaters and rollback read them; see question 4).

## Open questions for Anton

1. Cutoff: when does 1.0 stop working with 1.1 machines: a date, a number of days after 1.1 is stable, or once every machine of the account reads back 1.1?
2. Until a 1.0 machine upgrades, what may it still do: everything except join and pair with 1.1 machines, or only show "Update required"?
3. A machine that stays busy for days: does "mandatory" mean it waits for quiet however long, or that after a deadline it pauses work to install even with the setting off?
4. Old downloads: hide 1.0 from the website and install scripts only, or also mark the GitHub releases so links stop offering them? Deleting them would break rollback and the updaters' paths.
5. iPhone: does the iPhone app follow the same 1.1 floor, and what does an older iPhone app show?
6. The relay: should Connect refuse a 1.0 app after the cutoff, or leave that to the machines?

## Acceptance Criteria (draft, after the answers)

- [ ] AC-01: A 1.0 machine on the final 1.0.x build shows "Update required" with the reason and the version, and installs 1.1 at the next quiet moment; with "Pause running work for updates" off it never pauses running work (`decision_update_pause_setting`), unless Anton's answer to question 3 says otherwise.
- [ ] AC-02: After the cutoff, no download path offers 1.0 (website, `install.sh`, `install.ps1`, CLI install, the release links), and a fresh install gets 1.1 or newer.
- [ ] AC-03: After the cutoff, a 1.1 machine refuses to join, pair or hand off with a 1.0 machine and names the machine to update; nothing it already had with a 1.1 machine changes.
- [ ] AC-04: The version skew rule in project memory and `docs/studio/` says 1.0 is retired and why, and still blocks per operation for every later version.
- [ ] AC-05: Checked on real machines: a 1.0 machine updates by itself once quiet, and a fresh install from each download path is 1.1.

## Approach

Inventory first (T-01): every download, install and update path and what each reads (website, `install.sh`, `install.ps1`, CLI, desktop electron-updater tracks, the service update agent's channels, the train's manifests, iPhone), and what the final 1.0.x build must carry, because 1.0 builds already shipped can only be told through a newer 1.0.x build or through what their updater already reads. Then Anton answers the questions above, then the ACs are fixed and the tasks get files.

## Tasks

### T-01 Inventory the download, install and update paths
- AC: AC-01, AC-02 | Files: .specweave/increments/1429-retire-1-0-machines-upgrade-to-1-1/reports/ | Test: each path cites its code or config at `origin/main` and what a 1.0 machine reads today

### T-02 Anton answers the open questions; fix the ACs and tasks
- AC: AC-01, AC-02, AC-03, AC-04, AC-05 | Files: .specweave/increments/1429-retire-1-0-machines-upgrade-to-1-1/spec.md | Test: each question has Anton's answer, verbatim

### T-03 Verify and close
- AC: AC-01, AC-02, AC-03, AC-04, AC-05 | Files: .specweave/increments/1429-retire-1-0-machines-upgrade-to-1-1/ | Test: specweave verify 1429

## Review

Anything that blocks a machine, refuses a join or changes an updater is an access and update change: Muse Wonderful reviews it, and Anton accepts before release.
