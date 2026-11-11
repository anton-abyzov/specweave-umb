# Verified Skill: one theme switch, readable hover states and a submit flow that explains itself

## Problem

Anton, November 11, 2026: "the Verified Skill subpage doesn't seem to be synchronized. It's on dark theme, but both others had light theme. Make sure the switch is consistent. On hover, you see the text is not readable... 'Submit an existing repo' gives a little bit of a strange result. Why is it pending while we're scanning? ... It must be all clear for the end user what we are doing here."

Measured on November 11, 2026 in headless Chromium. Evidence: `~/.specwithcode/m4/scratch/2026-11-11-vskill-theme-hover-submit/`.

| Symptom | Cause |
|---|---|
| verified-skill.com dark while spec-weave.com and `/code/` are light | All three follow the system when nothing is stored (`theme-before.json`). The dark page came from a stored choice on verified-skill.com only: an old pick, or the signed-in account preference that `ThemeToggle.tsx` writes into `localStorage.theme` on every load. spec-weave.com has no accounts, so the two drift. |
| The switch differs | spec-weave.com cycles system, light, dark (Docusaurus). verified-skill.com flips light and dark and cannot return to system. A switch back to system is never carried to the other domain. |
| Hovered "Browse skills" is blank | `globals.css` `a:hover { color: var(--wv-iris-strong) }` (0,1,1) beats `.wv-btn--primary { color: var(--wv-on-iris) }` (0,1,0), and the hover background is the same `--wv-iris-strong`: contrast 1:1. Audit: 46 hits, all `a.wv-btn--primary`, both themes (`before-vs.txt`). spec-weave.com: 0 hits. |
| `Uncaught TypeError: Cannot read properties of undefined (reading 'length')` | `SearchPalette.tsx` window keydown handler reads `e.key.length`; browser autofill dispatches `keydown` without `key`. Confirmed at the reported position in the live chunk `2163-3ac8e4d7d3b78d00.js`. |
| "22 skipped" | Every skill already has a submission, so the API returns none as created and the page counts all of them as skipped, including 20 that were sent for a fresh scan. |
| "PENDING: QUEUED · 46D AGO" | The age is the row's creation date. `sw-project` and `sw-sync` were crawler rows (priority 0, created September 25, last touched November 5 and 6) that nothing was scanning, and a person's resubmit neither raised the priority nor queued a scan, so the row blocked every later submit of that skill. |
| A repository submitted on the site is never scanned | The site submits as a batch. With `SKIP_QUEUE_ENQUEUE=true` in production ("the VMs own processing") the batch path of `POST /api/v1/submissions` queues nothing and has no inline fallback. Five `cloudgpu-*` skills a signed-in person submitted on November 8 at 12:36 were still RECEIVED and untouched on November 11. In 21 days people's rows ended as 1 published (after 516 minutes) and 1 rejected (after about 9 days). |
| The queue does not drain (806,648 waiting, oldest February 25, 2026, about 237 an hour) | Three causes, measured November 11 against the production database (read-only) and the VMs' `/status`. (1) No VM runs `submission-scanner`: VM-1 has `github-events`, VM-2 `github-graphql-check, sourcegraph, vendor-org-discovery, sast-scanner`, VM-3 `github-sharded, skills-sh`; zero "Claimed by VM scanner" events in three days. (2) Every scan therefore runs in the Worker, whose judge is Gemini-first with no fallback; since November 10 about 90% end "Held for rescan: Tier 2 unavailable", and publishes fell from 5,827 (November 8) to 584 (November 10). (3) The stale sweep rejects 51,000 to 93,000 never-scanned rows a day ("Stale: in RECEIVED for 282h"), people's rows included. |
| Republish requests wait at priority 0 | A forced rescan resets the row to RECEIVED and leaves the priority it was created with, 0 for crawler rows. |
| Cloudflare RUM CORS error | The analytics beacon is blocked by the visitor's ad blocker. Not a site defect. |

## Scope

