# Equal coordinators, and a handoff you can see

November 19, 2026, revised the same day for the review `reports/reviews/review-gpt-6.2-astra-7.md` (fix first, EC-01 to EC-12). Anton decided the concept at 1:34 to 1:43 AM Eastern. At about 2:15 AM he asked for the work to be finished without asking him, so a ship verdict on this revision counts as his acceptance. Building starts on that verdict, not before.

Code facts are read at `origin/main` of `repositories/anton-abyzov/specwithcode` (`a13bc1110`); the files the review cites are unchanged since its baseline `719e2d8a2`.

## The idea in four lines

1. Every machine that has the project runs its own coordinator. They are equals. Typing on a machine talks to that machine's coordinator. Nothing moves a coordinator role, and nothing makes one give way.
2. A handoff moves **threads**, one transfer per thread. It never moves a project role, project memory or a routine.
3. It starts in exactly two ways: you ask (Hand off, or "hand off to M5"), or a thread's track is out of tokens on this machine and the project's usage-limit rule is `switch`. Closing the laptop never starts one.
4. Both starts open the same progress view. Only the reason line differs.

## Who owns a thread

Two equal coordinators could both act on one thread. So ownership is per thread, never per project (EC-05):

- A thread is named by its **lineage**: the source machine, the source thread id and the epoch it was handed at. The receiver already derives the continuation id from those three (`continuationThreadId`, `apps/server/src/handoff/HandoffReceiver.ts:192-202`). A project is named by its linked project id, never by its name.
- Each thread has one **execution owner** (its lease holder) and a **checkpoint sequence**. Only the current owner may offer a revision. The receiver claims it atomically: same operation again gets the same receipt; an older or divergent revision is refused and neither history is overwritten.
- A thread that just arrived is not sent back automatically for the same run and usage window. Different threads may cross in opposite directions at the same time.

## The transfer record

Losing a reply is neither failure nor permission to run here (EC-06). Proof 6 showed the window's disconnect cutting the server's handoff between hold and takeover and leaving a thread `handing-off` for good.

- Before the first hold, the source's **server** writes a batch and one record per thread: operation id, target, checkpoint sequence, intended disposition. The server runs the transfer; closing a window never cuts it.
- The target writes its acceptance before it launches anything.
- States per thread: `pending`, `held`, `sent`, `accepted`, `resumed`, `ready`, `stayed`, `failed`, `unknown`. On reconnect or restart of either machine, the source asks the target about that same operation, or replays it. It never picks another target and never runs the thread here while the answer is unknown.
- Only a definite "not accepted" releases the hold. A hold that never reached `sent` can always be released by hand ("Resume here"), which fixes the stuck case of proof 6.
- The previous turn must have stopped before the target starts the next one. A turn that ignores the interrupt for 45 seconds stays here with "Its turn did not stop in 45 seconds".

## What each thread does on arrival

A 99% reading is not permission to start a turn (EC-04). The batch carries a **disposition per thread**:

