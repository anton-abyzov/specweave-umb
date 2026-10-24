# Implement desktop push notifications

## Problem

SpecWithCode has renderer-driven browser notifications and an Electron native delivery bridge, but notification settings only offer a mode selector. There is no explicit connect, status, test or disconnect flow. Input-needed alerts override the mode, permission failures are opaque, reconnect clears baselines, and native targets omit project identity. Anton wants useful user-action alerts without a mobile application.

## Scope

In: shipped Claude Code evidence and official documentation; clean-room delivery decisions; native desktop and secure browser notification connection; permission/status/test/disconnect controls; persistent deduplication and reconnect behavior; correct machine/project/thread click targets; focused lifecycle and headless UI validation; reviewed PR with exact-head CI.

Out: mobile applications, paid transports, new accounts, hosted relay activation, installed service restarts, release or integration ownership. Browser delivery while the page is closed is not claimed: the current private WebSocket architecture has no Web Push subscription transport. Native delivery requires the app to run. Explicitly show these limits in settings.

## Acceptance Criteria

- [ ] AC-01: A research receipt identifies the shipped Claude Code artifact and REA evidence, distinguishes terminal notifications/hooks from native/browser push, and records observations, inferences and unknowns without copying implementation.
- [ ] AC-02: Device-local notification settings expose connect, permission/status, send test, disconnect and opt-out. Requests follow user gestures; denied/revoked/unsupported states give an actionable explanation. Native status does not claim browser permission proves OS delivery.
- [ ] AC-03: User input and approval transitions notify; ordinary background waits do not become blocked alerts. Disconnect prevents all system delivery including input-needed overrides and withdraws outstanding alerts. Existing sound and in-app preferences remain usable.
- [ ] AC-04: Delivery uses environment-scoped event identities, survives reconnect/reload without duplicate replay, and handles multiple windows/tabs. First connection avoids historical completion floods while surfacing current unresolved user-action requests.
- [ ] AC-05: Notification clicks route to the originating environment, project and thread. Native pending clicks survive renderer reload; failed/denied delivery does not claim successful physical presentation.
- [ ] AC-06: Focused automated lifecycle, permission and routing tests and headless desktop/narrow UI captures pass. Native OS delivery/click acceptance is recorded separately from mocks and headless proof; if installed acceptance requires release, it remains an explicit gate.
- [ ] AC-07: A fresh-context review and exact-head CI support a reviewable PR, with integration/release left to Complete screenshot sessions.

## Approach

Worktree: `/Users/antonabyzov/.specwithcode/m4/worktrees/desktop-notifications-1036`, branch `feat/desktop-notifications-1036`, based on `61e382c9c`. Extend existing notification adapters and coordinator rather than invent another feed. Use existing client settings storage and layout tokens. Keep 1031's broad settings redesign untouched; its spec is proposal-only, and no proposal artifact exists at its declared path as of this inspection. Keep state and permission semantics independent: OS permission is never inferred from a saved preference. A compact notification row holds connection status and actions, with the existing mode selector subordinate to connection.

## Decisions

### Asked
- None. Implementation and a reviewed PR are explicitly authorized; merge/release remain with their owner.
### Defaulted (change any before sw-do)
- D-01: Use existing local native and secure-browser delivery without a new hosted transport. Clearly state the running-app/open-page limit.
- D-02: Notification connection and deduplication are per client device and environment, not replicated to paired machines.
- D-03: Keep settings navigation, fonts and semantic colors unchanged. Buttons read Connect notifications, Send test and Disconnect.
### Open
- None.

## Tasks

### T-01 Research Claude Code and specify delivery
- AC: AC-01 | Files: /Users/antonabyzov/.specwithcode/m4/evidence/notifications-1036/research, /Users/antonabyzov/.specwithcode/m4/worktrees/desktop-notifications-1036/docs/notifications.md | Test: test -s /Users/antonabyzov/.specwithcode/m4/evidence/notifications-1036/research/findings.md

