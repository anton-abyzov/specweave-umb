# Pair a Chrome profile without pasting a code

Child of 1387. It takes over 1387's AC-20. It starts with a spike that can end it.

## Problem

Pairing a Chrome profile today means copying a code from SpecWithCode and pasting it into the extension. 1387 makes that as short as it can be with the current extension: pick the profile, one press copies the code, the extension's page opens on install with the field focused. Anton asked for better: "auto-pair with no code to paste, if the extension can safely receive it". Paths are in `repositories/anton-abyzov/specwithcode` at `origin/main` `d65dffec9`; the files cited here did not change since the first pin, `a23f3593f`.

The second review round showed that the first design was not safe as written:

- The relay accepts any loopback connection whose `Origin` starts with `chrome-extension://` (`apps/server/src/browserExtension/BrowserExtension.ts:71-77`). The extension id is whatever the client says it is (`apps/server/src/browserExtension/relayHub.ts:176`) and only sets a display flag. Any other extension, and any local program that forges the header, passes.
- A one-time offer id opened as `pair.html#<port>.<id>` rides in Chrome's command line (`open -na … --args <url>`, `apps/desktop/src/preview/ExternalBrowsers.ts`), where any program of the same user can read it for as long as it is valid.
- Worse, a local program could open the extension's genuine pairing page pointed at its own port. One click there would hand the user's signed-in Chrome profile to that program. Today that takes talking the user into pasting a foreign code.

So the question is not "can the page receive a code". It is "can one click in Chrome pair only with the SpecWithCode the user is looking at". That is not known yet.

## Scope

In: a spike that answers that question on macOS, Windows and Linux. If it passes: "Pair in Chrome", a one-time offer confirmed with one click in the extension's own page. Independently of the spike: the relay accepts only the store extension.

Out: the copy path, the profile picker, the extension's install page and names (1387). A token per profile, or tokens that expire. Native messaging and any new Chrome permission.

## Acceptance Criteria

### The spike

- [ ] AC-01: The spike is recorded in `reports/spike.md` with what was run on each system, and answers three questions:
  1. Does Chrome open `chrome-extension://<store id>/pair.html#…` in a chosen profile from the desktop app, and does the page read the fragment before removing it from the address bar and history?
  2. Can the page be made to talk only to the SpecWithCode that opened it? Candidates to try: the page connects only to the port the extension last paired with or the app's default ports (`packages/shared/src/studioIdentity.ts:8`) while the real app holds them; the offer is delivered to the page by the already paired extension of another profile, not by the URL; the user types the 4-digit number from SpecWithCode into the page instead of comparing it.
  3. Is the result easier to trick than pasting a code is today?
- [ ] AC-02: The kill rule. If question 2 has no answer that a local program cannot sidestep with less effort than today's paste, or question 1 fails on macOS, the increment closes as abandoned with `reports/spike.md` as its result, 1387's copy path stays the only way, and no "Pair in Chrome" ships. On a system where only question 1 fails, that system keeps the copy path and shows no "Pair in Chrome".

### The relay, whatever the spike says

- [ ] AC-03: The relay turns away other extensions and websites. `relayRequestAllowed` requires `Origin` to be exactly `chrome-extension://okoinngelinfjfkmkcnbgndapeiofgbb`. This is a gate for browsers, not proof of who is calling: a local program can send any `Origin` (`apps/server/src/browserExtension/BrowserExtension.ts:71`), so the pairing token stays the only authentication, and a request with the store origin and no valid token can neither pair nor connect. A copy loaded by hand connects only while a developer switch in Settings > Chrome is on, and its profile is labelled "not from the Chrome Web Store" as today (`fromStore`, `packages/contracts/src/browserExtension.ts:54`). Tests: another extension's origin is refused; the prefix alone is refused; the switch admits a hand-loaded id; the store origin with a missing or wrong token is refused for pairing and for connecting. This changes who may connect, so it ships only with Anton's yes (D-02).

### Pair in Chrome, only if the spike passes