| Disposition | When | On the target |
|---|---|---|
| Resume | Its run was interrupted by the handoff or stopped on the limit | Continues that run, once |
| Ready | Idle, finished its last turn (the limit path's ten-minute window), or a manual handoff of an idle thread | Installed idle. Starts nothing until you write |
| Stays | A question, approval or sign-in pending; you pressed Stop; settled; Review without a permitted reviewer there; over a size limit | Nothing moves. The row says why |

Each thread is judged on its own. A healthy sibling on the same track is never swept in.

## When it starts by itself

Same machine first, and never on a guess (EC-01, EC-02):

- For a thread on a track, **every** remote attempt, including the last admission check before sending, requires the thread's track to be exhausted on this machine: each source of the current model, then each later model on that track, per the user's saved routes, source permissions and track order. Each provider instance fails on its own; one instance's failure never holds a sibling. A provider with `supportsProviderSwitchingViaHandoff=false` is never moved across providers. `ask`, `wait`, no targets, near-reset waits and source consent work as today.
- That precedence beats a saved `other-machine-first` order for track threads. Settings says so under the order picker: "Projects on tracks use this machine's models first. This order applies to projects without tracks." Projects without tracks keep their saved order unchanged.
- A target counts only for the **same track**: the machine's allowed sign-ins are intersected with the thread's track. Before accepting, the receiver confirms the actual model, the account and a fresh usage reading below the threshold. A target on the same quota pool adds nothing; the next eligible sign-in on that machine is tried, never another track. Unknown or stale usage never qualifies an automatic move. By hand it is allowed with the line "Same account as m4: adds no usage" or "Usage unknown".
- **Every machine out.** The thread stays where it is. The progress view says "Complex track is out on every machine" and the earliest known reset among eligible sign-ins ("Next reset: M5 at 4:10 AM"), or "Reset unknown". It checks again at that reset. No move, no retry loop, no other track.

## Review keeps its reviewer

Today a review delegation never moves, on purpose (`MachineLimitHandoff.ts:417-422`). The new handoff carries the review routing marker, family restrictions, review policy and effort with the thread, and applies them to the receiver's first pick and every fallback, for marked reviews and older `Adversarial review:` prefix ones (EC-03). A receiver that cannot show a permitted reviewer family is not a target, and the row reads "Review stays here: no permitted reviewer on M5".

## The result comes back

Proof 5: a worker finished on the target and its launcher never heard (EC-07). The receiver creates the continuation as a system thread, and the wake only follows agent-launched threads (`LaunchedWorkerWake.ts:124-129`).

- The record keeps the **launcher** (the coordinator or parent that waits) apart from the execution owner.
- Before the takeover is sent, the source registers a follow row for the continuation in the existing remote worker store (`RemoteWorkerStore`, `RemoteWorkerFollower`), with the launcher as caller. The source can compute the continuation id beforehand.
- The follower reads the result over the existing peer route and delivers it once (`deliveredRunIds`). If the launcher's machine was offline, the result waits in the target's thread and is delivered after reconnect. A replayed receipt adds no second wake.

This is the first thing to build: it fixes a bug users hit today.

## Routines stay with their runner

Two active coordinators would otherwise both fire a coordinator-owned routine, or neither would (EC-08; proof 4 saw neither).

- Each routine has one durable **runner** machine and a revision, independent of any coordinator. Existing coordinator-owned routines keep the machine that runs them today as their runner.
- A thread handoff never copies, enables or moves a routine. A routine bound to a worker that moved stays on its runner and rests with "Its thread was handed off to M5", and the progress row offers "Move the routine too".
- Edits route to the runner. A stale edit is refused. Webhook URLs stay local.
- An explicit runner move stages the routine off on the target, confirms it off at the source, carries the due slot and run state, then turns it on once, under one operation id that a retry asks about first.

## Memory and context

A handoff changes only thread ownership (EC-09). The thread carries its context at a named revision. Coordinator conversations stay on their machines. Shared project memory reconciles only through the existing revision-checked sync (`linkedMemoryMerge.ts`, `LinkedMemorySync.ts`); packet arrival time is never precedence, and an unresolved conflict is shown, not replaced.

## Becoming equal

Phase 1 behavior is real code, not just labels (EC-10). Link acceptance writes `transferred` on the joining machine and only `active` counts (`ProjectLink.ts`, `CoordinatorRole.ts:93-105`).

- One migration turns every existing `active`, `transferred` and `standby` member into an active local coordinator, and new link acceptance writes `active`. Both coordinator histories, local worker ownership, project identity and Settings unlink stay.
- Retired: project-level give-way, standby takeover of the coordinator, and routing the composer to another machine. Kept: the per-thread execution fence.
- Peers state a capability (`handoff.v2`). A peer without it shows "Needs update" and is not a target. No build flag, and never a silent fallback to moving the coordinator. An old peer reconnecting with a superseding binding is not obeyed.
- The Extra coordinator labels and Fix (T-18) leave in the same pull request as this migration, after the routine runner is released.

## Sleep is not a start

Saved settings still fire today: an Away target with `sleepTrigger: "always"` or `"on-battery"`, and the desktop's renderer fallback (`awaySleepRoute.ts:105-114`, `DesktopHandoffSleep.ts:158-205`). Sleep is retired as a start event at sender and receiver, including legacy preferences and outstanding sleep intents (EC-11). A sleep or checkpoint notice stays, but it is never a request to move. A handoff already authorized before the lid closed stays recoverable through its transfer record.

The receiver's start kinds (`HandoffReceiver.ts:185-190`) are settled the same way:

| Kind | From now |
|---|---|
| `handoff`, `machine-handoff` | The two starts (manual and limit) through the transfer record |
| `sleep` | Refused as a start; an outstanding one is answered "not accepted" and released |
| `auto-takeover` | Retired as a thread start: silence on a machine starts nothing (T-23). Coordinator standby takeover leaves with T-22 |
| `continue-here` | Kept for one thread you pull to this machine by hand; it is a manual start |

## The progress view

![Hand off "specweave" to M5: 2 of 4 finished, 1 resumed, 1 failed](/Users/antonabyzov/Projects/github/specweave-umb/.specweave/increments/1390-sync-projects-across-machines-and-hand-off-work/reports/handoff-progress-mockup.png)

Mockup: `reports/handoff-progress-mockup.html`. Rules (EC-12):

- The card shows the project with its icon and the name in quotes, and the reason: "Complex track out of tokens on m4" or "You asked to hand off to M5".
- **Finished** = resumed + ready + stayed + failed. The summary counts the same rows: "2 of 4 finished: 1 resumed, 1 failed". The bar width is finished ÷ total from those rows.
- Row states, each with one meaning and one safe next step:

| Row | Means | Next step |
|---|---|---|
| Pending | Not held yet | Cancel |
| Held | Paused here, not sent | Resume here |
| Waiting for confirmation | Sent; M5 has not answered | Wait. Not counted as failed; never "Resume here" |
| Resumed on M5 | Its run continues there | Open on M5 |
| Ready on M5 | Installed idle; nothing started | Open on M5 |
| Stayed | Did not go, with the reason | The fix the reason names |
| Failed | M5 refused it; it runs here again | Try again |

- Record states map to rows: `pending` to Pending, `held` to Held, `sent`, `accepted` and `unknown` to Waiting for confirmation, and the rest by name.
- Any failed or stayed row means the summary never reads "all on M5".
- Every machine out: "Complex track is out on every machine", with the earliest reset or "Reset unknown", and no bar.

## Where each finding lands

The review's release and task disposition is followed in `spec.md`: T-09 to T-13 and T-18 are rewritten, T-19 to T-24 are added, and each pull request ships on its own in the order there.

| Finding | Rule | Spec |
|---|---|---|
| EC-01 Leaves while a local model has room | Track exhaustion here gates every remote attempt; beats a saved remote-first order for track threads, Settings explains | AC-37 · T-13 |
| EC-02 Target is not proof of capacity | Same-track intersection, receiver confirms model, account and fresh quota; unknown never automatic; every-machine-out stays with reset | AC-38, AC-39 · T-10, T-13 |
| EC-03 Review without its lock | Marker, families, policy and effort travel; no permitted reviewer means it stays | AC-40 · T-24 |
| EC-04 99% is not permission to start | Per-thread disposition: resume, ready or stays; no sibling sweep | AC-41 · T-10, T-11 |
| EC-05 One execution owner per thread | Lineage, owner and epoch, checkpoint sequence, atomic claim, receipt replay, no reverse bounce | AC-42 · T-20 |
| EC-06 Lost reply | Server-run transfer record, acceptance before launch, replay, release only on a definite no; stuck hold releasable | AC-43 · T-20 |
| EC-07 Result never returns | Launcher kept apart from owner; follow row registered before takeover; delivered once | AC-44 · T-19 |
| EC-08 Routine runner | One durable runner per routine; handoff never moves routines; explicit staged runner move | AC-45 · T-21 |
| EC-09 Memory conflicts | Handoff changes only thread ownership; memory through its revision-checked sync | AC-46 · T-11 |
| EC-10 Labels alone leave a coordinator that cannot run | Migrate members and link acceptance; capability check and "Needs update"; T-18 ships in the same PR | AC-35, AC-48 · T-20, T-22, T-18 |
| EC-11 Saved sleep triggers still start | Sleep (and silence) retired as a start at both ends, legacy settings and intents included | AC-36 · T-23 |
| EC-12 Bar counts outcomes as arrivals | Finished counts and bar from the same rows; seven row states; every-machine-out state | AC-47 · T-12 |

