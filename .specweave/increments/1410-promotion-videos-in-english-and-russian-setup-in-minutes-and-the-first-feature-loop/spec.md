# Promotion videos in English and Russian: setup in minutes and the first feature loop

Child of 1387. Asked for by Anton on November 18, 2026, in the message that accepted the first-run plan: "we need to create some promotion videos with a really high-quality Fable 5.2 model to advertise it appropriately, maybe for a Russian and English audience, because this is really looking cool."

## Problem

- **Nothing advertises the new first hour.** The existing videos sell one idea, the limit handoff (the one-tank promo, the November 5 limit reel). None shows what a new user gets in the first ten minutes: one agent ready, a plan as a card, the work, a review by another model family, Done.
- **The only film of it cannot be an ad.** `first-feature-loop.mp4` in 1398's `reports/` is a 15 s silent reference loop drawn from the prototype. It shows a version number and a model name, has no hook and no voice, and none of its screens is a released build.
- **The screens are not built.** 1387, 1396 and 1398 are accepted and not started. The playbook asks for a real capture as the opener and for verified claims only, so a final cut today would present a prototype as the product.
- **No number exists yet.** "Ten minutes" is the guide's own estimate. 1398 T-02 measures it in three runs by hand, and may end that increment if the median is over 15 minutes.
- **Two audiences, two voices.** Russian goes to Telegram AI Power, @antonaipower and VK; English to the SpecWithCode brand accounts. One language per account, never a translation posted as is.

## Scope

In: three storylines for Anton to pick from; scripts in English and in Russian, written separately; a claims table; a storyboard and an animatic; per language one vertical reel and one wide cut; a promo-safe variant of the 15 s loop; voice, music and mix; the scrub before delivery.

