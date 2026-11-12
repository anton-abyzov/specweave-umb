# Pause stale-sweep rejection of unscanned crawler submissions

## Problem

Coordinator, November 11, 2026, after increment 1292: "Pause the stale-sweep rejection of never-scanned crawler rows until a scanner is running. It's reversible and loses no data."

Measured November 11, 2026 on the production database (read-only) and Cloudflare analytics.

| Fact | Evidence |
|---|---|
| The VM submission scanner was removed from every VM on October 24, 2026 at 15:31 UTC | `/opt/scanner-worker/.env` on VM-1 was last written then and holds `ASSIGNED_SOURCES=github-events`; `/health` reports 1, 4 and 2 sources on the three VMs |
| Publishes fell from 39,000 to 49,000 a day (October 20 to 23) to about 6,000 a day | `SubmissionStateEvent`, `toState = 'PUBLISHED'` per day |
| Since October 31 the stale sweep rejects 71,000 to 98,000 rows a day that nothing scanned | events with trigger `Stale: in RECEIVED for Nh.`; 83,982 on November 10 |
| The sweep never re-sends a crawler row | it reads the 1,000 rows with the oldest `updatedAt`; with a backlog all of them are past the 24h mark, which is the reject branch |

`recoverStaleReceived` was written to clear rows a broken scanner left behind. With no scanner it is the main thing emptying the queue, and it empties it by rejecting skills unseen.

## Scope

In (vskill-platform): a switch that stops the stale sweep from rejecting crawler rows, set on in production; the priority lane from 1292 is unaffected.

Out: re-adding `submission-scanner` to a VM. Its intent review runs on paid Workers AI (4.5 to 25 million neurons a day while it ran, October 16 to 24; about zero since), which is the spend decision left to Anton. Restoring rows the sweep already rejected. The Worker judge fallback for crawler scans.

## Acceptance Criteria

- [ ] AC-01: With `PAUSE_STALE_RECEIVED_REJECTION` set to `true`, `recoverStaleReceived` changes no crawler row's state and does not read the stale window.
- [ ] AC-02: With the switch on, rows above the crawler lane are still re-sent by the priority lane.
- [ ] AC-03: With the switch unset or any other value, the sweep behaves as before.
- [ ] AC-04: The switch is a Worker variable in `wrangler.jsonc`, set to `true`, with a comment saying how to resume.
- [ ] AC-05: Live, after release: zero `Stale: in RECEIVED` rejections in the hour after the deploy, measured against the hour before.

## Approach

One early return in `recoverStaleReceived` after the priority lane, keyed on the Worker variable. Skipping the read as well as the reject is safe because the window holds only rows past 24h while there is a backlog, and it saves a 1,000-row query and about 2,000 KV reads every 10 minutes.

Rejected: resuming automatically when a VM heartbeat reports the scanner. The sweep would then expire the old end of the backlog while the scanner works toward it, which is the loss this change stops. Resuming is a deliberate one-line change.

Risk: the RECEIVED count now grows by the crawlers' intake until a scanner runs. No row is lost and the switch is one line to reverse.

## Decisions

### Asked
- none
### Defaulted
- D-01 The switch lives in `wrangler.jsonc`, so its state is reviewed and versioned; reversing it is a PR and a release.
- D-02 Rows the sweep rejected before this change stay rejected.
- D-03 While paused the sweep also skips its finalize check for crawler rows, so a row whose scan finished but whose state write was lost stays RECEIVED until the pause ends. Rare, and nothing is lost (review finding, accepted).
### Open
- O-01 Whether to run the VM submission scanner again, at Workers AI cost. Anton's call.

## Tasks

### T-01 Pause switch in the stale sweep, on in production
- AC: AC-01, AC-02, AC-03, AC-04 | Files: [vskill-platform/src/lib/queue/recovery.ts, vskill-platform/src/lib/env.d.ts, vskill-platform/wrangler.jsonc, vskill-platform/src/lib/queue/__tests__/stale-received-recovery.test.ts] | Test: `cd repositories/anton-abyzov/vskill-platform && npx vitest run src/lib/queue/__tests__/stale-received-recovery.test.ts src/db/dedup --maxWorkers=4 --reporter=dot`

### T-02 Ship and measure
- AC: AC-05 | Files: [~/.specwithcode/m4/scratch/2026-11-11-vskill-theme-hover-submit/stale-pause/] | Test: `test -s ~/.specwithcode/m4/scratch/2026-11-11-vskill-theme-hover-submit/stale-pause/after.txt`
