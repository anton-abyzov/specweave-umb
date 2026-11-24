---
title: "Livestream one-page script, November 20, 2026"
thread: "thread:delegated-task:command%3Amcp%3A5203f9f6-1c70-4578-a8a9-fc4f6def2ca7%3Adelegate-task%3Ae39e57d8-527e-47eb-85f1-fc96f841f3c8"
threadTitle: "Short GTA 6 livestream cheat sheet"
savedAt: "2026-11-20T20:02:22.128Z"
date: "November 20, 2026"
machine: "M5 (OBS, PS Remote Play); Gemini 4 Neon runs on M4"
long_version: "/Users/anton/Projects/github/specweave-umb/.specweave/reports/threads/2026-11-20-gta-6-livestream-full-script-and-run-sheet-5f882f-2ec49b.md"
---

# Livestream: one-page script (about 60 minutes)

Before you go live, do the pre-stream checklist in the long version (camera, Remote Play capture, `pause.flag`). Only one thing here is new: **Gemini 4 Neon is only on M4** (M5 has no GitHub Copilot). Start the Neon thread on M4 and watch it from SpecWithCode on M5.

| # | Min | What to say | What to do |
|---|---|---|---|
| 1 | 0–3 | "Today: I build something live with a two-day-old model, show you the app I build with, then GTA 6, and we find out whether AI can actually play it." | Scene `Starting Soon`, then `iPhone16` (face cam). Hold up the DualSense. |
| 2 | 3–8 | "Last time I built this with AI: a whole battle royale running in a browser tab." | Scene `M5 + iPhone16` with a **clean desktop**. In `/Users/anton/Projects/fortnite-3js`, run `npm run dev`, or open `https://anton-abyzov.github.io/fortnite-3js/`. Do one drop and one drive. *Unconfirmed: whether EYEWALL was already shown on a stream. It was finished November 12. Yesterday's stream was GTA 6 with Claude vs Codex.* |
| 3 | 8–20 | "This is Gemini 4 Neon. Google released it on November 18 and claims it's the fastest and makes the fewest things up. One prompt, let's see." | Open SpecWithCode on M5 and start a thread **on M4** with Copilot, model Gemini 4 Neon, effort High. Send **one** prompt, because a Copilot thread can't take a message mid-turn: *"Single HTML file, no libraries: a top-down neon city driving game. Arrow keys drive, collect 10 coins against a 60-second timer, show score and time, restart on R. Original art, drawn shapes only."* Read out the speed while it streams. |
| 4 | 20–25 | "Now the honest part: does it actually work?" | Open the HTML in the browser and play for 30 seconds. Then send a second prompt with whatever broke, or with "add a Playwright test that loads the page and checks the timer counts down", and run it. Give the result as it happens, pass or fail. |
| 5 | 25–30 | "Here's why I use this app: all my AI subscriptions and all my machines, one coordinator." | In SpecWithCode, show the threads on M5 and M4 side by side. Then copy a small project to M4 from the project's machine menu, using **Copy to another machine** (*button label unverified, check in your dry run*). Never click scenes that show other windows. |
| 6 | 30–50 | "GTA 6. The AI watches my screen and calls the move, I play it. Chat can veto." | Scene `PS5 Remote Window`, then `rm` the `pause.flag`. Resume the save. **Don't start a new game.** Read the AI calls and the chat votes out loud. |
| 7 | 50–56 | "Could the AI hold the controller itself? Here's how it would work." | Back to `iPhone16`, run `touch pause.flag`. Talk through the box below, then hold up the cable. |
| 8 | 56–60 | "Score: AI calls against chat vetoes. Next time: should AI press the buttons?" | Run the poll, thank people, Stop Streaming, and confirm Multiple output stopped. |

## Segment 7: can AI play it? (say this, it's accurate)

**Reading what I press (works today, I just haven't built it).** A DualSense on a USB cable shows up on the Mac as a normal game controller. You can read it two ways:

- Apple's **GameController framework**. It has a DualSense profile (`GCDualSenseGamepad`) and fires an event for every button press and every stick move.
- The lower **HID** layer, which reads the controller's raw input reports.

One catch: since macOS 11.3, an app only gets controller input while it is in front, unless it sets `GCController.shouldMonitorBackgroundEvents` (Apple docs). Remote Play would be in front during play, so a logger needs that flag. In macOS 15.4 the flag broke, and Apple fixed it in 15.5. *Not tested here: whether a background logger and Remote Play both receive input from the same pad at the same time.*

**What the logger is good for.** Recording my inputs next to the screen frames gives you training data: "this is what a human pressed here."

**Making the AI press buttons (the hard part).** PS Remote Play on the Mac takes input from a real controller only. It ignores the keyboard, as we found on November 19. So the AI would need one of three routes:

1. A **virtual controller** that macOS shows to Remote Play as a DualSense. That needs a DriverKit virtual HID driver, which needs an entitlement from Apple. *Unverified: whether Remote Play would accept a virtual pad.*
2. A **third-party Remote Play client** such as chiaki-ng, which is open source and accepts the keyboard, so software can drive it. It's unofficial.
3. A **hardware box**, a microcontroller that pretends to be a controller over USB.

**Even then:** in our frame tests the model gave three different buttons for the same PS5 menu, and it takes about 4 seconds to decide. That's fine for "go left at the door" and far too slow for driving.

**Rules:** an automated controller in a single-player story is a grey area. In online play it's botting, and Rockstar's and Sony's terms forbid cheats and unauthorized automation (*paraphrased, no clause checked*). On stream we only read inputs. We never inject them.

Sources: [Apple, shouldMonitorBackgroundEvents](https://developer.apple.com/tutorials/data/documentation/gamecontroller/gccontroller/shouldmonitorbackgroundevents.md), [Apple, GCDualSenseGamepad](https://developer.apple.com/documentation/gamecontroller/gcdualsensegamepad.md), [Apple forums, macOS 15.4 background input regression](https://developer.apple.com/forums/thread/780929). Earlier tests: `/Users/anton/Projects/github/specweave-umb/.specweave/reports/threads/2026-11-20-can-ai-call-my-moves-in-gta-6-tests-hosting-cues-80c754-8bebaa.md`.