In (vskill-platform only): theme default, switch and carry; the unreadable hover state and a site-wide hover and focus contrast audit; the keydown TypeError; the submit page (states, wording, layout in the Weave style); the person lane (Anton's second message, November 11: "a submit from the site is scanned promptly, with its own priority ahead of crawler backlog, and the UI tells the truth about wait times"); the queue throughput fix, as Worker code where the Worker can fix it and as named owner steps where it cannot.

Out: spec-weave.com files (owned by the animated landing worker, who gets the shared shell file to land); purging the backlog (needs Anton's approval); deploying the Hetzner VMs (`crawl-worker/DEPLOY-NOTES.md`: the owner deploys); the other crawler changes in `.specweave/docs/internal/research/skills-sh-sync-comparison.md`; the ad-blocked analytics beacon.

## Acceptance Criteria

- [ ] AC-01: With no stored choice, verified-skill.com follows `prefers-color-scheme` in light and in dark, the same as spec-weave.com and `/code/`.
- [ ] AC-02: The switch on verified-skill.com has the three states of spec-weave.com in the same order (system, light, dark), the same 32px control and the same accessible label text; the choice survives a reload.
- [ ] AC-03: A choice stored before this release that the visitor did not carry in is cleared once, and the signed-in account preference no longer overrides the device choice.
- [ ] AC-04: A light, dark or system choice made on verified-skill.com is carried on every link to spec-weave.com, and a carried `wv-theme=system` clears the stored choice on arrival.
- [ ] AC-05: On every audited page, in light and dark, no link or button has text below 3:1 against its background at rest, on hover or on focus.
- [ ] AC-06: A `keydown` event without `key` on any page throws nothing.
- [ ] AC-07: The submit result names each outcome in plain words (queued, fresh scan started, waiting in the queue, up to date, blocked, rejected, failed) with one sentence saying what happens next, and the summary never calls a rescan "skipped".
- [ ] AC-08: A waiting row shows how long it has waited in its current state and when it was first submitted, and links to its status page.
- [ ] AC-09: When a person resubmits a skill whose row is waiting, the row is raised to the person priority, and if nothing touched it for two minutes it is sent to the scanner; the response says which happened.
- [ ] AC-12: Every skill a signed-in person submits, single or batch, is sent to the Cloudflare queue on the person lane whatever `SKIP_QUEUE_ENQUEUE` says, with inline processing as the fallback when the send fails. An anonymous single submit runs inline as before and stays off the person lane.
- [ ] AC-13: Lanes are explicit constants: CI 90, person 50, internal discovery 40, republish 30, crawler 0. A forced rescan raises its row to the republish lane (person lane when a person asked).
- [ ] AC-14: A person-lane scan falls back to Workers AI when Gemini fails, so it ends with a verdict instead of a hold; crawler scans keep the existing opt-in.
- [ ] AC-15: The recovery sweep sends every RECEIVED row above the crawler lane that has been idle for 10 minutes back to the queue (at most 6 times a day, 100 sends a run, counter and touch written before the send) and never rejects one unscanned. Scans that fail after they start still end through the stuck-scan recovery and the dead-letter queue.
- [ ] AC-16: Live, after deploy: the six stranded people's rows leave RECEIVED within 30 minutes, and a new submit from the site reaches a verdict or a named hold within 10 minutes.
- [ ] AC-10: The submit page uses the Weave page header, buttons, inputs and status tags, in light and dark, with no inline hex colours.
- [ ] AC-11: PR merged, deployed, and the live site passes AC-01, AC-02, AC-05 and AC-06 in headless Chromium with light and dark screenshots saved.

## Approach

Theme. `ThemeToggle.tsx` becomes a three-state control that writes `data-theme` and `data-theme-choice` and stores `theme` only for light or dark. The head script in `layout.tsx` moves to `src/app/theme-init.js` (inlined through `next.config.ts` like the shell), sets both attributes before paint and runs the one-time reset. The account preference read and write leave the toggle; the API stays. `weave-shell.js` carries system as well as light and dark, on every link to a family domain, and marks a choice as the visitor's own. It is byte-identical in both repositories, so the same file goes to the spec-weave.com worker.

Rejected: a shared cookie or storage iframe (two registrable domains, partitioned storage); timestamps on the carried choice (the page you leave should match the page you land on, so the carried choice wins).

Hover. Scope the global link hover in `globals.css` so it never recolours `.wv-btn`. `weave.css` is untouched (spec-weave.com has no hits). The `/queue` trend arrow uses `--wv-pass` and `--wv-fail` instead of fixed hex (2.38:1 on the light canvas).

Submit page. `upsert.ts` returns `lastActivityAt`, `prioritized` and `restarted` for an existing row; `route.ts` passes them through. The page moves its outcome logic to `submit/outcomes.ts` (pure, tested) and its markup to Weave classes in `submit/submit.module.css`.

Person lane. `src/lib/queue/priorities.ts` names the lanes. In `route.ts` a non-internal caller always uses the queue; messages carry `lane: "person"`. The consumer and the inline path pass the lane to `createAiRouter({ workersAiFallback })`. `upsert.ts` claims an idle RECEIVED row with one guarded `UPDATE` (state, `updatedAt` older than two minutes) and sends it; its requeue messages carry the lane. The Cloudflare queue is the right carrier: its backlog was 27 messages on November 11 and the 20 rescans from Anton's own submit finished in minutes.

Throughput. What the Worker can fix: `recoverStaleReceived` starts with a priority lane (`state = 'RECEIVED' AND priority > 0`, idle 10 minutes, `ORDER BY priority DESC, "createdAt"`, limit 100; 1.8 ms on production through the existing `(state, priority, createdAt)` index) that only ever re-sends, and the stale branch skips prioritized rows. Republishes get lane 30. What it cannot fix is listed under Open: the crawler backlog drains only when a scanner with a working judge runs.

Rejected: enabling Workers AI for every scan in this change (cost at 20,000 to 27,000 scans a day is Anton's call); a `(state, updatedAt)` index for the stale query (a migration on a 3.9M-row table, and the lane query does not need it); a VM-side circuit breaker (the VM scanner is not running at all).

Risks: raising priority is one `UPDATE` per waiting row in a batch; the reset drops a deliberate older choice once; Workers AI use for people's scans is metered beyond the daily free allocation (about 200 neurons a scan, only when Gemini fails).

## Decisions

### Asked
- none
### Defaulted (change any before sw-do)
- D-01 Default stays "follow the system" on all three sites (1271 D-04); light for everyone was the alternative.
- D-02 Stored choices from before this release are cleared once on verified-skill.com.
- D-03 The account-level theme preference is no longer applied; theme is per device and carried across the family.
- D-04 The 806,000-row backlog is reported, not purged.
- D-05 People's scans may use Workers AI when Gemini fails. Volume is a few submits a day; "no paid spend" was decided for a Gemini fallback at crawler volume.
- D-06 Internal discovery through `POST /api/v1/submissions` drops from priority 50 to 40 so it never ties with a person.
- D-07 Prioritized rows are never stale-rejected; after 6 sends in a day the sweep waits for the counter to expire.
### Open (owner steps, not blocking this increment)
- O-01 Add `submission-scanner` to a VM's `ASSIGNED_SOURCES` and redeploy it. Without it nothing but the Worker scans the crawler backlog.
- O-02 Set `ENABLE_WORKERS_AI_FALLBACK=true`, or fix the Gemini quota, so crawler scans stop ending in a hold. This is spend at backlog volume.
- O-03 Decide whether the stale sweep keeps rejecting unscanned crawler rows after 24 hours (51,000 to 93,000 a day).

## Tasks

### T-01 Theme: three-state switch, system default, one-time reset, no account override
- AC: AC-01, AC-02, AC-03 | Files: [vskill-platform/src/app/components/ThemeToggle.tsx, vskill-platform/src/app/theme-init.js, vskill-platform/src/app/layout.tsx, vskill-platform/next.config.ts, vskill-platform/src/app/globals.css, vskill-platform/src/app/__tests__/theme-init.test.ts, vskill-platform/src/app/__tests__/weave-sync.test.ts] | Test: `cd repositories/anton-abyzov/vskill-platform && npx vitest run src/app/__tests__/theme-init.test.ts src/app/__tests__/weave-sync.test.ts --maxWorkers=4`

### T-02 Shell: carry system, every family link, mark the visitor's own choice
- AC: AC-04 | Files: [vskill-platform/src/app/weave-shell.js, vskill-platform/src/app/__tests__/weave-shell.test.ts, vskill-platform/src/app/__tests__/weave-sync.test.ts] | Test: `cd repositories/anton-abyzov/vskill-platform && npx vitest run src/app/__tests__/weave-shell.test.ts src/app/__tests__/weave-sync.test.ts --maxWorkers=4`

### T-03 Hover and focus: readable buttons, site-wide audit
- AC: AC-05 | Files: [vskill-platform/src/app/globals.css, vskill-platform/src/app/queue/QueuePageComponents.tsx, vskill-platform/src/app/__tests__/link-hover-scope.test.ts] | Test: `cd repositories/anton-abyzov/vskill-platform && npx vitest run src/app/__tests__/link-hover-scope.test.ts --maxWorkers=4`

### T-04 Keydown without a key no longer throws
- AC: AC-06 | Files: [vskill-platform/src/app/components/SearchPalette.tsx, vskill-platform/src/app/components/__tests__/SearchPalette.keyless.test.tsx] | Test: `cd repositories/anton-abyzov/vskill-platform && npx vitest run src/app/components/__tests__/SearchPalette.keyless.test.tsx --maxWorkers=4`

### T-05 Resubmit raises a waiting row, sends an idle one to the scanner and reports both
- AC: AC-08, AC-09 | Files: [vskill-platform/src/lib/submission/upsert.ts, vskill-platform/src/app/api/v1/submissions/route.ts, vskill-platform/src/lib/submission/__tests__/upsert-prioritize.test.ts] | Test: `cd repositories/anton-abyzov/vskill-platform && npx vitest run src/lib/submission/__tests__ src/app/api/v1/submissions/__tests__/http-contract.test.ts --maxWorkers=4`

### T-08 Person lane: always queued, named priorities, judge fallback
- AC: AC-12, AC-13, AC-14 | Files: [vskill-platform/src/lib/queue/priorities.ts, vskill-platform/src/lib/queue/types.ts, vskill-platform/src/lib/queue/consumer.ts, vskill-platform/src/lib/queue/process-submission.ts, vskill-platform/src/lib/ai/ai-router.ts, vskill-platform/src/app/api/v1/submissions/route.ts, vskill-platform/src/app/api/v1/submissions/__tests__/route.queue-fallback.test.ts, vskill-platform/src/lib/queue/__tests__/consumer.test.ts, vskill-platform/src/lib/ai/__tests__/ai-router-private.test.ts] | Test: `cd repositories/anton-abyzov/vskill-platform && npx vitest run src/app/api/v1/submissions/__tests__/route.queue-fallback.test.ts src/lib/queue/__tests__/consumer.test.ts src/lib/ai --maxWorkers=4`

### T-09 Recovery sweep: priority lane, no unscanned rejection above the crawler lane
- AC: AC-15 | Files: [vskill-platform/src/lib/queue/recovery.ts, vskill-platform/src/lib/submission/recovery.ts, vskill-platform/src/lib/submission/types.ts, vskill-platform/src/lib/submission/index.ts, vskill-platform/src/lib/submission-store.ts, vskill-platform/src/lib/queue/__tests__/stale-received-recovery.test.ts] | Test: `cd repositories/anton-abyzov/vskill-platform && npx vitest run src/lib/queue/__tests__/stale-received-recovery.test.ts src/db/dedup --maxWorkers=4`

### T-06 Submit page: outcomes in plain words, Weave layout
- AC: AC-07, AC-08, AC-10 | Files: [vskill-platform/src/app/submit/page.tsx, vskill-platform/src/app/submit/outcomes.ts, vskill-platform/src/app/submit/submit.module.css, vskill-platform/src/app/submit/__tests__/outcomes.test.ts] | Test: `cd repositories/anton-abyzov/vskill-platform && npx vitest run src/app/submit --maxWorkers=4`

### T-07 Ship: PR, CI, independent review, merge, release, live check
- AC: AC-11, AC-16 | Files: [~/.specwithcode/m4/scratch/2026-11-11-vskill-theme-hover-submit/live/] | Test: `cd ~/.specwithcode/m4/scratch/2026-11-11-vskill-theme-hover-submit && node theme-probe.mjs && node hover-audit.mjs https://verified-skill.com live/after-vs.json / /skills /studio /submit /queue /docs`
