---
title: "GTA 6 Livestream Full Script and Run Sheet"
thread: "thread:delegated-task:command%3Amcp%3A5203f9f6-1c70-4578-a8a9-fc4f6def2ca7%3Adelegate-task%3A7c29be75-c165-4e11-ab9e-a4f19017f234"
threadTitle: "GTA 6 livestream script and run sheet"
savedAt: "2026-11-20T18:55:34.736Z"
date: "November 20, 2026"
streamTitle: "I Let AI Run My Life in GTA 6 (Chat Can Overrule It) 🔴 LIVE"
where: "Twitch (main), YouTube and X (via obs-multi-rtmp) from OBS on M5"
thumbnail: "/Users/anton/Projects/github/specweave-umb/.specweave/reports/threads/2026-11-19-gta6-live/thumb-real-G2.jpg"
status: "Ready for 5-minute offline dry run; nothing posted or streamed"
---

# GTA 6 Livestream: Full Word-for-Word Script and Run Sheet

**Stream title:** `I Let AI Run My Life in GTA 6 (Chat Can Overrule It) 🔴 LIVE` (Twitch: `I Let AI Run My Life in GTA 6 (Chat Can Overrule It) 🔴`)

**Thumbnail (live on YouTube):** [thumb-real-G2.jpg](/Users/anton/Projects/github/specweave-umb/.specweave/reports/threads/2026-11-19-gta6-live/thumb-real-G2.jpg)

**Links:**
- YouTube (Public, scheduled, Auto-start ON, Auto-stop ON, DVR ON): `https://www.youtube.com/watch?v=MZLPv4uP8nQ`
- Twitch (VODs kept 7 days, Clips ON): `https://twitch.tv/aabyzov`
- X: `@aabyzov` (stream key configured in `obs-multi-rtmp`, Producer broadcast unverified)

**How the stream works:** PS5 streams to PS Remote Play on M5. OBS captures the Remote Play window, your camera, `Mic/Aux` (Shure MV7+), and game audio (`Video sound` -> `com.playstation.RemotePlay`). OBS outputs to Twitch, and `obs-multi-rtmp` mirrors to YouTube and X automatically (`sync-start` is enabled on both). `ai-call.py` screenshots the Remote Play window about every 20 s, asks Claude Fable 5.2 (`claude-fable-5-2` via `claude -p` on `admin@easychamp.com` Max 20x) for one decision, and writes it to the OBS `AI Call` overlay. `chat-vote.py` reads `#aabyzov` Twitch chat anonymously and writes `VETO` / `KEEP` counts to the `Chat Votes` overlay. You hold the DualSense the entire stream.

**Camera note (important):** The iPhone 16 Continuity Camera is currently unavailable in OBS on M5 while another worker investigates it. Do not select `iPhoneA` in OBS, because over USB it captures your iPhone screen (exposing apps and notifications), not the camera. Use **MacBook Pro Camera** (verified working right now in both `iPhone16` and `PS5 Remote Window` scenes) or **Studio Display Camera** (fallback option, but it rendered black in OBS at 1:08 PM ET, so confirm a live picture in preview before using it).

---

## Part 1: What to Do (Pre-Stream Run Sheet)

Run all terminal commands from `/Users/anton/.specwithcode/m4/scratch/2026-11-20-gta6-viral/`.

### Step-by-step pre-stream checklist

