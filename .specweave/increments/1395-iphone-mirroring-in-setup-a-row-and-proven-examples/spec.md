# iPhone Mirroring in setup: a row and proven examples

Child of 1387. It takes over 1387's AC-21 to AC-23. It starts with a spike that can end it.

## Problem

Agents can already reach apps on an iPhone through macOS's iPhone Mirroring window with the `computer_*` tools, and nothing in the product says so. Anton asked for an optional step with two or three practical examples, such as setting up an Instagram profile or publishing a video, "keeping to the rule that posts need the owner's yes".

It is not reliable today. `computer_click` often does nothing on the Mirroring window, typing works only with the pointer inside it, and only Latin text gets through (project memory, November 2026). The tools are built on `osascript` (`repositories/anton-abyzov/specwithcode/apps/desktop/src/computerUse/MacComputerUse.ts`), and no iPhone Mirroring code exists in `apps/`. Showing examples that do not work would be worse than showing nothing.

## Scope

In: making `computer_*` work on the Mirroring window, proving each example with a recorded run, and then one optional row in the Access step of first-run setup that shows only what was proven.

Out: any promise that every iPhone app works. A product-wide rule that agents stop before publishing (D-01). Android. Anything on the phone itself.

## Acceptance Criteria

### Proof first

- [ ] AC-01: Agents can drive the Mirroring window. On M4 with a paired iPhone, from a normal thread and with only the product's tools: `computer_click` lands on a named control 20 times out of 20, `computer_type` types Latin text into a focused field, and `computer_scroll` scrolls a list. The check is a script, `scripts/computer-use/iphone-mirroring-check.mjs`, that runs those steps and writes its log to `reports/iphone/`. It needs a phone, so no CI can run it. It is run by hand before any release that changes `apps/desktop/src/computerUse/`, and `docs/user/computer-use.md` names the macOS and iOS versions it last passed on.
- [ ] AC-02: The kill rule. If AC-01 cannot be met, no row ships. The increment closes with `reports/iphone/` as its result and one paragraph in `docs/user/computer-use.md` saying what works (agents can look at the phone's screen) and what does not.
- [ ] AC-03: Only proven examples ship. Each example has one recorded run on M4 with a real iPhone and only the product's `computer_*` tools, saved in `reports/iphone/`. An example without a passing run is cut. With none left, AC-02 applies. The candidates:
  - "Set up my Instagram profile: bio, link and photo. Show me before you save."
  - "Post the newest video in Photos as a Reel with this caption. Stop before Share and ask me."
  - "Walk through my app on the phone and screenshot each screen."

  Every example that would publish, send or save on an account ends by telling the agent to stop before the last button, and its recording shows the agent stopping. The runs need Anton's iPhone and an Instagram account he picks, and Share is his press.

### The row

- [ ] AC-04: "Your iPhone" is one more row in 1387's Access list, after Mac apps. `accessRows` returns it when Mac apps is shown and the machine's `iphoneMirroring` input is `present` (1387 AC-08). This increment supplies that input: the desktop main process checks that `/System/Applications/iPhone Mirroring.app` exists and hands the answer over the desktop bridge. A failed check is `unknown`, which hides the row. It is optional and has no grant of its own.
- [ ] AC-05: The row says: "Agents can work in apps on your iPhone through iPhone Mirroring." It reads "Needs Mac apps first" or "Ready to try". Opened, it shows "Open iPhone Mirroring", three steps (open iPhone Mirroring and enter the phone's passcode once; allow Mac apps above; ask an agent, and approve the access card for iPhone Mirroring the first time), the proven examples under "Tried with", and the limits. The limits are taken from Apple's iPhone Mirroring support page on the day of the build, with a link to it, plus the two this product adds: Latin text only, and it pauses when you pick the phone up.
- [ ] AC-06: The row never says the app asks before posting. It says: "Tell the agent where to stop. These examples do." (D-01).
- [ ] AC-07: "Open iPhone Mirroring" is a new desktop call. It opens that one app and nothing else, and has an entry in `apps/desktop/src/ipc/channels.ts`. Tests cover the row's states and that the call takes no argument.

### Gate, review, shipping

- [ ] AC-08: No code before Anton accepts. The gate is the line "Accepted by Anton on <date>" in 1387's spec, with D-01 answered here.
- [ ] AC-09: The row's strings go through `t` or `tx` with entries in de, es, fr, ja, ko, pt, ru and zh. `docs/user/computer-use.md` gains an iPhone section. CHANGELOG Unreleased has the entry. Muse Wonder Full 1.0 at Extra High reviews each PR at its head. Each PR is green, merged and released.

## Approach

1. T-02: fix clicking, typing and scrolling on the Mirroring window, and write the check script.
2. T-03: run and record each example with Anton's phone. Cut what fails.
3. T-04: the row, only with what passed. It lands after 1387's PR B, which owns the Access list and `accessRows`.

Rejected: shipping the row first and the proof later. Round 2 of the review pointed out that the row's state with no proven example was undefined, and a row that promises what does not work costs trust. Rejected: its own stage in setup. It is one optional row.

Risks: iPhone Mirroring is Apple's, and its window may resist synthetic input. Then AC-02 applies. The runs need Anton's time and phone.

## Decisions

### Asked
- D-01, for Anton: posting. Recommended **A. The examples tell the agent to stop before the last button, and the row does not claim the app enforces it.** B. Add a product rule that every agent stops and asks before publishing, sending, buying or deleting through the browser or the computer. B changes every agent's behaviour for every user, so it deserves its own increment. **Decided November 18, 2026: A.**

### Defaulted (change any before sw-do)
- D-02: No row without at least one proven example.
- D-03: The limits come from Apple's page with a link, not from memory.

### Open
- none

## Review

- Reviewer: meta (muse-wonder-full-1.0)
- Depth: deep
- Required: yes

Round 2 on 1387 raised the ordering blocker this spec fixes. It and the answer are in 1387's `reports/reviews/`.

## Tasks

### T-01 Acceptance: 1387 is accepted and D-01 is answered
- AC: AC-08 | Files: none | Test: grep -q "Accepted by Anton on" .specweave/increments/1387-first-run-setup-rethought-one-working-agent-models-by-role-chrome-and-mac-access-machines-and-phone/spec.md

### T-02 `computer_*` works on the iPhone Mirroring window, with a check script
- AC: AC-01, AC-02 | Files: repositories/anton-abyzov/specwithcode/apps/desktop/src/computerUse/MacComputerUse.ts, repositories/anton-abyzov/specwithcode/apps/desktop/src/computerUse/computerUseSteps.ts, repositories/anton-abyzov/specwithcode/apps/desktop/src/computerUse/computerUseSteps.test.ts, repositories/anton-abyzov/specwithcode/scripts/computer-use/iphone-mirroring-check.mjs | Test: grep -q "20 of 20" .specweave/increments/1395-iphone-mirroring-in-setup-a-row-and-proven-examples/reports/iphone/check.log && cd repositories/anton-abyzov/specwithcode/apps/desktop && node ../../node_modules/vite-plus/bin/vp test run src/computerUse

### T-03 Run and record each example with Anton's phone, and cut the ones that fail
- AC: AC-03 | Files: none | Test: grep -Eq "^Proven: [1-3]" .specweave/increments/1395-iphone-mirroring-in-setup-a-row-and-proven-examples/reports/iphone/examples.md

### T-04 The "Your iPhone" row, with only what passed
- AC: AC-04, AC-05, AC-06, AC-07 | Files: repositories/anton-abyzov/specwithcode/apps/web/src/components/onboarding/IPhoneRow.tsx, repositories/anton-abyzov/specwithcode/apps/web/src/components/onboarding/IPhoneRow.test.tsx, repositories/anton-abyzov/specwithcode/apps/web/src/onboarding/accessRows.logic.ts, repositories/anton-abyzov/specwithcode/apps/web/src/onboarding/accessRows.logic.test.ts, repositories/anton-abyzov/specwithcode/packages/contracts/src/ipc.ts, repositories/anton-abyzov/specwithcode/apps/desktop/src/preload.ts, repositories/anton-abyzov/specwithcode/apps/desktop/src/ipc/channels.ts, repositories/anton-abyzov/specwithcode/apps/desktop/src/ipc/methods/computerUse.ts | Test: cd repositories/anton-abyzov/specwithcode/apps/web && node ../../node_modules/vite-plus/bin/vp test run src/components/onboarding/IPhoneRow.test.tsx src/onboarding/accessRows.logic.test.ts

### T-05 Translations, docs, changelog, review, ship, verify and close
- AC: AC-09 | Files: repositories/anton-abyzov/specwithcode/apps/web/src/i18n/messages/en.ts, repositories/anton-abyzov/specwithcode/apps/web/src/i18n/messages/de.ts, repositories/anton-abyzov/specwithcode/apps/web/src/i18n/messages/es.ts, repositories/anton-abyzov/specwithcode/apps/web/src/i18n/messages/fr.ts, repositories/anton-abyzov/specwithcode/apps/web/src/i18n/messages/ja.ts, repositories/anton-abyzov/specwithcode/apps/web/src/i18n/messages/ko.ts, repositories/anton-abyzov/specwithcode/apps/web/src/i18n/messages/pt.ts, repositories/anton-abyzov/specwithcode/apps/web/src/i18n/messages/ru.ts, repositories/anton-abyzov/specwithcode/apps/web/src/i18n/messages/zh.ts, repositories/anton-abyzov/specwithcode/docs/user/computer-use.md, repositories/anton-abyzov/specwithcode/CHANGELOG.md | Test: specweave verify 1395-iphone-mirroring-in-setup-a-row-and-proven-examples