Out: posting and scheduling (the social-media-posting route, each post with Anton's yes); paid promotion; a talking-head or avatar segment; other languages; any change to the app.

## Acceptance Criteria

### Story and words

- [ ] AC-01: Three storylines are written in this spec as three different films, each with its device, form, first two seconds, beats, look and sound. Anton picks one, or a mix, before any composition is built (D-01).
- [ ] AC-02: English and Russian scripts are written separately, each in the way a creator speaks to that audience. Neither is a translation of the other. Each reads like a person talking, has no em dashes in voice or on-screen text, and goes through the unslop skill before Anton sees it.
- [ ] AC-03: Every cut opens on the product's value, said and shown in the first two seconds: the plans the viewer already pays for, one coordinator, Claude Code and Codex working on one feature. Setup and the first feature are the proof that follows. One idea per reel, and one call to action at the end that fits the platform.
- [ ] AC-04: `reports/claims.md` lists every claim made in voice or on screen with its source: a measured run with its date and machine, app behaviour at a named release, or a public source shown on screen. The time claim is the median measured in 1398 T-02 or in the release run, with "measured on one Mac" and the date on screen; the script says the measured number, whatever it is. The review by another provider states its condition, a second provider signed in. No savings, free, unlimited or "only app that" claim, and nothing that implies resold tokens or model access.

### What is on screen

- [ ] AC-05: Every shot that presents the product is captured headless from a released build, by the recipe in project memory (`video-production-rules`): a read-only pairing token, private text replaced by staged text in the app's own font, the session revoked afterwards. A shot taken from the prototype carries a "prototype" or «прототип» tag and appears in no final cut.
- [ ] AC-06: Every provider named or shown carries its official mark, copied as it is from `repositories/anton-abyzov/specwithcode/apps/web/src/components/ProviderLogoMarks.tsx` (Codex is the OpenAI mark, Muse the Meta mark). A provider is named the way the viewer knows it on first mention ("ChatGPT Codex"). A mark is moved and scaled, never recoloured, redrawn, morphed or generated. No version number or internal model name is on screen.
- [ ] AC-07: The look is the Weave system from the AI Power playbook: light canvas, iris accent, Schibsted Grotesk. No frame is plain black or an empty dark field. Something always moves. Parts of the story are joined by one continuous canvas or a cause on screen, not by hard cuts between cards. Text stays inside the platform safe zones on the vertical cuts.
- [ ] AC-08: The 15 s loop gets a promo-safe variant for the site and the docs: the reviewer shows its mark and family name with no version number, and every screen in it is from a released build.

### Files, sound and checks

- [ ] AC-09: Per language: a vertical reel, 1080x1920, 40 to 50 s, in two hook variants; and a wide cut, 1920x1080, 60 to 90 s. Masters and small H.264 previews are in `reports/`, and each HyperFrames project is in the scratch folder named in the Approach.
- [ ] AC-10: The voice is "Anton Abyzov best voice" on ElevenLabs and no other, generated only after Anton approves the spend (D-02), with stress and pronunciation checked on every take. Music is licensed and its license is saved beside the master. The mix measures -14 LUFS integrated, give or take 1.5, by `ebur128` on the final file, with the voice clearly above the music.
- [ ] AC-11: Before Anton sees a final: `npx hyperframes check` reports no error for its project; a contact sheet at about 4 frames per second is read for private strings (home paths, account names, emails, project names), black stretches and em dashes; and each claim is checked against `reports/claims.md`. Every hit is fixed and the cut is rendered again.
- [ ] AC-12: Scripts, storyboards and compositions are made on Claude Fable 5.2. When a worker does any of it, its actual model is read back after launch and recorded in `reports/`, and a worker that started on another model is moved or replaced before it writes anything.
- [ ] AC-13: Anton approves each final cut by name. Nothing is posted, scheduled or sent by this increment. The handoff to posting names the account language for each file.

## Approach

### The one thing

You can use the AI plans you already pay for on one feature together: one writes it, another checks it, and a board shows where it is. A new user gets there in the first minutes after install. The viewer should remember: "my two subscriptions, one app, and the work gets checked."

One viewer, one task: a developer with a new Mac and two plans asks for a dark mode switch. That request is the piece of data that travels from the hook to the payoff.

### Three storylines

**A. "Ten minutes on a new Mac" (recommended).** Device: a moment in someone's day, with a clock that really runs. Form: split screen to one.

- A new Mac, the two plans the viewer also pays for, and a clock in the corner that never stops. When it reads the measured time, one feature has been asked for, built by one AI, checked by another and sits in Done.
- First two seconds: the voice and the headline say "I already pay for Claude and ChatGPT." The Claude and OpenAI marks sit on the real Agents step, both Ready, and the clock starts at 0:00. In Russian: «Я уже плачу за Claude и ChatGPT.»
- Beats: hook (two plans, the clock starts) → tension (two apps, two chats, nobody checks the work) → reveal (one app, four stages in four beats, "the rest can wait") → proof (one sentence asked, a card appears, moves to Active, the other provider's mark reviews it, Done, the clock always in frame) → payoff (the clock stops, pull back to the whole board) → claim ("Your subscriptions. Your machines. One coordinator.") → end card.
- Look: light Weave canvas, real captures at 1.6 to 2 times their size, the clock in iris, licensed desk footage behind the opening and the end.
- Sound: Anton's voice, a light pulse that keeps time with the clock, one soft hit when the card lands in Done.

**B. "One card, start to Done".** Device: one object across the product. Form: an object-to-object chain; the camera never leaves the card.

- The sentence the viewer types folds into a card, and the camera rides it through Planned, Active, In review and Done. It feels calm: everything about the feature is in one place.
- First two seconds: the real composer with "Add a dark mode switch" already typed. Send is pressed in the first half second and the sentence folds into a card under the headline "One request. Two AIs. One board."
- Beats: hook (the sentence becomes a card) → tension (the card waits: who builds it, who checks it?) → reveal (the Claude mark picks it up, Active) → proof (a second provider's mark opens the review thread, its result) → payoff (Done, pull back to a board with more cards) → claim → end card.
- Look: light canvas, the card at twice its size with its real labels, each column a colour field the camera pushes through.
- Sound: music-led, voice optional, a soft paper fold on each change.

**C. "The thread".** Device: the object is the explanation, one violet thread with six knots. Form: one continuous flight along the thread.

- The camera flies along a thread over woven cloth. At each knot a real piece of the app surfaces and the thread pulls tight; at the end the weave resolves into the SpecWithCode mark. It feels crafted and premium.
- First two seconds: cloth in macro, a violet thread crosses the frame and ties its first knot around the Claude mark, under "Plan. Build. Review. Done."
- Beats: hook (the first knot) → six knots, a real piece of the app at each → payoff (the thread pulls tight, the card lands in Done) → claim (the weave becomes the mark) → end card.
- Look: cloth macro, either licensed footage or the backdrop generated for the 15 s film, iris thread, pieces of the app as paper-like cards.
- Sound: music only, a plucked string per knot.

A is recommended because a stranger follows a person, a clock and two plans they also pay for, and it opens on the value Anton set for every video on November 17, 2026. B is the proof section inside A. C is the 15 s silent loop that already exists and stays the site and docs piece (AC-08).

### What can be made when

1. **Now, no release needed (T-02, T-03).** Scripts, the claims table, the storyboard, the motion system, and an animatic cut from the prototype for Anton to judge story and pace. The animatic is tagged "prototype" and is never posted.
2. **During 1398 T-02.** The three runs by hand with today's app are recorded headless. They give the measured time for AC-04 and a first real capture of the Board, the review switch and a review thread, all of which exist today.
3. **When the screens ship (T-04 on).** The Access list is 1387's PR B, the setup card and the Board states are 1396, the guide is 1398. Each final is captured from the release that carries its screens, so a cut that shows only the Board and the review can be final before a cut that shows setup.

Projects live in `~/.specwithcode/m4/scratch/2026-11-18-setup-promo/<cut>/`, one HyperFrames project per cut, with shared assets beside them. Finals, previews and the claims table live in this increment's `reports/`.

### Rejected

- **Reusing the 15 s loop as the ad.** It shows a version number, has no hook, and is drawn from a prototype.
- **A final cut from the prototype now.** It would present screens that do not exist as the product. An animatic for Anton is the honest use of the prototype.
- **Translating one script.** The Russian hook that worked was the limit pain, in creator speech. A translated English line reads as a calque, as past cuts showed.
- **An avatar or AI replica of Anton.** The playbook bans it. A real two-second selfie of him saying the hook is welcome if he records one, and is not required.

### Risks

- The measured time comes in over ten minutes. The script says the measured number, and A's title changes with it.
- 1398's proof ends that increment. Then A's proof section is the same loop done by hand, which works today, and the guide is not shown.
- With one provider signed in there is no reviewer. Every cut shows two providers Ready first, and the caption states the condition.
- Kie.ai has no credits (402 on November 18, 2026). A and B need no generated image. C's cloth uses licensed macro footage first, then the Higgsfield backdrop already made.
- The playbook text still says "source available". The repository has been public under MIT since November 6, 2026, so these cuts make no license claim on screen and the caption follows the brand rules at posting time.

## Decisions

### Asked
- D-01, for Anton: which storyline. Recommended **A. "Ten minutes on a new Mac"**, with B's card as its proof section. B. "One card, start to Done". C. "The thread". **Storyline picked by Anton on November 18, 2026: A, with B's card as its proof section.** He was shown "The promo storyline pick (A recommended) with the paid voice pass" and answered: "Yes, do what's recommended."
- D-02, for Anton: the voice. Recommended **A. Anton's ElevenLabs voice on every cut, one paid pass per language once the scripts are locked.** B. Music and on-screen text only, which costs nothing and loses the creator's voice. **Decided November 18, 2026: A**, by the same answer. The choice of voice is settled. No paid pass is run until the scripts are locked and Anton has seen the cost.
- D-03, for Anton: timing. Recommended **A. Scripts, storyboard and a prototype animatic now; each final is captured and rendered when its screens are released.** B. Also publish a teaser from the prototype now, tagged "prototype". **Not answered by name. Work goes on under A as the default; nothing from the prototype is published.**

### Defaulted (change any before sw-do)
- D-04: Two cuts per language: a vertical reel in two hook variants, and a wide cut. The 15 s loop stays silent.
- D-05: Russian and English are written separately by the same author, on Fable 5.2, and each goes through unslop.
- D-06: No generated video. Real captures, licensed footage and motion graphics only; a generated still is a fallback for C's cloth.
- D-07: This increment ends at Anton's approval of the finals. Posting is its own step with its own yes.

### Open
- none

## Tasks

### T-01 Anton picks the storyline and answers the voice and timing questions
- AC: AC-01 | Files: none | Test: grep -q "Storyline picked by Anton on" .specweave/increments/1410-promotion-videos-in-english-and-russian-setup-in-minutes-and-the-first-feature-loop/spec.md

### T-02 Scripts in English and Russian, the claims table and the storyboard
- AC: AC-02, AC-03, AC-04 | Files: none | Test: test -s .specweave/increments/1410-promotion-videos-in-english-and-russian-setup-in-minutes-and-the-first-feature-loop/reports/script-en.md && test -s .specweave/increments/1410-promotion-videos-in-english-and-russian-setup-in-minutes-and-the-first-feature-loop/reports/script-ru.md && test -s .specweave/increments/1410-promotion-videos-in-english-and-russian-setup-in-minutes-and-the-first-feature-loop/reports/claims.md && ! grep -q "$(printf '\342\200\224')" .specweave/increments/1410-promotion-videos-in-english-and-russian-setup-in-minutes-and-the-first-feature-loop/reports/script-en.md .specweave/increments/1410-promotion-videos-in-english-and-russian-setup-in-minutes-and-the-first-feature-loop/reports/script-ru.md

### T-03 Motion system and a prototype animatic for Anton's look
- AC: AC-07, AC-12 | Files: none | Test: test -s .specweave/increments/1410-promotion-videos-in-english-and-russian-setup-in-minutes-and-the-first-feature-loop/reports/animatic-en.mp4 && test -s .specweave/increments/1410-promotion-videos-in-english-and-russian-setup-in-minutes-and-the-first-feature-loop/reports/models-used.md

### T-04 Capture the released screens, with staged text and the session revoked
- AC: AC-05, AC-06 | Files: none | Test: test -s .specweave/increments/1410-promotion-videos-in-english-and-russian-setup-in-minutes-and-the-first-feature-loop/reports/captures.md && grep -q "session revoked" .specweave/increments/1410-promotion-videos-in-english-and-russian-setup-in-minutes-and-the-first-feature-loop/reports/captures.md

### T-05 Build the reels and the wide cuts, and the promo-safe loop
- AC: AC-06, AC-07, AC-08, AC-09 | Files: none | Test: for f in reel-en-a reel-en-b reel-ru-a reel-ru-b wide-en wide-ru loop-promo; do test -s .specweave/increments/1410-promotion-videos-in-english-and-russian-setup-in-minutes-and-the-first-feature-loop/reports/$f.mp4 || exit 1; done

### T-06 Voice, music and mix
- AC: AC-10 | Files: none | Test: test -s .specweave/increments/1410-promotion-videos-in-english-and-russian-setup-in-minutes-and-the-first-feature-loop/reports/loudness.md

### T-07 Scrub every final, then Anton approves each by name
- AC: AC-11, AC-13 | Files: none | Test: test -s .specweave/increments/1410-promotion-videos-in-english-and-russian-setup-in-minutes-and-the-first-feature-loop/reports/scrub.md && grep -q "Finals approved by Anton on" .specweave/increments/1410-promotion-videos-in-english-and-russian-setup-in-minutes-and-the-first-feature-loop/spec.md

### T-08 Verify and close 1410
- AC: AC-13 | Files: none | Test: cd /Users/antonabyzov/Projects/github/specweave-umb && specweave task list 1410 | grep -q "7/8 done"
