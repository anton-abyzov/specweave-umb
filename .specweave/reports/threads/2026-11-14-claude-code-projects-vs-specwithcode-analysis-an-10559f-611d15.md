---
title: "Claude Code Projects vs SpecWithCode: analysis and post drafts"
thread: "thread:delegated-task:command%3Amcp%3A47d25bb4-1336-4930-bf17-5c42452fad13%3Adelegate-task%3A2982aadf-ba01-4269-819a-8560ae0b86d5"
threadTitle: "Answer the ClaudeDevs post with SpecWithCode"
savedAt: "2026-11-14T06:56:59.326Z"
date: Saturday, November 14, 2026
status: drafts, nothing published
source_post: https://x.com/ClaudeDevs/status/2121375309287301360
---

# Claude Code Projects vs SpecWithCode

Nothing is published. Each post below needs Anton's yes.

![Coordinator across agents and machines (illustration)](/Users/antonabyzov/.specwithcode/m4/evidence/claude-projects-compare-2026-11-14/card1.png)

## 1. What Anthropic announced

@ClaudeDevs, November 13, 2026, 5:51 PM. 541.8K views, 10.8K likes, 3.9K bookmarks at 2 AM on November 14.

- **Projects in Claude Code.** A coordinator in a project chat starts one thread per task, answers "where are we on everything?" and posts updates when a thread is ready or needs you.
- **/btw and /fork.** /btw puts a side topic in its own thread. /fork starts a new thread from the current one.
- **Reminders.** A thread hides until a set time, then comes back and the coordinator brings it up.
- **Read-only share link** for one thread, for anyone signed in to Claude. Threads that had computer access can't be shared.
- **Artifacts row** at the top of the threads panel, plus artifact thumbnails per thread.

**How they explain it.** Five short, dark-theme UI clips (18 s, 22 s, 13 s, 9 s, plus one still image). Each clip shows one feature with real UI and a believable task list ("Fix flaky cart test", "Add rate limiting to checkout"). The right panel groups threads into Ready for review, Waiting on you and Working. A decision card offers A/B options with a Recommended badge. Clips have no narration and one feature per post, and the thread is five posts long. Frames: `/Users/antonabyzov/.specwithcode/m4/evidence/claude-projects-compare-2026-11-14/source/main-contact.jpg` and `/Users/antonabyzov/.specwithcode/m4/evidence/claude-projects-compare-2026-11-14/source/5.jpg`.

## 2. Feature map, with evidence

Checked against `anton-abyzov/specwithcode` main `2e6f780dc` (November 14, 2026; latest tag v1.0.294).

| Their feature | SpecWithCode | Evidence |
|---|---|---|
| Coordinator runs parallel threads, reports status | Ships | Coordinator plus thread tools, `apps/server/src/mcp/toolkits/thread/tools.ts`; sidebar Working/attention groups, `apps/web/src/components/Sidebar.tsx:3860-3890` |
| Decision card, A/B, Recommended badge | Ships | `ask_user` description, `apps/server/src/mcp/toolkits/orchestrator/tools.ts:210` ("lettered options... recommended choice badged... thread shows as Needs you") |
| /fork | Ships, plus merge back | `studio_thread_fork`, "Conversation fork" in `apps/web/src/components/chat/MessagesTimeline.tsx:3620`, merge back in `ThreadRelationshipsControl.tsx:535` |
| Reminder on a thread | Partly: snooze until a time | `thread.snooze` with `snoozedUntil`, `apps/server/src/mcp/toolkits/thread/handlers.ts:503-509`; snoozed group in Sidebar. Unverified: whether the coordinator brings it up when it wakes |
| Artifacts row | Ships as artifact shelf | `ArtifactShelfList.tsx`, `ThreadArtifactStrip`; PR #87 (1264) |
| Read-only share link | **Gap** | No share-link code found |
| /btw | **Gap** (no slash command; ask the coordinator to start a thread) | No match for `btw` |

**What SpecWithCode adds** (claims used in the drafts):