- [ ] AC-04: Desktop app only. "Pair in Chrome" makes the server open one offer: a 128-bit one-time id and a 4-digit number, valid 120 s, single use, closed after five wrong ids or when the user leaves the row. The desktop app opens the extension's pairing page in the profile picked in 1387's row. `ExternalBrowsers` opens only http(s) today; it gains exactly one more shape, that page of the store extension id.
- [ ] AC-05: The page shows, in this order: "Only continue if you just pressed Pair in SpecWithCode on this computer."; "SpecWithCode on {machine} asks to pair this Chrome profile."; the number check the spike chose; the name field of 1387 (starting with Chrome's own name for the profile, which the offer carries); "Pair this profile" and "Not now".
- [ ] AC-06: Only the click on "Pair this profile" makes the extension ask for the machine's token over the socket and store it. The token never appears in a URL, a command line or the clipboard. The page is not web accessible, so no website can open it.
- [ ] AC-07: The row in SpecWithCode reads "Confirm in Chrome." with the number. After 20 s with no page connected: "Chrome did not open the pairing page. Add the extension to this profile first, or copy the code instead." The copy path stays one press away in every state.
- [ ] AC-08: Tests: an expired, used or unknown offer returns nothing; a forged origin is refused (AC-03); an offer id presented by a second client after the page connected is refused and closes the offer; the token is sent only after the pair message; leaving the row closes the offer.
- [ ] AC-09: `manifest.json` permissions are unchanged (`apps/chrome-extension/store/SUBMISSION.md:9`), so Chrome does not switch the extension off for anyone.

### Gate, review, shipping

- [ ] AC-10: No code before Anton accepts. The gate is the line "Accepted by Anton on <date>" in 1387's spec, with D-01 and D-02 answered here.
- [ ] AC-11: Muse Wonder Full 1.0 at Extra High, with full access, reviews `reports/spike.md` before AC-04 starts, and each PR at its head, as a security review first. Every finding is fixed or answered in `reports/reviews/`. Each PR is green, merged and released. The extension update goes through store review.

## Approach

1. T-02, the spike. Throwaway code in a scratch folder. It ends with a yes or a no in `reports/spike.md`.
2. T-03, the relay change, in its own PR. It needs no spike.
3. T-04 and T-05 only on a yes.

What was weighed before, and stays rejected:

| Way | Verdict |
|---|---|
| Pair on install, no click | Rejected. Installing would hand a profile to agents. |
| Any local page may message the extension (`externally_connectable` on loopback) | Rejected. A dev server's page could ask to pair. |
| Native messaging host | Rejected. The new permission makes Chrome switch the extension off for everyone until they accept it. |
| Reading the clipboard in the extension | Rejected. Same new-permission cost. |

Risks: the spike may say no, and then this increment ships only AC-03. The extension update waits on store review, which takes days because of its `debugger` permission. AC-03 breaks hand-loaded copies until the switch is on, which only developers use.

## Decisions

### Asked
- D-01, for Anton: spend the spike? Recommended **A. Yes, the spike only, with the kill rule of AC-02. Nothing is promised until it passes.** B. Stop at 1387's copy path. **Decided November 18, 2026: A, then B later the same day.** The spike was not run: two worker runs were stopped by the provider's safety check before any check started, and a stopped step is not retried or handed to another worker. Asked whether to drop "Pair in Chrome" and keep the copy path, Anton answered: "Yes, do what's recommended." So no "Pair in Chrome" ships and 1387's copy path is the only way to pair. T-02, T-04 and T-05 are skipped with that as the reason. T-06 closes this increment the normal way with AC-03 alone, not as abandoned; `reports/spike.md` records that nothing was run.
- D-02, for Anton: the relay. Recommended **A. Accept only the store extension, with a developer switch for hand-loaded copies.** B. Leave it as it is. A is recommended because today any other extension in the same Chrome that learns the code can connect. It is asked because it changes who may connect. **Decided November 18, 2026: A.**

### Defaulted (change any before sw-do)
- D-03: No new Chrome permission, ever, in this increment.
- D-04: One token per machine stays. A token per profile is its own piece of work.

### Open
- none

## Review

- Reviewer: meta (muse-wonder-full-1.0)
- Depth: deep
- Required: yes

Round 2 on 1387 raised the two blockers this spec is built around. They and the answers are in 1387's `reports/reviews/`.

## Tasks

### T-01 Acceptance: 1387 is accepted and D-01, D-02 are answered
- AC: AC-10 | Files: none | Test: grep -q "Accepted by Anton on" .specweave/increments/1387-first-run-setup-rethought-one-working-agent-models-by-role-chrome-and-mac-access-machines-and-phone/spec.md

### T-02 Spike: can one click in Chrome pair only with the SpecWithCode on screen
- AC: AC-01, AC-02 | Files: none | Test: grep -Eq "^Verdict: (pass|stop)" .specweave/increments/1394-pair-a-chrome-profile-without-pasting-a-code/reports/spike.md

### T-03 The relay accepts only the store extension
- AC: AC-03 | Files: repositories/anton-abyzov/specwithcode/apps/server/src/browserExtension/BrowserExtension.ts, repositories/anton-abyzov/specwithcode/apps/server/src/browserExtension/BrowserExtension.test.ts, repositories/anton-abyzov/specwithcode/apps/server/src/browserExtension/chromeTools.test.ts, repositories/anton-abyzov/specwithcode/apps/server/src/browserExtension/relayHub.ts, repositories/anton-abyzov/specwithcode/packages/contracts/src/settings.ts, repositories/anton-abyzov/specwithcode/apps/web/src/components/settings/BrowserExtensionSettings.tsx | Test: cd repositories/anton-abyzov/specwithcode/apps/server && node ../../node_modules/vite-plus/bin/vp test run src/browserExtension

### T-04 The one-time offer on the server and in the extension's page (only after a pass)
- AC: AC-04, AC-05, AC-06, AC-08, AC-09 | Files: repositories/anton-abyzov/specwithcode/apps/server/src/browserExtension/pairingOffer.ts, repositories/anton-abyzov/specwithcode/apps/server/src/browserExtension/pairingOffer.test.ts, repositories/anton-abyzov/specwithcode/apps/server/src/browserExtension/BrowserExtension.ts, repositories/anton-abyzov/specwithcode/packages/contracts/src/browserExtension.ts, repositories/anton-abyzov/specwithcode/apps/chrome-extension/src/pair.html, repositories/anton-abyzov/specwithcode/apps/chrome-extension/src/pair.js, repositories/anton-abyzov/specwithcode/apps/chrome-extension/src/background.js, repositories/anton-abyzov/specwithcode/apps/chrome-extension/test/extension.test.js, repositories/anton-abyzov/specwithcode/apps/server/src/browserExtension/extensionVersion.generated.ts | Test: cd repositories/anton-abyzov/specwithcode/apps/server && node ../../node_modules/vite-plus/bin/vp test run src/browserExtension/pairingOffer.test.ts && cd ../chrome-extension && node ../../node_modules/vite-plus/bin/vp test run

### T-05 "Pair in Chrome" in the app (only after a pass)
- AC: AC-04, AC-07 | Files: repositories/anton-abyzov/specwithcode/apps/web/src/components/settings/BrowserExtensionSetup.tsx, repositories/anton-abyzov/specwithcode/apps/web/src/components/settings/BrowserExtensionSetup.test.tsx, repositories/anton-abyzov/specwithcode/apps/desktop/src/preview/ExternalBrowsers.ts, repositories/anton-abyzov/specwithcode/apps/desktop/src/preview/ExternalBrowsers.test.ts | Test: cd repositories/anton-abyzov/specwithcode/apps/desktop && node ../../node_modules/vite-plus/bin/vp test run src/preview/ExternalBrowsers.test.ts && cd ../web && node ../../node_modules/vite-plus/bin/vp test run src/components/settings/BrowserExtensionSetup.test.tsx

### T-06 Review, ship, verify and close, or close as abandoned with the spike's result
- AC: AC-11 | Files: none | Test: specweave verify 1394-pair-a-chrome-profile-without-pasting-a-code