1. **On M5: clean up the desktop and stay awake.**
   - Hide the Wispr Flow bubble (it sits over Remote Play's PS button).
   - Move the macOS Dock back to the MacBook screen so it never covers the game window.
   - Close FaceTime or any app holding a camera, and turn on Do Not Disturb so macOS notifications never pop onto screen.
   - Open Terminal and keep the Mac awake for 4 hours:
     ```bash
     caffeinate -s -t 14400
     ```

2. **On PS5 and M5: connect PS Remote Play and resume (do NOT start a new game).**
   - **On M5:** bring PS Remote Play (`RemotePlay.app`, v9.5.0) to the front and connect to your PS5.
   - **On PS5 / DualSense:** connect your DualSense controller (Sony's docs recommend USB to the Mac for Remote Play, or paired directly). Confirm GTA 6 resumes where yesterday's save left off (prison corridor behind the guard, suspended at 5:55 PM on November 19 with 0 trophies). **Do not start a new game**, or it could overwrite yesterday's progress.
   - Leave Remote Play visible as a large window (not minimized) so window capture works.

3. **On M5: check OBS profile, camera fallback, audio, and game capture.**
   - Open OBS and confirm the top bar shows Profile **`GTA6 Twitch`** and Scene Collection **`Untitled`**.
   - If a `"Properties for 'Video Capture Device Full'"` dialog is still open, click **Cancel** (clicking OK could switch it back to `iPhoneA`).
   - Switch to scene **`iPhone16`** and check the camera preview:
     - `Video Capture Device Full` is currently set to **MacBook Pro Camera** (verified working). Angle the MacBook lid so you are framed cleanly.
     - If you prefer **Studio Display Camera**, test it first in Properties and confirm it actually renders a live image (earlier today OBS showed black on it; if black, keep **MacBook Pro Camera**).
     - Leave `iPhoneA` unselected.
   - Switch to scene **`PS5 Remote Window`** and check `Camera Quadrant` (bottom-right corner, also set to **MacBook Pro Camera** fallback).
   - Point OBS's `GTA Remote Play` capture at the new Remote Play window (its macOS window ID changes every launch):
     ```bash
     ~/.specwithcode/m4/scratch/2026-11-19-gta6-live/venv/bin/python /Users/anton/.specwithcode/m4/scratch/2026-11-20-gta6-viral/fix-capture.py
     ```
     (Or in OBS: double-click `GTA Remote Play` and re-select the live PS Remote Play window manually.)
   - Check audio meters in OBS while moving in-game and speaking:
     - `Mic/Aux` (Shure MV7+) moves when you talk and is unmuted on Track 1.
     - `Video sound` (`com.playstation.RemotePlay`) moves when the game makes sound, is unmuted on Track 1, and has Monitoring set to **Off** (so game audio does not double).
     - Wear headphones or AirPods for listening only (not as mic input, because AirPods drop mic quality to 24 kHz), or keep Studio Display speakers low to prevent mic echo.

4. **On M5: check multi-output destinations (Twitch, YouTube, X).**
   - In OBS, open **Docks > Multiple output** and confirm **`YouTube`** and **`X @aabyzov`** are listed with sync-start enabled (main OBS output goes to **Twitch**).
   - **YouTube:** already verified Public, title and G2 thumbnail updated, Auto-start ON, Auto-stop ON, DVR ON (`MZLPv4uP8nQ`). Starting OBS automatically takes YouTube live, even past the 12:00 PM ET scheduled time.
   - **X (`@aabyzov`):** unverified because X was signed out in M5 Chrome. Open `https://studio.x.com/producer` in Chrome, sign in if needed, and verify the broadcast and stream key are active (or untick sync-start on `X @aabyzov` if you only want Twitch + YouTube today).

5. **On M5: start the AI caller and Twitch vote counter, then run a 5-minute offline dry run.**
   - Open two Terminal tabs in `/Users/anton/.specwithcode/m4/scratch/2026-11-20-gta6-viral/`:
     - Tab 1 (Twitch vote counter, anonymous read-only):
       ```bash
       python3 /Users/anton/.specwithcode/m4/scratch/2026-11-20-gta6-viral/chat-vote.py aabyzov
       ```
     - Tab 2 (live AI caller, capped at 25 calls to protect the Claude Max 20x plan):
       ```bash
       python3 /Users/anton/.specwithcode/m4/scratch/2026-11-20-gta6-viral/ai-call.py --every 20 --max 25
       ```
   - **5-minute dry run (NOT live):** watch scene **`PS5 Remote Window`** in OBS while playing for 1 to 2 minutes. Confirm:
     - The game renders smoothly inside `GTA Remote Play`.
     - One real `AI: ...` / `WHY: ...` line appears cleanly at top center without covering the bottom-left minimap.
     - `CHAT  VETO 0  ·  KEEP 0` appears below the AI line and resets on the next call.
     - Pause the AI loop before going live so you do not burn calls during the Starting Soon screen:
       ```bash
       touch /Users/anton/.specwithcode/m4/scratch/2026-11-20-gta6-viral/pause.flag
       ```
     - If the dry run burned several calls, press `Ctrl+C` in Tab 2 and restart `ai-call.py --every 20 --max 25` right after pausing so you start the live show with the full 25-call budget.

6. **On iPhone 16 (optional, only if you want to retry Continuity Camera later):**
   - Keep **iPhone Mirroring** closed on M5 (it blocks Continuity Camera).
   - If the other worker tells you the Mac side is fixed, verify `Settings > General > AirPlay & Continuity > Continuity Camera` is ON, Wi-Fi and Bluetooth are ON (same Wi-Fi as M5, same Apple Account), lock the iPhone, and place it on its stand near M5. Do not hold up the stream waiting on it.

7. **On M5: go live.**
   - Switch OBS to scene **`Starting Soon`**.
   - Mute `Mic/Aux` if you want silence during the countdown card.
   - Click **Start Streaming** in OBS (starts Twitch, YouTube, and X together).
   - Confirm in Twitch dashboard (`https://twitch.tv/aabyzov`) and YouTube Studio (`MZLPv4uP8nQ`) that video and audio are arriving.
   - Post the approved announcements (drafts in Part 4 below) if you want them out as you go live.
   - Open Twitch chat on a second monitor or phone so you can read chat and hit **Clip** during live moments. Keep YouTube and X chat open nearby to read aloud.

---

## Part 2: OBS Scene Switching Map

Exact scene names verified from `/Users/anton/Library/Application Support/obs-studio/basic/scenes/Untitled.json` on M5:

| When | Switch OBS to scene | What is on screen | Notes |
|---|---|---|---|
| Stream start (`0:00` to `2:00`) | **`Starting Soon`** | `ai-controls-starting-soon-1920x1080.png` | Keep `Mic/Aux` muted until ready to talk; keep `pause.flag` present so AI calls do not run yet. |
| Opening hook (`2:00` to `3:30`) | **`iPhone16`** | Full-screen face camera (**MacBook Pro Camera** fallback, or Studio Display Camera if live) | Unmute `Mic/Aux`. Hold up the DualSense so viewers see you control the pad. |
| Main gameplay (`3:30` to `55:00`) | **`PS5 Remote Window`** | `GTA Remote Play` + `Camera Quadrant` (bottom-right) + `AI Call` (top) + `Chat Votes` (top) + `Video sound` | Remove `pause.flag` (`rm /Users/anton/.specwithcode/m4/scratch/2026-11-20-gta6-viral/pause.flag`) right as you switch here. |
| Closing & chat poll (`55:00` to `60:00`) | **`iPhone16`** | Full-screen face camera | Create `pause.flag` (`touch .../pause.flag`) so the AI stops calling moves during wrap-up. |
| End of broadcast | Stop Streaming | Stream ends on Twitch, YouTube (Auto-stop ON), and X | Confirm all three outputs stopped in **Multiple output**. |

### Scenes to NEVER click on air

- **`All 4 Screens`**: contains the stale `NDI Ministorm Screen` tile (previously showed a pairing prompt and email).
- **`Full Camera`** and **`Macbook Camera for iPhone Share`**: both use `iPhoneA` (USB screen mirror of your iPhone, not the camera).
- **`M5 + iPhone16`** and **`StudioDisplay ScreenSharing`**: full desktop captures that will expose open windows, chats, or Chrome tabs unless cleared first.

---

## Part 3: Full Livestream Script (Word for Word, in Order, with Timings)

Timings below are rough targets for a 60-minute opening hour (you can keep playing up to 4:00 PM ET using the Beat 10 loop). **Follow the game, not the clock.**

Each beat carries its verification label:
- **Tested:** verified on M5 with real frames or live chat.
- **Built, not tested live:** code works on saved frames or test runs; needs the 5-minute offline dry run.
- **From guides, unverified in our play:** Prologue sequence comes from games.gg and Fextralife guides; adapt if the game differs.
- **Your call live:** depends on what happens on stream.

---

### Beat 0 (`0:00` to `2:00`) - Pre-Roll Countdown
- **OBS scene:** `Starting Soon`
- **Status:** Tested (scene renders full frame in OBS)
- **Action:** Click **Start Streaming**. Confirm Twitch, YouTube, and X are live. Keep `pause.flag` active. Check that `Mic/Aux` is ready to unmute.

---

### Beat 1 (`2:00` to `3:30`) - Opening Hook (Full Camera -> Game)
- **OBS scene:** Start on `iPhone16` (hold DualSense in frame), then switch to `PS5 Remote Window` halfway through.
- **Status:** Your call live | **Clip target:** Hook
- **Say word for word:**
  > "Everyone is playing GTA 6 right now. I'm letting an AI run my life in it. Here is the deal: I hold the controller the entire time, the AI never presses a button. Instead, it watches my game screen, and about every 20 seconds it puts one decision right up there at the top of the screen, with one line explaining why. Whatever it calls, I have to play it. Unless you stop it. If you are on Twitch, type VETO or KEEP in chat. The counter updates live right under the AI call, and every new AI call resets the vote. If VETO wins, I do the opposite. If you are watching on YouTube or X, shout in chat too, I'll read you out loud. Let's turn the AI loose."
- **Action:** Switch OBS to **`PS5 Remote Window`** and unpause the AI caller:
  ```bash
  rm -f /Users/anton/.specwithcode/m4/scratch/2026-11-20-gta6-viral/pause.flag
  ```

---

### Beat 2 (`3:30` to `5:00`) - First Live AI Call
- **OBS scene:** `PS5 Remote Window`
- **Status:** Built, not tested live (verified 3.3 to 5.2 s per call on saved frames)
- **Action:** Wait for `AI is thinking...` to switch to the first `AI: ...` / `WHY: ...` line. Point up at the overlay.
- **Say word for word:**
  > "There it is, first call on screen. Let's read it out: [read the exact AI line and WHY line aloud]. That is the loop: every 20 seconds, one screenshot in, one decision out. Alright, I'm doing it. Twitch chat, remember, type VETO if you think the AI is losing its mind."
- **Action:** Carry out the AI's move immediately on the DualSense.

---

### Beat 3 (`5:00` to `8:00`) - Prison Corridor and Guard *(Only if your PS5 save resumes here)*
- **OBS scene:** `PS5 Remote Window`
- **Status:** Tested on this exact recorded scene (Fable 5.2 got "follow the guard" right 2 of 2 times)
- **Context:** Yesterday's save stopped in the prison corridor behind the guard (the cell and Yolanda's crossword are already played, so skip them).
- **Say word for word (when the guard says "Alright, come on" and the AI calls follow):**
  > "Look at that: '[read AI line, e.g., Follow the guard]'. Easy one, robot. Even I could figure that out. Let's see how cocky it stays once things actually get chaotic."
- **Action:** Follow the guard. If the PS5 reloaded an earlier autosave instead of the corridor, just read whatever the AI calls and play it without mentioning the cell/crossword unless it actually appears on screen.

---

### Beat 4 (`8:00` to `11:00`) - First Cutscene (AI Stays Quiet)
- **OBS scene:** `PS5 Remote Window`
- **Status:** Tested (Fable 5.2 outputs `AI: watching...` on cutscenes 2 of 2 times)
- **Action:** When the overlay flips to `AI: watching...`, point at it.
- **Say word for word:**
  > "Look up top: 'AI: watching...' It actually knows when it's a cutscene and shuts up. Unlike you, chat. Seriously though, during cutscenes nothing is forced, so tell me in chat: where do you think this story is going? And if you're on YouTube or X, drop your predictions, I'm reading both chats."

---

### Beat 5 (`11:00` to `15:00`) - Counselor Cutscene (30-Second Tech Explainer)
- **OBS scene:** `PS5 Remote Window`
- **Status:** Tested / Measured (3.3 to 5.2 s latency in `ai-call.py`; 16 of 16 scenes right in vision tests; `claude-fable-5-2` on Claude Max 20x plan) | **Clip target:** LinkedIn clip
- **Action:** Use the quieter counselor dialogue to deliver a clean, self-contained 30-second clip explaining the engineering setup.
- **Say word for word:**
  > "Quick 30 seconds on how this actually works while they talk. My PS5 is streaming through PS Remote Play into my Mac. A tiny Python script grabs just the game window every 20 seconds, skips it if the screen hasn't changed, and sends the frame to Claude Fable 5.2 running on my Claude subscription. Three to five seconds later, one move and one reason land straight on OBS. A second script listens to Twitch chat for VETO and KEEP. The AI decides, the human executes and checks. Honestly, that's the exact same split I use in software engineering."

---

### Beat 6 (`15:00` to `20:00`) - Robbery Flashback
- **OBS scene:** `PS5 Remote Window`
- **Status:** From guides, unverified in our play; Your call live | **Clip target:** Robbery clip
- **Fact-check guardrail:** Do NOT say "the AI told me to rob a store" — the robbery is scripted by the story.
- **Say word for word:**
  > "Alright, story time: Lucia robs a store. To be completely honest with you, that part is the story, not the AI's idea. The game makes me rob it. The AI just calls how I do it. Let's see what kind of criminal advisor this model is. [Read each AI call aloud as it appears.] Chat, VETO is live right now, do we listen to the machine or overrule it?"
- **Action:** Read every AI line out loud and execute it unless Twitch `VETO` beats `KEEP`.

---

### Beat 7 (`20:00` to `23:00`) - Customer Grabs Lucia / Quick-Time Button Prompt
- **OBS scene:** `PS5 Remote Window`
- **Status:** Fact (measured 3.3 to 5.2 s AI latency vs ~1 s prompt; guide beat unverified in our play) | **Clip target:** `The AI is too slow for GTA 6`
- **Action:** Press the button prompt yourself immediately — do not wait for the AI.
- **Say word for word:**
  > "Whoa, button prompt! I'm hitting that myself! Look, this is why I hold the controller. The AI takes three to five seconds to read a frame and answer. That prompt gave me about one second. And when we tested it on PS5 menus earlier, it named the wrong controller button half the time anyway. So the AI calls strategy, I press the buttons. Hit Clip on that one."

---

### Beat 8 (`23:00` to `28:00`) - Police Chase (AI Narrating the Past)
- **OBS scene:** `PS5 Remote Window`
- **Status:** Built, behaviour live (guide beat unverified in our play) | **Clip target:** `My AI narrates GTA 6 five seconds late`
- **Action:** Drive/escape at full speed and let the 4-second-delayed AI lines pop up on screen naturally.
- **Say word for word:**
  > "Okay, we are running from the cops and the AI is still trying to coach me. Look at what it just put up top: '[read late AI line aloud]'. Bro, that was five seconds ago! The AI is literally narrating the past right now. Too late, robot, I'm already around the corner! Chat, if it drops a late call while we're mid-crash, clip that."

---

### Beat 9 (`28:00` to `32:00`) - The Arrest
- **OBS scene:** `PS5 Remote Window`
- **Status:** From guides (unavoidable scripted arrest), unverified in our play | **Clip target:** `Even the AI couldn't stop this arrest`
- **Fact-check guardrail:** Do NOT say "the AI got me arrested in 20 minutes" — the arrest is scripted.
- **Say word for word:**
  > "And we are busted. Alright, full honesty: that arrest is scripted, you can't avoid it. Even an AI watching every move couldn't talk me out of this one. Still makes a great clip though. Let's see where the game drops us next once the Prologue opens up."

---

### Beat 10 (`32:00` to `55:00`+) - Post-Prologue Open Choices & Chat VETO Battles
- **OBS scene:** `PS5 Remote Window`
- **Status:** Built; votes depend on live Twitch viewers | **Clip target:** `My chat overruled the AI in GTA 6` / `The AI's worst call in GTA 6`
- **Fact-check guardrail (criminal profile):** Do NOT say "hidden score" or promise "Irredeemable" today. Guides (Polygon, Clarín) say GTA 6 tracks a criminal profile icon separately for Jason and Lucia, and Rockstar has not officially confirmed the five tiers. Check the in-game icon before naming anything.
- **Say word for word (entering open play):**
  > "Now the real show starts. No more scripted hallway: where we go, who we talk to, which car we take, all up to the AI, unless Twitch chat overrides it. Guides say GTA 6 rates what kind of criminal you are, with an icon in the game, so let's keep an eye out for it and see where the AI takes us. No promises we hit any extreme tier in one hour, we're just letting it play out."
- **Say word for word (when VETO beats KEEP on screen):**
  > "Hold on, look at the counter! VETO wins! Chat just overruled the machine! The AI wanted me to [state AI call], so I am doing the exact opposite. You guys own whatever happens next. Hit Clip on that!"
- **Say word for word (every 10 minutes to re-hook new viewers):**
  > "If you just joined: I'm letting an AI run my life in GTA 6. It screenshots my game every 20 seconds and puts its move at the top of the screen. I hold the controller and do what it says. Twitch chat can type VETO or KEEP to overrule it, and YouTube and X, keep talking to me in chat, I'm reading you live."

---

### Beat 11 (`55:00` to `60:00`, or end of session) - Closing Poll & Wrap-Up
- **OBS scene:** Switch to `iPhone16` (full-screen camera) and pause the AI (`touch /Users/anton/.specwithcode/m4/scratch/2026-11-20-gta6-viral/pause.flag`).
- **Status:** Your call live
- **Fact-check guardrail:** Do NOT promise "Next stream, the AI holds the controller" — controller automation is not built (Remote Play ignores the keyboard). Ask it as a poll instead.
- **Say word for word:**
  > "What a run. Honestly, that was way funnier than I expected: the AI nailed the quiet moments, completely panicked when things moved fast, and chat kept it humble with the vetoes. Before we wrap, one question for chat on Twitch, YouTube, and X: should we actually try to let the AI hold the controller one day? Type YES or NO in chat right now. [Read out answers for 60 seconds.] Thank you everyone for hanging out, voting, and clipping those moments. Follow or subscribe so you catch the next experiment, and I'll see you soon!"
- **Action:** Raid a GTA 6 channel on Twitch if you want, then click **Stop Streaming** in OBS and confirm all three outputs (Twitch, YouTube, X) stopped.

---

### Live Recovery Lines (Keep Visible While Streaming)

| What goes wrong | What shows on screen | Say word for word | What to do |
|---|---|---|---|
| AI call errors out or times out | `AI: (no signal, I'm on my own)` | "The AI just rage-quit. Alright chat, I'm on my own until it comes back." | Keep playing; the next 20 s tick retries automatically. |
| AI stays quiet or cutscene | `AI: watching...` | "Nothing to decide here, chat picks." | Keep moving or watch the cutscene. |
| AI takes over 10 s or misses a fast cue | `AI is thinking...` | "Too slow, AI, I'm following what's on screen." | Ignore the late call and play the visible cue. |
| AI makes a clearly wrong call | Wrong `AI:` line | "Wait, read that again: '[read it]'. That is completely wrong, and that is why we clip it." | Laugh, hit Clip in Twitch, and do the sensible move (or let chat VETO). |
| AI hits the 25-call cap | `AI: out of calls for today. You're on your own.` | "We just burned through all 25 AI calls to protect my Claude subscription. From here on out, chat IS the AI — tell me what to do!" | Either continue with chat calling moves, or restart `ai-call.py --every 30 --max 15` only if you want to spend more plan budget. |
| Remote Play disconnects | Black `GTA Remote Play` area | "PS5 Remote Play dropped for a second, give me 15 seconds to reconnect." | Reconnect in Remote Play, then re-run `fix-capture.py`. |

---

### Live Control Commands (Quick Reference on M5)

- **Pause AI calls:** `touch /Users/anton/.specwithcode/m4/scratch/2026-11-20-gta6-viral/pause.flag`
- **Resume AI calls:** `rm -f /Users/anton/.specwithcode/m4/scratch/2026-11-20-gta6-viral/pause.flag`
- **Reset Twitch votes manually:** `touch /Users/anton/.specwithcode/m4/scratch/2026-11-20-gta6-viral/reset.flag`
- **Re-bind OBS after Remote Play reconnects:** `~/.specwithcode/m4/scratch/2026-11-19-gta6-live/venv/bin/python /Users/anton/.specwithcode/m4/scratch/2026-11-20-gta6-viral/fix-capture.py`
- **Stop either script cleanly:** `Ctrl+C` in its Terminal tab (`ai-call.py` clears `overlay.txt` on exit).

---

### Honest Vertical Clips to Cut in Twitch (No ffmpeg Needed)

Twitch saves your VOD for 7 days and Clips are enabled. Press **Clip** while live or cut from the VOD afterward. Publish a clip only if the moment actually happened:

| Moment | Honest Clip Title | When It Is Honest |
|---|---|---|
| Quick-time button prompt | `The AI is too slow for GTA 6` | Always (latency measured at 3.3 to 5.2 s vs ~1 s prompt) |
| Police chase late overlays | `My AI narrates GTA 6 five seconds late` | Only if delayed lines visibly land during the chase |
| Scripted arrest | `Even the AI couldn't stop this arrest` | Always (arrest is scripted) |
| Twitch VETO beats KEEP | `My chat overruled the AI in GTA 6` | Only if VETO actually wins a vote on screen |
| Real AI hallucination or bad call | `The AI's worst call in GTA 6` | Only for an actual wrong call |

---

## Part 4: Announcement Post Drafts (Version 2, Not Posted)

All drafts below use the verified claims and G2 thumbnail (`/Users/anton/Projects/github/specweave-umb/.specweave/reports/threads/2026-11-19-gta6-live/thumb-real-G2.jpg`). Adjust "Live now" vs time before posting. Nothing has been posted automatically.

**X (`@aabyzov`)**
> Live now: I'm letting AI run my life in GTA 6.
>
> It watches my screen and puts every decision up top. I hold the controller and do it.
>
> Twitch chat can type VETO and I do the opposite. 🔴
>
> YouTube: https://www.youtube.com/watch?v=MZLPv4uP8nQ
> Twitch: https://twitch.tv/aabyzov

**LinkedIn**
> I'm streaming GTA 6 live with an AI calling my moves.
>
> A vision model looks at the game window, and three to five seconds later its decision is on screen. I hold the controller and carry it out.
>
> What testing on recorded frames showed:
> - It read the scene right 16 out of 16 times.
> - It stays quiet in cutscenes and menus.
> - It is too slow for button prompts, so a human stays on the controller.
>
> AI decides, a human executes and checks. Same split I use at work.
>
> Watch live on YouTube (https://www.youtube.com/watch?v=MZLPv4uP8nQ), Twitch (https://twitch.tv/aabyzov), or X.

**Threads**
> AI runs my life in GTA 6, live right now. 🎮
>
> It watches my screen and calls every move. I just play it. Twitch chat can veto it.
>
> YouTube: https://www.youtube.com/watch?v=MZLPv4uP8nQ
> Twitch: https://twitch.tv/aabyzov

**Telegram (Russian, `t.me/antonaipower`)**
> Выхожу в прямой эфир по GTA 6.
>
> ИИ смотрит на экран и принимает решения за меня, а я играю на геймпаде. Чат на Twitch может написать VETO, и я сделаю наоборот.
>
> YouTube: https://www.youtube.com/watch?v=MZLPv4uP8nQ
> Twitch: https://twitch.tv/aabyzov

---

## Part 5: Fact-Check Ledger and Open Gaps

| Item | Verification Status | Notes |
|---|---|---|
| GTA 6 worldwide launch | **Verified** | Confirmed November 19, 2026 on PS5 and Xbox Series X\|S via Rockstar (`rockstargames.com/VI/out-now`) and Take-Two. |
| Five-tier criminal profile | **Secondary sources only** | Listed by Polygon and Clarín (Professional, Hardened, Violent, Psycho, Irredeemable); unconfirmed by Rockstar. Visible as an in-game icon (not hidden); Irredeemable takes hours. |
| Save position | **Verified from frames** | November 19, 5:55 PM frames show prison corridor behind the guard, PS5 suspended, 0 trophies. Cell and crossword already played. |
| Story beats after corridor | **Unverified in our play** | Counselor cutscene, robbery flashback, button prompt, chase, and scripted arrest come from games.gg and Fextralife guides. |
| AI vision caller (`ai-call.py`) | **Tested on saved frames; not tested live** | 16/16 scenes right on Fable 5.2 (`claude-fable-5-2`, `admin@easychamp.com` Max 20x); 3.3 to 5.2 s per call; capped at 25 calls. Live gameplay dry run still needed. |
| Twitch vote counter (`chat-vote.py`) | **Tested on live Twitch chat** | Read 281 lines in 25 s anonymously; Twitch `#aabyzov` only. YouTube and X chat are not auto-counted. |
| Controller automation / Jev / OpenAI Decisions | **Not built / Not configured** | Remote Play ignores Mac keyboard; Jev and OpenAI keys are absent on M5. You hold the DualSense. |
| OBS profile, overlays, and audio config | **Verified on M5** | Profile `GTA6 Twitch`, scene `PS5 Remote Window` (`AI Call`, `Chat Votes`, `GTA Remote Play`, `Camera Quadrant`, `Video sound`), `Mic/Aux` = Shure MV7+. Live gameplay audio levels still unverified. |
| Camera in OBS | **Fallback active (iPhone broken)** | iPhone Continuity Camera unavailable in OBS (another worker fixing). **MacBook Pro Camera** verified working as fallback; **Studio Display Camera** rendered black earlier today (check preview before using). Never select `iPhoneA` (USB screen mirror). |
| Streaming destinations | **Twitch & YouTube verified; X unverified** | YouTube `MZLPv4uP8nQ` Public with Auto-start/Auto-stop ON and G2 thumbnail. Twitch title and clips verified. X Producer was signed out in Chrome and not verified. |

### Source files and earlier reports
- Checked script v2: `/Users/anton/Projects/github/specweave-umb/.specweave/reports/threads/2026-11-20-ai-runs-my-life-in-gta-6-the-script-and-the-vira-80c754-845f05.md`
- Day 2 show plan and posts: `/Users/anton/Projects/github/specweave-umb/.specweave/reports/threads/2026-11-20-gta-6-live-day-2-show-plan-and-posts-80c754-487544.md`
- Vision test and cost report: `/Users/anton/Projects/github/specweave-umb/.specweave/reports/threads/2026-11-20-can-ai-call-my-moves-in-gta-6-tests-hosting-cues-80c754-8bebaa.md`
- OBS audio and destination preflight: `/Users/anton/Projects/github/specweave-umb/.specweave/reports/threads/2026-11-19-m5-obs-audio-ndi-tiles-and-caldigit-check-fd2103-ad86a6.md`
- Live scripts: `/Users/anton/.specwithcode/m4/scratch/2026-11-20-gta6-viral/ai-call.py`, `/Users/anton/.specwithcode/m4/scratch/2026-11-20-gta6-viral/chat-vote.py`, `/Users/anton/.specwithcode/m4/scratch/2026-11-20-gta6-viral/fix-capture.py`