- Threads on many agents. Adapters for Claude Code, Codex, Cursor, Grok, OpenCode, Antigravity, Pi, Devin and ACP agents in `apps/server/src/orchestration-v2/Adapters/`.
- Threads on other machines (Macs and Linux; ministorm and M1 workers) through `studio_thread_launch` with `machine` and Connect. Windows workers are not claimed.
- When one provider hits its usage limit, the same chat continues on another signed-in provider, but only if a project rule allows it (stated with the condition).
- iPhone app (App Store 0.1.1) and Android app (Play 0.2.2).
- Open source (MIT). That is the exact wording the "Marketing and brand rules" memory allows once the development repository is public. Checked November 14, 2026: `anton-abyzov/specwithcode` is PUBLIC, GitHub reports the MIT License, and LICENSE came from commit `072265ee0` ("Open source SpecWithCode under MIT", November 6, 2026). The posts add no new grant; they describe the existing one. One rule disagrees: `AGENTS.md:96` still says "Do not add a project-wide MIT grant". Anton's November 6 decision in both memories replaces it, so that line is stale. Anton should confirm before the first post goes out.

Not claimed: anything about Claude's machine or provider limits, savings, or token resale.

## 3. Recommendation

Post it. Today is Saturday, November 14; the announcement went up Friday, November 13, at 5:51 PM ET. Quote it instead of replying under it, because promo replies on @ClaudeDevs read as spam.

The platforms split. X is news-driven, and a quote of a post that is still climbing loses most of its value by Monday, so X goes out on Saturday. LinkedIn reach for B2B and dev content drops on weekends, so it waits for Monday morning.

- **X**: a 4-post thread from @aabyzov that quotes the @ClaudeDevs post. Use the founder voice, since this is a builder's take. Repost it from @specwithcode. Send through Blotato. **Saturday, November 14, 11:00 AM ET.**
- **Threads**: one post with card1 and card3. **Saturday, November 14, 2:00 PM ET.**
- **LinkedIn**: the SpecWithCode company page through Postiz (`cmvj9s4nq0001ousuatpivcfm`), 3 images. **Monday, November 17, 9:00 AM ET.** A personal version for Anton is optional.

Tone: give Anthropic credit and keep it factual. The comparison table names our gaps, which makes the rest believable. Before scheduling, read the Blotato and Postiz queues for collisions; that check has not run yet.

Every word stays inside the facts in section 2. I did not use "way stronger" in the copy. The "adds" column makes that point without claiming it.

## 4. Drafts

Unslop rules applied by hand from `~/.agents/skills/unslop/SKILL.md`: no em dashes, no AI vocabulary, plain verbs.

### X thread (Blotato, quote of the @ClaudeDevs post)

