# 1026 Keep the Chrome extension connected and show when it is not

## Problem
On October 23, 2026 at 8:00 AM EDT the EasyChamp SEO watch got `chrome_profiles` = [] on the M4 and fell back to Claude in Chrome, which asked the user to pick among four unnamed browsers. The user reports the SpecWithCode Browser extension drops after some days and needs a manual Reconnect, and the toolbar icon looks the same when it is off. Source review of `apps/chrome-extension/src/background.js` (store 1.0.1, repo 1.0.3): a 4401 close ("pairing code rejected") is terminal, so one rejected attempt (for example another SpecWithCode server briefly holding port 8319 while the real service restarts) stops every retry until Reconnect; the keepalive ping gets no reply, so a dead socket can still show Connected; the badge is blank for every state except Connected and Rejected; status is lost when Chrome stops the worker. The service keeps no relay history, so the last disconnect reason is unknowable after the fact.

## Scope
In: extension retry policy, heartbeat, badge/tooltip/popup status, session-persisted status, relay pong and welcome capability, last-disconnect hint in `chrome_profiles`. Out: token TTL or revocation changes, new extension permissions, service restarts. The Chrome Web Store upload of 1.0.4 is done after merge with the user's approval of October 23.

## Acceptance Criteria
- [ ] AC-01: After a 4401 close the extension keeps retrying with a slow backoff (30 s up to 5 min) and connects on its own once the service accepts the unchanged token; a reset token is still refused by the service (no revocation bypass), and Pause and Unpair stop all attempts.
- [ ] AC-02: With a service that answers pings, a socket that stops answering is torn down within 40 s and retried; an older service without the capability is never torn down for silence.
- [ ] AC-03: The toolbar badge and tooltip state the truth in text, not color alone: ON (connected), OFF red (paired but not connected, with since/next try), ! red (code not accepted, retrying), II (paused), OFF gray (not paired); the popup shows the same state with when it was last connected and when the next try is.
- [ ] AC-04: Status survives the service worker being stopped (chrome.storage.session), and opening the popup triggers an immediate attempt when disconnected.
- [ ] AC-06: When SpecWithCode Browser is paired on the machine, Claude threads do not get Claude Code's built-in Claude in Chrome tools, so agents use the named SpecWithCode profile instead of asking the user to pick an unnamed browser; a Settings › Chrome switch turns this off, and threads without a paired profile keep Claude in Chrome.
- [ ] AC-05: The relay answers ping with pong and advertises heartbeat in welcome; `chrome_profiles` with no profile names the last profile that disconnected, when, and why.

## Approach
Extension: retry schedule per phase, heartbeat armed only when welcome says `heartbeat: true`, badge from phase, session-stored status and retry-not-before. Server: `relayHub.ts` pong + welcome capability + last-disconnect record; `chromeTools.ts` hint. Tests in `apps/chrome-extension/test/background.test.js` and `apps/server/src/browserExtension/chromeTools.test.ts`. Version 1.0.4.

## Decisions
### Defaulted
- D-01: Rejected retries back off to 5 min; loopback only, the server still verifies the token.
- D-02: Unpaired profiles show a gray OFF, not red, so profiles the user never paired do not look broken.
### Open
- none

## Tasks

### T-01 Extension reconnect, heartbeat and truthful status
- AC: AC-01, AC-02, AC-03, AC-04 | Files: /Users/antonabyzov/.specwithcode/m4/worktrees/chrome-extension-reconnect/apps/chrome-extension/src/background.js, /Users/antonabyzov/.specwithcode/m4/worktrees/chrome-extension-reconnect/apps/chrome-extension/src/popup.js, /Users/antonabyzov/.specwithcode/m4/worktrees/chrome-extension-reconnect/apps/chrome-extension/test/background.test.js | Test: cd /Users/antonabyzov/.specwithcode/m4/worktrees/chrome-extension-reconnect/apps/chrome-extension && node ../../node_modules/vite-plus/bin/vp test run

### T-02 Relay pong, heartbeat capability and last-disconnect hint
- AC: AC-05, AC-02 | Files: /Users/antonabyzov/.specwithcode/m4/worktrees/chrome-extension-reconnect/apps/server/src/browserExtension/relayHub.ts, /Users/antonabyzov/.specwithcode/m4/worktrees/chrome-extension-reconnect/apps/server/src/browserExtension/chromeTools.ts, /Users/antonabyzov/.specwithcode/m4/worktrees/chrome-extension-reconnect/apps/server/src/browserExtension/chromeTools.test.ts | Test: cd /Users/antonabyzov/.specwithcode/m4/worktrees/chrome-extension-reconnect/apps/server && node ../../node_modules/vite-plus/bin/vp test run src/browserExtension

### T-04 Prefer SpecWithCode Browser over Claude in Chrome for Claude threads
- AC: AC-06 | Files: /Users/antonabyzov/.specwithcode/m4/worktrees/chrome-extension-reconnect/apps/server/src/orchestration-v2/Adapters/ClaudeAdapterV2.ts, /Users/antonabyzov/.specwithcode/m4/worktrees/chrome-extension-reconnect/apps/server/src/browserExtension/BrowserExtension.ts | Test: cd /Users/antonabyzov/.specwithcode/m4/worktrees/chrome-extension-reconnect/apps/server && node ../../node_modules/vite-plus/bin/vp test run src/browserExtension src/orchestration-v2/Adapters/ClaudeAdapterV2.test.ts

### T-03 Verify and close 1026
- AC: AC-01, AC-02, AC-03, AC-04, AC-05 | Files: /Users/antonabyzov/.specwithcode/m4/evidence/chrome-routing-20261023/report.md | Test: cd /Users/antonabyzov/.specwithcode/m4/worktrees/chrome-extension-reconnect && node apps/chrome-extension/scripts/build.mjs --check