### T-02 Implement notification connection and lifecycle
- AC: AC-02, AC-03, AC-04, AC-05 | Files: /Users/antonabyzov/.specwithcode/m4/worktrees/desktop-notifications-1036/apps/web/src/components/settings/NotificationSettings.tsx, /Users/antonabyzov/.specwithcode/m4/worktrees/desktop-notifications-1036/apps/web/src/notificationConnection.ts, /Users/antonabyzov/.specwithcode/m4/worktrees/desktop-notifications-1036/apps/web/src/notificationHistory.ts, /Users/antonabyzov/.specwithcode/m4/worktrees/desktop-notifications-1036/apps/web/src/components/ThreadNotificationCoordinator.tsx, /Users/antonabyzov/.specwithcode/m4/worktrees/desktop-notifications-1036/packages/contracts/src/ipc.ts, /Users/antonabyzov/.specwithcode/m4/worktrees/desktop-notifications-1036/apps/desktop/src/ipc/methods/threadNotifications.ts, /Users/antonabyzov/.specwithcode/m4/worktrees/desktop-notifications-1036/apps/web/src/components/settings/SettingsPanels.tsx | Test: node node_modules/vite-plus/bin/vp test run apps/web/src/notificationConnection.test.ts apps/web/src/notificationHistory.test.ts apps/web/src/components/ThreadNotificationCoordinator.test.tsx apps/desktop/src/ipc/methods/threadNotifications.test.ts

### T-03 Validate lifecycle and UI
- AC: AC-02, AC-03, AC-04, AC-05, AC-06 | Files: /Users/antonabyzov/.specwithcode/m4/worktrees/desktop-notifications-1036/apps/web/src/components/ThreadNotificationCoordinator.badge.test.tsx, /Users/antonabyzov/.specwithcode/m4/worktrees/desktop-notifications-1036/apps/web/src/notificationConnection.test.ts, /Users/antonabyzov/.specwithcode/m4/worktrees/desktop-notifications-1036/apps/web/src/notificationHistory.test.ts, /Users/antonabyzov/.specwithcode/m4/worktrees/desktop-notifications-1036/apps/web/src/components/ThreadNotificationCoordinator.test.tsx, /Users/antonabyzov/.specwithcode/m4/worktrees/desktop-notifications-1036/apps/desktop/src/ipc/methods/threadNotifications.test.ts, /Users/antonabyzov/.specwithcode/m4/worktrees/desktop-notifications-1036/apps/web/tests/notifications, /Users/antonabyzov/.specwithcode/m4/evidence/notifications-1036 | Test: node apps/web/tests/notifications/check.mjs

### T-05 Repair F-06 scoped active notification identity
- AC: AC-03, AC-05 | Files: /Users/antonabyzov/.specwithcode/m4/worktrees/desktop-notifications-1036/apps/web/src/hooks/useActiveNotificationThread.ts, /Users/antonabyzov/.specwithcode/m4/worktrees/desktop-notifications-1036/apps/web/src/components/ThreadNotificationCoordinator.tsx, /Users/antonabyzov/.specwithcode/m4/worktrees/desktop-notifications-1036/apps/web/src/components/ThreadNotificationCoordinator.test.tsx | Test: node node_modules/vite-plus/bin/vp test run apps/web/src/components/ThreadNotificationCoordinator.test.tsx

### T-06 Integrate 1040 shared action contract
- AC: AC-03, AC-04, AC-05, AC-07 | Files: /Users/antonabyzov/.specwithcode/m4/worktrees/desktop-notifications-1036/apps/web/src/components/ThreadNotificationCoordinator.tsx, /Users/antonabyzov/.specwithcode/m4/worktrees/desktop-notifications-1036/apps/web/src/components/ThreadNotificationCoordinator.test.tsx, /Users/antonabyzov/.specwithcode/m4/worktrees/desktop-notifications-1036/apps/web/src/notificationEpisodes.ts, /Users/antonabyzov/.specwithcode/m4/worktrees/desktop-notifications-1036/apps/web/src/notificationEpisodes.test.ts | Test: node node_modules/vite-plus/bin/vp test run apps/web/src/components/ThreadNotificationCoordinator.test.tsx

Dependency: PR #655 `ce10160adb07188234039c609aab30a148729471`, stacked without rewriting previous notification commits. User-action candidates come from the shared classifier and revalidate immediately before delivery. Revision-based plan/held shell actions notify only on explicit transitions, never on first snapshot or unrelated revision updates. Operational/history notifications remain separate. Final reviewer and CI must bind the resulting head; signed-app OS acceptance remains open.

### T-04 Verify and close 1036
- AC: AC-06, AC-07 | Files: /Users/antonabyzov/Projects/github/specweave-umb/.specweave/increments/1036-implement-desktop-push-notifications/spec.md, /Users/antonabyzov/.specwithcode/m4/evidence/notifications-1036/review.md | Test: npx --yes specweave@3.1.7 verify 1036