**1/** (card1, quote https://x.com/ClaudeDevs/status/2121375309287301360)

> Anthropic just shipped Projects in Claude Code. A coordinator in one project chat runs your tasks as parallel threads and tells you when one is ready or needs you.
>
> Good call. SpecWithCode has worked this way for a while, and it runs on more than Claude.

**2/** (card2)

> What's the same in SpecWithCode today:
>
> - the coordinator starts a thread per task and reports back
> - a decision card with a recommended answer when a thread needs you
> - fork a thread, or put one away until a set time
> - every report and artifact on one project shelf

**3/** (card3)

> Where it goes further:
>
> - threads run on Claude Code, Codex, Cursor, Grok, OpenCode and more, on accounts you already have
> - one coordinator sends threads to your other Macs and Linux boxes
> - iPhone and Android apps for the same project

**4/**

> Two things they shipped that we don't have yet: a read-only share link for a thread, and /btw. Both are good ideas.
>
> SpecWithCode is open source (MIT) and free to try: specwithcode.com

Lengths: 254 (+ quote URL), 266, 236, 184 characters.

### LinkedIn (SpecWithCode company page, card1 + card2 + card3)

> Anthropic shipped Projects in Claude Code on Friday, and the idea is right.
>
> You talk to one coordinator. It splits the work into parallel threads, tells you what's ready, and asks only when a thread needs a decision.
>
> SpecWithCode works the same way today:
>
> - one project chat with a coordinator that starts a thread per task
> - a decision card with the recommended answer marked
> - fork a thread, snooze one until a set time, find every report on one shelf
>
> And a few things on top:
>
> - threads can run on Claude Code, Codex, Cursor, Grok, OpenCode and more, using accounts you already have
> - the coordinator can send threads to your other Macs and Linux machines
> - iPhone and Android apps for the same project
>
> Fair credit where it's due. They have a read-only share link for threads and a /btw command, and we don't yet.
>
> SpecWithCode is open source (MIT).
>
> https://specwithcode.com/?utm_source=linkedin&utm_medium=social&utm_campaign=claude-projects-compare

### Threads (card1 + card3)

> Anthropic shipped Projects in Claude Code. One coordinator, parallel threads, and it tells you when something's ready.
>
> SpecWithCode works the same way, and the threads can run on Codex, Cursor, Grok or Claude Code, on any of your Macs or Linux boxes. There's a phone app too.
>
> Open source (MIT). specwithcode.com

## 5. Visuals

The visuals are HTML rendered with headless Chrome, 3200x1800 at 2x. They are labeled as illustrations in the footer. The task names are our own, not Anthropic's. Provider logos come from `apps/marketing/public/harnesses/`.

- `/Users/antonabyzov/.specwithcode/m4/evidence/claude-projects-compare-2026-11-14/card1.png`: the coordinator answers "where are we on everything?" across agents and machines.
- `/Users/antonabyzov/.specwithcode/m4/evidence/claude-projects-compare-2026-11-14/card2.png`: the decision card with Recommended.
- `/Users/antonabyzov/.specwithcode/m4/evidence/claude-projects-compare-2026-11-14/card3.png`: the comparison, including our two gaps.
- Sources: `/Users/antonabyzov/.specwithcode/m4/evidence/claude-projects-compare-2026-11-14/build-html/`

I did not use real app screenshots. The existing captures show private threads, fleet IDs and a thread title naming T3. A clean capture needs a demo fixture project, which the app does not have. If Anton wants real captures, the next step is a seeded demo project captured headless.

## 6. Video (lead visual for all three posts)

![Threads punch-in from the video](/Users/antonabyzov/.specwithcode/m4/evidence/claude-projects-compare-2026-11-14/video/poster-threads.png)

The video is `/Users/antonabyzov/.specwithcode/m4/evidence/claude-projects-compare-2026-11-14/video/specwithcode-coordinator-1080p.mp4`: 29.8 s, 1920x1080, 30 fps, 5.6 MB, made with HyperFrames.

Beats:

1. **Hook, 0-4.6 s.** "Projects in Claude Code just shipped." Then "SpecWithCode already runs this, on every agent you use."
2. **Real app, 4.6-13.2 s.** The camera punches in on the composer, "where are we on everything?" is typed, and the coordinator's reply reveals line by line. Then it punches in on the Threads panel and its Working group.
3. **Agents, 13.2-17.2 s.** The real Settings > Providers list: Codex, Claude, Cursor, Grok and Muse Code, all signed in.
4. **Machines, 17.2-21.8 s.** Real Settings > Machines rows for m1, m3 and linux-mini, showing the "m4 to m1 Full access" grants.
5. **Decision card, 21.8-26.2 s.** The card is rebuilt with the app's real labels, and the Recommended badge pops in.
6. **End card, 26.2-29.8 s.** The SpecWithCode mark, "Open source (MIT)", specwithcode.com, and "Claude Code is a product of Anthropic. SpecWithCode is independent."

How the screens were captured:

- Headless Chrome against the local web UI on `127.0.0.1:8319`, with a read-only pairing (`orchestration:read`, 1 h).
- On the main app screen, private thread, chat and project titles, and the coordinator's text, were swapped in the DOM for demo names. Every frame of that scene carries the label "Real SpecWithCode app. Demo project, names changed."
- The provider and machine rows are real labels. Plan names were swapped for "Signed in", and the subline text after "Connect" or "Tailscale" was painted out. "Anna's Macbook Air" and the account email are cropped out.
- The capture session `29627216` was revoked afterwards. The pairing token had already been used up.

Sound: sound effects only (typing, send click, whooshes, pop, riser, bass hit). They are the files bundled with HyperFrames, and the package does not state their license. Measured, not listened to: -13.6 LUFS integrated, true peak -4.9 dBTP. There is no music bed. HeyGen is signed out, and the old promo track has no license note. Adding licensed music takes `heygen auth login --oauth` and a re-render.

Checks: `npx hyperframes check` passes with no warnings. A 2-second scrub of the rendered file shows no black or empty frames: `/Users/antonabyzov/.specwithcode/m4/evidence/claude-projects-compare-2026-11-14/video/scrub.jpg`.

Sources:

- `/Users/antonabyzov/.specwithcode/m4/evidence/claude-projects-compare-2026-11-14/video/film-source/`
- `/Users/antonabyzov/.specwithcode/m4/evidence/claude-projects-compare-2026-11-14/video/app-staged-capture.png`

Use: attach the video to X post 1/ and to the LinkedIn and Threads posts, and keep the cards for X posts 2/ and 3/. LinkedIn through Postiz takes one video or 2+ images, so the LinkedIn post uses the video alone.

## Open items

- Read the Blotato and Postiz queues before scheduling.
- Confirm that a snoozed thread resurfaces in the coordinator chat before claiming parity with reminders. The drafts only say "put one away until a set time".
- Optional: a short motion version of card1 in the style of their clips.
